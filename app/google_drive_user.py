"""Functions used to connect to Google Drive"""

from __future__ import print_function
import sys
import os
from datetime import datetime
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


D1 = datetime.now().strftime("%m/%d/%Y %H:%M:%S")

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
    response = service.spreadsheets().batchUpdate(spreadsheetId=spreadsheet_id, body=body).execute()

    return response


def clear_sheet_formatting(http, spreadsheetId, worksheetId):
    # http = credentials.authorize(httplib2.Http())

    background_color = {'red': 1.0, 'green': 1.0, 'blue': 1.0}
    font_color = {'red': 0.0, 'green': 0.0, 'blue': 0.0}

    discoveryUrl = ('https://sheets.googleapis.com/$discovery/rest?'
                    'version=v4')
    service = discovery.build('sheets', 'v4', http=http, discoveryServiceUrl=discoveryUrl)

    requests = []

    requests.append([{
        'updateCells': {
            'range': {
                'sheetId': worksheetId
            },
            'fields': 'userEnteredValue'
        }
    }, {
        "unmergeCells": {
            "range": {"sheetId": worksheetId}
        }
    }, {
        "repeatCell": {
            "range": {
                "sheetId": worksheetId,

            },
            "cell": {
                "userEnteredFormat": {
                    "backgroundColor": background_color,
                    "horizontalAlignment": 'LEFT',
                    "textFormat": {
                        "foregroundColor": font_color,
                        "bold": 'false'
                    }
                }
            },
            "fields": "userEnteredFormat(backgroundColor,textFormat,horizontalAlignment)"
        }
    }, {
        "updateBorders": {
            "range": {"sheetId": worksheetId},
            "top": {"style": "NONE"},
            "bottom": {"style": "NONE"},
            "innerHorizontal": {"style": "NONE"},
            "innerVertical": {"style": "NONE"}
        }
    }])

    body = {
        'requests': requests
    }
    response = service.spreadsheets().batchUpdate(spreadsheetId=spreadsheetId, body=body).execute()

    return response


def write_range(creds, spreadsheetId, rangeName, values):

    service = build("sheets", "v4", credentials=creds)

    body = {
        'values': values
    }

    value_input_option = 'USER_ENTERED'

    result = service.spreadsheets().values().update(spreadsheetId=spreadsheetId, range=rangeName,
                                                    valueInputOption=value_input_option, body=body).execute()

    return result


def merge_cells(http, spreadsheetId, worksheetId, cell_range, merge_type):
    if merge_type is None:
        merge_type = 'MERGE_ALL'

    discoveryUrl = ('https://sheets.googleapis.com/$discovery/rest?'
                    'version=v4')
    service = discovery.build('sheets', 'v4', http=http, discoveryServiceUrl=discoveryUrl)

    requests = []

    requests.append(
        {
            "mergeCells": {
                "range": {
                    "sheetId": worksheetId,
                    "startRowIndex": cell_range['startRowIndex'],
                    "endRowIndex": cell_range['endRowIndex'],
                    "startColumnIndex": cell_range['startColumnIndex'],
                    "endColumnIndex": cell_range['endColumnIndex']
                },
                "mergeType": merge_type
            }
        }
    )

    body = {
        'requests': requests
    }

    response = service.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheetId,
        body=body).execute()

    return response


def sort_sheet(creds, spreadsheet_id, worksheet_id, cell_range, column, sort_order):
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


def format_cell_font(http, spreadsheetId, worksheetId, cell_range, font_props):
    font_color = {'red': 0.0, 'green': 0.0, 'blue': 0.0}

    if 'font_color' in font_props:
        font_color = font_props['font_color']

    background_color = {'red': 1.0, 'green': 1.0, 'blue': 1.0}

    if 'background_color' in font_props:
        background_color = font_props['background_color']

    font_size = 12

    if 'font_size' in font_props:
        font_size = font_props['font_size']

    font_bold = 'false'

    if 'font_bold' in font_props:
        font_bold = font_props['font_bold']

    horizontalAlignment = 'CENTER'

    if 'horizontalAlignment' in font_props:
        horizontalAlignment = font_props['horizontalAlignment']

    discoveryUrl = ('https://sheets.googleapis.com/$discovery/rest?'
                    'version=v4')
    service = discovery.build('sheets', 'v4', http=http, discoveryServiceUrl=discoveryUrl)

    requests = []

    requests.append(
        [
            {
                "repeatCell": {
                    "range": {
                        "sheetId": worksheetId,
                        "startRowIndex": cell_range['startRowIndex'],
                        "endRowIndex": cell_range['endRowIndex'],
                        "startColumnIndex": cell_range['startColumnIndex'],
                        "endColumnIndex": cell_range['endColumnIndex']
                    },
                    "cell": {
                        "userEnteredFormat": {
                            "backgroundColor": background_color,
                            "horizontalAlignment": horizontalAlignment,
                            "textFormat": {
                                "foregroundColor": font_color,
                                "fontSize": font_size,
                                "bold": font_bold
                            }
                        }
                    },
                    "fields": "userEnteredFormat(backgroundColor,textFormat,horizontalAlignment)"
                }
            }
        ]
    )

    body = {
        'requests': requests
    }

    response = service.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheetId,
        body=body).execute()

    return response


