from browser import Browser
from bs4 import BeautifulSoup
from collections import namedtuple
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.remote.remote_connection import LOGGER

import aiohttp
import async_timeout
import asyncio
import json
import logging
import re

BASE_URL = 'https://medium.com/'
SIGN_IN_URL = '{}m/signin'.format(BASE_URL)
TOPICS = [
    'programming',
    'software-engineering'
]

LOGGER.setLevel(logging.WARNING)

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


async def scrape_top_posts(username, password):
    MAX_POSTS = 25
    NUM_PAGES = 0
    SLEEP_TIME_IN_S = 1

    top_posts = {topic: [] for topic in TOPICS}

    chrome_options = Options()
    chrome_options.set_headless()
    driver = webdriver.Chrome(chrome_options=chrome_options)
    browser = Browser(driver)

    await asyncio.sleep(0)

    try:
        await browser.sign_in_to_medium_with_google(username, password)

        for topic in TOPICS:
            await asyncio.sleep(0)

            browser.navigate_to_url(topic_url(topic))
            await browser.scroll_to_bottom_n_times(NUM_PAGES)

            logging.info('Extracting post urls from {}'.format(topic))
            post_urls = browser.extract_post_urls_from_current_page()
            posts = await fetch_posts(topic, post_urls, SLEEP_TIME_IN_S)

            top_posts[topic] = sorted(
                posts, key=lambda post: post.total_clap_count, reverse=True)[:MAX_POSTS]
            logging.info('Finished fetching top posts from {}'.format(topic))

        return top_posts
    finally:
        logging.info('Closing browser')
        browser.close()


def topic_url(topic):
    return '{}topic/{}'.format(BASE_URL, topic)
