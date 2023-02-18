from requests_html import HTMLSession
import json
import os
import datetime

class FollowerGetter:
    def get_html(url):
        with HTMLSession() as session:
            with session.get(url) as response:
                response.html.render(sleep=5)
                return response.html

    def get_info(self, target_id):
        return ""
    
    def generate_result(self):
        if not os.path.isfile(self.ids_file):
            return
        with open(self.ids_file, "r", encoding='utf8') as ids_file:
            now_string = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
            with open(f'{self.result_filename_base}_{now_string}.csv', 'w', encoding='utf8') as result_file:
                result_file.write(f'{self.header}\n')
                for id in ids_file:
                    try:
                        target_id = str.strip(id)
                        if len(id) == 0:
                            continue
                        result_file.write(self.get_info(target_id) + "\n")
                    except Exception as e:
                        # [TODO]: logging to file
                        print(f'Failed to get info of {self.tag}: {id}')
                        print(str(e))

class InstagramFollowerGetter(FollowerGetter):
    def __init__(self):
        super().__init__()
        self.tag = "instagram"
        self.ids_file = "instagram_ids.conf"
        self.result_filename_base = "instagram_result"
        self.header = "id,post,follower,follow"
    
    def get_info(self, target_id):
        url = f'https://www.instagram.com/{target_id}'
        html = FollowerGetter.get_html(url)
        elems = html.find("span._ac2a")
        if len(elems) >= 3:
            return f'{target_id},{elems[0].text.replace(",","")},{elems[1].attrs["title"].replace(",","")},{elems[2].text.replace(",","")}'
        raise Exception("Invalid page")

class TwitterFollowerGetter(FollowerGetter):
    def __init__(self):
        super().__init__()
        self.tag = "twitter"
        self.ids_file = "twitter_ids.conf"
        self.result_filename_base = "twitter_result"
        self.header = "id,tweet,follower,follow"
    
    def get_info(self, target_id):
        url = f'https://twitter.com/{target_id}'
        html = FollowerGetter.get_html(url)
        elem = html.find('script[data-testid="UserProfileSchema-test"]')[0]
        json_val = json.loads(elem.text)
        interactionStatistic = json_val["author"]["interactionStatistic"]
        post = next(filter(lambda x: x["name"] == "Tweets", interactionStatistic), None)
        follower = next(filter(lambda x: x["name"] == "Follows", interactionStatistic), None)
        follow = next(filter(lambda x: x["name"] == "Friends", interactionStatistic), None)
        if not post or not follower or not follow:
            Exception("Invalid page")
        return f'{target_id},{str(post["userInteractionCount"])},{str(follower["userInteractionCount"])},{str(follow["userInteractionCount"])}'

instances = [
    InstagramFollowerGetter(),
    TwitterFollowerGetter(),
]

for instance in instances:
    instance.generate_result()