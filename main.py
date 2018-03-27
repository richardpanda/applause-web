from datetime import datetime, timedelta
from jinja2 import Environment, PackageLoader
from sanic import response, Sanic
from sanic.response import html

import asyncio
import json
import logging
import medium
import os

LOGGING_FILENAME = 'applause.log'
TOP_POSTS_FILENAME = 'top_posts.txt'

app = Sanic(__name__)
app.static('/static', './static')

logging.basicConfig(
    filename=LOGGING_FILENAME,
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.DEBUG
)
env = Environment(loader=PackageLoader('main', 'templates'))

top_posts = {
    'by_topic': {topic: [] for topic in medium.TOPICS},
    'last_updated': ''
}


@app.route('/')
async def index(request):
    template = env.get_template('index.html')
    return html(template.render(
        last_updated=top_posts['last_updated'],
        topics=medium.TOPICS
    ))


@app.route('/favicon.ico')
async def favicon(request):
    return await response.file('./static/favicon.ico')


@app.route('/topic/<topic:string>')
async def show_posts(request, topic):
    template = env.get_template('posts.html')
    return html(template.render(
        last_updated=top_posts['last_updated'],
        posts=top_posts['by_topic'][topic],
        topic=topic
    ))


def load_top_posts_from_file(top_posts, filename):
    try:
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
    except IOError:
        logging.info('{} does not exist'.format(filename))


def secs_until_midnight(dt_now):
    dt_tomorrow = timedelta(days=1) + dt_now
    dt_midnight = dt_tomorrow.replace(hour=0, minute=0, second=0)
    return int((dt_midnight - dt_now).total_seconds())


async def update_top_posts(top_posts):
    username = os.environ['APPLAUSE_WEB__FACEBOOK_USERNAME']
    password = os.environ['APPLAUSE_WEB__FACEBOOK_PASSWORD']

    while True:
        logging.info('Starting Medium scraper')
        top_posts['by_topic'] = await medium.scrape_top_posts(username, password)
        top_posts['last_updated'] = datetime.now().strftime(
            '%Y-%m-%d %H:%M:%S'
        )
        logging.info('Finished scraping Medium posts')

        logging.info('Saving top posts to {}'.format(TOP_POSTS_FILENAME))
        with open(TOP_POSTS_FILENAME, 'w') as f:
            json.dump(top_posts, f)

        sleep_time_in_s = secs_until_midnight(datetime.now())
        logging.info(
            'Waking up Medium scraper in {} seconds'.format(
                sleep_time_in_s
            )
        )
        await asyncio.sleep(sleep_time_in_s)


def main():
    load_top_posts_from_file(top_posts, TOP_POSTS_FILENAME)

    loop = asyncio.get_event_loop()
    server = app.create_server(
        host='0.0.0.0',
        port=int(os.getenv('APPLAUSE_WEB__SERVER_PORT', 8080))
    )
    asyncio.ensure_future(server, loop=loop)
    loop.create_task(update_top_posts(top_posts))
    logging.info('Starting web server and scraper')
    loop.run_forever()


if __name__ == '__main__':
    main()
