from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, FloatField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError, NumberRange
from app.models import User

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=64)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    first_name = StringField('First Name', validators=[DataRequired(), Length(max=64)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(max=64)])
    phone = StringField('Phone', validators=[DataRequired(), Length(min=10, max=20)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')

class DepositForm(FlaskForm):
    amount = FloatField('Amount', validators=[DataRequired(), NumberRange(min=1)])
    submit = SubmitField('Deposit')

class WithdrawForm(FlaskForm):
    amount = FloatField('Amount', validators=[DataRequired(), NumberRange(min=1)])
    submit = SubmitField('Withdraw')

class InvestmentForm(FlaskForm):
    amount = FloatField('Amount', validators=[DataRequired(), NumberRange(min=1)])
    submit = SubmitField('Invest')

class BreakInvestmentForm(FlaskForm):
    confirm = BooleanField('I understand that breaking this investment will incur a 4% penalty', validators=[DataRequired()])
    submit = SubmitField('Break Investment')

class ContactForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(max=64)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    subject = StringField('Subject', validators=[DataRequired(), Length(max=128)])
    message = TextAreaField('Message', validators=[DataRequired()])
    submit = SubmitField('Send Message')

class PackageForm(FlaskForm):
    name = StringField('Package Name', validators=[DataRequired(), Length(max=64)])
    description = TextAreaField('Description', validators=[DataRequired()])
    min_investment = FloatField('Minimum Investment', validators=[DataRequired(), NumberRange(min=1)])
    max_investment = FloatField('Maximum Investment', validators=[NumberRange(min=1)])
    expected_roi = FloatField('Expected ROI (%)', validators=[DataRequired(), NumberRange(min=0.1)])
    duration = FloatField('Duration (Days)', validators=[DataRequired(), NumberRange(min=1)])
    is_active = BooleanField('Active')
    submit = SubmitField('Save Package')

class UpdateInvestmentForm(FlaskForm):
    profit_loss = FloatField('Profit/Loss Amount', validators=[DataRequired()])
    roi_percentage = FloatField('ROI Percentage', validators=[DataRequired()])
    status = SelectField('Status', choices=[
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    ])
    submit = SubmitField('Update Investment')

class TradingDataForm(FlaskForm):
    date = StringField('Date (YYYY-MM-DD)', validators=[DataRequired()])
    instrument = SelectField('Stock Symbol', choices=[
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
    ], validators=[DataRequired()])
    open_price = FloatField('Open Price', validators=[DataRequired()])
    close_price = FloatField('Close Price', validators=[DataRequired()])
    high_price = FloatField('High Price', validators=[DataRequired()])
    low_price = FloatField('Low Price', validators=[DataRequired()])
    volume = FloatField('Volume', validators=[DataRequired()])
    submit = SubmitField('Add Data')