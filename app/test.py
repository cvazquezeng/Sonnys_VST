import requests
webhook_url = 'https://sonnysdirect.webhook.office.com/webhookb2/653a9e3d-5cab-4559-b35f-89e729b34e67@80a0cabe-dfaf-4e95-bdcb-366958455b28/IncomingWebhook/6b21e8aef9e944e8827645c53c1bd9ad/03ba285c-6d2f-45a9-aacb-778b9aa98af9'  # Replace with your Teams webhook URL
message = "test ignore"
mention_users = ['carlos.vazquez@sonnysdirect.com', 'carlos.zapata@sonnysdirect.com']

def send_teams_notificationtest(webhook_url, message, mention_users):
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
                            "text": f"{mention_text}\n\n{message}",
                            "wrap": True
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
        print(f"Notification sent successfully: {message}")
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err} - Response: {response.text}")
    except Exception as err:
        print(f"Other error occurred: {err}")

# Call the function with the required parameters
send_teams_notificationtest(webhook_url, message, mention_users)