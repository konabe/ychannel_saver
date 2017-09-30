from channel import Channel
from auth import get_authenticated_service

import os
import re
import urllib
from copy import deepcopy

from oauth2client.tools import argparser

from pytube import YouTube

import dateutil.parser
from datetime import datetime, timedelta

data_dir_name = os.path.join(os.path.dirname(__file__), 'data')

NO_DOWNLOAD = True

def main():

    init()
    service = get_authenticated_service()

    #CUI title
    print('-'*50); print(); print(' '*15+'Y Channel Saver'); print(); print('-'*50)

    #input channel URL
    channel_url = input('[Channel URL]')
    #TODO 動画URLからチャンネルを自動的に取得
    paths = urllib.parse.urlparse(channel_url).path.split("/")
    if len(paths) == 3 and paths[1] == "channel":  # https://www.youtube.com/channel/(ID)
        channel_id = paths[2]
    else:
        print("invalid URL. you can get valid URL to click channel icon.")
        return

    channel = Channel(service, channel_id)
    if not channel.get_info():
        return -1
    channel_dir_name = os.path.join(data_dir_name, channel.name)

    #retrieve videos of channel which you can save.
    init_flag = True; kwargs = {}; count = 0
    finish_flag = False
    #TODO チャンネル立ち上げ日の取得から取得開始日時を取得
    start_published = datetime(2005,2,1) # the date youtube started
    tmp_published = None
    end_publised = datetime.now()

    while True: # get 500 videos per month

        tmp_published = deepcopy(start_published)
        next_month = tmp_published.month + 1 if tmp_published.month!= 12 else 1
        next_year = tmp_published.year + 1 if tmp_published.month == 12 else tmp_published.year
        tmp_published = tmp_published.replace(year=next_year, month=next_month)

        print("date : " + start_published.isoformat() +
                " =====> " + tmp_published.isoformat())

        if tmp_published > end_publised:
            print("date finished")
            break

        init_flag = True
        finish_flag = False

        while True:

            if init_flag:
                kwargs['part'] = 'id, snippet'
                kwargs['channelId'] = channel.id
                kwargs['maxResults'] = 50
                kwargs['order'] = 'date'
                kwargs['type'] = 'video'
                kwargs['publishedAfter'] = start_published.isoformat("T") + "Z"
                kwargs['publishedBefore'] = tmp_published.isoformat("T") + "Z"
                init_flag = False
            else:
                kwargs['pageToken'] = nextPageToken

            results = service.search().list(**kwargs).execute()
            try:
                nextPageToken = results['nextPageToken']
            except KeyError:
                finish_flag = True

            items = results['items']

            for item in items[::-1]:
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


                if not os.path.exists(channel_dir_name):
                    os.mkdir(channel_dir_name)

                print('[No.%d] %s' % (count, video_title))
                print('Date : %s' % parsed_date)
                if(not NO_DOWNLOAD):
                    try:
                        data.download(channel_dir_name)
                    except (FileExistsError, OSError):
                        print('the file already exists. skipped downloading. \n')
                        continue
                    print('Download completed : %s' % file_name+'.mp4')
                print()

            print()
            if finish_flag:
                break
        try:
            kwargs.pop('pageToken')
        except(KeyError):
            pass
        start_published = deepcopy(tmp_published)

    print("Finish!")

def init():
    if not os.path.exists(data_dir_name):
        os.mkdir(data_dir_name)

if __name__ == "__main__":
    main()
