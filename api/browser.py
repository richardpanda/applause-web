import env
import logging
import medium

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from time import sleep


class Browser():
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(self.driver, 10)

    def build_cookie_str(self):
        return ';'.join([f"{c['name']}={c['value']}" for c in self.driver.get_cookies()])

    def close(self):
        self.driver.close()

    def navigate_to_url(self, url):
        logging.info('Navigating to {}'.format(url))
        self.driver.get(url)

    def refresh(self):
        self.driver.get(self.driver.current_url)

    def sign_in_to_facebook(self, username, password):
        sleep_time = 2

        email_input = self.wait.until(
            EC.presence_of_element_located((By.ID, 'email'))
        )
        logging.info('Entering Facebook username')
        email_input.send_keys(username)
        sleep(sleep_time)

        password_input = self.driver.find_element_by_id('pass')
        logging.info('Entering Facebook password')
        password_input.send_keys(password)
        sleep(sleep_time)

        login_button = self.driver.find_element_by_id('loginbutton')
        logging.info('Clicking on login button')
        self.driver.execute_script("arguments[0].click();", login_button)
        sleep(sleep_time)

    def sign_in_to_medium_with_facebook(self, username, password):
        sleep_time = 2

        self.navigate_to_url(medium.SIGN_IN_URL)
        sleep(sleep_time)

        logging.info('Waiting for Facebook sign in button')
        facebook_signin_button = self.wait.until(
            EC.presence_of_element_located(
                (By.XPATH, '//button[@data-action="facebook-auth"]')
            )
        )
        sleep(sleep_time)

        logging.info('Clicking on Facebook sign in button')
        facebook_signin_button.click()
        sleep(sleep_time)

        self.sign_in_to_facebook(username, password)

        if env.is_production():
            logging.info('Reloading page')
            self.refresh()
            sleep(sleep_time)

        logging.info('Waiting for redirect to Medium')
        self.wait.until(EC.url_to_be(medium.BASE_URL))
        sleep(sleep_time)