def format_range_border(http, spreadsheetId, worksheetID, border_range, style):
    # http = credentials.authorize(httplib2.Http())
    discoveryUrl = ('https://sheets.googleapis.com/$discovery/rest?'
                    'version=v4')
    service = discovery.build('sheets', 'v4', http=http, discoveryServiceUrl=discoveryUrl)

    requests = []
    # Change the spreadsheet's border.
    # outRange.setBorder(true, true, true, true, false, false, 'black', SpreadsheetApp.BorderStyle.SOLID_MEDIUM)
    # setBorder(top, left, bottom, right, vertical, horizontal, color, style)

    requests.append({
        "updateBorders": {
            "range": {
                "sheetId": worksheetID,
                "startRowIndex": border_range['startRowIndex'],
                "endRowIndex": border_range['endRowIndex'],
                "startColumnIndex": border_range['startColumnIndex'],
                "endColumnIndex": border_range['endColumnIndex']
            }, 'top': {
                "style": style,
                "color": {
                    "blue": 0.0,
                    "green": 0.0,
                    "red": 0.0
                },
            }, 'bottom': {
                "style": style,
                "color": {
                    "red": 0.0,
                    "green": 0.0,
                    "blue": 0.0
                },
            }, 'left': {
                "style": style,
                "color": {
                    "red": 0.0,
                    "green": 0.0,
                    "blue": 0.0
                },
            }, 'right': {
                "style": style,
                "color": {
                    "red": 0.0,
                    "green": 0.0,
                    "blue": 0.0
                },
            }
        }
    })

    body = {
        'requests': requests
    }

    response = service.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheetId,
        body=body).execute()

    return response


def list_files_in_folder(creds, folder_id):

    try:
        # create drive api client
        service = build("drive", "v3", credentials=creds)
        files = []
        page_token = None
        while True:
            # pylint: disable=maybe-no-member
            response = (
                service.files()
                .list(
                    q="mimeType='image/jpeg'",
                    spaces="drive",
                    corpora='drive',
                    pageSize=100,
                    driveId=folder_id,
                    includeTeamDriveItems='true',
                    supportsTeamDrives='true',
                    supportsAllDrives='true',
                    fields="nextPageToken, files(id, name)",
                    pageToken=page_token,
                )
                .execute()
            )
            for file in response.get("files", []):
                # Process change
                print(f'Found file: {file.get("name")}, {file.get("id")}')
            files.extend(response.get("files", []))
            page_token = response.get("nextPageToken", None)
            if page_token is None:
                break

    except HttpError as error:
        print(f"An error occurred: {error}")
        files = None

    return files


def rename_worksheet(http, name, spreadsheet_id, worksheet_id):
    discoveryUrl = ('https://sheets.googleapis.com/$discovery/rest?'
                    'version=v4')
    service = discovery.build('sheets', 'v4', http=http, discoveryServiceUrl=discoveryUrl)

    request_body = {
        "requests": [
            {
                "updateSheetProperties": {
                    "fields": "title",
                    "properties": {
                        "title": name,
                        "sheetId": worksheet_id
                    }
                }
            }
        ]
    }

    result = service.spreadsheets().batchUpdate(spreadsheetId=spreadsheet_id, body=request_body).execute()
    return result


def create_sheet(http, title, parent_folder_ids):
    service = discovery.build('drive', 'v3', http=http)

    body = {
        "parents": [parent_folder_ids],
        "name": title,
        "mimeType": "application/vnd.google-apps.spreadsheet"
    }

    req = service.files().create(body=body)
    new_sheet = req.execute()

    # Get id of fresh sheet

    return new_sheet


def copy_file(http, origin_file_id, copy_title, parent_folder_ids):
    service = discovery.build('drive', 'v3', http=http)
    """Copy an existing file.

    Args:
      origin_file_id: ID of the origin file to copy.
      copy_title: Title of the copy.
      parents: folder for copy

    Returns:
      The copied file if successful, None otherwise.
    """
    body = {
        "parents": [parent_folder_ids],
        "name": copy_title,
        "mimeType": "application/vnd.google-apps.spreadsheet"
    }

    try:
        return service.files().copy(fileId=origin_file_id, supportsAllDrives='true', body=body).execute()
    except errors.HttpError as error:
        print('An error occurred: %s' % error)
    return None


