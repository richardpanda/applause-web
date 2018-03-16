from bs4 import BeautifulSoup
from collections import namedtuple
from time import sleep

import json
import re
import requests

BASE_URL = 'https://medium.com'
TOPICS = [
    'programming',
    'software-engineering'
]

Post = namedtuple('Post', 'title creator url total_clap_count')


def extract_post(html_doc):
    soup = BeautifulSoup(html_doc, 'html.parser')

    post_info_str = ''
    for s in soup.find_all('script'):
        text = s.get_text()
        if text.startswith('{"@context":"'):
            post_info_str = text
            break

    post_info_json = json.loads(post_info_str)

    script_str = ''
    for s in soup.find_all('script'):
        text = s.get_text()
        if text.startswith('// <![CDATA[\nwindow["obvInit"]('):
            script_str = text
            break

    total_clap_count_regex = r'"totalClapCount":(\d+),"'
    match = re.search(total_clap_count_regex, script_str)

    title = post_info_json['name']
    creator = post_info_json['author']['name']
    url = post_info_json['mainEntityOfPage']
    total_clap_count = int(match.group(1))

    return Post(title, creator, url, total_clap_count)


def extract_post_urls(driver):
    a_tags = driver.find_elements_by_tag_name('a')
    return set([a.get_property('href') for a in a_tags if '?source=topic_page' in a.get_property('href')])


def fetch_posts(urls, sleep_time_in_s=0):
    posts = []
    for url in urls:
        print(url)
        r = requests.get(url)
        posts.append(extract_post(r.text))
        sleep(sleep_time_in_s)
    return posts


def topic_url(topic):
    return '{}/topic/{}'.format(BASE_URL, topic)
