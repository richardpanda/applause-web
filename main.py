from selenium import webdriver
from time import sleep

import medium
import os


def short_nap():
    sleep(1)


def nap():
    sleep(3)


def log_in_to_google(driver, username, password):
    signin_button = driver.find_element_by_xpath(
        '//a[@data-action="sign-in-prompt"]')
    signin_button.click()
    nap()

    google_signin_button = driver.find_element_by_xpath(
        '//button[@data-action="google-auth"]')
    google_signin_button.click()
    nap()

    email_input = driver.find_element_by_name('identifier')
    email_input.send_keys(username)

    next_button = driver.find_element_by_id('identifierNext')
    next_button.click()
    nap()

    password_input = driver.find_element_by_name('password')
    password_input.send_keys(password)

    next_button = driver.find_element_by_id('passwordNext')
    next_button.click()
    nap()


def scroll_n_times(driver, n):
    for _ in range(n):
        driver.execute_script(
            'window.scrollTo(0, document.body.scrollHeight);')
        nap()


def main():
    MAX_POSTS = 25
    NUM_PAGES = 3

    driver = webdriver.Chrome()
    driver.get('https://medium.com/topic/software-engineering')
    nap()

    username = os.environ['APPLAUSE_WEB__GOOGLE_USERNAME']
    password = os.environ['APPLAUSE_WEB__GOOGLE_PASSWORD']
    log_in_to_google(driver, username, password)

    scroll_n_times(driver, NUM_PAGES)

    post_urls = medium.extract_post_urls(driver)
    posts = medium.fetch_posts(post_urls, short_nap)
    top_posts = sorted(
        posts, key=lambda post: post.total_clap_count, reverse=True)[:MAX_POSTS]

    driver.close()


if __name__ == '__main__':
    main()
