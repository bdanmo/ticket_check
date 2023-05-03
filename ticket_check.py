import requests
import json
import keyring
from datetime import datetime, timedelta

USER_BMO = "U02HB4RNNPQ"
API_TOKEN = keyring.get_password("check_ticket", "API_TOKEN")
ENGBOT_TOKEN = keyring.get_password("check_ticket", "ENGBOT_TOKEN")
BASE_URL = "https://shsupport.jitbit.com/helpdesk/"
API_TICKETS_ENDPOINT = f"{BASE_URL}api/Tickets"
TECH_ID = 10654784

now = datetime.now()
two_days_ago = now - timedelta(hours=48)
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
    overdue_tickets = []
    for ticket in tickets:
        print(f"Inspecting ticket {ticket['IssueID']}")
        updated_time = datetime.strptime(ticket['LastUpdated'], '%Y-%m-%dT%H:%M:%S.%fZ')
        if now - updated_time > timedelta(hours=48):
            print(f"Ticket {ticket['IssueID']} is overdue")
            overdue_tickets.append(ticket)
        else:
            print(f"Skipping ticket {ticket['IssueID']}")
    if len(overdue_tickets) > 0:
        print(f"Found {len(overdue_tickets)} overdue tickets")
        message = f"Tickets not updated in 48 hours:\n"
        for ticket in overdue_tickets:
            ticket_url = f"{BASE_URL}Ticket/{ticket['IssueID']}"
            message += f"- <{ticket_url}|#{ticket['IssueID']}> - {ticket['Subject']}\n"

        data = {
            "token": ENGBOT_TOKEN,
            "channel": USER_BMO,
            "as_user": True,
            "text": message,
        }

        print("Sending Slack message...")
        try:
            slack_response = requests.post(url="https://slack.com/api/chat.postMessage", data=data)
            slack_response_data = slack_response.json()

            # Check if the "ok" field in the Slack response is set to False
            if not slack_response_data.get('ok'):
                print(f"Error sending message to Slack: {slack_response_data.get('error')}")
            else:
                print("Message sent to Slack successfully!")

        except requests.exceptions.RequestException as e:
            print(f"Something went wrong sending the Slack message!\n{e}")