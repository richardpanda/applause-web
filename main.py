from selenium import webdriver
from time import sleep

import os


def nap():
    sleep(3)


def log_in_to_google(driver):
    signin_button = driver.find_element_by_xpath(
        '//a[@data-action="sign-in-prompt"]')
    signin_button.click()
    nap()

    google_signin_button = driver.find_element_by_xpath(
        '//button[@data-action="google-auth"]')
    google_signin_button.click()
    nap()

    email_input = driver.find_element_by_name('identifier')
    email_input.send_keys(os.environ['APPLAUSE_WEB__GOOGLE_USERNAME'])

    next_button = driver.find_element_by_id('identifierNext')
    next_button.click()
    nap()

    password_input = driver.find_element_by_name('password')
    password_input.send_keys(os.environ['APPLAUSE_WEB__GOOGLE_PASSWORD'])

    next_button = driver.find_element_by_id('passwordNext')
    next_button.click()
    nap()


def scroll_n_times(driver, n):
    for _ in range(n):
        driver.execute_script(
            'window.scrollTo(0, document.body.scrollHeight);')
        nap()


def main():
    NUM_PAGES = 10

    driver = webdriver.Chrome()
    driver.get('https://medium.com/topic/software-engineering')
    nap()

    log_in_to_google(driver)
    scroll_n_times(driver, NUM_PAGES)
    driver.close()


if __name__ == '__main__':
    main()
