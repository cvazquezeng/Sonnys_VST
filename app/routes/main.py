# main.py

from flask import Blueprint, render_template, redirect, url_for, request, jsonify
from flask_login import login_required, logout_user, current_user
from sqlalchemy import func, text
from app.models import Ticket, ClosedTicket
from app import db
from datetime import datetime, timedelta
import logging
from app.models import Ticket


main_bp = Blueprint('main', __name__)

@main_bp.route('/')
@main_bp.route('/home')
@login_required
def home():
    return redirect(url_for('main.home_status'))

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
def open_tickets():
    tickets = Ticket.query.all()
    return render_template('open_tickets.html', title='Open Andon Tickets')


@main_bp.route('/dashboard')
def dashboard():
    closed_tickets = ClosedTicket.query.order_by(ClosedTicket.request_made_at.desc()).all()
    for ticket in closed_tickets:
        logging.debug(f"Ticket ID: {ticket.id}, Issue Type: {ticket.issue_type}, Comment: {ticket.comment}, Request Made At: {ticket.request_made_at}")
    return render_template('dashboard.html', closed_tickets=[ticket.to_dict() for ticket in closed_tickets])



@main_bp.route('/filter_tickets', methods=['POST'])
@login_required
def filter_tickets():
    data = request.get_json()
    print("Received data:", data)
    start_date = data.get('start_date')
    end_date = data.get('end_date')
    line_machine = data.get('line_machine')
    issue_type = data.get('issue_type')

    query = ClosedTicket.query

    if start_date:
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
    else:
        start_date = datetime.now() - timedelta(days=7)

    if end_date:
        end_date = datetime.strptime(end_date, '%Y-%m-%d')
    else:
        end_date = datetime.now()

    query = query.filter(ClosedTicket.closed_at >= start_date)
    query = query.filter(ClosedTicket.closed_at <= end_date)

    if line_machine:
        query = query.filter(ClosedTicket.line_machine == line_machine)
    if issue_type:
        query = query.filter(ClosedTicket.issue_type == issue_type)

    tickets = query.all()
    print("Filtered tickets:", tickets)

    total_tickets = len(tickets)
    avg_closing_time = db.session.query(func.avg(ClosedTicket.closed_at - ClosedTicket.created_at)).scalar()
    avg_ack_time = db.session.query(func.avg(ClosedTicket.acknowledged_at - ClosedTicket.created_at)).scalar()
    closed_without_ack = db.session.query(func.count()).filter(ClosedTicket.acknowledged_at == None).scalar()

    response = {
        'total_tickets': total_tickets,
        'avg_closing_time': str(avg_closing_time),
        'avg_ack_time': str(avg_ack_time),
        'closed_without_ack': closed_without_ack,
        'tickets': [ticket.to_dict() for ticket in tickets]
    }

    print("Response data:", response)
    return jsonify(response)

