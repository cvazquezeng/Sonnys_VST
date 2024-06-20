from datetime import datetime, timedelta
import requests
from flask import current_app
from app.models import Ticket, db, ClosedTicket
import json
from .utils import convert_utc_to_est  # Import the function


def save_tickets(app):
    with app.app_context():
        fetch_active_tickets()
      
def update_tickets(app):
    with app.app_context():
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
    url = 'https://andon.sageclarity.com/AndonCenter/getAndonEntryDataTable.do?lineIds=1383,1384,1385,1386,1387,1388,1389,1390,1391,1392,1393,1394,1395,1396,1397,1398,1399,1400,1401,1402,1403,1404,1405,1406,1407,1408,1409,1410,1411,1412,1413,1414,1415,1416,1417,1419,1420,1421,1423,1424,1425,1426,1427,1428,1429,1430,1431,1437,1438,1440,1442,1444,1446,1448,1450,1452,1454,1455,1456,1457,1459,1461,1463,1572,1573,1574,1575,1576,1577,1578,1579,1580&currentDate=2024-06-20&companyId=71&pageNumber=1&statusIds=421,422,423,424,425,426&order=0&rowsPerPage=5125&filterFromDate=Jun%2010,%202024%2012:05%20AM&filterToDate=Jun%2020,%202024%2012:05%20AM&_dc=1718803882854'
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        
        for item in data['Data']:
            ticket_id = item.get('andonEntryMasterId')
            line_machine = item.get('line')
            request_made_at = datetime.fromtimestamp(item['startUtc'] / 1000) if item['startUtc'] else None
            acknowledged_at = None
            closed_at = None
            issue_type = None
            comment = None

            # Parse issue_type and comment from nonMandatoryFields
            for field in item.get('nonMandatoryFields', []):
                if field.get('fieldId') == 1137:  # Assuming 1137 is the fieldId for issue_type
                    issue_type = field.get('fieldValue')
                elif field.get('fieldId') == 1228:  # Assuming 1228 is the fieldId for comment
                    comment = field.get('fieldValue')

            # Parse transaction dates
            for transaction in item.get('transactionMasterViewList', []):
                if transaction['statusId'] == 421:  # Request Made
                    if transaction['transactionUtc']:
                        request_made_at = datetime.fromtimestamp(transaction['transactionUtc'] / 1000)
                elif transaction['statusId'] == 422:  # Acknowledged
                    if transaction['transactionUtc']:
                        acknowledged_at = datetime.fromtimestamp(transaction['transactionUtc'] / 1000)
                elif transaction['statusId'] == 423:  # Closed
                    if transaction['transactionUtc']:
                        closed_at = datetime.fromtimestamp(transaction['transactionUtc'] / 1000)

            notification_groups = item.get('notificationGroupNames')
            if notification_groups:
                notification_groups = notification_groups[:255]  # Truncate to fit within column length

            try:
                # Insert into ClosedTicket
                existing_ticket = ClosedTicket.query.filter_by(ticket_id=ticket_id).first()
                if not existing_ticket:
                    new_ticket = ClosedTicket(
                        ticket_id=ticket_id,
                        line_machine=line_machine,
                        request_made_at=request_made_at,
                        acknowledged_at=acknowledged_at,
                        closed_at=closed_at,
                        issue_type=issue_type,
                        comment=comment,
                        notification_groups=notification_groups
                    )
                    db.session.add(new_ticket)
                    print(f"New ticket {ticket_id} added to the database.")
                else:
                    if (
                        existing_ticket.line_machine != line_machine or
                        existing_ticket.request_made_at != request_made_at or
                        existing_ticket.acknowledged_at != acknowledged_at or
                        existing_ticket.closed_at != closed_at or
                        existing_ticket.issue_type != issue_type or
                        existing_ticket.comment != comment or
                        existing_ticket.notification_groups != notification_groups
                    ):
                        existing_ticket.line_machine = line_machine
                        existing_ticket.request_made_at = request_made_at
                        existing_ticket.acknowledged_at = acknowledged_at
                        existing_ticket.closed_at = closed_at
                        existing_ticket.issue_type = issue_type
                        existing_ticket.comment = comment
                        existing_ticket.notification_groups = notification_groups
                        db.session.add(existing_ticket)
                        print(f"Existing ticket {ticket_id} updated in the database.")
                    else:
                        print(f"No changes for ticket {ticket_id}. Skipping update.")

                db.session.commit()
            except Exception as e:
                db.session.rollback()
                print(f"Error committing new ticket {ticket_id}: {e}")
    else:
        print(f"Failed to fetch closed tickets, status code: {response.status_code}")