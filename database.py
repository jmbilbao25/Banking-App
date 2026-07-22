import sqlite3
import uuid
import json
from datetime import datetime, timezone

DATABASE = 'banking.db'


def get_db():
    """Get a database connection with row factory."""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initialize the database and create the orders table."""
    conn = get_db()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id TEXT PRIMARY KEY,
            items TEXT NOT NULL,
            account TEXT NOT NULL,
            total REAL NOT NULL,
            callback_url TEXT,
            status TEXT NOT NULL DEFAULT 'PENDING',
            created_at TEXT NOT NULL,
            paid_at TEXT
        )
    ''')
    conn.commit()
    conn.close()


def create_order(items, account, callback_url=None):
    """Create a new order and return its ID.

    Args:
        items: List of dicts with 'name', 'quantity', 'price'.
        account: Customer account identifier.
        callback_url: URL to notify when payment is complete.

    Returns:
        The new order ID (UUID string).
    """
    conn = get_db()
    order_id = str(uuid.uuid4())[:8]
    total = sum(item['quantity'] * item['price'] for item in items)
    now = datetime.now(timezone.utc).isoformat()

    conn.execute(
        'INSERT INTO orders (id, items, account, total, callback_url, status, created_at) '
        'VALUES (?, ?, ?, ?, ?, ?, ?)',
        (order_id, json.dumps(items), account, total, callback_url, 'PENDING', now)
    )
    conn.commit()
    conn.close()
    return order_id


def get_order(order_id):
    """Get an order by ID. Returns a dict or None."""
    conn = get_db()
    row = conn.execute('SELECT * FROM orders WHERE id = ?', (order_id,)).fetchone()
    conn.close()
    if row is None:
        return None
    order = dict(row)
    order['order_items'] = json.loads(order.pop('items'))
    return order


def get_all_orders():
    """Get all orders, most recent first."""
    conn = get_db()
    rows = conn.execute('SELECT * FROM orders ORDER BY created_at DESC').fetchall()
    conn.close()
    orders = []
    for row in rows:
        order = dict(row)
        order['order_items'] = json.loads(order.pop('items'))
        orders.append(order)
    return orders


def mark_order_paid(order_id):
    """Mark an order as PAID. Returns True if successful, False if not found or already paid."""
    conn = get_db()
    now = datetime.now(timezone.utc).isoformat()
    cursor = conn.execute(
        'UPDATE orders SET status = ?, paid_at = ? WHERE id = ? AND status = ?',
        ('PAID', now, order_id, 'PENDING')
    )
    affected = cursor.rowcount
    conn.commit()
    conn.close()
    return affected > 0
