from datetime import datetime, timedelta
import requests
from flask import current_app
from app.models import Ticket, db, ClosedTicket
import json
from .utils import convert_utc_to_edt  # Use relative import

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
    
    notification_groups_to_notify = [
        'Facilities', 'Maintenance 1st Shift', 
        'Robot Programming - 5605', 'Robot Programming - 5607', 
        'Testing','Sr Manager - Mfg Engineering'
    ]
    
    if response_active.status_code == 200:
        data_active = response_active.json().get('data', [])
        active_ticket_ids = {item['id'] for item in data_active}

        for item in data_active:
            ticket_id = item['id']
            timestamp = datetime.fromtimestamp(item['ts_epoch'] / 1000)  # Assume timestamp is in EDT
            formatted_timestamp = timestamp.strftime('%Y-%m-%d %H:%M:%S')  # MySQL compatible format
            formatted_timestamp_ampm = timestamp.strftime('%Y-%m-%d %I:%M %p')  # Convert to AM/PM format for Teams notification
            
            print(f"Received Timestamp: {timestamp}")  # Debug print
            
            color = item['ui']['colour']
            properties = {prop['name']: prop['value'] for prop in item['properties']}
            line_machine = properties.get('Line/Machine', '')
            andon_status = properties.get('Andon Status', '')
            notification_groups = properties.get('Notification Groups', '')
            issue_type = properties.get('Issue Type', '')
            comment = properties.get('Comment', '')

            # Split notification_groups string into a list of individual group names
            notification_groups_list = [group.strip() for group in notification_groups.split(',')]

            existing_ticket = Ticket.query.filter_by(ticket_id=ticket_id).first()
            if not existing_ticket:
                new_ticket = Ticket(
                    ticket_id=ticket_id,
                    line_machine=line_machine,
                    andon_status=andon_status,
                    notification_groups=notification_groups,
                    issue_type=issue_type,
                    comment=comment,
                    timestamp=timestamp,  # Use MySQL compatible format
                    color=color,
                    closed_at=None,  # New ticket is active
                    notified=False  # Initialize notified to False
                )
                db.session.add(new_ticket)
                db.session.commit()  # Commit here to ensure the ticket is added to the DB

                # Check if any of the notification groups to notify are found in the notification_groups string
                if any(group in notification_groups_list for group in notification_groups_to_notify):
                    new_ticket.notified = True  # Set notified to True before sending notification
                    db.session.commit()  # Commit the notified change
                    webhook_url = 'https://sonnysdirect.webhook.office.com/webhookb2/653a9e3d-5cab-4559-b35f-89e729b34e67@80a0cabe-dfaf-4e95-bdcb-366958455b28/IncomingWebhook/7b4e3100232e4a25932cb9cd144a6355/03ba285c-6d2f-45a9-aacb-778b9aa98af9'  # Replace with your Teams webhook URL
                    mention_users = ['carlos.vazquez@sonnysdirect.com', 'carlos.zapata@sonnysdirect.com','farid.ramezan@sonnysdirect.com','evan.reif@sonnysdirect.com']  # Replace with actual usernames to mention
                    ticket_details = {
                        "ticket_id": str(ticket_id),  # Ensure this is a string
                        "line_machine": line_machine,
                        "andon_status": andon_status,
                        "issue_type": issue_type,
                        "timestamp": formatted_timestamp_ampm,  # Use AM/PM format for Teams notification
                        "comment": comment,
                        "notification_groups": notification_groups
                    }
                    print(f"Sending notification for ticket: {ticket_id}")
                    send_teams_notification(webhook_url, ticket_details, mention_users)
            else:
                with db.session.begin_nested():
                    if existing_ticket.andon_status != andon_status:
                        existing_ticket.andon_status = andon_status

                    if existing_ticket.closed_at is not None:
                        print(f"Reopening ticket: {ticket_id}")
                    existing_ticket.closed_at = None  # Reopen ticket if it was closed

                    # Check if any of the notification groups to notify are found in the notification_groups string
                    if any(group in notification_groups_list for group in notification_groups_to_notify) and not existing_ticket.notified:
                        existing_ticket.notified = True  # Set notified to True before sending notification
                        db.session.commit()  # Commit the notified change to avoid race condition

                        webhook_url = 'https://sonnysdirect.webhook.office.com/webhookb2/653a9e3d-5cab-4559-b35f-89e729b34e67@80a0cabe-dfaf-4e95-bdcb-366958455b28/IncomingWebhook/7b4e3100232e4a25932cb9cd144a6355/03ba285c-6d2f-45a9-aacb-778b9aa98af9'  # Replace with your Teams webhook URL
                        mention_users = ['carlos.vazquez@sonnysdirect.com', 'carlos.zapata@sonnysdirect.com','farid.ramezan@sonnysdirect.com','evan.reif@sonnysdirect.com']  # Replace with actual usernames to mention
                        ticket_details = {
                            "ticket_id": str(ticket_id),  # Ensure this is a string
                            "line_machine": line_machine,
                            "andon_status": andon_status,
                            "issue_type": issue_type,
                            "timestamp": formatted_timestamp_ampm,  # Use AM/PM format for Teams notification
                            "comment": comment,
                            "notification_groups": notification_groups
                        }
                        print(f"Sending notification for ticket: {ticket_id}")
                        send_teams_notification(webhook_url, ticket_details, mention_users)

        try:
            db.session.commit()
            print("Session committed successfully.")
        except Exception as e:
            db.session.rollback()
            print(f"Error committing session: {e}")
    else:
        print(f"Failed to fetch active tickets, status code: {response_active.status_code}")


