import json
import requests
import time
from google.oauth2 import service_account
from googleapiclient.discovery import build
import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Google Sheets Configuration
SPREADSHEET_ID = os.getenv('SPREADSHEET_ID')
RANGE_NAME = 'top10!A2:D'  # Adjust if necessary

# Slack Webhook URL
SLACK_WEBHOOK_URL = os.getenv('SLACK_WEBHOOK_URL')

# Authenticate with Google Sheets API
def authenticate_google_sheets():
    creds = service_account.Credentials.from_service_account_file(
        'credentials.json', scopes=['https://www.googleapis.com/auth/spreadsheets.readonly']
    )
    return build('sheets', 'v4', credentials=creds)

# Get data from Google Sheets
def get_sheet_data():
    service = authenticate_google_sheets()
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range=RANGE_NAME).execute()
    return result.get('values', [])

# Send message to Slack
def send_slack_message(name, level, element):
    slack_message = {
        'text': f'📢 New Entry Added:\n*Name:* {name}\n*Star Level:* {level}\n*Element:* {element}'
    }
    response = requests.post(SLACK_WEBHOOK_URL, json=slack_message)
    if response.status_code == 200:
        print('Message sent successfully to Slack.')
    else:
        print(f'Error sending message: {response.status_code}, {response.text}')

# Monitor Google Sheets for new rows
def monitor_sheet():
    seen_rows = set()
    print("Monitoring Google Sheets for new entries...")
    
    while True:
        rows = get_sheet_data()
        for row in rows:
            row_tuple = tuple(row)
            if row_tuple not in seen_rows:
                seen_rows.add(row_tuple)
                if len(row) >= 3:
                    send_slack_message(row[0], row[1], row[2])
        time.sleep(10)  # Poll every 10 seconds

if __name__ == '__main__':
    monitor_sheet()
