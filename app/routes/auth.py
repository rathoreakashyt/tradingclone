from flask import Blueprint, render_template, flash, redirect, url_for, request, session
from flask_login import login_user, logout_user, current_user
from werkzeug.urls import url_parse
from app import db
from app.models import User, Wallet, Transaction
from app.forms import LoginForm, RegistrationForm
from datetime import datetime
from app.utils import generate_reference

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        if current_user.is_admin:
            return redirect(url_for('admin.dashboard'))
        return redirect(url_for('user.dashboard'))
        
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password', 'danger')
            return redirect(url_for('auth.login'))
            
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            if user.is_admin:
                next_page = url_for('admin.dashboard')
            else:
                next_page = url_for('user.dashboard')
        return redirect(next_page)
    
    return render_template('auth/login.html', title='Sign In', form=form)

@auth_bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.home'))

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    
    # Get referral code from URL parameter
    referrer_id = request.args.get('ref')
    
    # Store in session to persist across form submissions
    if referrer_id:
        session['referrer_id'] = referrer_id
    
    form = RegistrationForm()
    if form.validate_on_submit():
        # Get referrer_id from session if available
        referrer_id = session.get('referrer_id')
        
        user = User(
            username=form.username.data,
            email=form.email.data,
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            phone=form.phone.data,
            referred_by=referrer_id if referrer_id else None
        )
        user.set_password(form.password.data)
        
        # Create a wallet for the user
        wallet = Wallet(balance=0.0)
        user.wallet = wallet
        
        db.session.add(user)
        db.session.commit()
        
        # Process referral if exists
        if referrer_id:
            try:
                referrer_id = int(referrer_id)
                referrer = User.query.get(referrer_id)
                
                if referrer:
                    # Update referrer's count if they have a 'referrals' field
                    if hasattr(referrer, 'referrals'):
                        referrer.referrals = (referrer.referrals or 0) + 1
                    
                    # Credit referrer's wallet
                    referrer.wallet.balance += 40  # ₹40 bonus
                    referrer.wallet.last_updated = datetime.utcnow()
                    
                    # Create a transaction record for the referral bonus
                    referral_transaction = Transaction(
                        user_id=referrer.id,
                        amount=40,
                        transaction_type='referral',
                        status='completed',
                        reference=generate_reference(),
                        description=f'Referral bonus - {user.email} joined'
                    )
                    
                    db.session.add(referral_transaction)
                    db.session.commit()
                    
                    flash('You registered through a referral link. Your friend has received a bonus!', 'info')
                    
                    # Clear the referrer_id from session
                    session.pop('referrer_id', None)
            except (ValueError, TypeError):
                # Invalid referrer ID - just ignore
                pass
        
        flash('Congratulations, you are now registered!', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html', title='Register', form=form, referrer_id=referrer_id)

@auth_bp.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    if current_user.is_authenticated:
        if current_user.is_admin:
            return redirect(url_for('admin.dashboard'))
        return redirect(url_for('user.dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data) or not user.is_admin:
            flash('Invalid admin credentials', 'danger')
            return redirect(url_for('auth.admin_login'))
            
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('admin.dashboard')
        return redirect(next_page)
    
    return render_template('auth/admin_login.html', title='Admin Login', form=form)