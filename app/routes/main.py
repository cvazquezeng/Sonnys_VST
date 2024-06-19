from flask import Blueprint, render_template, redirect, url_for, request
from flask_login import login_required, logout_user, current_user
from sqlalchemy import func
from app.models import Ticket
from sqlalchemy import text  # Add this import

from app import db

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
@main_bp.route('/home')
@login_required
def home():
    return redirect(url_for('main.dashboard'))

# app/routes/main.py
@main_bp.route('/dashboard', methods=['GET'])
@login_required
def dashboard():
    filter_by = request.args.get('filter_by', 'line_machine')
    filter_value = request.args.get('filter_value', None)

    base_query = """
    SELECT
        {filter_column},
        AVG(TIMESTAMPDIFF(SECOND, request_made_at, acknowledged_at)) AS avg_response_time
    FROM ticket
    WHERE acknowledged_at IS NOT NULL
    """

    if filter_value:
        base_query += f" AND {filter_by} = :filter_value"
    
    base_query += f" GROUP BY {filter_by};"

    filter_column = 'line_machine' if filter_by == 'line_machine' else 'issue_type'

    response_times_query = base_query.format(filter_column=filter_column)

    with db.engine.connect() as connection:
        result = connection.execute(text(response_times_query), {'filter_value': filter_value})
        response_times = result.fetchall()

    labels = [row[0] for row in response_times]
    data = [row[1] for row in response_times]

    # Get unique line_machines and issue_types for the dropdowns
    line_machines_query = "SELECT DISTINCT line_machine FROM ticket WHERE line_machine IS NOT NULL;"
    issue_types_query = "SELECT DISTINCT issue_type FROM ticket WHERE issue_type IS NOT NULL;"

    with db.engine.connect() as connection:
        line_machines = connection.execute(text(line_machines_query)).fetchall()
        issue_types = connection.execute(text(issue_types_query)).fetchall()

    return render_template('dashboard.html', labels=labels, data=data, filter_by=filter_by, filter_value=filter_value, line_machines=line_machines, issue_types=issue_types)



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
