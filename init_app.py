"""
Initialization script for Broker Platform

This script initializes the database, creates admin user and sample data.
Run this script after setting up the database to populate it with initial data.
"""

import os
import sys
from datetime import datetime, timedelta
import random
from werkzeug.security import generate_password_hash
from app import create_app, db
from app.models import User, Wallet, Package, Investment, Transaction, TradingData
from app.utils import generate_reference, generate_dummy_trading_data

app = create_app()

def init_database():
    """Initialize the database with sample data"""
    with app.app_context():
        # Create tables
        db.create_all()
        
        print("Creating admin user...")
        # Create admin user if it doesn't exist
        if not User.query.filter_by(username='admin').first():
            admin = User(
                username='admin',
                email='admin@example.com',
                first_name='Admin',
                last_name='User',
                phone='1234567890',
                is_admin=True
            )
            admin.set_password('admin1234')
            
            # Create a wallet for admin
            admin_wallet = Wallet(balance=0.0)
            admin.wallet = admin_wallet
            
            db.session.add(admin)
            db.session.commit()
            print("Admin user created.")
        else:
            print("Admin user already exists.")
        
        print("Creating sample packages...")
        # Create sample packages if none exist
        if Package.query.count() == 0:
            packages = [
                {
                    'name': 'Starter Package',
                    'description': 'Perfect for new investors looking to start their investment journey with minimal risk.',
                    'min_investment': 1000.0,
                    'max_investment': 5000.0,
                    'expected_roi': 8.0,
                    'duration': 30,
                    'is_active': True
                },
                {
                    'name': 'Growth Package',
                    'description': 'Designed for investors seeking substantial medium-term growth with moderate risk.',
                    'min_investment': 5000.0,
                    'max_investment': 20000.0,
                    'expected_roi': 12.0,
                    'duration': 90,
                    'is_active': True
                },
                {
                    'name': 'Premium Package',
                    'description': 'Our premium offering for serious investors seeking maximum returns with managed risk levels.',
                    'min_investment': 10000.0,
                    'max_investment': None,
                    'expected_roi': 15.0,
                    'duration': 180,
                    'is_active': True
                }
            ]
            
            for package_data in packages:
                package = Package(**package_data)
                db.session.add(package)
            
            db.session.commit()
            print(f"{len(packages)} packages created.")
        else:
            print("Packages already exist.")
        
        print("Creating sample trading data...")
        # Create sample trading data if none exists
        if TradingData.query.count() == 0:
            trading_data = generate_dummy_trading_data(days=30, instrument='BTC')
            
            for data in trading_data:
                trading_entry = TradingData(
                    date=data['date'],
                    open_price=data['open_price'],
                    close_price=data['close_price'],
                    high_price=data['high_price'],
                    low_price=data['low_price'],
                    volume=data['volume'],
                    instrument=data['instrument']
                )
                db.session.add(trading_entry)
            
            db.session.commit()
            print(f"{len(trading_data)} trading data entries created.")
        else:
            print("Trading data already exists.")
        
        print("Creating sample user...")
        # Create a sample user if none exist (excluding admin)
        if User.query.filter_by(is_admin=False).count() == 0:
            user = User(
                username='testuser',
                email='user@example.com',
                first_name='Test',
                last_name='User',
                phone='9876543210',
                is_admin=False
            )
            user.set_password('user1234')
            
            # Create a wallet for the user with initial balance
            user_wallet = Wallet(balance=10000.0)
            user.wallet = user_wallet
            
            db.session.add(user)
            db.session.commit()
            
            # Create sample transactions for the user
            transactions = [
                {
                    'user_id': user.id,
                    'amount': 5000.0,
                    'transaction_type': 'deposit',
                    'status': 'completed',
                    'reference': generate_reference(),
                    'description': 'Initial deposit',
                    'created_at': datetime.utcnow() - timedelta(days=10)
                },
                {
                    'user_id': user.id,
                    'amount': 5000.0,
                    'transaction_type': 'deposit',
                    'status': 'completed',
                    'reference': generate_reference(),
                    'description': 'Additional deposit',
                    'created_at': datetime.utcnow() - timedelta(days=5)
                }
            ]
            
            for trans_data in transactions:
                transaction = Transaction(**trans_data)
                db.session.add(transaction)
            
            # Create sample investments for the user
            starter_package = Package.query.filter_by(name='Starter Package').first()
            if starter_package:
                investment = Investment(
                    user_id=user.id,
                    package_id=starter_package.id,
                    amount=2000.0,
                    status='active',
                    profit_loss=50.0,
                    roi_percentage=starter_package.expected_roi,
                    start_date=datetime.utcnow() - timedelta(days=15),
                    end_date=datetime.utcnow() + timedelta(days=15)
                )
                db.session.add(investment)
                
                # Create transaction for the investment
                investment_transaction = Transaction(
                    user_id=user.id,
                    amount=2000.0,
                    transaction_type='investment',
                    status='completed',
                    reference=generate_reference(),
                    description=f'Investment in {starter_package.name}',
                    created_at=datetime.utcnow() - timedelta(days=15)
                )
                db.session.add(investment_transaction)
            
            db.session.commit()
            print("Sample user with wallet, transactions, and investment created.")
        else:
            print("Sample users already exist.")
        
        print("Database initialization complete.")

if __name__ == '__main__':
    print("Initializing database...")
    init_database()
    print("Done.")