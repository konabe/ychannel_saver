import httplib2
import os
import sys

from apiclient.discovery import build
from apiclient.errors import HttpError
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import argparser, run_flow

from pytube import YouTube

import dateutil.parser
from datetime import datetime

"""
Authenticated phase
"""

CLIENT_SECRETS_FILE = "client_secret.json"

YOUTUBE_READ_WRITE_SSL_SCOPE = "https://www.googleapis.com/auth/youtube.readonly"
API_SERVICE_NAME = "youtube"
API_VERSION = "v3"

MISSING_CLIENT_SECRETS_MESSAGE = "WARNING: Please configure OAuth 2.0"

def get_authenticated_service(args):
  flow = flow_from_clientsecrets(CLIENT_SECRETS_FILE, scope=YOUTUBE_READ_WRITE_SSL_SCOPE,
    message=MISSING_CLIENT_SECRETS_MESSAGE)

  storage = Storage("%s-oauth2.json" % sys.argv[0])
  credentials = storage.get()

  if credentials is None or credentials.invalid:
    credentials = run_flow(flow, storage, args)

  return build(API_SERVICE_NAME, API_VERSION,
      http=credentials.authorize(httplib2.Http()))

args = argparser.parse_args()
service = get_authenticated_service(args)

#CUI title
print('-'*50); print(); print(' '*15+'Y Channel Saver'); print(); print('-'*50)

#input channel id
#TODO enable to input the URL, analyzing semantics of the URL
channel_id = input('Channel ID ? > ')

#get the channel information
kwargs = {
    'part': 'snippet,statistics',
    'id' : channel_id
}
#TODO add exception processing
results = service.channels().list(**kwargs).execute()
channel_name = results['items'][0]['snippet']['title']
video_count = results['items'][0]['statistics']['videoCount']
print('Channel Name : %s \nVideo Count : %s' % (channel_name, video_count))

#retrieve videos of channel which you can save.
init_flag = True; kwargs = {}; count = 0
#TODO cannot get more than 500 videos at once.
while True:
    if init_flag:
        kwargs['part'] = 'id, snippet'
        kwargs['channelId'] = channel_id
        kwargs['maxResults'] = 50
        kwargs['order'] = 'date'
        kwargs['type'] = 'video'
        init_flag = False
    else:
        kwargs['pageToken'] = nextPageToken
    results = service.search().list(**kwargs).execute()
    nextPageToken = results['nextPageToken']
    items = results['items']

    print('\n[DOWN LOAD]\n')

    for item in items:
        #anaylze the videos
        count += 1
        video_title = item['snippet']['title']
        video_id = item['id']['videoId']
        video_kwargs = {
            'part' : 'snippet',
            'id' : video_id
        }
        video_results = service.videos().list(**video_kwargs).execute()
        date = video_results['items'][0]['snippet']['publishedAt']
        parsed_date = dateutil.parser.parse(date)
        date = parsed_date.strftime('%Y%m%d%H%M%S')
        file_name = date + ' ' + video_title

        #prepare for download videos
        url = "https://www.youtube.com/watch?v=" + video_id
        yt = YouTube(url)
        yt.set_filename(file_name)
        data = yt.filter('mp4')[-1]
        if not os.path.exists(channel_name):
            os.mkdir(channel_name)

        print('[No.%d] %s' % (count, video_title))
        print('Date : %s' % parsed_date)
        data.download(channel_name)
        print('Download completed : %s' % file_name+'.mp4')
        print

    print()

#
