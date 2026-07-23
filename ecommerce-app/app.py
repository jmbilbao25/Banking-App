import os
import io
import uuid
import qrcode
import time
from flask import Flask, request, jsonify, render_template, send_file, redirect, url_for, session
from models import db, User

app = Flask(__name__)
app.secret_key = 'super-secret-ecommerce-key'

# Setup local SQLite DB for simple auth
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///ecommerce.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

with app.app_context():
    db.create_all()
    
BANK_PUBLIC_BASE = os.environ.get('BANK_PUBLIC_BASE', 'http://127.0.0.1:5001')
MERCHANT_ACCOUNT = os.environ.get('MERCHANT_ACCOUNT', 'jmb-grocery')

PRODUCTS = [
    {"id": "p1", "name": "Jasmine Rice (5kg)", "price": 12.00, "image": "🍚"},
    {"id": "p2", "name": "Fresh Eggs (12pcs)", "price": 4.50, "image": "🥚"},
    {"id": "p3", "name": "Whole Milk (1L)", "price": 3.00, "image": "🥛"},
    {"id": "p4", "name": "Chicken Breast (1kg)", "price": 8.50, "image": "🍗"},
    {"id": "p5", "name": "Bananas (bundle)", "price": 2.50, "image": "🍌"}
]

# Simple in-memory storage for orders since it's a prototype
ORDERS = {}

@app.route('/health')
def health():
    return jsonify({"status": "ok"})

@app.route('/')
def home():
    current_user = User.query.get(session['user_id']) if 'user_id' in session else None
    cart = session.get('cart', {})
    cart_count = sum(cart.values())
    return render_template('store.html', products=PRODUCTS, theme="JMB Grocery", current_user=current_user, cart_count=cart_count)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if User.query.filter_by(username=username).first():
            return render_template('register.html', error="Username taken")
        
        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()
        
        session['user_id'] = new_user.id
        return redirect(url_for('home'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session['user_id'] = user.id
            return redirect(url_for('home'))
        return render_template('login.html', error="Invalid credentials")
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('home'))

@app.route('/cart')
def view_cart():
    cart = session.get('cart', {})
    cart_items = []
    total = 0
    for product_id, quantity in cart.items():
        product = next((p for p in PRODUCTS if p["id"] == product_id), None)
        if product:
            subtotal = product['price'] * quantity
            total += subtotal
            cart_items.append({"product": product, "quantity": quantity, "subtotal": subtotal})
    return render_template('cart.html', cart_items=cart_items, total=total)

@app.route('/cart/add/<product_id>')
def add_to_cart(product_id):
    cart = session.get('cart', {})
    cart[product_id] = cart.get(product_id, 0) + 1
    session['cart'] = cart
    return redirect(url_for('home'))

@app.route('/cart/remove/<product_id>')
def remove_from_cart(product_id):
    cart = session.get('cart', {})
    if product_id in cart:
        del cart[product_id]
        session['cart'] = cart
    return redirect(url_for('view_cart'))

@app.route('/checkout/create')
def create_checkout():
    cart = session.get('cart', {})
    if not cart:
        return redirect(url_for('home'))
        
    order_items = []
    total = 0
    for product_id, quantity in cart.items():
        product = next((p for p in PRODUCTS if p["id"] == product_id), None)
        if product:
            subtotal = product['price'] * quantity
            total += subtotal
            order_items.append({"product": product, "quantity": quantity, "subtotal": subtotal})
            
    order_id = str(uuid.uuid4())[:8]
    ORDERS[order_id] = {
        "id": order_id,
        "items": order_items,
        "total": total,
        "status": "PENDING",
        "expires_at": int(time.time()) + 300  # 5 minutes expiration
    }
    
    session.pop('cart', None)
    return redirect(url_for('checkout', order_id=order_id))

@app.route('/checkout/<order_id>')
def checkout(order_id):
    order = ORDERS.get(order_id)
    if not order:
        return "Order not found", 404
        
    if order['status'] == 'PENDING' and time.time() > order['expires_at']:
        order['status'] = 'EXPIRED'
        
    payment_url = f"{BANK_PUBLIC_BASE}/pay?order_id={order_id}&amount={order['total']}&merchant_account={MERCHANT_ACCOUNT}&expires={order['expires_at']}"
    return render_template('checkout.html', order=order, payment_url=payment_url)

@app.route('/api/orders/<order_id>/status')
def order_status(order_id):
    order = ORDERS.get(order_id)
    if not order:
        return jsonify({"error": "not found"}), 404
        
    if order['status'] == 'PENDING' and time.time() > order['expires_at']:
        order['status'] = 'EXPIRED'
        
    return jsonify({"status": order["status"]})

@app.route('/api/orders/<order_id>')
def get_order(order_id):
    order = ORDERS.get(order_id)
    if not order:
        return jsonify({"error": "not found"}), 404
    return jsonify(order)

@app.route('/api/orders/<order_id>/paid', methods=['POST'])
def mark_paid(order_id):
    if order_id in ORDERS:
        order = ORDERS[order_id]
        if order['status'] == 'EXPIRED':
            return jsonify({"error": "order expired"}), 400
        order["status"] = "PAID"
        return jsonify({"status": "success"}), 200
    return jsonify({"error": "not found"}), 404

@app.route('/qr/<order_id>')
def generate_qr(order_id):
    order = ORDERS.get(order_id)
    if not order:
        return "Order not found", 404
        
    payment_url = f"{BANK_PUBLIC_BASE}/pay?order_id={order_id}&amount={order['total']}&merchant_account={MERCHANT_ACCOUNT}&expires={order['expires_at']}"
    
    img = qrcode.make(payment_url)
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    
    return send_file(buffer, mimetype="image/png")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
