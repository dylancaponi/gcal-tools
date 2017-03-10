# from __future__ import print_function
import httplib2
import os
import calendar
import time

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage
from yaml import load

import datetime

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/calendar-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/calendar'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Google Calendar API Python Quickstart'


def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'calendar-python-quickstart.json')
    print(credential_dir)
    print(credential_path)
    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials

event = {
  'summary': 'Google I/O 2015',
  'location': '800 Howard St., San Francisco, CA 94103',
  'description': 'A chance to hear more about Google\'s developer products.',
  'start': {
    'dateTime': '2015-05-28T09:00:00-07:00',
    'timeZone': 'America/Los_Angeles',
  },
  'end': {
    'dateTime': '2017-03-08T17:00:00-07:00',
    'timeZone': 'America/Los_Angeles',
  },
  'recurrence': [
    'RRULE:FREQ=DAILY;COUNT=2'
  ],
  'attendees': [
    {'email': 'lpage@example.com'},
    {'email': 'sbrin@example.com'},
  ],
  # 'reminders': {
  #   'useDefault': False,
  #   'overrides': [
  #     {'method': 'email', 'minutes': 24 * 60},
  #     {'method': 'popup', 'minutes': 10},
  #   ],
  # },
}


def submit_event(service, calendar_id, event_body):
  print('---- start event ---')
  print(event_body)
  print ('--- end event ---')
  wait = True
  while wait:
    try:
      created_event = service.events().quickAdd(
        calendarId=calendar_id,
        # text="WHAT:  2017 Entertainment Industry Dinner WHO:  honoring Bill Prady WHEN: WEDNESDAY MAY 24 6:30pm WHERE:  Beverly Hilton Hotel;  9876 Wilshire Blvd;  Beverly Hills DESCRIPTION:  Franci Blattner  310-446-4266  fblattner@adl.org").execute()
        text=event_body).execute()
      wait = None
    except Exception as e:
      print(e)
      wait = True
      print('waiting 5 seconds')
      time.sleep(5)


def main():
    """Shows basic usage of the Google Calendar API.

    Creates a Google Calendar API service object and outputs a list of the next
    10 events on the user's calendar.
    """
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http=http)

    calendar_id = load(open('creds.yaml', 'r'))['calendar_id']
    # cred = load(open('creds.yaml', 'r'))[ENV]

    f = open("example_email.txt")
    next_line = f.readline()
    days_of_week = list(calendar.day_name)
    event_body = ""
    while next_line != "":
      if any(day.lower() in next_line.lower() for day in days_of_week):
        # print('---')
        date = next_line.strip()
      # print(next_line)
      # change contact to description

      if "WHAT: " in next_line:
        if event_body != "":
          submit_event(service, calendar_id, event_body)

        event_body = next_line
      elif "WHEN: " in next_line:
        event_body += next_line.replace("WHEN: ", "WHEN: " + date)
      elif "CONTACT: " in next_line:
        event_body += next_line.replace("CONTACT:", "DESCRIPTION:")
      elif "WHO: " in next_line:
      # if any(day.lower() in next_line.lower() for day in days_of_week):
        event_body += next_line
      else:
        pass

      next_line = f.readline()
    # submit final event
    submit_event(service, calendar_id, event_body)

    now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
    print('Getting the upcoming 10 events')
    eventsResult = service.events().list(
        calendarId='primary', timeMin=now, maxResults=10, singleEvents=True,
        orderBy='startTime').execute()
    events = eventsResult.get('items', [])

    if not events:
        print('No upcoming events found.')
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        print(start, event['summary'])



if __name__ == '__main__':
    main()
