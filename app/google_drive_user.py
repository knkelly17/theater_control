"""Functions used to connect to Google Drive"""

# pylint: disable=no-member

from __future__ import print_function
import logging
import sys
import os
import re
from datetime import datetime
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

log = logging.getLogger(__name__)

D1 = datetime.now().strftime("%m/%d/%Y %H:%M:%S")

def get_target_width(range_string: str) -> int:
    """Calculates the column width of a Google Sheets range string (e.g., 'Sheet1!A1:K')."""
    # 1. Strip the sheet name if it exists
    if "!" in range_string:
        range_string = range_string.split("!")[-1]
        
    # 2. Split into start and end coordinates (e.g., ['A1', 'K'])
    parts = range_string.split(":")
    start_cell = parts[0]
    # Handle single cell ranges (e.g., "A1") safely by matching start and end
    end_cell = parts[1] if len(parts) > 1 else start_cell
    
    # 3. Strip out numbers and spaces, leaving only uppercase column letters
    start_col = re.sub(r"[^A-Za-z]", "", start_cell).upper()
    end_col = re.sub(r"[^A-Za-z]", "", end_cell).upper()
    
    # 4. Helper to convert column letters to a 1-based numerical index (Base-26)
    def col_to_num(col: str) -> int:
        num = 0
        for char in col:
            num = num * 26 + (ord(char) - ord('A') + 1)
        return num
    
    # 5. Calculate width
    return col_to_num(end_col) - col_to_num(start_col) + 1


SCOPES = ['https://www.googleapis.com/auth/drive',
          'https://www.googleapis.com/auth/calendar',
          'https://www.googleapis.com/auth/admin.directory.user',
          'https://www.googleapis.com/auth/gmail.settings.basic',
          'https://www.googleapis.com/auth/gmail.settings.sharing',
          'https://www.googleapis.com/auth/script.projects',
          'https://www.googleapis.com/auth/spreadsheets'
          ]

APPLICATION_NAME = 'Google Drive API Python'


def get_credentials():
    '''Gets valid user credentials from storage.'''

    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'google_userV2.json')
    client_secret_file = os.path.join(credential_dir,
                                      'client_secret.json')

    file_check = os.path.isfile(client_secret_file)
    if file_check is False:
        print('client_secret.json is missing from ~/.credentials')
        sys.exit()

    credentials = None
    if os.path.exists(credential_path):
        credentials = Credentials.from_authorized_user_file(credential_path, SCOPES)

    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                client_secret_file, SCOPES
            )
            credentials = flow.run_local_server(port=0)
            # Save the credentials for the next run
        with open(credential_path, "w", encoding="utf-8") as token:
            token.write(credentials.to_json())

    return credentials


def clear_sheet(creds, spreadsheet_id, worksheet_id):
    """Clear a google sheet (leave formatting)"""

    service = build("sheets", "v4", credentials=creds)

    requests = [{
        'updateCells': {
            'range': {
                'sheetId': worksheet_id
            },
            'fields': 'userEnteredValue'
        }
    }]

    body = {
        'requests': requests
    }
    response = service.spreadsheets().batchUpdate(spreadsheetId=spreadsheet_id, body=body).execute()  # pylint: disable=maybe-no-member

    return response


def clear_range(creds, spreadsheet_id, range_name):
    """Clear a range in a Google sheet (leave formatting)"""

    service = build("sheets", "v4", credentials=creds)

    body = {}

    result = service.spreadsheets().values().clear(  # pylint: disable=maybe-no-member
        spreadsheetId=spreadsheet_id, range=range_name, body=body
    ).execute()

    return result


def sheets_batch_update(creds, spreadsheet_id, title, find, replacement):
    """ Update the sheet details in batch, the user has access to."""

    #creds, _ = google.auth.default()
    # pylint: disable=maybe-no-member

    try:
        service = build("sheets", "v4", credentials=creds)

        requests = []
        # Change the spreadsheet's title.
        requests.append(
            {
                "updateSpreadsheetProperties": {
                    "properties": {"title": title},
                    "fields": "title",
                }
            }
        )
        # Find and replace text
        requests.append(
            {
                "findReplace": {
                    "find": find,
                    "replacement": replacement,
                    "allSheets": True,
                }
            }
        )
        # Add additional requests (operations) ...

        body = {"requests": requests}
        response = (
            service.spreadsheets()
            .batchUpdate(spreadsheetId=spreadsheet_id, body=body)
            .execute()
        )
        find_replace_response = response.get("replies")[1].get("findReplace")
        print(
            f"{find_replace_response.get('occurrencesChanged')} replacements made."
        )
        return response

    except HttpError as error:
        print(f"An error occurred: {error}")
        return error



