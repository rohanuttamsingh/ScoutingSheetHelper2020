import requests
import json

# tba setup
tba_session = requests.Session()
BASE_URL = 'https://www.thebluealliance.com/api/v3'

# tba credentials setup
with open('client_secret_tba.json') as json_file:
    data = json.load(json_file)
    tba_auth_key = data['tba_auth_key']
    tba_session.headers.update({'X-TBA-Auth-Key': tba_auth_key})

def get_teams(event):
    """Returns all teams from event in a list
    event: event key (e.g. 2020mdbet)"""
    teams_raw = tba_session.get(BASE_URL + '/event/%s/teams/keys' % event).json()
    teams = []
    for team_raw in teams_raw:
        teams.append(team_raw[3:])
    return teams

def get_color_schedule(event, color):
    """Returns match schedule of specified alliance color in a list
    event: event key (e.g. 2020mdbet)
    color: red or blue"""
    schedule = []
    event_list = tba_session.get(BASE_URL + '/event/%s/matches/simple' % event).json() # list of dicts
    for match in event_list:
        schedule.append(match['alliances'][color]['team_keys'])
    for alliance in schedule:
        for i in range(len(alliance)):
            alliance[i] = alliance[i][3:]
            # trims 'frc' from beginning of every team number
    return schedule

def get_metrics(event):
    """Returns all OPRs, DPRs, and CCWM's from event in a dictionary
    event: event key (e.g. 2020mdbet)"""
    return tba_session.get(BASE_URL + '/event/%s/oprs' %event).json()

def get_teams_attending_two_events(event1, event2):
    """Returns all teams that are attending 2 specified events
    event1: event key of 1st event of interest
    event2: event key of 2nd event of interest"""
    teams_at_both = []
    teams1 = get_teams(event1)
    teams2 = get_teams(event2)
    for team1 in teams1:
        if team1 in teams2:
            teams_at_both.append(team1)
    return teams_at_both

def test():
    key = input('enter event key: ')
    print('teams:', get_teams(key))
    print('red schedule:', get_color_schedule(key, 'red'), 'blue schedule: ', get_color_schedule(key, 'blue'))
    print('metrics:', get_metrics(key))

if __name__ == '__main__':
    # test()
    print(get_teams_attending_two_events('2020vahay', '2020mdedg'))
