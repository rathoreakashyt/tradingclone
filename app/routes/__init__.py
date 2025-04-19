from flask import Blueprint, render_template, flash, redirect, url_for
from app.forms import ContactForm
from datetime import datetime

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
@main_bp.route('/home')
def home():
    return render_template('home.html', title='Home', now=datetime.utcnow())

@main_bp.route('/about')
def about():
    return render_template('about.html', title='About Us', now=datetime.utcnow())

@main_bp.route('/contact', methods=['GET', 'POST'])
def contact():
    form = ContactForm()
    if form.validate_on_submit():
        # In a real application, you'd process the contact form
        # For now, we'll just show a success message
        flash('Your message has been sent. Thank you!', 'success')
        return redirect(url_for('main.home'))
    return render_template('contact.html', title='Contact Us', form=form, now=datetime.utcnow())