@main_bp.route('/dashboard2')
def dashboard2():
    range = request.args.get('range', 'today')
    now = datetime.now()

    if range == '30days':
        start_date = now - timedelta(days=30)
        end_date = now
        range_display = "Last 30 Days"
    elif range == '7days':
        start_date = now - timedelta(days=7)
        end_date = now
        range_display = "Last 7 Days"
    elif range == '24hours':
        start_date = now - timedelta(hours=24)
        end_date = now
        range_display = "Last 24 Hours"
    elif range == 'yesterday':
        start_date = (now - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
        range_display = "Yesterday"
    else:  # today
        start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = now.replace(hour=23, minute=59, second=59, microsecond=999999)
        range_display = "Today"


    tickets_opened = ClosedTicket.query.filter(ClosedTicket.request_made_at >= start_date, ClosedTicket.request_made_at < end_date).count()
    tickets_closed = ClosedTicket.query.filter(ClosedTicket.closed_at >= start_date, ClosedTicket.closed_at < end_date).count()

    average_time_to_close = db.session.query(
        func.avg(text("TIMESTAMPDIFF(SECOND, request_made_at, closed_at)"))
    ).filter(ClosedTicket.closed_at >= start_date, ClosedTicket.closed_at < end_date).scalar()

    average_time_to_acknowledge = db.session.query(
        func.avg(text("TIMESTAMPDIFF(SECOND, request_made_at, acknowledged_at)"))
    ).filter(ClosedTicket.acknowledged_at >= start_date, ClosedTicket.acknowledged_at < end_date).scalar()

    logging.debug(f"Start date: {start_date}")
    logging.debug(f"End date: {end_date}")
    logging.debug(f"Tickets opened: {tickets_opened}")
    logging.debug(f"Tickets closed: {tickets_closed}")
    logging.debug(f"Average time to close (seconds): {average_time_to_close}")
    logging.debug(f"Average time to acknowledge (seconds): {average_time_to_acknowledge}")

    def format_seconds(seconds):
        if seconds is None or seconds == 0:
            return 'N/A'
        minutes, _ = divmod(seconds, 60)
        hours, minutes = divmod(minutes, 60)
        return f'{int(hours)}h {int(minutes)}m'

    formatted_average_time_to_close = format_seconds(average_time_to_close)
    formatted_average_time_to_acknowledge = format_seconds(average_time_to_acknowledge)

    logging.debug(f"Formatted average time to close: {formatted_average_time_to_close}")
    logging.debug(f"Formatted average time to acknowledge: {formatted_average_time_to_acknowledge}")

    return render_template('dashboard2.html', 
                           tickets_opened=tickets_opened, 
                           tickets_closed=tickets_closed, 
                           average_time_to_close=formatted_average_time_to_close,
                           average_time_to_acknowledge=formatted_average_time_to_acknowledge,
                           range_display=range_display)


@main_bp.route('/api/detailed_data')
def detailed_data():
    try:
        selected_range = request.args.get('range', 'today')
        now = datetime.now()
        details = []

        if selected_range == 'today':
            start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = now
            shifts = [
                {'label': 'Morning Shift', 'start': start_date.replace(hour=7, minute=0), 'end': start_date.replace(hour=15, minute=30)},
                {'label': 'Night Shift', 'start': start_date.replace(hour=15, minute=30), 'end': start_date.replace(hour=23, minute=59, second=59, microsecond=999999)}
            ]
        elif selected_range == 'yesterday':
            start_date = (now - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = start_date + timedelta(days=1)
            shifts = [
                {'label': 'Morning Shift', 'start': start_date.replace(hour=7, minute=0), 'end': start_date.replace(hour=15, minute=30)},
                {'label': 'Night Shift', 'start': start_date.replace(hour=15, minute=30), 'end': start_date.replace(hour=23, minute=59, second=59, microsecond=999999)}
            ]
        elif selected_range == '24hours':
            start_date = now - timedelta(hours=24)
            end_date = now
            shifts = []

            morning_shift_start = start_date.replace(hour=7, minute=0, second=0, microsecond=0)
            night_shift_start = start_date.replace(hour=15, minute=30, second=0, microsecond=0)
            next_morning_shift_start = morning_shift_start + timedelta(days=1)
            next_night_shift_start = night_shift_start + timedelta(days=1)

            if start_date < morning_shift_start:
                shifts.append({'label': 'Night Shift', 'start': start_date, 'end': morning_shift_start})
            if start_date < night_shift_start:
                shifts.append({'label': 'Morning Shift', 'start': max(start_date, morning_shift_start), 'end': night_shift_start})
            if start_date < next_morning_shift_start:
                shifts.append({'label': 'Night Shift', 'start': max(start_date, night_shift_start), 'end': min(end_date, next_morning_shift_start)})
            if end_date > next_morning_shift_start:
                shifts.append({'label': 'Morning Shift', 'start': next_morning_shift_start, 'end': min(end_date, next_night_shift_start)})
            if end_date > next_night_shift_start:
                shifts.append({'label': 'Night Shift', 'start': next_night_shift_start, 'end': end_date})

        elif selected_range == '7days':
            start_date = now - timedelta(days=7)
            end_date = now
            day = start_date

            for _ in range(7):
                day_start = day.replace(hour=0, minute=0, second=0, microsecond=0)
                day_end = day_start + timedelta(days=1)
                opened = ClosedTicket.query.filter(ClosedTicket.request_made_at >= day_start, ClosedTicket.request_made_at < day_end).count()
                closed = ClosedTicket.query.filter(ClosedTicket.closed_at >= day_start, ClosedTicket.closed_at < day_end).count()
                details.append({'time': day_start.strftime('%A'), 'opened': opened, 'closed': closed})
                day += timedelta(days=1)

        elif selected_range == '30days':
            start_date = now - timedelta(days=30)
            end_date = now
            week_count = 5  # Assuming you want to divide the 30 days into 5 weeks
            for week in range(week_count):
                week_start = start_date + timedelta(weeks=week)
                week_end = week_start + timedelta(weeks=1)
                opened = ClosedTicket.query.filter(ClosedTicket.request_made_at >= week_start, ClosedTicket.request_made_at < week_end).count()
                closed = ClosedTicket.query.filter(ClosedTicket.closed_at >= week_start, ClosedTicket.closed_at < week_end).count()
                details.append({'time': f'Week {week+1}', 'opened': opened, 'closed': closed})

        # Log the details for debugging
        logging.debug(f"Details: {details}")

        if selected_range in ['today', 'yesterday', '24hours']:
            for shift in shifts:
                opened = ClosedTicket.query.filter(ClosedTicket.request_made_at >= shift['start'], ClosedTicket.request_made_at < shift['end']).count()
                closed = ClosedTicket.query.filter(ClosedTicket.closed_at >= shift['start'], ClosedTicket.closed_at < shift['end']).count()
                details.append({'time': shift['label'], 'opened': opened, 'closed': closed})

        tickets_opened = ClosedTicket.query.filter(ClosedTicket.request_made_at >= start_date, ClosedTicket.request_made_at < end_date).count()
        tickets_closed = ClosedTicket.query.filter(ClosedTicket.closed_at >= start_date, ClosedTicket.closed_at < end_date).count()

        average_time_to_close = db.session.query(func.avg(text("TIMESTAMPDIFF(SECOND, request_made_at, closed_at)"))).filter(ClosedTicket.closed_at >= start_date, ClosedTicket.closed_at < end_date).scalar()
        average_time_to_acknowledge = db.session.query(func.avg(text("TIMESTAMPDIFF(SECOND, request_made_at, acknowledged_at)"))).filter(ClosedTicket.acknowledged_at >= start_date, ClosedTicket.acknowledged_at < end_date).scalar()

        def format_seconds(seconds):
            if seconds is None or seconds == 0:
                return 'N/A'
            minutes, _ = divmod(seconds, 60)
            hours, minutes = divmod(minutes, 60)
            return f'{int(hours)}h {int(minutes)}m'

        formatted_average_time_to_close = format_seconds(average_time_to_close)
        formatted_average_time_to_acknowledge = format_seconds(average_time_to_acknowledge)

        response = {
            'range': selected_range,
            'details': details,
            'summary': {
                'tickets_opened': tickets_opened,
                'tickets_closed': tickets_closed,
                'average_time_to_close': formatted_average_time_to_close,
                'average_time_to_acknowledge': formatted_average_time_to_acknowledge
            }
        }

        logging.debug(f"Response data: {response}")
        return jsonify(response)
    except Exception as e:
        logging.error(f"Error in detailed_data endpoint: {e}")
        return jsonify({'error': str(e)}), 500

@main_bp.route('/home_status')
def home_status():
    return render_template('home_status.html')