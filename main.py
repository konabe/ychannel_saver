from channel import Channel
from auth import get_authenticated_service

import os
import re
import urllib

from oauth2client.tools import argparser

from pytube import YouTube

import dateutil.parser
from datetime import datetime

def main():

    #Authenticated phase
    args = argparser.parse_args()
    service = get_authenticated_service(args)

    #CUI title
    print('-'*50); print(); print(' '*15+'Y Channel Saver'); print(); print('-'*50)

    #input channel URL
    channel_url = input('[Channel URL]')
    paths = urllib.parse.urlparse(channel_url).path.split("/")
    if len(paths) == 3 and paths[1] == "channel": #https://www.youtube.com/channel/(ID)
        channel_id = paths[2]
    else:
        print("invalid URL. you can get valid URL to click channel icon.")
        return

    channel = Channel(service, channel_id)
    if not channel.get_info():
        return -1

    #retrieve videos of channel which you can save.
    init_flag = True; kwargs = {}; count = 0
    finish_flag = False
    #TODO cannot get more than 500 videos at once.
    while True:
        if init_flag:
            kwargs['part'] = 'id, snippet'
            kwargs['channelId'] = channel.id
            kwargs['maxResults'] = 50
            kwargs['order'] = 'date'
            kwargs['type'] = 'video'
            #kwargs['publishedBefore'] = "2015-06-17T07:07:37Z"
            init_flag = False
        else:
            kwargs['pageToken'] = nextPageToken

        results = service.search().list(**kwargs).execute()
        try:
            nextPageToken = results['nextPageToken']
        except KeyError:
            finish_flag = True

        items = results['items']

        print('\n[DOWN LOAD]\n')


        for item in items:
            #anaylze the videos
            count += 1
            video_title = item['snippet']['title']
            #file_name check
            video_title = re.sub(r'[\\|/|"|<|>|\|]', '***', video_title)
            video_title = re.sub(r'[?]', '？', video_title)
            video_title = re.sub(r'[:]', '：', video_title)
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

            # TODO : dataディレクトリに入れられるようにする
            if not os.path.exists(channel.name):
                os.mkdir(channel.name)

            print('[No.%d] %s' % (count, video_title))
            print('Date : %s' % parsed_date)
            try:
                data.download(channel.name)
            except OSError:
                if(os.path.exists(file_name+'.mp4')):
                    print('the file already exists. skip downloading.')
            print('Download completed : %s' % file_name+'.mp4')
            print()

        print()
        if finish_flag:
            break

    print("Finish!")

if __name__ == "__main__":
    main()