def read_sheet(creds, spreadsheet_id, range_name):
    """Shows basic usage of the Sheets API.

    Creates a Sheets API service object and prints the names and majors of
    students in a sample spreadsheet:
    https://docs.google.com/spreadsheets/d/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms/edit
    """
    #discoveryUrl = ('https://sheets.googleapis.com/$discovery/rest?'
     #               'version=v4')
    #service = discovery.build('sheets', 'v4', http=http, discoveryServiceUrl=discoveryUrl)

    service = build("sheets", "v4", credentials=creds)

    result = service.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range=range_name).execute()
    values = result.get('values', [])

    return values


def read_sheet_multi(http, spreadsheetId, ranges):
    """Shows basic usage of the Sheets API.

    Creates a Sheets API service object and prints the names and majors of
    students in a sample spreadsheet:
    https://docs.google.com/spreadsheets/d/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms/edit
    """
    discoveryUrl = ('https://sheets.googleapis.com/$discovery/rest?'
                    'version=v4')
    service = discovery.build('sheets', 'v4', http=http, discoveryServiceUrl=discoveryUrl)

    # result = service.spreadsheets().values().get(spreadsheetId=spreadsheetId, range=rangeName).execute()

    # request = service.spreadsheets().values().batchGet(spreadsheetId=spreadsheet_id, ranges=ranges, valueRenderOption=value_render_option, dateTimeRenderOption=date_time_render_option)
    request = service.spreadsheets().values().batchGet(spreadsheetId=spreadsheetId, ranges=ranges)
    response = request.execute()
    values = response['valueRanges']

    # values = response.get('values', [])

    return values


def append_rows(http, spreadsheet_id, update_range, values):
    request_body = {
        "values": values
    }
    discovery_url = ('https://sheets.googleapis.com/$discovery/rest?'
                     'version=v4')

    service = discovery.build('sheets', 'v4', http=http, discoveryServiceUrl=discovery_url)
    request = service.spreadsheets().values().append(spreadsheetId=spreadsheet_id,
                                                     range=update_range,
                                                     valueInputOption='USER_ENTERED',
                                                     body=request_body).execute()

    return request


def getValues(http, spreadsheetID, rangeName, fieldsList):
    # values = google_drive_user.read_sheet(http,spreadsheetID,rangeName)

    values = read_sheet_multi(http, spreadsheetID, rangeName)

    data_values = values[0]['values']

    output = []
    if not data_values:
        output.append(['No Values'])
    else:
        columnList = data_values.pop(0)
        for row in data_values:
            rowObject = {}
            for thisField in fieldsList:
                # rowList.append(row[columnList.index(thisField)])
                rowObject[thisField] = row[columnList.index(thisField)]
            output.append(rowObject)
    return output


def create_file(http, type, name, parentID):
    service = discovery.build('drive', 'v3', http=http)
    parents = [parentID]

    file_metadata = {
        'name': name,
        'mimeType': type,
        'parents': parents
    }
    file = service.files().create(body=file_metadata,
                                  fields='id').execute()

    return file
    # print ('Folder ID: %s' % file.get('id'))

def check_forwarding(creds):
  """Enable email forwarding.
  Returns:Draft object, including forwarding id and result meta data.

  Load pre-authorized user credentials from the environment.
  TODO(developer) - See https://developers.google.com/identity
  for guides on implementing OAuth2 for the application.
  """

  try:
    creds.with_subject('kkelly@apixio.com')

    # create gmail api client
    service = build("gmail", "v1", credentials=creds)

    address = {"userId": "kkelly@apixio.com"}

    # pylint: disable=E1101
    result = (
        service.users()
        .settings()
        .forwardingAddresses()
        .list(userId="me")
        .execute()
    )
    if result.get("verificationStatus") == "accepted":
        body = {
          "emailAddress": result.get("forwardingEmail"),
          "enabled": True,
          "disposition": "trash",
      }
    result = (
          service.users()
          .settings()
          .updateAutoForwarding(userId="me", body=body)
          .execute()
      )
    print(f"Forwarding is enabled : {result}")

  except HttpError as error:
    print(f"An error occurred: {error}")
    result = None

  return result

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
    except Exception as e:
        print("Error executing script:", e)

def main():
    '''Testing only'''
    creds = get_credentials()
    run_gas_api(creds, 1)


if __name__ == '__main__':
    main()
