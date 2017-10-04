import dateutil.parser
import re, os
from pytube import YouTube

NO_DOWNLOAD = False

class Video:

    def __init__(self, service, item):
        self.service = service
        self.item = item

    def __validate_title(self):
        title = self.item['snippet']['title']
        #file_name check
        title = re.sub(r'[\\|/|"|<|>|\|]', '***', title)
        title = re.sub(r'[?]', '？', title)
        title = re.sub(r'[:]', '：', title)
        self.title = title

    def get_info(self):

        self.__validate_title()

        self.id = self.item['id']['videoId']
        video_kwargs = {
            'part' : 'snippet',
            'id' : self.id
        }
        video_results = self.service.videos().list(**video_kwargs).execute()

        date = video_results['items'][0]['snippet']['publishedAt']
        self.parsed_date = dateutil.parser.parse(date)

        date_str = self.parsed_date.strftime('%Y%m%d%H%M%S')
        self.file_name = date_str + ' ' + self.title

    def save(self, count, channel_dir_name):

        #prepare for download videos
        url = "https://www.youtube.com/watch?v=" + self.id
        yt = YouTube(url)
        yt.set_filename(self.file_name)
        data = yt.filter('mp4')[-1]

        if not os.path.exists(channel_dir_name):
            os.mkdir(channel_dir_name)

        print('[No.%d] %s' % (count, self.title))
        print('Date : %s' % self.parsed_date)
        if(not NO_DOWNLOAD):
            try:
                data.download(channel_dir_name)
            except (FileExistsError, OSError):
                print('the file already exists. skipped downloading. \n')
                return
            print('Download completed : %s' % self.file_name+'.mp4')
        print()

    print()
