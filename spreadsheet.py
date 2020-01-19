import gspread
import requests
import json
from oauth2client.service_account import ServiceAccountCredentials

# google sheets setup
scope = ['https://spreadsheets.google.com/feeds']
creds = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scope)
client = gspread.authorize(creds)

# url of corresponding spreadsheet
url = 'https://docs.google.com/spreadsheets/d/1n9x4QEhjhXnEcLyd7jicAnf58Ng2pqDMO-IC-b-BOrs' # Infinite Recharge Scouting Sheet Template

# open sheet
sheet = client.open_by_url(url)

# individual worksheets of google sheets document
key_worksheet = sheet.worksheet('Key')
teams_worksheet = sheet.worksheet('Teams')
sample_team_worksheet = sheet.worksheet('Sample Team')
schedule_worksheet = sheet.worksheet('Schedule')
team_data_worksheet = sheet.worksheet('Team Data')

# setting event key to value in A1 of Key worksheet
event_key = key_worksheet.cell(1, 1).value

# 2537 cell format
format_2537 = CellFormat(backgroundColor=Color(.148, .98, .216)) # 25fa37 converted to rgb out of 1

# tba setup
tba_session = requests.Session()
BASE_URL = 'https://www.thebluealliance.com/api/v3'

# tba credentials setup
with open('client_secret_tba.json') as json_file:
    data = json.load(json_file)
    tba_auth_key = data['tba_auth_key']
    tba_session.headers.update({'X-TBA-Auth-Key': tba_auth_key})
