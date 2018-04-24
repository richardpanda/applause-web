import logging
import medium
import os

from browser import Browser
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from time import sleep


def create_browser():
    firefox_options = Options()
    firefox_options.add_argument('--headless')
    firefox_options.add_argument('--no-sandbox')
    driver = webdriver.Firefox(firefox_options=firefox_options)
    return Browser(driver)


def fetch_top_posts_from_topic_id(topic_id, cookie_str):
    MAX_POSTS = 20
    NUM_PAGES = 2

    base_url = f'https://medium.com/_/api/topics/{topic_id}/stream?limit=25'
    to = ''
    posts = []

    for _ in range(NUM_PAGES):
        url = base_url
        if to:
            url = f'{url}&to={to}'

        logging.debug(f'Sending GET request to {url}')
        stream = medium.fetch_stream(url, cookie_str)

        if 'Post' not in stream['payload']['references']:
            break

        posts += medium.extract_posts_from_stream(stream)
        to = stream['payload']['paging']['next']['to']

    return sorted(posts, key=lambda post: post.total_clap_count, reverse=True)[:MAX_POSTS]


def update_top_posts(top_posts, topics):
    username = os.environ['APPLAUSE_WEB__FACEBOOK_USERNAME']
    password = os.environ['APPLAUSE_WEB__FACEBOOK_PASSWORD']

    while True:
        try:
            browser = create_browser()
            browser.sign_in_to_medium_with_facebook(username, password)
            cookie_str = browser.build_cookie_str()
        finally:
            browser.close()

        for topic in topics:
            logging.info(f'Fetching posts from {topic.name}')
            top_posts[topic.name] = fetch_top_posts_from_topic_id(
                topic.id, cookie_str)
            logging.info(f'Updated top posts for {topic.name}')

        midnight_secs = secs_until_midnight(datetime.now())
        logging.info(f'Waking up Medium scraper in {midnight_secs} seconds')
        sleep(midnight_secs)


def secs_until_midnight(dt_now):
    dt_tomorrow = timedelta(days=1) + dt_now
    dt_midnight = dt_tomorrow.replace(hour=0, minute=0, second=0)
    return int((dt_midnight - dt_now).total_seconds())
