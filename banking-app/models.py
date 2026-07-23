from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone

db = SQLAlchemy()

class Account(db.Model):
    __tablename__ = 'accounts'
    id = db.Column(db.String(50), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(20), nullable=False)  # CONSUMER or MERCHANT
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    password = db.Column(db.String(100), nullable=False, default='password123')
    balance = db.Column(db.Float, default=0.0)

class Transaction(db.Model):
    __tablename__ = 'transactions'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    order_id = db.Column(db.String(100), nullable=False)
    from_acct = db.Column(db.String(50), db.ForeignKey('accounts.id'), nullable=False)
    to_acct = db.Column(db.String(50), db.ForeignKey('accounts.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
