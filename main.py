from selenium import webdriver
from time import sleep

import json
import medium
import os


def log_in_to_google(driver, username, password, sleep_time_in_s=0):
    signin_button = driver.find_element_by_xpath(
        '//a[@data-action="sign-in-prompt"]')
    signin_button.click()
    sleep(sleep_time_in_s)

    google_signin_button = driver.find_element_by_xpath(
        '//button[@data-action="google-auth"]')
    google_signin_button.click()
    sleep(sleep_time_in_s)

    email_input = driver.find_element_by_name('identifier')
    email_input.send_keys(username)

    next_button = driver.find_element_by_id('identifierNext')
    next_button.click()
    sleep(sleep_time_in_s)

    password_input = driver.find_element_by_name('password')
    password_input.send_keys(password)

    next_button = driver.find_element_by_id('passwordNext')
    next_button.click()
    sleep(sleep_time_in_s)


def scroll_to_bottom(driver):
    driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')


def main():
    MAX_POSTS = 25
    NUM_PAGES = 0
    SHORT_SLEEP_TIME_IN_S = 1
    LONG_SLEEP_TIME_IN_S = 3

    top_posts = {topic: [] for topic in medium.TOPICS}

    driver = webdriver.Chrome()
    driver.get(medium.BASE_URL)
    sleep(LONG_SLEEP_TIME_IN_S)

    username = os.environ['APPLAUSE_WEB__GOOGLE_USERNAME']
    password = os.environ['APPLAUSE_WEB__GOOGLE_PASSWORD']
    log_in_to_google(driver, username, password, SHORT_SLEEP_TIME_IN_S)

    for topic in top_posts.keys():
        driver.get(medium.topic_url(topic))
        sleep(LONG_SLEEP_TIME_IN_S)

        for _ in range(NUM_PAGES):
            scroll_to_bottom(driver)
            sleep(LONG_SLEEP_TIME_IN_S)

        post_urls = medium.extract_post_urls(driver)
        posts = medium.fetch_posts(post_urls, SHORT_SLEEP_TIME_IN_S)

        top_posts[topic] = sorted(
            posts, key=lambda post: post.total_clap_count, reverse=True)[:MAX_POSTS]

    json.dumps(top_posts, indent=4)
    driver.close()


if __name__ == '__main__':
    main()
