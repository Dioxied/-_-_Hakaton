import datetime
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/calendar']

def get_user_credentials():

    flow = InstalledAppFlow.from_client_secrets_file('client_secret.json', SCOPES)#Вместо client_secret.json ваш файл из Google Calendar API
    creds = flow.run_local_server(port=0)#Ваш порт
    return creds

def create_event_in_user_calendar(user_email, summary, description, start_datetime, end_datetime):
    creds = get_user_credentials()
    service = build('calendar', 'v3', credentials=creds)
    event = {
        'summary': summary,
        'description': description,
        'start': {
            'dateTime': start_datetime.isoformat(),
            'timeZone': 'UTC',
        },
        'end': {
            'dateTime': end_datetime.isoformat(),
            'timeZone': 'UTC',
        }
    }
    created_event = service.events().insert(calendarId=user_email, body=event).execute()
    return created_event

