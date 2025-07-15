import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
import datetime
import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from server.core.config import settings

SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/calendar.readonly",
]

def get_credentials():
    """
    사용자 인증을 처리하고 유효한 Google API 자격 증명을 반환합니다.
    """
    creds = None
    if os.path.exists(settings.TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(settings.TOKEN_PATH, SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(settings.GOOGLE_CREDENTIALS_PATH, SCOPES)
            flow.redirect_uri = settings.REDIRECT_URI
            creds = flow.run_local_server(port=0)
        
        with open(settings.TOKEN_PATH, "w") as token:
            token.write(creds.to_json())
    return creds

def get_gmail_service():
    """Gmail API 서비스를 빌드하고 반환합니다."""
    credentials = get_credentials()
    return build("gmail", "v1", credentials=credentials)

def get_calendar_service():
    """Google Calendar API 서비스를 빌드하고 반환합니다."""
    credentials = get_credentials()
    return build("calendar", "v3", credentials=credentials)
