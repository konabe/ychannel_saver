import dateutil.parser
import re, os
from pytube import YouTube

NO_DOWNLOAD = False

class Video:

    def __init__(self, service, item):
        self.service = service
        self.item = item

    def get_info(self):
        self.title = self.item['snippet']['title']
        #file_name check
        self.title = re.sub(r'[\\|/|"|<|>|\|]', '***', self.title)
        self.title = re.sub(r'[?]', '？', self.title)
        self.title = re.sub(r'[:]', '：', self.title)
        video_id = self.item['id']['videoId']
        video_kwargs = {
            'part' : 'snippet',
            'id' : video_id
        }
        video_results = self.service.videos().list(**video_kwargs).execute()
        date = video_results['items'][0]['snippet']['publishedAt']
        self.parsed_date = dateutil.parser.parse(date)
        date = self.parsed_date.strftime('%Y%m%d%H%M%S')
        self.file_name = date + ' ' + self.title

        #prepare for download videos
        url = "https://www.youtube.com/watch?v=" + video_id
        yt = YouTube(url)
        yt.set_filename(self.file_name)
        self.data = yt.filter('mp4')[-1]


    def save(self, count, channel_dir_name):
        if not os.path.exists(channel_dir_name):
            os.mkdir(channel_dir_name)

        print('[No.%d] %s' % (count, self.title))
        print('Date : %s' % self.parsed_date)
        if(not NO_DOWNLOAD):
            try:
                self.data.download(channel_dir_name)
            except (FileExistsError, OSError):
                print('the file already exists. skipped downloading. \n')
                return
            print('Download completed : %s' % self.file_name+'.mp4')
        print()

    print()
