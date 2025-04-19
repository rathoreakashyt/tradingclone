from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import db, login

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    first_name = db.Column(db.String(64))
    last_name = db.Column(db.String(64))
    phone = db.Column(db.String(20))
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    bank_details = db.relationship('BankDetails', backref='user', uselist=False)

    
    # Referral system fields
    referred_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    referrals = db.Column(db.Integer, default=0)
    
    # User's wallet
    wallet = db.relationship('Wallet', backref='user', uselist=False)
    
    # User's investments
    investments = db.relationship('Investment', backref='user', lazy='dynamic')
    
    # User's transactions
    transactions = db.relationship('Transaction', backref='user', lazy='dynamic')
    
    def __repr__(self):
        return f'<User {self.username}>'
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

class Wallet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    balance = db.Column(db.Float, default=0.0)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Wallet {self.id} of User {self.user_id}>'

class Package(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    description = db.Column(db.Text)
    min_investment = db.Column(db.Float)
    max_investment = db.Column(db.Float, nullable=True)
    expected_roi = db.Column(db.Float)  # Percentage
    duration = db.Column(db.Integer)  # In days
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Package's investments
    investments = db.relationship('Investment', backref='package', lazy='dynamic')
    
    def __repr__(self):
        return f'<Package {self.name}>'

class Investment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    package_id = db.Column(db.Integer, db.ForeignKey('package.id'))
    amount = db.Column(db.Float)
    status = db.Column(db.String(20), default='active')  # active, completed, cancelled
    profit_loss = db.Column(db.Float, default=0.0)
    roi_percentage = db.Column(db.Float)
    start_date = db.Column(db.DateTime, default=datetime.utcnow)
    end_date = db.Column(db.DateTime, nullable=True)
    
    def __repr__(self):
        return f'<Investment {self.id} by User {self.user_id}>'

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    amount = db.Column(db.Float)
    # Updated to include 'referral' as a valid transaction type
    transaction_type = db.Column(db.String(20))  # deposit, withdrawal, investment, payout, referral
    status = db.Column(db.String(20), default='pending')  # pending, completed, failed
    reference = db.Column(db.String(64), unique=True)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Transaction {self.id} by User {self.user_id}>'

class TradingData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    open_price = db.Column(db.Float)
    close_price = db.Column(db.Float)
    high_price = db.Column(db.Float)
    low_price = db.Column(db.Float)
    volume = db.Column(db.Float)
    instrument = db.Column(db.String(20))  # e.g., 'BTC', 'ETH', 'STOCK'
    
    def __repr__(self):
        return f'<TradingData {self.id} for {self.instrument}>'
    
class BankDetails(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', name='fk_bank_details_user'), unique=True)
    account_holder = db.Column(db.String(100))
    bank_name = db.Column(db.String(100))
    account_number = db.Column(db.String(30))
    ifsc_code = db.Column(db.String(20))
    branch_name = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<BankDetails for User {self.user_id}>'