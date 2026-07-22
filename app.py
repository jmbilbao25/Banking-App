import io
import segno
import requests
from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for
from database import init_db, create_order, get_order, get_all_orders, mark_order_paid

app = Flask(__name__)

# Configuration
BANKING_APP_BASE_URL = 'http://127.0.0.1:5000'
ECOM_CALLBACK_URL = 'http://127.0.0.1:5001'  # Default e-commerce app URL


# ──────────────────────────────────────────────
# HTML Routes
# ──────────────────────────────────────────────

@app.route('/')
def home():
    """Dashboard showing all orders."""
    orders = get_all_orders()
    return render_template('index.html', orders=orders, base_url=BANKING_APP_BASE_URL)


@app.route('/pay/<order_id>', methods=['GET'])
def pay_page(order_id):
    """Payment page — shown when customer scans QR code."""
    order = get_order(order_id)
    if order is None:
        return render_template('pay.html', order=None, error='Order not found.'), 404
    return render_template('pay.html', order=order)


@app.route('/pay/<order_id>', methods=['POST'])
def process_payment(order_id):
    """Process the payment: mark as paid and notify e-commerce app."""
    order = get_order(order_id)
    if order is None:
        return render_template('pay.html', order=None, error='Order not found.'), 404

    if order['status'] == 'PAID':
        return redirect(url_for('success_page', order_id=order_id))

    # Mark as paid in database
    success = mark_order_paid(order_id)
    if not success:
        return render_template('pay.html', order=order, error='Payment could not be processed.'), 500

    # Notify the e-commerce app via callback
    if order.get('callback_url'):
        try:
            requests.post(order['callback_url'], json={
                'order_id': order_id,
                'status': 'PAID'
            }, timeout=5)
        except requests.RequestException:
            # Log the failure but don't block the user — payment is already recorded
            pass

    return redirect(url_for('success_page', order_id=order_id))


@app.route('/success/<order_id>')
def success_page(order_id):
    """Payment success confirmation page."""
    order = get_order(order_id)
    if order is None:
        return redirect(url_for('home'))
    return render_template('success.html', order=order)


@app.route('/test-qr', methods=['GET', 'POST'])
def test_qr():
    """Test page to create an order and generate a QR code."""
    if request.method == 'POST':
        account = request.form.get('account', 'test@email.com')
        names = request.form.getlist('item_name')
        qtys = request.form.getlist('item_qty')
        prices = request.form.getlist('item_price')

        items = []
        for name, qty, price in zip(names, qtys, prices):
            if name.strip():
                items.append({'name': name, 'quantity': int(qty), 'price': float(price)})

        if items:
            order_id = create_order(items, account)
            order = get_order(order_id)
            return render_template('test_qr.html', order=order)

    return render_template('test_qr.html', order=None)



# ──────────────────────────────────────────────
# API Routes (for E-Commerce integration)
# ──────────────────────────────────────────────

@app.route('/api/orders', methods=['POST'])
def api_create_order():
    """Create a new payment request from the e-commerce app.

    Expected JSON body:
    {
        "items": [{"name": "Widget", "quantity": 2, "price": 49.99}],
        "account": "customer@email.com",
        "callback_url": "http://ecom:5001/api/orders/123/paid"  (optional)
    }
    """
    data = request.get_json()
    if not data:
        return jsonify({'error': 'JSON body required'}), 400

    items = data.get('items')
    account = data.get('account')
    callback_url = data.get('callback_url')

    if not items or not account:
        return jsonify({'error': 'Missing required fields: items, account'}), 400

    # Validate items structure
    for item in items:
        if not all(k in item for k in ('name', 'quantity', 'price')):
            return jsonify({'error': 'Each item must have: name, quantity, price'}), 400

    order_id = create_order(items, account, callback_url)
    payment_url = f'{BANKING_APP_BASE_URL}/pay/{order_id}'
    qr_url = f'{BANKING_APP_BASE_URL}/api/orders/{order_id}/qr'

    return jsonify({
        'order_id': order_id,
        'payment_url': payment_url,
        'qr_url': qr_url,
        'status': 'PENDING'
    }), 201


@app.route('/api/orders/<order_id>', methods=['GET'])
def api_get_order(order_id):
    """Get order details as JSON."""
    order = get_order(order_id)
    if order is None:
        return jsonify({'error': 'Order not found'}), 404
    return jsonify(order)


@app.route('/api/orders/<order_id>/qr', methods=['GET'])
def api_get_qr(order_id):
    """Generate and return a QR code PNG image for the payment URL."""
    order = get_order(order_id)
    if order is None:
        return jsonify({'error': 'Order not found'}), 404

    payment_url = f'{BANKING_APP_BASE_URL}/pay/{order_id}'
    qr = segno.make(payment_url)

    # Render to an in-memory buffer
    buffer = io.BytesIO()
    qr.save(buffer, kind='png', scale=8, border=2, dark='#3b82f6', light='#0f172a')
    buffer.seek(0)

    return send_file(buffer, mimetype='image/png', download_name=f'qr_{order_id}.png')


# ──────────────────────────────────────────────
# App Entry Point
# ──────────────────────────────────────────────

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5000)
