from datetime import datetime, timedelta

import asyncio
import json
import logging
import medium
import tornado.web
import os


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
            top_posts['by_topic'] = {
                topic: [medium.Post(*post) for post in posts]
                for topic, posts in top_posts_json['by_topic'].items()
            }
            top_posts['last_updated'] = top_posts_json['last_updated']
    except (IOError, OSError):
        logging.info('{} does not exist'.format(filename))


def secs_until_midnight(dt_now):
    dt_tomorrow = timedelta(days=1) + dt_now
    dt_midnight = dt_tomorrow.replace(hour=0, minute=0, second=0)
    return int((dt_midnight - dt_now).total_seconds())


async def update_top_posts(top_posts, filename):
    username = os.environ['APPLAUSE_WEB__FACEBOOK_USERNAME']
    password = os.environ['APPLAUSE_WEB__FACEBOOK_PASSWORD']

    while True:
        logging.info('Starting Medium scraper')
        top_posts['by_topic'] = await medium.scrape_top_posts(username, password)
        top_posts['last_updated'] = datetime.now().strftime(
            '%Y-%m-%d %H:%M:%S'
        )
        logging.info('Finished scraping Medium posts')

        logging.info('Saving top posts to {}'.format(filename))
        with open(filename, 'w') as f:
            json.dump(top_posts, f)

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
        self.render(
            'index.html',
            last_updated=self.top_posts['last_updated'],
            topics=sorted(self.top_posts['by_topic'].keys())
        )


class TopicHandler(tornado.web.RequestHandler):
    def initialize(self, top_posts):
        self.top_posts = top_posts

    def get(self, topic):
        self.render(
            'posts.html',
            last_updated=self.top_posts['last_updated'],
            posts=self.top_posts['by_topic'][topic],
            topic=topic
        )


def main():
    LOGGING_FILENAME = 'applause.log'
    TOP_POSTS_FILENAME = 'top_posts.txt'

    logging.basicConfig(
        filename=LOGGING_FILENAME,
        format='%(asctime)s - %(levelname)s - %(message)s',
        level=logging.DEBUG
    )

    top_posts = {
        'by_topic': {topic: [] for topic in medium.TOPICS},
        'last_updated': ''
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

    loop.create_task(update_top_posts(top_posts, TOP_POSTS_FILENAME))
    logging.info('Starting web server and scraper')
    loop.run_forever()


if __name__ == '__main__':
    main()
