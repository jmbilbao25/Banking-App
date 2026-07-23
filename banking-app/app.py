import os
import io
import uuid
import qrcode
import requests
import time
from flask import Flask, request, jsonify, render_template, session, redirect, url_for, send_file
from models import db, Account, Transaction
from seed import seed_data

app = Flask(__name__)
app.secret_key = 'super-secret-bank-key-for-prototype-only'

db_user = os.environ.get('DB_USER', 'bankuser')
db_password = os.environ.get('DB_PASSWORD', 'devpass')
db_host = os.environ.get('DB_HOST', 'mysql')
db_name = os.environ.get('DB_NAME', 'bankdb')

import socket

# Use SQLite as fallback if explicitly requested OR if the DB host cannot be resolved (e.g., running locally outside Docker)
use_sqlite = os.environ.get('USE_SQLITE')
if not use_sqlite:
    try:
        socket.gethostbyname(db_host)
    except socket.error:
        print(f"Warning: Could not resolve DB_HOST '{db_host}'. Falling back to SQLite.")
        use_sqlite = True

if use_sqlite:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///banking.db"
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{db_user}:{db_password}@{db_host}/{db_name}"

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# Seed database at startup
try:
    seed_data(app, db)
except Exception as e:
    print(f"Error seeding database: {e}")

ECOM_CALLBACK_BASE = os.environ.get('ECOM_CALLBACK_BASE', 'http://ecommerce:5000')
if not os.environ.get('ECOM_CALLBACK_BASE'):
    try:
        socket.gethostbyname('ecommerce')
    except socket.error:
        print("Warning: Could not resolve 'ecommerce'. Falling back ECOM_CALLBACK_BASE to http://127.0.0.1:5000")
        ECOM_CALLBACK_BASE = 'http://127.0.0.1:5000'

@app.route('/health')
def health():
    return jsonify({"status": "ok"})

@app.route('/')
def index():
    return redirect(url_for('accounts'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        account_id = request.form.get('account_id')
        password = request.form.get('password')
        account = Account.query.get(account_id)
        if account and account.password == password:
            session['account_id'] = account.id
            next_url = session.pop('next_url', None)
            if next_url:
                return redirect(next_url)
            return redirect(url_for('accounts'))
        return render_template('login.html', error="Invalid credentials")
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('account_id', None)
    return redirect(url_for('login'))

@app.route('/accounts')
def accounts():
    if 'account_id' not in session:
        return redirect(url_for('login'))
        
    current_account = Account.query.get(session['account_id'])
    
    if current_account.is_admin:
        # Admin can see all consumer accounts
        display_accounts = Account.query.filter_by(type='CONSUMER').all()
    elif current_account.type == 'CONSUMER':
        # Consumers only see their own account
        display_accounts = [current_account]
    else:
        # Merchants can see all accounts for demo purposes, or maybe just theirs
        display_accounts = Account.query.filter_by(type='CONSUMER').all()
        
    all_accounts = Account.query.filter_by(type='CONSUMER').all() if current_account.is_admin else []
    
    return render_template('accounts.html', accounts=display_accounts, current_user=current_account, all_accounts=all_accounts)

@app.route('/admin/add_funds', methods=['POST'])
def add_funds():
    if 'account_id' not in session:
        return redirect(url_for('login'))
    current_account = Account.query.get(session['account_id'])
    if not current_account.is_admin:
        return "Unauthorized", 403
        
    target_id = request.form.get('account_id')
    amount = float(request.form.get('amount', 0))
    
    target = Account.query.get(target_id)
    if target and amount > 0:
        target.balance += amount
        db.session.commit()
        
    return redirect(url_for('accounts'))

@app.route('/admin/qr')
def test_qr():
    if 'account_id' not in session:
        return redirect(url_for('login'))
    current_account = Account.query.get(session['account_id'])
    if not current_account.is_admin:
        return "Unauthorized", 403
        
    amount = request.args.get('amount', '5.00')
    merchant = request.args.get('merchant', 'sweetcrumb-pastries')
    order_id = "test-" + str(uuid.uuid4())[:8]
    
    # Use request.host_url to automatically get the correct base URL for the bank (e.g. 127.0.0.1:5001 or bank.IP.nip.io)
    base_url = request.host_url.rstrip('/')
    payment_url = f"{base_url}/pay?order_id={order_id}&amount={amount}&merchant_account={merchant}"
    
    img = qrcode.make(payment_url)
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    
    return send_file(buffer, mimetype="image/png")

@app.route('/scan')
def scan():
    if 'account_id' not in session:
        return redirect(url_for('login'))
    return render_template('scan.html')

@app.route('/pay', methods=['GET', 'POST'])
def pay():
    if 'account_id' not in session:
        session['next_url'] = request.url
        return redirect(url_for('login'))

    if request.method == 'GET':
        order_id = request.args.get('order_id')
        amount = request.args.get('amount')
        merchant_account = request.args.get('merchant_account')
        expires = request.args.get('expires')
        
        if expires and time.time() > int(expires):
            return render_template('pay.html', order_id=order_id, error="This QR code has expired.", expired=True)
            
        existing_tx = Transaction.query.filter_by(order_id=order_id).first()
        if existing_tx:
            return render_template('pay.html', order_id=order_id, error="This order has already been paid.", expired=True)
        
        # Only allow paying from the currently logged in account
        accounts = [Account.query.get(session['account_id'])]
        
        # Try to fetch detailed order items from Ecommerce app API
        order_details = None
        if order_id:
            try:
                resp = requests.get(f"{ECOM_CALLBACK_BASE}/api/orders/{order_id}", timeout=2)
                if resp.status_code == 200:
                    order_details = resp.json()
            except Exception as e:
                print(f"Could not fetch order details: {e}")
                
        return render_template('pay.html', order_id=order_id, amount=amount, merchant_account=merchant_account, expires=expires, accounts=accounts, order_details=order_details)
    
    data = request.form
    order_id = data.get('order_id')
    expires = data.get('expires')
    
    if expires and time.time() > int(expires):
        return render_template('pay.html', order_id=order_id, error="This QR code has expired.", expired=True)
        
    try:
        amount = float(data.get('amount', 0))
    except ValueError:
        amount = 0.0
    merchant_account = data.get('merchant_account')
    consumer_account = data.get('consumer_account')
    
    if not all([order_id, amount, merchant_account, consumer_account]):
        return "Missing data", 400

    consumer = Account.query.get(consumer_account)
    merchant = Account.query.get(merchant_account)
    
    if not consumer or not merchant:
        return "Invalid accounts", 400
        
    if consumer.balance < amount:
        return "Insufficient balance", 400
        
    existing_tx = Transaction.query.filter_by(order_id=order_id).first()
    if existing_tx:
        return render_template('pay.html', order_id=order_id, error="This order has already been paid.", expired=True)
        
    consumer.balance -= amount
    merchant.balance += amount
    
    tx = Transaction(order_id=order_id, from_acct=consumer.id, to_acct=merchant.id, amount=amount)
    db.session.add(tx)
    db.session.commit()
    
    # Callback to ecommerce app
    try:
        callback_url = f"{ECOM_CALLBACK_BASE}/api/orders/{order_id}/paid"
        requests.post(callback_url, timeout=5)
    except Exception as e:
        print(f"Callback failed: {e}")
        
    return render_template('success.html', order_id=order_id)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
