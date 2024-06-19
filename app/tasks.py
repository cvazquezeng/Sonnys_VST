from datetime import datetime, timedelta
import requests
from flask import current_app
from app.models import Ticket, db
import json
from .utils import convert_utc_to_est  # Import the function


def save_tickets(app):
    with app.app_context():
        fetch_active_tickets()
      
def update_tickets(app):
        fetch_closed_tickets()
        
def fetch_active_tickets():
    url_active = 'https://andon.sageclarity.com/AndonCenter/sites/71/events?filters=%7B%7D&sort=%7B%22date%22:1%7D'
    response_active = requests.get(url_active)
    active_ticket_ids = set()

    if response_active.status_code == 200:
        data_active = response_active.json().get('data', [])
        active_ticket_ids = {item['id'] for item in data_active}
        print(f"Active ticket IDs: {active_ticket_ids}")

        for item in data_active:
            ticket_id = item['id']
            timestamp = datetime.fromtimestamp(item['ts_epoch'] / 1000)
            color = item['ui']['colour']
            properties = {prop['name']: prop['value'] for prop in item['properties']}
            line_machine = properties.get('Line/Machine', '')
            andon_status = properties.get('Andon Status', '')
            notification_groups = properties.get('Notification Groups', '')
            issue_type = properties.get('Issue Type', '')
            comment = properties.get('Comment', '')

            existing_ticket = Ticket.query.filter_by(ticket_id=ticket_id).first()
            if not existing_ticket:
                new_ticket = Ticket(
                    ticket_id=ticket_id,
                    line_machine=line_machine,
                    andon_status=andon_status,
                    notification_groups=notification_groups,
                    issue_type=issue_type,
                    comment=comment,
                    timestamp=timestamp,
                    color=color,
                    closed_at=None  # New ticket is active
                )
                db.session.add(new_ticket)
                print(f"Added new ticket: {ticket_id}")
            else:
                if existing_ticket.andon_status != andon_status:
                    existing_ticket.andon_status = andon_status
                    print(f"Updated andon_status for ticket {ticket_id} to {andon_status}")
                
                if existing_ticket.closed_at is not None:
                    print(f"Reopening ticket: {ticket_id}")
                existing_ticket.closed_at = None  # Reopen ticket if it was closed

        try:
            db.session.commit()
            print("Session committed successfully.")
        except Exception as e:
            db.session.rollback()
            print(f"Error committing session: {e}")
    else:
        print(f"Failed to fetch active tickets, status code: {response_active.status_code}")



def fetch_closed_tickets():
    today = datetime.utcnow()
    seven_days_ago = today - timedelta(days=10)

    today_str = today.strftime('%b%%20%d,%%20%Y%%20%I:%M%%20%p')
    seven_days_ago_str = seven_days_ago.strftime('%b%%20%d,%%20%Y%%20%I:%M%%20%p')

    print(f"Fetching closed tickets from {seven_days_ago_str} to {today_str}")

    url_closed = (
        f'https://andon.sageclarity.com/AndonCenter/getAndonEntryDataTable.do?lineIds=1383,1384,1385,1386,1387,1388,1389,1390,1391,1392,1393,1394,1395,1396,1397,1398,1399,1400,1401,1402,1403,1404,1405,1406,1407,1408,1409,1410,1411,1412,1413,1414,1415,1416,1417,1419,1420,1421,1422,1423,1424,1425,1426,1427,1428,1429,1430,1431,1437,1438,1440,1442,1444,1446,1448,1450,1452,1454,1455,1456,1457,1459,1461,1463,1572,1573,1574,1575,1576,1577,1578,1579,1580'
        f'&currentDate={today.strftime("%Y-%m-%d")}'
        f'&companyId=71&pageNumber=1&statusIds=421,422,423,424,425,426&order=0&rowsPerPage=5125'
        f'&filterFromDate={seven_days_ago_str}&filterToDate={today_str}&_dc=1718803882854'
    )

    response_closed = requests.get(url_closed)
    
    #print(f"Request URL: {url_closed}")
    print(f"Response status code: {response_closed.status_code}")
    if response_closed.status_code == 200:
        data_closed = response_closed.json()
        ##print(f"Response JSON: {json.dumps(data_closed, indent=2)}")
        
        data_closed_entries = data_closed.get('Data', [])
        #print(f"Closed ticket data entries: {data_closed_entries}")

        closed_ticket_ids = {item['andonEntryMasterId'] for item in data_closed_entries}
        #print(f"Closed ticket IDs: {closed_ticket_ids}")

        for item in data_closed_entries:
            ticket_id = item['andonEntryMasterId']
            closed_timestamp = None
            acknowledged_timestamp = None
            request_made_timestamp = None

            for transaction in item.get('transactionMasterViewList', []):
                status = transaction.get('status')
                transaction_date = transaction.get('transactionUtc')
                if status == "Closed":
                    closed_timestamp = transaction_date
                elif status == "Acknowledged":
                    acknowledged_timestamp = transaction_date
                elif status == "Request Made":
                    request_made_timestamp = transaction_date

            existing_ticket = Ticket.query.filter_by(ticket_id=ticket_id).first()
            if existing_ticket:
                if closed_timestamp and not existing_ticket.closed_at:
                    closed_timestamp_dt = datetime.utcfromtimestamp(closed_timestamp / 1000)
                    existing_ticket.closed_at = convert_utc_to_est(closed_timestamp_dt)  # Convert to EST
                if acknowledged_timestamp and not existing_ticket.acknowledged_at:
                    acknowledged_timestamp_dt = datetime.utcfromtimestamp(acknowledged_timestamp / 1000)
                    existing_ticket.acknowledged_at = convert_utc_to_est(acknowledged_timestamp_dt)  # Convert to EST
                if request_made_timestamp and not existing_ticket.request_made_at:
                    request_made_timestamp_dt = datetime.utcfromtimestamp(request_made_timestamp / 1000)
                    existing_ticket.request_made_at = convert_utc_to_est(request_made_timestamp_dt)  # Convert to EST
                try:
                    db.session.commit()
                except Exception as e:
                    db.session.rollback()
                    print(f"Error committing ticket {ticket_id}: {e}")
            else:
                print(f"No existing ticket found for ID: {ticket_id}")
    else:
        print(f"Failed to fetch closed tickets, status code: {response_closed.status_code}")