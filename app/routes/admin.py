from flask import Blueprint, render_template, flash, redirect, url_for, request
from flask_login import login_required, current_user
from app import db
from app.models import User, Wallet, Package, Investment, Transaction, TradingData
from app.forms import PackageForm, UpdateInvestmentForm, TradingDataForm
from app.utils import generate_reference, generate_dummy_trading_data, format_currency
from datetime import datetime, timedelta
from functools import wraps

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# Custom decorator to ensure the user is an admin
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('You need admin privileges to access this page.', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    # Get statistics
    total_users = User.query.filter_by(is_admin=False).count()
    total_investments = Investment.query.count()
    active_investments = Investment.query.filter_by(status='active').count()
    
    # Get total investment amount
    total_investment_amount = db.session.query(db.func.sum(Investment.amount)).scalar() or 0
    
    # Get recent transactions
    recent_transactions = Transaction.query.order_by(Transaction.created_at.desc()).limit(10).all()
    
    # Get trading data for charts
    trading_data = TradingData.query.order_by(TradingData.date.desc()).limit(30).all()
    
    return render_template('admin/dashboard.html', 
                           title='Admin Dashboard',
                           total_users=total_users,
                           total_investments=total_investments,
                           active_investments=active_investments,
                           total_investment_amount=total_investment_amount,
                           recent_transactions=recent_transactions,
                           trading_data=trading_data,
                           format_currency=format_currency)

@admin_bp.route('/users')
@login_required
@admin_required
def users():
    # Get all non-admin users
    users = User.query.filter_by(is_admin=False).all()
    
    return render_template('admin/users.html',
                          title='Manage Users',
                          users=users,
                          format_currency=format_currency)

@admin_bp.route('/packages', methods=['GET', 'POST'])
@login_required
@admin_required
def packages():
    form = PackageForm()
    
    if form.validate_on_submit():
        package = Package(
            name=form.name.data,
            description=form.description.data,
            min_investment=form.min_investment.data,
            max_investment=form.max_investment.data,
            expected_roi=form.expected_roi.data,
            duration=form.duration.data,
            is_active=form.is_active.data
        )
        
        db.session.add(package)
        db.session.commit()
        
        flash('Package added successfully!', 'success')
        return redirect(url_for('admin.packages'))
    
    # Get all packages
    packages = Package.query.all()
    
    return render_template('admin/packages.html',
                          title='Manage Packages',
                          form=form,
                          packages=packages,
                          format_currency=format_currency)

@admin_bp.route('/packages/edit/<int:package_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_package(package_id):
    package = Package.query.get_or_404(package_id)
    form = PackageForm(obj=package)
    
    if form.validate_on_submit():
        package.name = form.name.data
        package.description = form.description.data
        package.min_investment = form.min_investment.data
        package.max_investment = form.max_investment.data
        package.expected_roi = form.expected_roi.data
        package.duration = form.duration.data
        package.is_active = form.is_active.data
        
        db.session.commit()
        
        flash('Package updated successfully!', 'success')
        return redirect(url_for('admin.packages'))
    
    return render_template('admin/edit_package.html',
                          title='Edit Package',
                          form=form,
                          package=package)

@admin_bp.route('/packages/delete/<int:package_id>')
@login_required
@admin_required
def delete_package(package_id):
    package = Package.query.get_or_404(package_id)
    
    # Check if package has any active investments
    if Investment.query.filter_by(package_id=package.id, status='active').first():
        flash('Cannot delete package with active investments', 'danger')
        return redirect(url_for('admin.packages'))
    
    db.session.delete(package)
    db.session.commit()
    
    flash('Package deleted successfully!', 'success')
    return redirect(url_for('admin.packages'))

@admin_bp.route('/investments')
@login_required
@admin_required
def investments():
    # Get all investments
    investments = Investment.query.all()
    
    return render_template('admin/investments.html',
                          title='Manage Investments',
                          investments=investments,
                          format_currency=format_currency)

@admin_bp.route('/investments/update/<int:investment_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def update_investment(investment_id):
    investment = Investment.query.get_or_404(investment_id)
    form = UpdateInvestmentForm(obj=investment)
    
    if form.validate_on_submit():
        investment.profit_loss = form.profit_loss.data
        investment.roi_percentage = form.roi_percentage.data
        investment.status = form.status.data
        
        if form.status.data == 'completed' and investment.end_date is None:
            investment.end_date = datetime.utcnow()
        
        db.session.commit()
        
        flash('Investment updated successfully!', 'success')
        return redirect(url_for('admin.investments'))
    
    return render_template('admin/update_investment.html',
                          title='Update Investment',
                          form=form,
                          investment=investment)

@admin_bp.route('/payments')
@login_required
@admin_required
def payments():
    # Get all transactions
    transactions = Transaction.query.order_by(Transaction.created_at.desc()).all()
    
    return render_template('admin/payments.html',
                          title='Payment History',
                          transactions=transactions,
                          format_currency=format_currency)

@admin_bp.route('/trading', methods=['GET', 'POST'])
@login_required
@admin_required
def trading():
    form = TradingDataForm()
    
    # Add Indian stock options for the form dropdown
    indian_stocks = [
        ('RELIANCE', 'Reliance Industries Ltd.'),
        ('TCS', 'Tata Consultancy Services Ltd.'),
        ('HDFCBANK', 'HDFC Bank Ltd.'),
        ('INFY', 'Infosys Ltd.'),
        ('HINDUNILVR', 'Hindustan Unilever Ltd.'),
        ('ICICIBANK', 'ICICI Bank Ltd.'),
        ('SBIN', 'State Bank of India'),
        ('BAJFINANCE', 'Bajaj Finance Ltd.'),
        ('BHARTIARTL', 'Bharti Airtel Ltd.'),
        ('KOTAKBANK', 'Kotak Mahindra Bank Ltd.')
    ]
    
    # Update the form choices if it has an instrument field
    if hasattr(form, 'instrument'):
        form.instrument.choices = indian_stocks
    
    if form.validate_on_submit():
        try:
            date = datetime.strptime(form.date.data, '%Y-%m-%d')
            
            trading_data = TradingData(
                date=date,
                open_price=form.open_price.data,
                close_price=form.close_price.data,
                high_price=form.high_price.data,
                low_price=form.low_price.data,
                volume=form.volume.data,
                instrument=form.instrument.data
            )
            
            db.session.add(trading_data)
            db.session.commit()
            
            flash('Trading data added successfully!', 'success')
            return redirect(url_for('admin.trading'))
        except ValueError:
            flash('Invalid date format. Please use YYYY-MM-DD', 'danger')
    
    # Get trading data
    trading_data = TradingData.query.order_by(TradingData.date.desc()).all()
    
    return render_template('admin/trading.html',
                          title='Trading Data',
                          form=form,
                          trading_data=trading_data,
                          indian_stocks=indian_stocks)

@admin_bp.route('/trading/generate', methods=['GET', 'POST'])
@login_required
@admin_required
def generate_trading():
    stock = request.args.get('stock', 'RELIANCE')
    days = int(request.args.get('days', 30))
    
    # Generate dummy trading data
    dummy_data = generate_dummy_trading_data(days=days, instrument=stock)
    
    # Clear existing data
    TradingData.query.delete()
    
    # Add dummy data to database
    for data in dummy_data:
        trading_data = TradingData(
            date=data['date'],
            open_price=data['open_price'],
            close_price=data['close_price'],
            high_price=data['high_price'],
            low_price=data['low_price'],
            volume=data['volume'],
            instrument=data['instrument']
        )
        db.session.add(trading_data)
    
    db.session.commit()
    
    flash(f'Dummy trading data for {stock} generated successfully!', 'success')
    return redirect(url_for('admin.trading'))