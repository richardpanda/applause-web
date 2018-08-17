import json
import redis

from flask import Flask, jsonify

r = redis.StrictRedis(host="127.0.0.1", port=6379, db=0)
app = Flask(__name__)


@app.route("/api/topics/<string:topic>/posts")
def show_posts(topic):
    posts = r.lrange(f"posts:{topic}", 0, -1)
    return jsonify(top_posts=[json.loads(post.decode()) for post in posts])


@app.route("/api/topics")
def show_topics():
    topics = r.lrange("topics", 0, -1)
    return jsonify(topics=[topic.decode() for topic in topics])


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
