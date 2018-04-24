import env
import logging
import medium
import threading

from flask import Flask
from flask_restful import Resource, Api
from resources import Posts, Topics
from selenium.webdriver.remote.remote_connection import LOGGER
from utils import update_top_posts

app = Flask(__name__)
api = Api(app)

topics = medium.fetch_topics()
if not env.is_production():
    topics = [
        topic for topic in topics if topic.name in 'programming software-engineering']

topic_names = [topic.name for topic in topics]
top_posts = {topic: [] for topic in topic_names}

api.add_resource(Posts, '/api/topic/<string:topic>/posts',
                 resource_class_kwargs={'top_posts': top_posts})
api.add_resource(Topics, '/api/topics',
                 resource_class_kwargs={'topics': topic_names})

if __name__ == '__main__':
    LOGGING_FILENAME = 'applause.log'
    LOGGER.setLevel(logging.WARNING)
    logging.basicConfig(
        filename=LOGGING_FILENAME,
        format='%(asctime)s - %(levelname)s - %(message)s',
        level=logging.DEBUG
    )
    logging.getLogger('urllib3').setLevel(logging.WARNING)

    thread = threading.Thread(target=update_top_posts,
                              args=(top_posts, topics))
    thread.start()
    app.run(port=8080)
