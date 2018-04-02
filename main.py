from browser import Browser
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.remote.remote_connection import LOGGER

import asyncio
import env
import json
import logging
import medium
import tornado.autoreload
import tornado.web
import os

LAST_UPDATED_FORMAT = '%Y-%m-%d %H:%M:%S'


def load_app_state_from_file(app_state, filename, topics):
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

            last_updated_topic = topics[
                (app_state['topic_index']-1)
            ]
            app_state['last_updated'] = app_state['top_posts'][last_updated_topic]['last_updated']

    except (IOError, OSError):
        logging.info('{} does not exist'.format(filename))


def secs_until_midnight(dt_now):
    dt_tomorrow = timedelta(days=1) + dt_now
    dt_midnight = dt_tomorrow.replace(hour=0, minute=0, second=0)
    return int((dt_midnight - dt_now).total_seconds())


async def update_app_state(app_state, filename, sleep_time_in_s=0):
    MAX_POSTS = 25
    NUM_PAGES = 5 if env.is_production() else 1

    username = os.environ['APPLAUSE_WEB__FACEBOOK_USERNAME']
    password = os.environ['APPLAUSE_WEB__FACEBOOK_PASSWORD']

    timeout_urls = []
    json_decode_error_urls = []

    while True:
        logging.info('Starting Medium scraper')

        try:
            await asyncio.sleep(0)

            chrome_options = Options()
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            driver = webdriver.Chrome(chrome_options=chrome_options)
            browser = Browser(driver)

            await asyncio.sleep(0)
            await browser.sign_in_to_medium_with_facebook(username, password)

            num_topics = len(medium.TOPICS)
            for _ in range(num_topics):
                topic = medium.TOPICS[app_state['topic_index']]
                await asyncio.sleep(0)

                browser.navigate_to_url(medium.topic_url(topic))
                await browser.scroll_to_bottom_n_times(NUM_PAGES)

                logging.info('Extracting post urls from {}'.format(topic))
                post_urls = browser.extract_post_urls_from_current_page()
                posts, timeout_links, json_decode_error_links = await medium.fetch_posts(topic, post_urls, sleep_time_in_s)

                timeout_urls += timeout_links
                json_decode_error_urls += json_decode_error_links

                app_state['top_posts'][topic]['list'] = sorted(
                    posts, key=lambda post: post.total_clap_count, reverse=True)[:MAX_POSTS]
                app_state['top_posts'][topic]['last_updated'] = datetime.now().strftime(
                    LAST_UPDATED_FORMAT
                )

                app_state['last_updated'] = app_state['top_posts'][topic]['last_updated']
                app_state['topic_index'] += 1
                app_state['topic_index'] %= num_topics

                logging.info(
                    'Finished fetching top posts from {}'.format(topic)
                )

                logging.info('Saving top posts to {}'.format(filename))
                with open(filename, 'w') as f:
                    json.dump(app_state, f)
        finally:
            logging.info('Closing browser')
            browser.close()

        logging.info('Finished scraping Medium posts')

        if timeout_urls:
            logging.debug('URLs that timed out:\n{}'.format(
                '\n'.join(timeout_urls)
            ))

        if json_decode_error_urls:
            logging.debug('URLs that could not be JSON decoded:\n{}'.format(
                '\n'.join(json_decode_error_urls)
            ))

        sleep_time_in_s = secs_until_midnight(datetime.now())
        logging.info(
            'Waking up Medium scraper in {} seconds'.format(
                sleep_time_in_s
            )
        )
        await asyncio.sleep(sleep_time_in_s)


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

    top_posts = {
        topic: dict(list=[], last_updated='')
        for topic in medium.TOPICS
    }
    app_state = dict(
        last_updated='',
        top_posts=top_posts,
        topic_index=0
    )
    load_app_state_from_file(app_state, APP_STATE_FILENAME, medium.TOPICS)

    loop = asyncio.get_event_loop()

    handlers = [
        (r'/', IndexHandler,
            {'app_state': app_state, 'topics': medium.TOPICS}),
        (r'/topic/([\w-]+)', TopicHandler,
            {'top_posts': app_state['top_posts']})
    ]
    app = tornado.web.Application(
        handlers=handlers,
        static_path='static',
        template_path='templates'
    )
    app.listen(int(os.getenv('APPLAUSE_WEB__SERVER_PORT', 8080)))

    loop.create_task(update_app_state(
        app_state, APP_STATE_FILENAME, SLEEP_TIME_IN_S
    ))
    logging.info('Starting web server and scraper')
    loop.run_forever()


if __name__ == '__main__':
    main()