def fetch_closed_tickets():
    today = datetime.now()
    five_days_ago = today - timedelta(days=1)

    # Format the dates to the required format
    current_date = today.strftime('%b%%20%d,%%20%Y%%2000:00:AM')
    filter_from_date = five_days_ago.strftime('%b%%20%d,%%20%Y%%2000:AM')
    filter_to_date = today.strftime('%b%%20%d,%%20%Y%%2023:59:PM')

    url = f'https://andon.sageclarity.com/AndonCenter/getAndonEntryDataTable.do?lineIds=1383,1384,1385,1386,1387,1388,1389,1390,1391,1392,1393,1394,1395,1396,1397,1398,1399,1400,1401,1402,1403,1404,1405,1406,1407,1408,1409,1410,1411,1412,1413,1414,1415,1416,1417,1419,1420,1421,1423,1424,1425,1426,1427,1428,1429,1430,1431,1437,1438,1440,1442,1444,1446,1448,1450,1452,1454,1455,1456,1457,1459,1461,1463,1572,1573,1574,1575,1576,1577,1578,1579,1580&currentDate={current_date}&companyId=71&pageNumber=1&statusIds=421,422,423,424,425,426&order=0&rowsPerPage=5125&filterFromDate={filter_from_date}&filterToDate={filter_to_date}&_dc=1718803882854'
    print(url)
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        
        for item in data['Data']:
            ticket_id = item.get('andonEntryMasterId')
            line_machine = item.get('line')
            request_made_at = datetime.fromtimestamp(item['startUtc'] / 1000) if item['startUtc'] else None  # Assume timestamp is in EDT
            print(f"Request Made At: {request_made_at}")  # Debug print

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
                        print(f"Transaction UTC request_made_at: {request_made_at}")  # Debug print
                elif transaction['statusId'] == 422:  # Acknowledged
                    if transaction['transactionUtc']:
                        acknowledged_at = datetime.fromtimestamp(transaction['transactionUtc'] / 1000)
                        print(f"Transaction UTC acknowledged_at: {acknowledged_at}")  # Debug print
                elif transaction['statusId'] == 423:  # Closed
                    if transaction['transactionUtc']:
                        closed_at = datetime.fromtimestamp(transaction['transactionUtc'] / 1000)
                        print(f"Transaction UTC closed_at: {closed_at}")  # Debug print

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
                    #print(f"New ticket {ticket_id} added to the database.")
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
                        #print(f"Existing ticket {ticket_id} updated in the database.")
                    else:
                        print(f"No changes for ticket {ticket_id}. Skipping update.")

                db.session.commit()
            except Exception as e:
                db.session.rollback()
                print(f"Error committing new ticket {ticket_id}: {e}")
    else:
        print(f"Failed to fetch closed tickets, status code: {response.status_code}")

import requests

def send_teams_notification(webhook_url, ticket_details, mention_users):
    headers = {
        'Content-Type': 'application/json'
    }
    
    # Prepare the mentions part of the payload
    mentions = []
    mention_text = ""
    for user in mention_users:
        user_name = user.split('@')[0]  # Extracting name from email
        mention_text += f"<at>{user_name}</at> "
        mentions.append({
            "type": "mention",
            "text": f"<at>{user_name}</at>",
            "mentioned": {
                "name": user_name,
                "id": user  # Use email for the id
            }
        })
    
    # Construct the Adaptive Card payload
    payload = {
        "type": "message",
        "attachments": [
            {
                "contentType": "application/vnd.microsoft.card.adaptive",
                "contentUrl": None,
                "content": {
                    "type": "AdaptiveCard",
                    "version": "1.2",
                    "body": [
                        {
                            "type": "TextBlock",
                            "text": "New Open Ticket Notification",
                            "weight": "Bolder",
                            "size": "Medium"
                        },
                        {
                            "type": "FactSet",
                            "facts": [
                                {"title": "Ticket ID:", "value": ticket_details["ticket_id"]},
                                {"title": "Line/Machine:", "value": ticket_details["line_machine"]},
                                {"title": "Status:", "value": ticket_details["andon_status"]},
                                {"title": "Issue:", "value": ticket_details["issue_type"]},
                                {"title": "Timestamp:", "value": ticket_details["timestamp"]},
                                {"title": "Comment:", "value": ticket_details["comment"]},
                                {"title": "Notification Groups:", "value": ticket_details["notification_groups"]}
                            ]
                        },
                        {
                            "type": "TextBlock",
                            "text": f"{mention_text}",
                            "wrap": True
                        },
                        {
                            "type": "ActionSet",
                            "actions": [
                                {
                                    "type": "Action.OpenUrl",
                                    "title": "View Ticket",
                                    "url": "https://andon.sageclarity.com/AndonCenter/mobile/"
                                }
                            ]
                        }
                    ],
                    "msteams": {
                        "entities": mentions
                    }
                }
            }
        ]
    }
    
    try:
        response = requests.post(webhook_url, headers=headers, json=payload)
        response.raise_for_status()
        print(f"Notification sent successfully: {ticket_details['ticket_id']}")
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err} - Response: {response.text}")
    except Exception as err:
        print(f"Other error occurred: {err}")

#FETCH CLOSED TICKETS???