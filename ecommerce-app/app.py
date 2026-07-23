import os
import io
import uuid
import qrcode
import time
import socket
from flask import Flask, request, jsonify, render_template, send_file, redirect, url_for, session
from models import db, User, Product, Order, OrderItem

app = Flask(__name__)
app.secret_key = 'super-secret-ecommerce-key'

# Setup database connection
db_user = os.environ.get('DB_USER', 'ecomuser')
db_password = os.environ.get('DB_PASSWORD', 'devpass')
db_host = os.environ.get('DB_HOST', 'mysql')
db_name = os.environ.get('DB_NAME', 'ecomdb')

use_sqlite = os.environ.get('USE_SQLITE')
if not use_sqlite:
    try:
        socket.gethostbyname(db_host)
    except socket.error:
        print(f"Warning: Could not resolve DB_HOST '{db_host}'. Falling back to SQLite.")
        use_sqlite = True

if use_sqlite:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///ecommerce.db"
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{db_user}:{db_password}@{db_host}/{db_name}"

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

from sqlalchemy.exc import OperationalError
with app.app_context():
    retries = 10
    while retries > 0:
        try:
            db.create_all()
            print("Database initialized.")
            
            # Seed products if the table is empty
            if Product.query.count() == 0:
                products_to_seed = [
                    Product(id="p1", name="Jasmine Rice (5kg)", price=12.00, image_url="/static/images/rice.png", stock=50),
                    Product(id="p2", name="Fresh Eggs (12pcs)", price=4.50, image_url="/static/images/eggs.png", stock=100),
                    Product(id="p3", name="Whole Milk (1L)", price=3.00, image_url="/static/images/milk.png", stock=30),
                    Product(id="p4", name="Chicken Breast (1kg)", price=8.50, image_url="/static/images/chicken.png", stock=40),
                    Product(id="p5", name="Bananas (bundle)", price=2.50, image_url="/static/images/bananas.png", stock=60),
                    Product(id="p6", name="Fresh Avocados (3pcs)", price=5.00, image_url="/static/images/avocados.png", stock=25)
                ]
                db.session.bulk_save_objects(products_to_seed)
                db.session.commit()
                print("Products seeded successfully.")
                
            break
        except OperationalError:
            print(f"Database not ready yet, retrying in 5 seconds... ({retries} retries left)")
            time.sleep(5)
            retries -= 1
BANK_PUBLIC_BASE = os.environ.get('BANK_PUBLIC_BASE', 'http://127.0.0.1:5001')
MERCHANT_ACCOUNT = os.environ.get('MERCHANT_ACCOUNT', 'techstart-grocery')
APP_TITLE = "TechStart Grocery"

def format_order_dict(order):
    items = []
    for item in order.items:
        prod = db.session.get(Product, item.product_id)
        img_url = prod.image_url if prod else "/static/images/rice.png"
        items.append({
            "product": {
                "id": item.product_id,
                "name": item.product_name,
                "price": item.price,
                "image_url": img_url
            },
            "product_id": item.product_id,
            "product_name": item.product_name,
            "price": item.price,
            "quantity": item.quantity,
            "subtotal": item.subtotal
        })
    return {
        "id": order.id,
        "items": items,
        "total": order.total_amount,
        "status": order.status,
        "created_at": order.created_at.strftime('%Y-%m-%d %H:%M:%S') if order.created_at else "",
        "expires_at": order.expires_at
    }

@app.route('/health')
def health():
    return jsonify({"status": "ok"})

