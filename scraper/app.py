import json
import medium
import redis
import os

from browser import Browser
from selenium import webdriver
from selenium.webdriver.firefox.options import Options

if __name__ == "__main__":
    REDIS_HOST = os.getenv("REDIS_HOST", "127.0.0.1")
    r = redis.StrictRedis(host=REDIS_HOST, port=6379, db=0)
    topics = medium.fetch_topics()
    # topics = [
    #     topic for topic in topics if topic.name in "programming software-engineering"
    # ]
    r.delete("topics")
    r.rpush("topics", *[topic.name for topic in topics])

    username = os.environ["APPLAUSE__FACEBOOK_USERNAME"]
    password = os.environ["APPLAUSE__FACEBOOK_PASSWORD"]

    try:
        firefox_options = Options()
        firefox_options.add_argument("--headless")
        firefox_options.add_argument("--no-sandbox")
        driver = webdriver.Firefox(firefox_options=firefox_options)
        browser = Browser(driver)
        browser.sign_in_to_medium_with_facebook(username, password)
        cookie_str = browser.build_cookie_str()
    finally:
        browser.close()

    for topic in topics:
        print(f"Scraping {topic.name}")
        top_posts = medium.fetch_top_posts_from_topic_id(topic.id, cookie_str)
        key = f"posts:{topic.name}"
        r.delete(key)
        r.rpush(key, *[json.dumps(post._asdict()) for post in top_posts])

    print("Done scraping!")
