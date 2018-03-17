from expected_conditions import element_appears_n_times, url_is
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from time import sleep

import google
import json
import medium
import os


def scroll_to_bottom(driver):
    driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')


def main():
    INITIAL_NUM_STREAM_ITEMS = 3
    MAX_POSTS = 25
    NUM_PAGES = 0
    SHORT_SLEEP_TIME_IN_S = 1
    LONG_SLEEP_TIME_IN_S = 3

    top_posts = {topic: [] for topic in medium.TOPICS}

    driver = webdriver.Chrome()
    wait = WebDriverWait(driver, 10)
    driver.get(medium.SIGN_IN_URL)

    try:
        google_signin_button = wait.until(
            EC.presence_of_element_located(
                (By.XPATH, '//button[@data-action="google-auth"]')
            )
        )
        google_signin_button.click()

        username = os.environ['APPLAUSE_WEB__GOOGLE_USERNAME']
        password = os.environ['APPLAUSE_WEB__GOOGLE_PASSWORD']
        google.log_in(driver, username, password)

        wait.until(url_is(medium.BASE_URL))

        for topic in top_posts.keys():
            driver.get(medium.topic_url(topic))

            num_stream_items = INITIAL_NUM_STREAM_ITEMS
            for _ in range(NUM_PAGES):
                wait.until(
                    element_appears_n_times(
                        (By.CLASS_NAME, 'js-streamItem'), num_stream_items)
                )
                scroll_to_bottom(driver)
                num_stream_items += 1

            post_urls = medium.extract_post_urls(driver)
            posts = medium.fetch_posts(post_urls, SHORT_SLEEP_TIME_IN_S)

            top_posts[topic] = sorted(
                posts, key=lambda post: post.total_clap_count, reverse=True)[:MAX_POSTS]

        print(json.dumps(top_posts, indent=4))
    finally:
        driver.close()


if __name__ == '__main__':
    main()
