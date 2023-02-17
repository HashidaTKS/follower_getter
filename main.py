from requests_html import HTMLSession
import json
import os
import datetime

def get_html(url):
    with HTMLSession() as session:
        with session.get(url) as response:
            response.html.render(sleep=5)
            return response.html

def get_instagram_info(target_id, result_file):
    url = f'https://www.instagram.com/{target_id}'
    html = get_html(url)
    elems = html.find("span._ac2a")
    if len(elems) >= 3:
        result_file.write(f'{target_id},{elems[0].text.replace(",","")},{elems[1].attrs["title"].replace(",","")},{elems[2].text.replace(",","")}\n')

def get_twitter_info(target_id, result_file):
    url = f'https://twitter.com/{target_id}'
    html = get_html(url)
    elem = html.find('script[data-testid="UserProfileSchema-test"]')[0]
    json_val = json.loads(elem.text)
    interactionStatistic = json_val["author"]["interactionStatistic"]
    result_list = [target_id]
    post = next(filter(lambda x: x["name"] == "Tweets", interactionStatistic), None)
    if post:
        # should be error
        result_list.append(str(post["userInteractionCount"]))
    else:
        result_list.append('')
    follower = next(filter(lambda x: x["name"] == "Follows", interactionStatistic), None)
    if follower:
        result_list.append(str(follower["userInteractionCount"]))
    else:
        # should be error
        result_list.append('')
    follow = next(filter(lambda x: x["name"] == "Friends", interactionStatistic), None)
    if follow:
        # should be error
        result_list.append(str(follow["userInteractionCount"]))
    else:
        result_list.append('')
    result_file.write(','.join(result_list) + "\n")

now_string = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
if os.path.isfile("instagram_ids.conf"):
    with open("instagram_ids.conf", "r", encoding='utf8') as instagram_source_file:
        with open(f'instagram_result_{now_string}.csv', 'w', encoding='utf8') as instagram_result_file:
            instagram_result_file.write('id,post,follower,follow\n')
            for id in instagram_source_file:
                try:
                    target_id = str.strip(id)
                    if len(id) == 0:
                        continue
                    get_instagram_info(target_id, instagram_result_file)
                except Exception as e:
                    # [TODO]: logging to file
                    print(f'Failed to get data of instagram: {id}')
                    print(str(e))

# [TODO]: Commonize twitter process and instagram process
if os.path.isfile("twitter_ids.conf"):
    with open("twitter_ids.conf", "r", encoding='utf8') as twitter_source_file:
        with open(f'twitter_result_{now_string}.csv', 'w', encoding='utf8') as twitter_result_file:
            twitter_result_file.write('id,tweet,follower,follow\n')
            for id in twitter_source_file:
                try:
                    target_id = str.strip(id)
                    if len(id) == 0:
                        continue
                    get_twitter_info(target_id, twitter_result_file)
                except Exception as e:
                    # [TODO]: logging to file
                    print(f'Failed to get data of twitter: {id}')
                    print(str(e))
