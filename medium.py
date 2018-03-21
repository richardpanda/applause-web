from browser import Browser
from bs4 import BeautifulSoup
from collections import namedtuple
from selenium import webdriver

import aiohttp
import async_timeout
import asyncio
import json
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


async def fetch_posts(urls, sleep_time_in_s=0):
    posts = []
    for url in urls:
        print(url)
        page = await fetch_page(url)
        post = extract_post(page)
        posts.append(post)
        await asyncio.sleep(sleep_time_in_s)
    return posts


async def scrape_top_posts(username, password):
    MAX_POSTS = 25
    NUM_PAGES = 0
    SLEEP_TIME_IN_S = 1

    top_posts = {topic: [] for topic in TOPICS}
    driver = webdriver.Chrome()
    browser = Browser(driver)

    await asyncio.sleep(0)

    try:
        await browser.sign_in_to_medium_with_google(username, password)

        for topic in TOPICS:
            await asyncio.sleep(0)

            browser.navigate_to_url(topic_url(topic))
            await browser.scroll_to_bottom_n_times(NUM_PAGES)

            post_urls = browser.extract_post_urls_from_current_page()
            posts = await fetch_posts(post_urls, SLEEP_TIME_IN_S)

            top_posts[topic] = sorted(
                posts, key=lambda post: post.total_clap_count, reverse=True)[:MAX_POSTS]

        return top_posts
    finally:
        browser.close()


def topic_url(topic):
    return '{}topic/{}'.format(BASE_URL, topic)
