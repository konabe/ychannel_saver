import sys
import httplib2
import os

from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from apiclient.discovery import build
from oauth2client.tools import run_flow
from apiclient.errors import HttpError

# TODO to get token automatically
def get_authenticated_service():

    CLIENT_SECRETS_FILE = os.path.join(os.path.dirname(__file__), "client_secret.json")
    OATUH2_FILE = os.path.join(os.path.dirname(__file__), "main.py-oauth2.json")

    YOUTUBE_READ_WRITE_SSL_SCOPE = "https://www.googleapis.com/auth/youtube.readonly"
    API_SERVICE_NAME = "youtube"
    API_VERSION = "v3"

    MISSING_CLIENT_SECRETS_MESSAGE = "WARNING: Please configure OAuth 2.0"

    flow = flow_from_clientsecrets(CLIENT_SECRETS_FILE, scope=YOUTUBE_READ_WRITE_SSL_SCOPE,
            message=MISSING_CLIENT_SECRETS_MESSAGE)

    storage = Storage(OATUH2_FILE)
    credentials = storage.get()

    return build(API_SERVICE_NAME, API_VERSION,
            http=credentials.authorize(httplib2.Http()))
