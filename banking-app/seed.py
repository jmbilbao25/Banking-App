from models import Account

def seed_data(app, db):
    with app.app_context():
        db.create_all()

        # Idempotent seed
        if not Account.query.filter_by(id='jmb-grocery').first():
            merchant = Account(id='jmb-grocery', name='JMB Grocery', type='MERCHANT', balance=0.0, password='password123', is_admin=False)
            db.session.add(merchant)

        if not Account.query.filter_by(id='alice-consumer').first():
            alice = Account(id='alice-consumer', name='Alice Smith', type='CONSUMER', balance=1000.0, password='password123', is_admin=True)
            db.session.add(alice)

        if not Account.query.filter_by(id='bob-consumer').first():
            bob = Account(id='bob-consumer', name='Bob Jones', type='CONSUMER', balance=1500.0, password='password123')
            db.session.add(bob)

        db.session.commit()
