from flask import Blueprint, render_template, redirect, url_for, flash, session, request, Response
from flask_login import login_user, logout_user, login_required, current_user
from ..forms import LoginForm
from ..models import User
from .. import login_manager

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            flash('Logged in successfully.', 'success')
            return redirect(url_for('main.stack_status_5605'))
        else:
            flash('Invalid username or password.', 'error')
            return redirect(url_for('auth.login'))
    return render_template('login.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    session.pop('_flashes', None)  # Clear flash messages
    flash('You have been logged out due to inactivity.', 'logout')
    return redirect(url_for('auth.login'))

@auth_bp.route('/password_recovery')
def password_recovery():
    return "Password recovery page is under construction."

@login_manager.unauthorized_handler
def unauthorized_callback() -> Response:
    if current_user.is_authenticated:
        flash('You do not have permission to access this page.', 'error')
    else:
        flash('Please log in to access this page.', 'login-required')
    return redirect(url_for('auth.login'))
