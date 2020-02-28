from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

import get_tba_data as tba

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

SPREADSHEET_ID = '1-XxmqQ11Bt-7CXdv15jJwG4fhCMnX_V056vsYL6vc00' # 2020 Bethesda Scouting Sheet Machine
# SPREADSHEET_ID = '14-0lqzfEFppumw82uaCD8cBPqLVUKH2E7I_QyU3aK_s' # [test] 2019 Bethesda Scouting Sheet Machine

value_input_option = 'USER_ENTERED'

# Ranges for cells to be read from and written to
KEY_RANGE = 'Key!A1'
TEAMS_RANGE = 'teams'
MATCHES_RANGE = 'matches'
RED_SCHEDULE_RANGE = 'red_sched'
BLUE_SCHEDULE_RANGE = 'blue_sched'
METRICS_RANGE = 'metrics'
SAMPLE_TEAM_SHEET_RANGE = 'SampleTeam!A1:W22'

creds = None
# The file token.pickle stores the user's access and refresh tokens, and is
# created automatically when the authorization flow completes for the first
# time.
if os.path.exists('token.pickle'):
    with open('token.pickle', 'rb') as token:
        creds = pickle.load(token)
# If there are no (valid) credentials available, let the user log in.
if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file(
            'credentials.json', SCOPES)
        creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open('token.pickle', 'wb') as token:
        pickle.dump(creds, token)

service = build('sheets', 'v4', credentials=creds)

# Call the Sheets API
sheet = service.spreadsheets()

def get_key():
    key_result = service.spreadsheets().values().get(spreadsheetId=SPREADSHEET_ID, range=KEY_RANGE).execute()
    return key_result['values'][0][0]

def fill_teams(event):
    teams_raw = tba.get_teams(event)
    teams = []
    for team in teams_raw:
        teams.append([team])
    body = {'values': teams}
    result = service.spreadsheets().values().update(spreadsheetId=SPREADSHEET_ID, range=TEAMS_RANGE, valueInputOption=value_input_option, body=body).execute()
    # print(result) # for debugging

def fill_red_schedule(event):
    red_schedule = tba.get_color_schedule(event, 'red')
    body = {'values': red_schedule}
    result = service.spreadsheets().values().update(spreadsheetId=SPREADSHEET_ID, range=RED_SCHEDULE_RANGE, valueInputOption=value_input_option, body=body).execute()
    # print(result) # for debugging

def fill_blue_schedule(event):
    """Returns number of updated rows"""
    blue_schedule = tba.get_color_schedule(event, 'blue')
    body = {'values': blue_schedule}
    result = service.spreadsheets().values().update(spreadsheetId=SPREADSHEET_ID, range=BLUE_SCHEDULE_RANGE, valueInputOption=value_input_option, body=body).execute()
    return result['updatedRows']
    # print(result) # for debugging

def create_match_list(num_matches):
    matches = []
    for i in range(num_matches):
        matches.append([i+1])
    return matches

def fill_matches(num_matches):
    body = {'values': create_match_list(num_matches)}
    result = service.spreadsheets().values().update(spreadsheetId=SPREADSHEET_ID, range=MATCHES_RANGE, valueInputOption=value_input_option, body=body).execute()
    # print(result) # for debugging

def fill_schedule(event):
    """Call this method to fill the entire schedule"""
    fill_red_schedule(event)
    num_matches = fill_blue_schedule(event)
    fill_matches(num_matches)

def fill_metrics(event):
    """Call this method to fill OPRs, DPRs, and CCWMs for all teams"""
    metrics = tba.get_metrics(event)
    team_data = []
    for team in metrics['oprs']:
        team_data.append([team[3:], metrics['oprs'][team], metrics['dprs'][team], metrics['ccwms'][team]])
    body = {'values': team_data}
    result = service.spreadsheets().values().update(spreadsheetId=SPREADSHEET_ID, range=METRICS_RANGE, valueInputOption=value_input_option, body=body).execute()
    print(result) # for debugging

def get_sample_team_sheet():
    team_sheet = service.spreadsheets().values().get(spreadsheetId=SPREADSHEET_ID, range=SAMPLE_TEAM_SHEET_RANGE).execute()
    return team_sheet['values']

def create_team_sheets(event):
    requests = []
    teams = tba.get_teams(event)
    index = 7
    for team in reversed(teams):
        requests.append({
            'addSheet': {
                'properties': {
                    'title': team,
                    'index': index
                }
            }
        })
    body = {'requests': requests}
    response = service.spreadsheets().batchUpdate(spreadsheetId=SPREADSHEET_ID, body=body).execute()

def copy_to_team_sheets(event, to_copy):
    teams = tba.get_teams(event)
    for team in teams:
        team_sheet = to_copy
        team_sheet[0][1] = team
        body = {'values': team_sheet}
        range = team + '!A1:W22'
        result = service.spreadsheets().values().update(spreadsheetId=SPREADSHEET_ID, range=range, valueInputOption=value_input_option, body=body).execute()

if __name__ == '__main__':
    key = get_key()
    # fill_teams(key)
    # fill_red_schedule(key)
    # fill_blue_schedule(key)
    # print(create_match_list(80))
    # fill_matches(20)
    # fill_schedule(key)
    # fill_metrics(key)
    sample_team_sheet = get_sample_team_sheet()
    # print(sample_team_sheet)
    create_team_sheets(key)
    copy_to_team_sheets(key, sample_team_sheet)
