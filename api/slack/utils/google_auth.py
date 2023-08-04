import google_auth_oauthlib.flow
import os.path
import requests
from urllib import parse
import db
import oauth2client
from oauth2client.client import flow_from_clientsecrets
from googleapiclient.discovery import build


scopes = [
    'openid',
    'https://www.googleapis.com/auth/calendar.readonly',
    'https://www.googleapis.com/auth/userinfo.email',
    'https://www.googleapis.com/auth/userinfo.profile',
    'https://www.googleapis.com/auth/drive'
]


def get_flow_from_secret_file(state=None):
    return google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        os.path.dirname(os.path.realpath(__file__)) + '/credentials.json',
        scopes=scopes,
        state=state
    )


def check_access_token_expired(access_token):
    url = "https://www.googleapis.com/oauth2/v2/tokeninfo?access_token={}".format(access_token)

    response = requests.post(url, headers={
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': 'application/json'
    })
    if response.status_code != 200:
        return True
    elif response.json()["expires_in"] < 100:
        return True
    else:
        return False


def refresh_access_token(user_info, client_id, client_secret, refresh_token):
    url = "https://accounts.google.com/o/oauth2/token"
    response = requests.post(
        url,
        data=parse.urlencode(
            {
                'grant_type': 'refresh_token',
                'client_id': client_id,
                'client_secret': client_secret,
                'refresh_token': refresh_token
            }
        ),
        headers={
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'application/json'
        }
    )
        
    return db.update_user_info(user_info=user_info, access_token=response.json()["access_token"])

def get_credentials(access_token):
    """ 사용자 credentials 정보 가져오기 """
    user_agent = "Google Sheets API for Python"
    revoke_uri = "https://accounts.google.com/o/oauth2/revoke"
    credentials = oauth2client.client.AccessTokenCredentials(
        access_token=access_token,
        user_agent=user_agent,
        revoke_uri=revoke_uri)
    return credentials

def credentials_to_dict(credentials):
    """ 사용자 credentials 정보 to dict """
    return {'token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': credentials.scopes}

def get_calender_next_sync_token(credentials, calendarId: str = "dev@orotcode.com"):
    service = build('calendar', 'v3', credentials=credentials)
    page_token = None
    while True:
        events = service.events().list(calendarId=calendarId, pageToken=page_token).execute()
        page_token = events.get('nextPageToken')
        if not page_token:
            return events.get('nextSyncToken')