@app.route('/')
def home():
    current_user = db.session.get(User, session['user_id']) if 'user_id' in session else None
    cart = session.get('cart', {})
    cart_count = sum(cart.values())
    
    search_query = request.args.get('q', '').strip()
    if search_query:
        products = Product.query.filter(Product.name.ilike(f"%{search_query}%")).all()
    else:
        products = Product.query.all()

    error_msg = session.pop('cart_error', None)
        
    return render_template('store.html', products=products, theme=APP_TITLE, current_user=current_user, cart_count=cart_count, search_query=search_query, cart_error=error_msg)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if User.query.filter_by(username=username).first():
            return render_template('register.html', error="Username taken", theme=APP_TITLE)
        
        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()
        
        session['user_id'] = new_user.id
        return redirect(url_for('home'))
    return render_template('register.html', theme=APP_TITLE)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session['user_id'] = user.id
            return redirect(url_for('home'))
        return render_template('login.html', error="Invalid credentials", theme=APP_TITLE)
    return render_template('login.html', theme=APP_TITLE)

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('home'))

@app.route('/cart')
def view_cart():
    cart = session.get('cart', {})
    cart_items = []
    total = 0
    error_msg = session.pop('cart_error', None)

    for product_id, quantity in list(cart.items()):
        product = db.session.get(Product, product_id)
        if product:
            if quantity > product.stock:
                quantity = product.stock
                if quantity == 0:
                    del cart[product_id]
                else:
                    cart[product_id] = quantity
                session['cart'] = cart
                error_msg = f"Quantity for {product.name} adjusted to maximum available stock ({product.stock})."

            if quantity > 0:
                subtotal = product.price * quantity
                total += subtotal
                cart_items.append({"product": product, "quantity": quantity, "subtotal": subtotal})

    return render_template('cart.html', cart_items=cart_items, total=total, error=error_msg, theme=APP_TITLE)

@app.route('/cart/add/<product_id>')
def add_to_cart(product_id):
    product = db.session.get(Product, product_id)
    if not product:
        return redirect(url_for('home'))
        
    cart = session.get('cart', {})
    current_qty = cart.get(product_id, 0)
    
    if current_qty + 1 > product.stock:
        session['cart_error'] = f"Cannot add more '{product.name}'. Only {product.stock} left in stock."
    else:
        cart[product_id] = current_qty + 1
        session['cart'] = cart
        
    return redirect(url_for('home'))

@app.route('/cart/update/<product_id>', methods=['POST'])
def update_cart_item(product_id):
    product = db.session.get(Product, product_id)
    if not product:
        return redirect(url_for('view_cart'))
        
    try:
        new_qty = int(request.form.get('quantity', 1))
    except ValueError:
        new_qty = 1
        
    cart = session.get('cart', {})
    if new_qty <= 0:
        cart.pop(product_id, None)
    elif new_qty > product.stock:
        cart[product_id] = product.stock
        session['cart_error'] = f"Only {product.stock} available in stock for {product.name}."
    else:
        cart[product_id] = new_qty
        
    session['cart'] = cart
    return redirect(url_for('view_cart'))

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
        
    order_items_data = []
    total = 0
    for product_id, quantity in cart.items():
        product = db.session.get(Product, product_id)
        if product:
            if quantity > product.stock:
                session['cart_error'] = f"Stock for {product.name} changed. Please review your cart."
                return redirect(url_for('view_cart'))
            subtotal = product.price * quantity
            total += subtotal
            order_items_data.append({
                "product": product,
                "quantity": quantity,
                "subtotal": subtotal
            })
            
    order_id = str(uuid.uuid4())[:8]
    user_id = session.get('user_id')
    expires_at = int(time.time()) + 300  # 5 minutes expiration
    
    new_order = Order(
        id=order_id,
        user_id=user_id,
        total_amount=total,
        status='PENDING',
        expires_at=expires_at
    )
    db.session.add(new_order)
    
    for item in order_items_data:
        order_item = OrderItem(
            order_id=order_id,
            product_id=item["product"].id,
            product_name=item["product"].name,
            price=item["product"].price,
            quantity=item["quantity"],
            subtotal=item["subtotal"]
        )
        db.session.add(order_item)
        
    db.session.commit()
    
    # Store order id in guest_orders if guest user
    if not user_id:
        guest_orders = session.get('guest_orders', [])
        guest_orders.append(order_id)
        session['guest_orders'] = guest_orders

    session.pop('cart', None)
    return redirect(url_for('checkout', order_id=order_id))

