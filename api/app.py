import json
import redis
import os

from flask import Flask, jsonify

REDIS_HOST = os.getenv("REDIS_HOST", "127.0.0.1")
r = redis.StrictRedis(host=REDIS_HOST, port=6379, db=0)
app = Flask(__name__)


@app.route("/api/topic/<string:topic>/posts")
def show_posts(topic):
    posts = r.lrange(f"posts:{topic}", 0, -1)
    return jsonify(posts=[json.loads(post.decode()) for post in posts])


@app.route("/api/topics")
def show_topics():
    topics = r.lrange("topics", 0, -1)
    return jsonify(topics=[topic.decode() for topic in topics])


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
