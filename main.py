from jinja2 import Environment, PackageLoader
from sanic import Sanic
from sanic.response import html

import asyncio
import medium
import os

app = Sanic(__name__)
app.static('/static', './static')

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


async def update_top_posts():
    global top_posts
    username = os.environ['APPLAUSE_WEB__GOOGLE_USERNAME']
    password = os.environ['APPLAUSE_WEB__GOOGLE_PASSWORD']
    top_posts = await medium.scrape_top_posts(username, password)

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    server = app.create_server(
        host='127.0.0.1',
        port=8080
    )
    asyncio.ensure_future(server, loop=loop)
    loop.create_task(update_top_posts())
    loop.run_forever()
