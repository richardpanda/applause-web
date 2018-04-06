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
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.remote.remote_connection import LOGGER

LAST_UPDATED_FORMAT = '%Y-%m-%d %H:%M:%S'


def load_app_state_from_file(app_state, filename, topic_names):
    try:
        if os.stat(filename).st_size == 0:
            logging.info('{} is empty.'.format(filename))
            return

        with open(filename, 'r') as f:
            logging.info('Loading top posts from {}'.format(filename))
            app_state_json = json.load(f)

            for topic, top_posts_obj in app_state_json['top_posts'].items():
                app_state['top_posts'][topic]['list'] = [
                    medium.Post(*post) for post in top_posts_obj['list']
                ]
                app_state['top_posts'][topic]['last_updated'] = top_posts_obj['last_updated']

            app_state['topic_index'] = app_state_json['topic_index']

            last_updated_topic = topic_names[
                (app_state['topic_index']-1)
            ]
            app_state['last_updated'] = app_state['top_posts'][last_updated_topic]['last_updated']

    except (IOError, OSError):
        logging.info('{} does not exist'.format(filename))


def secs_until_midnight(dt_now):
    dt_tomorrow = timedelta(days=1) + dt_now
    dt_midnight = dt_tomorrow.replace(hour=0, minute=0, second=0)
    return int((dt_midnight - dt_now).total_seconds())


async def update_app_state(app_state, topics, filename, sleep_time_in_s=0):
    MAX_POSTS = 25
    NUM_PAGES = 5 if env.is_production() else 2

    username = os.environ['APPLAUSE_WEB__FACEBOOK_USERNAME']
    password = os.environ['APPLAUSE_WEB__FACEBOOK_PASSWORD']

    while True:
        logging.info('Starting Medium scraper')

        try:
            await asyncio.sleep(sleep_time_in_s)

            chrome_options = Options()
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            driver = webdriver.Chrome(chrome_options=chrome_options)
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
            logging.info('Updating app state')

            app_state['top_posts'][topic.name]['list'] = sorted(
                posts, key=lambda post: post.total_clap_count, reverse=True)[:MAX_POSTS]
            app_state['top_posts'][topic.name]['last_updated'] = datetime.now().strftime(
                LAST_UPDATED_FORMAT
            )

            app_state['last_updated'] = app_state['top_posts'][topic.name]['last_updated']
            app_state['topic_index'] += 1
            app_state['topic_index'] %= len(topics)

            logging.info(f'Saving app state to {filename}')
            with open(filename, 'w') as f:
                json.dump(app_state, f)

        midnight_secs = secs_until_midnight(datetime.now())
        logging.info(f'Waking up Medium scraper in {midnight_secs} seconds')
        await asyncio.sleep(midnight_secs)


class IndexHandler(tornado.web.RequestHandler):
    def initialize(self, app_state, topics):
        self.app_state = app_state
        self.topics = topics

    def get(self):
        self.render(
            'index.html',
            last_updated=self.app_state['last_updated'],
            topics=self.topics
        )


class TopicHandler(tornado.web.RequestHandler):
    def initialize(self, top_posts):
        self.top_posts = top_posts

    def get(self, topic):
        self.render(
            'posts.html',
            last_updated=self.top_posts[topic]['last_updated'],
            posts=self.top_posts[topic]['list'],
            topic=topic.title().replace('-', ' ')
        )


def main():
    APP_STATE_FILENAME = 'app_state.txt'
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
        topics = [topic
                  for topic in topics if topic.name in 'programming software-engineering']

    top_posts = {
        topic.name: dict(list=[], last_updated='')
        for topic in topics
    }
    app_state = dict(
        last_updated='',
        top_posts=top_posts,
        topic_index=0
    )
    topic_names = [topic.name for topic in topics]
    load_app_state_from_file(app_state, APP_STATE_FILENAME, topic_names)

    loop = asyncio.get_event_loop()

    handlers = [
        (r'/', IndexHandler,
            {'app_state': app_state, 'topics': topic_names}),
        (r'/topic/([\w-]+)', TopicHandler,
            {'top_posts': app_state['top_posts']})
    ]
    app = tornado.web.Application(
        handlers=handlers,
        static_path='static',
        template_path='templates'
    )
    app.listen(int(os.getenv('APPLAUSE_WEB__SERVER_PORT', 8080)))

    if not env.is_production():
        tornado.autoreload.start()
        dirs = ['static', 'templates']
        for d in dirs:
            for fn in os.listdir(d):
                tornado.autoreload.watch('{}/{}'.format(d, fn))

    loop.create_task(update_app_state(
        app_state, topics, APP_STATE_FILENAME, SLEEP_TIME_IN_S
    ))
    logging.info('Starting web server and scraper')
    loop.run_forever()


if __name__ == '__main__':
    main()
