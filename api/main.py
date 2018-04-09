import asyncio
import env
import json
import logging
import medium
import time
import tornado.autoreload
import tornado.web
import os

from browser import Browser
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.remote.remote_connection import LOGGER


def load_top_posts_from_file(top_posts, filename):
    try:
        if os.stat(filename).st_size == 0:
            logging.info('{} is empty.'.format(filename))
            return

        with open(filename, 'r') as f:
            logging.info(f'Loading top posts from {filename}')
            top_posts_json = json.load(f)

            for topic, posts in top_posts_json.items():
                top_posts[topic] = [medium.Post(*post) for post in posts]

    except (IOError, OSError):
        logging.info(f'{filename} does not exist')


def secs_until_midnight(dt_now):
    dt_tomorrow = timedelta(days=1) + dt_now
    dt_midnight = dt_tomorrow.replace(hour=0, minute=0, second=0)
    return int((dt_midnight - dt_now).total_seconds())


async def update_top_posts(top_posts, topics, filename, sleep_time_in_s=0):
    MAX_POSTS = 20
    NUM_PAGES = 5 if env.is_production() else 2

    username = os.environ['APPLAUSE_WEB__FACEBOOK_USERNAME']
    password = os.environ['APPLAUSE_WEB__FACEBOOK_PASSWORD']

    while True:
        logging.info('Starting Medium scraper')

        await asyncio.sleep(sleep_time_in_s)

        firefox_options = Options()
        firefox_options.add_argument('--headless')
        firefox_options.add_argument('--no-sandbox')
        driver = webdriver.Firefox(firefox_options=firefox_options)

        try:
            browser = Browser(driver)

            await asyncio.sleep(sleep_time_in_s)
            await browser.sign_in_to_medium_with_facebook(username, password, sleep_time_in_s)

            cookie_str = browser.build_cookie_str()
        finally:
            logging.info('Closing browser')
            browser.close()

        for topic in topics:
            logging.info(f'Fetching posts from {topic.name}')

            base_url = f'https://medium.com/_/api/topics/{topic.id}/stream?limit=25'
            to = ''
            posts = []

            for _ in range(NUM_PAGES):
                sleep_time_str = '1 second' if sleep_time_in_s == 1 else f'{sleep_time_in_s} seconds'
                logging.debug(f'Sleeping for {sleep_time_str}')
                await asyncio.sleep(sleep_time_in_s)

                url = base_url
                if to:
                    url = f'{url}&to={to}'

                logging.debug(f'Sending GET request to {url}')

                stream = await medium.fetch_stream(url, cookie_str)

                if 'Post' not in stream['payload']['references']:
                    break

                posts += medium.extract_posts_from_stream(stream)
                to = stream['payload']['paging']['next']['to']

            logging.info(f'Finished fetching posts from {topic.name}')

            top_posts[topic.name] = sorted(
                posts, key=lambda post: post.total_clap_count, reverse=True)[:MAX_POSTS]

            logging.info(f'Saving top posts to {filename}')
            with open(filename, 'w') as f:
                json.dump(top_posts, f)

        midnight_secs = secs_until_midnight(datetime.now())
        logging.info(f'Waking up Medium scraper in {midnight_secs} seconds')
        await asyncio.sleep(midnight_secs)


class PostsHandler(tornado.web.RequestHandler):
    def initialize(self, top_posts):
        self.top_posts = top_posts

    def get(self, topic):
        posts = [post._asdict() for post in self.top_posts[topic]]
        self.write({'posts': posts})
        self.flush()


class TopicsHandler(tornado.web.RequestHandler):
    def initialize(self, topics):
        self.topics = topics

    def get(self):
        self.write({'topics': self.topics})
        self.flush()


def main():
    TOP_POSTS_FILENAME = 'top_posts.txt'
    LOGGING_FILENAME = 'applause.log'
    SLEEP_TIME_IN_S = 2 if env.is_production() else 1

    LOGGER.setLevel(logging.WARNING)
    logging.basicConfig(
        filename=LOGGING_FILENAME,
        format='%(asctime)s - %(levelname)s - %(message)s',
        level=logging.DEBUG
    )

    topics = medium.fetch_topics()
    if not env.is_production():
        topics = [topic for topic in topics
                  if topic.name in 'programming software-engineering']

    top_posts = {topic.name: [] for topic in topics}
    topic_names = [topic.name for topic in topics]
    load_top_posts_from_file(top_posts, TOP_POSTS_FILENAME)

    loop = asyncio.get_event_loop()

    handlers = [
        (r'/api/topic/([\w-]+)/posts', PostsHandler,
         {'top_posts': top_posts}),
        (r'/api/topics', TopicsHandler, {'topics': topic_names})
    ]
    app = tornado.web.Application(handlers=handlers)
    app.listen(8080)

    if not env.is_production():
        tornado.autoreload.start()

    loop.create_task(update_top_posts(
        top_posts, topics, TOP_POSTS_FILENAME, SLEEP_TIME_IN_S
    ))
    logging.info('Starting web server and scraper')
    loop.run_forever()


if __name__ == '__main__':
    main()
