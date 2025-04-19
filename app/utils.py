import uuid
import random
from datetime import datetime, timedelta

def generate_reference():
    """Generate a unique transaction reference."""
    return str(uuid.uuid4())[:8].upper()

def calculate_expected_return(amount, roi_percentage, duration):
    """Calculate the expected return based on investment amount, ROI %, and duration."""
    # Simple interest calculation
    return amount * (roi_percentage / 100) * (duration / 365)

def calculate_current_value(investment):
    """Calculate the current value of an investment based on start date and end date."""
    if investment.status != 'active':
        return investment.amount + investment.profit_loss
        
    total_duration = (investment.end_date - investment.start_date).days
    elapsed_duration = (datetime.utcnow() - investment.start_date).days
        
    # Ensure we don't exceed the total duration
    progress = min(elapsed_duration / total_duration, 1.0)
        
    expected_profit = investment.amount * (investment.roi_percentage / 100)
    current_profit = expected_profit * progress
        
    return investment.amount + current_profit

def calculate_break_penalty(current_value):
    """Calculate the penalty for breaking an investment (4% of current value)."""
    return current_value * 0.04

def break_investment(investment):
    """Process breaking an investment with a 4% penalty on current value."""
    current_value = calculate_current_value(investment)
    penalty = calculate_break_penalty(current_value)
    
    # Calculate the final amount after penalty
    final_amount = current_value - penalty
    
    # Update investment status
    investment.status = 'cancelled'
    investment.end_date = datetime.utcnow()
    investment.profit_loss = final_amount - investment.amount
    
    # Return the info for transaction creation
    return {
        'current_value': current_value,
        'penalty': penalty,
        'final_amount': final_amount
    }

def generate_dummy_trading_data(days=30, instrument='TCS'):
    """Generate dummy trading data for charts with Indian stocks."""
    # Dictionary of major Indian stocks with their typical price ranges
    indian_stocks = {
        'RELIANCE': {'base': 2850, 'volatility': 0.03},
        'TCS': {'base': 3450, 'volatility': 0.025},
        'HDFCBANK': {'base': 1650, 'volatility': 0.02},
        'INFY': {'base': 1450, 'volatility': 0.025},
        'HINDUNILVR': {'base': 2400, 'volatility': 0.018},
        'ICICIBANK': {'base': 950, 'volatility': 0.03},
        'SBIN': {'base': 630, 'volatility': 0.035},
        'BAJFINANCE': {'base': 6800, 'volatility': 0.04},
        'BHARTIARTL': {'base': 850, 'volatility': 0.025},
        'KOTAKBANK': {'base': 1750, 'volatility': 0.02}
    }
    
    # Set base price based on selected stock (default to RELIANCE if not found)
    stock_info = indian_stocks.get(instrument, indian_stocks['TCS'])
    base_price = stock_info['base']
    volatility = stock_info['volatility']
    
    data = []
    
    for i in range(days):
        date = datetime.utcnow() - timedelta(days=days-i)
        daily_volatility = random.uniform(-volatility, volatility)
            
        open_price = base_price
        close_price = base_price * (1 + daily_volatility)
        high_price = max(open_price, close_price) * (1 + random.uniform(0, 0.015))
        low_price = min(open_price, close_price) * (1 - random.uniform(0, 0.015))
        volume = random.uniform(10000, 100000)  # Higher volumes for Indian stocks
            
        data.append({
            'date': date,
            'open_price': round(open_price, 2),
            'close_price': round(close_price, 2),
            'high_price': round(high_price, 2),
            'low_price': round(low_price, 2),
            'volume': round(volume, 2),
            'instrument': instrument
        })
            
        # Update base price for next day
        base_price = close_price
    
    return data


def format_currency(amount):
    """Format a number as currency."""
    return f"₹{amount:,.2f}"