import json
import re
import requests

from bs4 import BeautifulSoup
from collections import namedtuple

BASE_URL = "https://medium.com/"
BASE_IMG_URL = "https://cdn-images-1.medium.com/max/800/"
SIGN_IN_URL = "{}m/signin".format(BASE_URL)

Post = namedtuple("Post", "title creator url total_clap_count img_url")
Topic = namedtuple("Topic", "id name")


def extract_posts_from_stream(stream):
    posts = []
    for _, post in stream["payload"]["references"]["Post"].items():
        title = post["title"]
        creator_name = stream["payload"]["references"]["User"][post["creatorId"]][
            "name"
        ]
        user_name = creator_name.replace(" ", "").lower()
        unique_slug = post["uniqueSlug"]
        url = f"https://medium.com/@{user_name}/{unique_slug}"
        total_clap_count = post["virtuals"]["totalClapCount"]
        img_id = post["virtuals"]["previewImage"]["imageId"]
        img_url = f"{BASE_IMG_URL}{img_id}"
        posts.append(Post(title, creator_name, url, total_clap_count, img_url))
    return posts


def fetch_stream(url, cookie_str):
    resp = requests.get(url, headers={"Cookie": cookie_str})
    # Remove '])}while(1);</x>' from beginning of string
    return json.loads(resp.text[16:])


def fetch_top_posts_from_topic_id(topic_id, cookie_str):
    MAX_POSTS = 20
    NUM_PAGES = 2

    base_url = f"https://medium.com/_/api/topics/{topic_id}/stream?limit=25"
    to = ""
    posts = []

    for _ in range(NUM_PAGES):
        url = base_url
        if to:
            url = f"{url}&to={to}"

        stream = fetch_stream(url, cookie_str)

        if "Post" not in stream["payload"]["references"]:
            break

        posts += extract_posts_from_stream(stream)
        to = stream["payload"]["paging"]["next"]["to"]

    return sorted(posts, key=lambda post: post.total_clap_count, reverse=True)[
        :MAX_POSTS
    ]


def fetch_topics():
    resp = requests.get("https://medium.com/topics")
    data = re.findall('<script>// <!\[CDATA\[\nwindow\["obvInit"]\((.*)\)', resp.text)
    data_json = json.loads(data[0])
    topics = [
        Topic(topic_id, topic_json["name"].replace(" ", "-").lower())
        for topic_id, topic_json in data_json["references"]["Topic"].items()
    ]
    return sorted(topics, key=lambda topic: topic.name)


def topic_url(topic):
    return "{}topic/{}".format(BASE_URL, topic)