@app.route('/checkout/<order_id>')
def checkout(order_id):
    order = db.session.get(Order, order_id)
    if not order:
        return "Order not found", 404
        
    if order.status == 'PENDING' and time.time() > order.expires_at:
        order.status = 'EXPIRED'
        db.session.commit()
        
    order_dict = format_order_dict(order)

    payment_url = f"{BANK_PUBLIC_BASE}/pay?order_id={order_id}&amount={order.total_amount}&merchant_account={MERCHANT_ACCOUNT}&expires={order.expires_at}"
    return render_template('checkout.html', order=order_dict, payment_url=payment_url, theme=APP_TITLE)

@app.route('/transactions')
def transactions():
    try:
        current_user = db.session.get(User, session['user_id']) if 'user_id' in session else None
        
        if current_user:
            user_orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.created_at.desc()).all()
        else:
            guest_orders = session.get('guest_orders', [])
            if guest_orders:
                user_orders = Order.query.filter(Order.id.in_(guest_orders)).order_by(Order.created_at.desc()).all()
            else:
                user_orders = Order.query.filter_by(user_id=None).order_by(Order.created_at.desc()).limit(15).all()
            
        formatted_orders = [format_order_dict(o) for o in user_orders]
        return render_template('transactions.html', orders=formatted_orders, current_user=current_user, theme=APP_TITLE)
    except Exception as e:
        app.logger.error(f"Error rendering transactions: {e}")
        return render_template('transactions.html', orders=[], current_user=None, theme=APP_TITLE, error="Could not load transaction history.")


@app.route('/api/orders/<order_id>/status')
def order_status(order_id):
    order = db.session.get(Order, order_id)
    if not order:
        return jsonify({"error": "not found"}), 404
        
    if order.status == 'PENDING' and time.time() > order.expires_at:
        order.status = 'EXPIRED'
        db.session.commit()
        
    return jsonify({"status": order.status})

@app.route('/api/orders/<order_id>')
def get_order(order_id):
    order = db.session.get(Order, order_id)
    if not order:
        return jsonify({"error": "not found"}), 404
        
    if order.status == 'PENDING' and time.time() > order.expires_at:
        order.status = 'EXPIRED'
        db.session.commit()
        
    return jsonify(format_order_dict(order))

@app.route('/api/orders/<order_id>/paid', methods=['POST'])
def mark_paid(order_id):
    order = db.session.get(Order, order_id)
    if not order:
        return jsonify({"error": "order not found"}), 404
        
    if order.status == 'PAID':
        return jsonify({"error": "Order has already been paid"}), 400
        
    if order.status == 'EXPIRED' or time.time() > order.expires_at:
        order.status = 'EXPIRED'
        db.session.commit()
        return jsonify({"error": "Order has expired"}), 400
        
    order.status = "PAID"
    for item in order.items:
        product = db.session.get(Product, item.product_id)
        if product:
            product.stock = max(0, product.stock - item.quantity)
            
    db.session.commit()
    return jsonify({"status": "success"}), 200

@app.route('/qr/<order_id>')
def generate_qr(order_id):
    order = db.session.get(Order, order_id)
    if not order:
        return "Order not found", 404
        
    if order.status in ['EXPIRED', 'PAID'] or time.time() > order.expires_at:
        if order.status == 'PENDING':
            order.status = 'EXPIRED'
            db.session.commit()
        return jsonify({"error": f"QR Code unavailable. Order status is {order.status}."}), 400
        
    payment_url = f"{BANK_PUBLIC_BASE}/pay?order_id={order_id}&amount={order.total_amount}&merchant_account={MERCHANT_ACCOUNT}&expires={order.expires_at}"
    
    img = qrcode.make(payment_url)
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    
    return send_file(buffer, mimetype="image/png")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
