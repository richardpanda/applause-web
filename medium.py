from bs4 import BeautifulSoup
from collections import namedtuple

import aiohttp
import async_timeout
import asyncio
import json
import logging
import os
import re

BASE_URL = 'https://medium.com/'
SIGN_IN_URL = '{}m/signin'.format(BASE_URL)
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


async def fetch_page(url):
    async with aiohttp.ClientSession() as session:
        async with async_timeout.timeout(10):
            async with session.get(url) as response:
                return await response.text()


async def fetch_posts(topic, urls, sleep_time_in_s=0):
    logging.info('Fetching posts from {}'.format(topic))
    posts = []
    for url in urls:
        logging.debug('Visiting {}'.format(url))
        page = await fetch_page(url)
        post = extract_post(page)
        posts.append(post)
        logging.debug('Sleeping for {} second{}'.format(
            sleep_time_in_s,
            '' if sleep_time_in_s == 1 else 's'
        ))
        await asyncio.sleep(sleep_time_in_s)
    return posts


def topic_url(topic):
    return '{}topic/{}'.format(BASE_URL, topic)
