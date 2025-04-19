from flask import Blueprint, render_template, flash, redirect, url_for, request
from flask_login import login_required, current_user
from app import db
from app.models import User, Wallet, Package, Investment, Transaction, TradingData
from app.forms import DepositForm, WithdrawForm, InvestmentForm, BreakInvestmentForm
from app.utils import generate_reference, calculate_expected_return, calculate_current_value, format_currency
from datetime import datetime, timedelta

user_bp = Blueprint('user', __name__, url_prefix='/user')

@user_bp.route('/dashboard')
@login_required
def dashboard():
    # Get user's active investments
    active_investments = Investment.query.filter_by(user_id=current_user.id, status='active').all()
    
    # Get recent transactions
    recent_transactions = Transaction.query.filter_by(user_id=current_user.id).order_by(Transaction.created_at.desc()).limit(5).all()
    
    # Get trading data for charts
    trading_data = TradingData.query.order_by(TradingData.date.desc()).limit(30).all()
    
    # Calculate portfolio value
    portfolio_value = current_user.wallet.balance
    for investment in active_investments:
        portfolio_value += calculate_current_value(investment)
    
    return render_template('user/dashboard.html', 
                           title='Dashboard',
                           active_investments=active_investments,
                           recent_transactions=recent_transactions,
                           trading_data=trading_data,
                           portfolio_value=portfolio_value,
                           format_currency=format_currency,
                           calculate_current_value=calculate_current_value)  # Make sure to pass this function

@user_bp.route('/packages')
@login_required
def packages():
    # Get all available packages
    packages = Package.query.filter_by(is_active=True).all()
    
    return render_template('user/packages.html',
                          title='Investment Packages',
                          packages=packages,
                          format_currency=format_currency)
    
@user_bp.route('/invest')
@login_required
def invest():
    # Get available packages
    packages = Package.query.filter_by(is_active=True).all()
    
    return render_template('user/invest.html', 
                           title='Invest',
                           packages=packages,
                           format_currency=format_currency)

@user_bp.route('/invest/<int:package_id>', methods=['GET', 'POST'])
@login_required
def invest_package(package_id):
    package = Package.query.get_or_404(package_id)
    form = InvestmentForm()
    
    if form.validate_on_submit():
        amount = form.amount.data
        
        # Validate investment amount
        if amount < package.min_investment:
            flash(f'Minimum investment amount is {format_currency(package.min_investment)}', 'danger')
            return redirect(url_for('user.invest_package', package_id=package.id))
        
        if package.max_investment and amount > package.max_investment:
            flash(f'Maximum investment amount is {format_currency(package.max_investment)}', 'danger')
            return redirect(url_for('user.invest_package', package_id=package.id))
        
        # Check if user has enough balance
        if amount > current_user.wallet.balance:
            flash('Insufficient funds in your wallet', 'danger')
            return redirect(url_for('user.invest_package', package_id=package.id))
        
        # Create investment
        end_date = datetime.utcnow() + timedelta(days=package.duration)
        investment = Investment(
            user_id=current_user.id,
            package_id=package.id,
            amount=amount,
            roi_percentage=package.expected_roi,
            start_date=datetime.utcnow(),
            end_date=end_date
        )
        
        # Create transaction record
        transaction = Transaction(
            user_id=current_user.id,
            amount=amount,
            transaction_type='investment',
            status='completed',
            reference=generate_reference(),
            description=f'Investment in {package.name} package'
        )
        
        # Deduct from wallet
        current_user.wallet.balance -= amount
        current_user.wallet.last_updated = datetime.utcnow()
        
        db.session.add(investment)
        db.session.add(transaction)
        db.session.commit()
        
        flash('Investment successful!', 'success')
        return redirect(url_for('user.dashboard'))
    
    expected_return = calculate_expected_return(
        package.min_investment, 
        package.expected_roi, 
        package.duration
    )
    
    return render_template('user/invest_package.html',
                          title=f'Invest in {package.name}',
                          package=package,
                          form=form,
                          expected_return=expected_return,
                          format_currency=format_currency)

