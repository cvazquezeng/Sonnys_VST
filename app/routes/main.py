# app/routes/main.py
from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, logout_user, current_user


main_bp = Blueprint('main', __name__)

@main_bp.route('/')
@main_bp.route('/home')
@login_required
def home():
    return redirect(url_for('main.dashboard'))

@main_bp.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', title='Dashboard')

@main_bp.route('/profile')
@login_required
def profile():
    return render_template('profile.html', title='Profile')

@main_bp.route('/settings')
@login_required
def settings():
    return render_template('settings.html', title='Settings')

@main_bp.route('/5605_stack_control')
@login_required
def stack_control_5605():
    return render_template('stack_control_5605.html', title='5605 Stack Control')

@main_bp.route('/5605_stack_status')
@login_required
def stack_status_5605():
    return render_template('stack_status_5605.html', title='5605 Stack Status')

@main_bp.route('/5607_stack_control')
@login_required
def stack_control_5607():
    return render_template('stack_control_5607.html', title='5607 Stack Control')

@main_bp.route('/5607_stack_status')
@login_required
def stack_status_5607():
    return render_template('stack_status_5607.html', title='5607 Stack Status')

@main_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))
@main_bp.route('/open_tickets')
@login_required
def open_tickets():
    return render_template('open_tickets.html', title='Open Andon Tickets')
