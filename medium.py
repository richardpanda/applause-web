from bs4 import BeautifulSoup
from expected_conditions import element_appears_n_times, url_is
from collections import namedtuple
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

import aiohttp
import async_timeout
import asyncio
import google
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


def extract_post_urls(driver):
    a_tags = driver.find_elements_by_tag_name('a')
    return set([a.get_property('href') for a in a_tags if '?source=topic_page' in a.get_property('href')])


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
    INITIAL_NUM_STREAM_ITEMS = 3
    MAX_POSTS = 25
    NUM_PAGES = 1
    SLEEP_TIME_IN_S = 1

    top_posts = {topic: [] for topic in TOPICS}
    driver = webdriver.Chrome()
    wait = WebDriverWait(driver, 10)
    await asyncio.sleep(0)
    driver.get(SIGN_IN_URL)

    try:
        await asyncio.sleep(0)
        google_signin_button = wait.until(
            EC.presence_of_element_located(
                (By.XPATH, '//button[@data-action="google-auth"]')
            )
        )
        await asyncio.sleep(0)
        google_signin_button.click()

        await asyncio.sleep(0)
        google.log_in(driver, username, password)

        await asyncio.sleep(0)
        wait.until(url_is(BASE_URL))

        for topic in TOPICS:
            await asyncio.sleep(0)
            driver.get(topic_url(topic))

            num_stream_items = INITIAL_NUM_STREAM_ITEMS
            for _ in range(NUM_PAGES):
                await asyncio.sleep(0)
                wait.until(
                    element_appears_n_times(
                        (By.CLASS_NAME, 'js-streamItem'), num_stream_items)
                )
                scroll_to_bottom(driver)
                num_stream_items += 1

            post_urls = extract_post_urls(driver)
            posts = await fetch_posts(post_urls, SLEEP_TIME_IN_S)

            top_posts[topic] = sorted(
                posts, key=lambda post: post.total_clap_count, reverse=True)[:MAX_POSTS]

        return top_posts
    finally:
        driver.close()


def scroll_to_bottom(driver):
    driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')


def topic_url(topic):
    return '{}topic/{}'.format(BASE_URL, topic)
