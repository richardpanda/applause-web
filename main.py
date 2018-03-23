from datetime import datetime, timedelta
from jinja2 import Environment, PackageLoader
from sanic import Sanic
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
top_posts = {topic: [] for topic in medium.TOPICS}


@app.route('/topic/<topic:string>')
async def show_posts(request, topic):
    template = env.get_template('posts.html')
    return html(template.render(posts=top_posts[topic], topic=topic))


@app.route('/')
async def index(request):
    template = env.get_template('index.html')
    return html(template.render(topics=medium.TOPICS))


def secs_until_midnight(dt_now):
    dt_tomorrow = timedelta(days=1) + dt_now
    dt_midnight = dt_tomorrow.replace(hour=0, minute=0, second=0)
    return (dt_midnight - dt_now).total_seconds()


async def update_top_posts():
    global top_posts

    username = os.environ['APPLAUSE_WEB__GOOGLE_USERNAME']
    password = os.environ['APPLAUSE_WEB__GOOGLE_PASSWORD']

    while True:
        logging.info('Starting Medium scraper')
        top_posts = await medium.scrape_top_posts(username, password)
        logging.info('Finished scraping Medium posts')
        with open(TOP_POSTS_FILENAME, 'w') as f:
            logging.info('Saving top posts to {}'.format(TOP_POSTS_FILENAME))
            json.dump(top_posts, f)
        sleep_time_in_s = secs_until_midnight(datetime.now())
        logging.info(
            'Sleeping Medium scraper for {} seconds'.format(
                int(sleep_time_in_s)
            )
        )
        await asyncio.sleep(secs_until_midnight(datetime.now()))


if __name__ == '__main__':
    try:
        with open(TOP_POSTS_FILENAME, 'r') as f:
            logging.info('Loading top posts from {}'.format(
                TOP_POSTS_FILENAME))
            top_posts_json = json.load(f)
            top_posts = {
                topic: [medium.Post(*post) for post in posts]
                for topic, posts in top_posts_json.items()
            }
    except IOError:
        logging.info('{} does not exist'.format(TOP_POSTS_FILENAME))

    loop = asyncio.get_event_loop()
    server = app.create_server(
        host='0.0.0.0',
        port=int(os.getenv('APPLAUSE_WEB__SERVER_PORT', 8080))
    )
    asyncio.ensure_future(server, loop=loop)
    loop.create_task(update_top_posts())
    logging.info('Starting web server and scraper')
    loop.run_forever()
