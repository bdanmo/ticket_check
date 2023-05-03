import requests
import keyring
import json

#get API_TOKEN from keyring
API_TOKEN = keyring.get_password("check_ticket", "API_TOKEN")
your_helpdesk_url = "https://shsupport.jitbit.com/helpdesk"
users_endpoint = f"{your_helpdesk_url}/api/Users"

headers = {
    "Authorization": f"Bearer {API_TOKEN}"
}

response = requests.get(users_endpoint, headers=headers)

if response.status_code != 200:
    print(f"Error: {response.status_code} - {response.text}")
else:
    users = response.json()
    for user in users:
        print(f"User ID: {user['UserID']} - Name: {user['FirstName']} {user['LastName']} - Email: {user['Email']}")
