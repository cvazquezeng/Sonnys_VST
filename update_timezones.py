from app import create_app, db
from app.models import ClosedTicket
import pytz
from datetime import datetime

app = create_app('config_class')  # Replace 'config_class' with your actual configuration class

def convert_to_timezone(utc_dt):
    if utc_dt:
        utc_dt = utc_dt.replace(tzinfo=pytz.UTC)
        eastern = utc_dt.astimezone(pytz.timezone('America/New_York'))
        return eastern
    return None

def update_timezones():
    with app.app_context():
        tickets = ClosedTicket.query.all()
        for ticket in tickets:
            ticket.request_made_at = convert_to_timezone(ticket.request_made_at)
            ticket.acknowledged_at = convert_to_timezone(ticket.acknowledged_at)
            ticket.closed_at = convert_to_timezone(ticket.closed_at)
            db.session.commit()
        print(f"Updated {len(tickets)} tickets to Eastern Time.")

if __name__ == '__main__':
    update_timezones()
