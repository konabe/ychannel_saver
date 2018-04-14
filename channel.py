import dateutil.parser

class Channel:

    def __init__(self, service, channel_id):
        self.service = service
        self.id = channel_id

    def get_info(self):
        kwargs = {
            'part': 'snippet,statistics',
            'id' : self.id
        }
        results = self.service.channels().list(**kwargs).execute()
        if results['items'] == []:
            print('Channel not found. Check the channel id')
            return False
        else:
            self.name = results['items'][0]['snippet']['title']
            publishedAt = dateutil.parser.parse(
                    results['items'][0]['snippet']['publishedAt']
                    )
            self.publishedAt_year = publishedAt.year
            self.publishedAt_month = publishedAt.month
            self.video_count = results['items'][0]['statistics']['videoCount']
            print('Channel Name : %s \nVideo Count : %s' % (self.name, self.video_count))
            return True
