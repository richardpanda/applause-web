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
import tornado.web
import os

LAST_UPDATED_FORMAT = '%Y-%m-%d %H:%M:%S'


def latest_datetime_str(dt_strs):
    sorted_dt_strs = sorted(
        [dt_str for dt_str in dt_strs if dt_str],
        key=lambda dt: datetime.strptime(dt, LAST_UPDATED_FORMAT),
        reverse=True
    )
    return sorted_dt_strs[0] if sorted_dt_strs else ''


def load_top_posts_from_file(top_posts, filename):
    try:
        if os.stat(filename).st_size == 0:
            logging.info('{} is empty.'.format(filename))
            return

        with open(filename, 'r') as f:
            logging.info('Loading top posts from {}'.format(
                filename
            ))
            top_posts_json = json.load(f)
            for topic, top_posts_obj in top_posts_json.items():
                top_posts[topic]['list'] = [
                    medium.Post(*post) for post in top_posts_obj['list']
                ]
                top_posts[topic]['last_updated'] = top_posts_obj['last_updated']
    except (IOError, OSError):
        logging.info('{} does not exist'.format(filename))


def secs_until_midnight(dt_now):
    dt_tomorrow = timedelta(days=1) + dt_now
    dt_midnight = dt_tomorrow.replace(hour=0, minute=0, second=0)
    return int((dt_midnight - dt_now).total_seconds())


async def update_top_posts(top_posts, filename, sleep_time_in_s=0):
    MAX_POSTS = 25
    NUM_PAGES = 5 if env.is_production() else 1

    username = os.environ['APPLAUSE_WEB__FACEBOOK_USERNAME']
    password = os.environ['APPLAUSE_WEB__FACEBOOK_PASSWORD']

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

            for topic in medium.TOPICS:
                await asyncio.sleep(0)

                browser.navigate_to_url(medium.topic_url(topic))
                await browser.scroll_to_bottom_n_times(NUM_PAGES)

                logging.info('Extracting post urls from {}'.format(topic))
                post_urls = browser.extract_post_urls_from_current_page()
                posts = await medium.fetch_posts(topic, post_urls, sleep_time_in_s)

                top_posts[topic]['list'] = sorted(
                    posts, key=lambda post: post.total_clap_count, reverse=True)[:MAX_POSTS]
                top_posts[topic]['last_updated'] = datetime.now().strftime(
                    LAST_UPDATED_FORMAT
                )

                logging.info(
                    'Finished fetching top posts from {}'.format(topic)
                )

                logging.info('Saving top posts to {}'.format(filename))
                with open(filename, 'w') as f:
                    json.dump(top_posts, f)
        finally:
            logging.info('Closing browser')
            browser.close()

        logging.info('Finished scraping Medium posts')

        sleep_time_in_s = secs_until_midnight(datetime.now())
        logging.info(
            'Waking up Medium scraper in {} seconds'.format(
                sleep_time_in_s
            )
        )
        await asyncio.sleep(sleep_time_in_s)


class IndexHandler(tornado.web.RequestHandler):
    def initialize(self, top_posts):
        self.top_posts = top_posts

    def get(self):
        last_updated_strs = [
            top_posts_obj['last_updated']
            for top_posts_obj in self.top_posts.values()
        ]

        self.render(
            'index.html',
            last_updated=latest_datetime_str(last_updated_strs),
            topics=medium.TOPICS
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
    LOGGING_FILENAME = 'applause.log'
    SLEEP_TIME_IN_S = 2 if env.is_production() else 1
    TOP_POSTS_FILENAME = 'top_posts.txt'

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
    load_top_posts_from_file(top_posts, TOP_POSTS_FILENAME)

    loop = asyncio.get_event_loop()

    handlers = [
        (r'/', IndexHandler, {'top_posts': top_posts}),
        (r'/topic/([\w-]+)', TopicHandler, {'top_posts': top_posts})
    ]
    app = tornado.web.Application(
        handlers=handlers,
        static_path='static',
        template_path='templates'
    )
    app.listen(int(os.getenv('APPLAUSE_WEB__SERVER_PORT', 8080)))

    loop.create_task(update_top_posts(
        top_posts, TOP_POSTS_FILENAME, SLEEP_TIME_IN_S
    ))
    logging.info('Starting web server and scraper')
    loop.run_forever()


if __name__ == '__main__':
    main()