@user_bp.route('/wallet', methods=['GET', 'POST'])
@login_required
def wallet():
    deposit_form = DepositForm()
    withdraw_form = WithdrawForm()
    
    if 'deposit' in request.form and deposit_form.validate():
        amount = deposit_form.amount.data
        
        # Create transaction record
        transaction = Transaction(
            user_id=current_user.id,
            amount=amount,
            transaction_type='deposit',
            status='completed',  # In real app, this would be 'pending' until payment confirmation
            reference=generate_reference(),
            description='Wallet deposit'
        )
        
        # Add to wallet
        current_user.wallet.balance += amount
        current_user.wallet.last_updated = datetime.utcnow()
        
        db.session.add(transaction)
        db.session.commit()
        
        flash('Deposit successful!', 'success')
        return redirect(url_for('user.wallet'))
    
    elif 'withdraw' in request.form and withdraw_form.validate():
        amount = withdraw_form.amount.data
        
        # Check if user has enough balance
        if amount > current_user.wallet.balance:
            flash('Insufficient funds in your wallet', 'danger')
            return redirect(url_for('user.wallet'))
        
        # Save bank details
        account_holder = request.form.get('account_holder')
        bank_name = request.form.get('bank_name')
        account_number = request.form.get('account_number')
        ifsc_code = request.form.get('ifsc_code')
        branch_name = request.form.get('branch_name')
        
        # Check if user already has bank details
        if current_user.bank_details:
            # Update existing bank details
            current_user.bank_details.account_holder = account_holder
            current_user.bank_details.bank_name = bank_name
            current_user.bank_details.account_number = account_number
            current_user.bank_details.ifsc_code = ifsc_code
            current_user.bank_details.branch_name = branch_name
        else:
            # Create new bank details
            from app.models import BankDetails
            bank_details = BankDetails(
                user_id=current_user.id,
                account_holder=account_holder,
                bank_name=bank_name,
                account_number=account_number,
                ifsc_code=ifsc_code,
                branch_name=branch_name
            )
            db.session.add(bank_details)
        
        # Create transaction record
        transaction = Transaction(
            user_id=current_user.id,
            amount=amount,
            transaction_type='withdrawal',
            status='completed',
            reference=generate_reference(),
            description=f'Wallet withdrawal to {bank_name} account {account_number[-4:]}'
        )
        
        # Deduct from wallet
        current_user.wallet.balance -= amount
        current_user.wallet.last_updated = datetime.utcnow()
        
        db.session.add(transaction)
        db.session.commit()
        
        flash('Withdrawal successful!', 'success')
        return redirect(url_for('user.wallet'))
    
    # Get transaction history
    transactions = Transaction.query.filter_by(user_id=current_user.id).order_by(Transaction.created_at.desc()).all()
    
    return render_template('user/wallet.html',
                          title='My Wallet',
                          deposit_form=deposit_form,
                          withdraw_form=withdraw_form,
                          transactions=transactions,
                          format_currency=format_currency)

@user_bp.route('/roi')
@login_required
def roi():
    # Get all investments
    investments = Investment.query.filter_by(user_id=current_user.id).all()
    
    # Calculate total invested and current value
    total_invested = sum(inv.amount for inv in investments)
    current_value = sum(calculate_current_value(inv) for inv in investments)
    
    # Calculate overall profit/loss
    overall_profit = current_value - total_invested
    
    # Calculate ROI percentage
    overall_roi_percentage = (overall_profit / total_invested * 100) if total_invested > 0 else 0
    
    return render_template('user/roi.html',
                          title='Return on Investment',
                          investments=investments,
                          total_invested=total_invested,
                          current_value=current_value,
                          overall_profit=overall_profit,
                          overall_roi_percentage=overall_roi_percentage,
                          calculate_current_value=calculate_current_value,
                          format_currency=format_currency)

@user_bp.route('/break_investment/<int:investment_id>', methods=['POST'])
@login_required
def break_investment(investment_id):
    """Break an active investment with a 4% penalty."""
    from app.utils import calculate_break_penalty
    
    investment = Investment.query.filter_by(id=investment_id, user_id=current_user.id).first_or_404()
    
    # Check if investment is active
    if investment.status != 'active':
        flash('This investment cannot be broken because it is not active.', 'danger')
        return redirect(url_for('user.roi'))
    
    # Calculate current value and penalty
    current_value = calculate_current_value(investment)
    penalty = calculate_break_penalty(current_value)
    final_amount = current_value - penalty
    
    # Update investment status
    investment.status = 'cancelled'
    investment.end_date = datetime.utcnow()
    investment.profit_loss = final_amount - investment.amount
    
    # Create a transaction record for the break
    transaction = Transaction(
        user_id=current_user.id,
        amount=final_amount,
        transaction_type='investment_break',
        status='completed',
        reference=generate_reference(),
        description=f'Investment broken with {format_currency(penalty)} penalty'
    )
    
    # Add the final amount back to user's wallet
    current_user.wallet.balance += final_amount
    current_user.wallet.last_updated = datetime.utcnow()
    
    # Commit the changes
    db.session.add(transaction)
    db.session.commit()
    
    flash(f'Investment successfully broken. You have received {format_currency(final_amount)} in your wallet after a {format_currency(penalty)} penalty.', 'success')
    return redirect(url_for('user.roi'))

@user_bp.route('/refer')
@login_required
def refer():
    """
    Generate and display a referral link for the current user
    """
    # Create the referral URL with the user's ID
    base_url = request.host_url.rstrip('/')
    referral_link = f"{base_url}/auth/register?ref={current_user.id}"
    
    # Get referral statistics
    referral_transactions = Transaction.query.filter_by(
        user_id=current_user.id,
        transaction_type='referral'
    ).all()
    
    total_referral_earnings = sum(transaction.amount for transaction in referral_transactions)
    
    return render_template('user/refer.html',
                          title='Refer a Friend',
                          referral_link=referral_link,
                          referral_transactions=referral_transactions,
                          total_referral_earnings=total_referral_earnings,
                          format_currency=format_currency)