def update_sheetv2(creds, spreadsheet_id, worksheet_id):
    """Update Sheet -- still testing"""

    service = build("sheets", "v4", credentials=creds)

    requests = [{
        'updateCells': {
            'range': {
                'sheetId': worksheet_id,
                "startRowIndex": 0,
                "startColumnIndex": 0,
                "endColumnIndex": 1,
                "endRowIndex": 1
            },
            'fields': '*',
            'rows': [
                {
                    'values': [
                        {
                            'userEnteredValue': {
                                "stringValue": "another test"
                            }
                        }

                    ]}
            ]

        }
    }]

    body = {
        'requests': requests
    }

    response = (
        service.spreadsheets()
        .batchUpdate(spreadsheetId=spreadsheet_id, body=body)
        .execute()
        )

    return response


def write_range(creds, spreadsheet_id, range_name, values):
    ''' Write to a range in a spreadsheet'''

    service = build("sheets", "v4", credentials=creds)

    body = {
        'values': values
    }

    value_input_option = 'USER_ENTERED'

    result = (
        service
        .spreadsheets()
        .values()
        .update(
            spreadsheetId=spreadsheet_id,
            range=range_name,
            valueInputOption=value_input_option,
            body=body
            )
        .execute()
    )

    return result

def sort_sheet(creds, spreadsheet_id, worksheet_id, cell_range, column, sort_order):
    '''Sort Google Sheet'''
    if sort_order is None:
        sort_order = 'ASCENDING'


    service = build("sheets", "v4", credentials=creds)

    requests = []

    requests.append(
        {
            "sortRange": {
                "range": {
                    "sheetId": worksheet_id,
                    "startRowIndex": cell_range['startRowIndex'],
                    "endRowIndex": cell_range['endRowIndex'],
                    "startColumnIndex": cell_range['startColumnIndex'],
                    "endColumnIndex": cell_range['endColumnIndex']
                },
                "sortSpecs":
                    {
                        "dimensionIndex": column,
                        "sortOrder": sort_order
                    }
            }
        }
    )

    body = {
        'requests': requests
    }

    response = service.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body=body).execute()

    return response

def run_gas_api (creds, show_id):
    '''testing google api'''
    service = build('script', 'v1', credentials=creds)

    # Target script project ID and the target function name
    script_id = 'AKfycbz4GnXz0aof1rmmbGLNk_FCthKl0q1D0hXBLi2T2p6LAfgEFHg5KSjc7rAKnq32B3oG'
    request = {
        'function': 'populateCastSheet',  # Name of JS function to run
        'parameters': [show_id]        # Parameters passed to it
    }

    try:
        response = service.scripts().run(scriptId=script_id, body=request).execute() # pylint: disable=maybe-no-member
        print(response['response']['result']['showCast'])
    except HttpError as error:
        print("Error executing script:", error)


def read_sheet(creds, spreadsheet_id, range_name):
    '''Read and return values from a Google Sheet Range'''

    target_width = get_target_width(range_name)

    service = build("sheets", "v4", credentials=creds)

    result = (
        service.
        spreadsheets().
        values().get(
            spreadsheetId=spreadsheet_id,
            range=range_name)
        .execute()
    )
    values = result.get('values', [])

    for value in values:
        while len(value) < target_width:
            value.append("")

    return values


def main():
    '''Testing only'''
    creds = get_credentials()
    # run_gas_api(creds, 1)
    sheet_id = '1BuNP3ruI6dw-VHDj3erRm--O606qF-Hc0vn25cv81_U'
    range_name = 'Students!A1:F'
    data = read_sheet(creds, sheet_id, range_name)
    print(data)


if __name__ == '__main__':
    main()
