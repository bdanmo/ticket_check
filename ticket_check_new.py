import requests
import json
from datetime import datetime, timedelta
from static.secret import API_TOKEN, ENGBOT_TOKEN

BASE_URL = "https://shsupport.jitbit.com/helpdesk/"
API_TICKETS_ENDPOINT = f"{BASE_URL}api/Tickets"
TECH_ID = 10654784
SLACK_CH = "C056RFX3SP4"
NEW_STATUS = 1  # Assuming 'NEW' status has a value of 1

now = datetime.now()
payload = {
    "mode": "unclosed",
    "handledByUserID": f"{TECH_ID}",
    "count": 50  # Max number of tickets per call
}

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {API_TOKEN}"
}

response = requests.get(API_TICKETS_ENDPOINT, headers=headers, params=payload)

if response.status_code != 200:
    print(f"Error: {response.status_code} - {response.text}")
else:
    print("Processing API response...")
    tickets = json.loads(response.text)
    print(f"Total tickets returned: {len(tickets)}")
    new_tickets = []
    for ticket in tickets:
        print(f"Inspecting ticket {ticket['IssueID']}")
        if ticket['StatusID'] == NEW_STATUS:
            print(f"Ticket {ticket['IssueID']} has a NEW status")
            new_tickets.append(ticket)
        else:
            print(f"Skipping ticket {ticket['IssueID']}")

    if len(new_tickets) > 0:
        print(f"Found {len(new_tickets)} NEW tickets")
        message = f"New tickets:\n"
        for ticket in new_tickets:
            ticket_url = f"{BASE_URL}Ticket/{ticket['IssueID']}"
            message += f"- <{ticket_url}|#{ticket['IssueID']}> - {ticket['Subject']}\n"

        data = {
            "token": ENGBOT_TOKEN,
            "channel": SLACK_CH,
            "as_user": True,
            "text": message,
        }

        print("Sending Slack message...")
        try:
            slack_response = requests.post(url="https://slack.com/api/chat.postMessage", data=data)
            slack_response_data = slack_response.json()

            if not slack_response_data.get('ok'):
                print(f"Error sending message to Slack: {slack_response_data.get('error')}")
            else:
                print("Message sent to Slack successfully!")

        except requests.exceptions.RequestException as e:
            print(f"Something went wrong sending the Slack message!\n{e}")
