import asyncio
import env
import logging
import medium

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


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

    async def sign_in_to_facebook(self, username, password, sleep_time_in_s=0):
        await asyncio.sleep(sleep_time_in_s)
        logging.info('Waiting for username input to be present')
        email_input = self.wait.until(
            EC.presence_of_element_located((By.ID, 'email'))
        )
        logging.info('Entering Facebook username')
        email_input.send_keys(username)

        await asyncio.sleep(sleep_time_in_s)
        password_input = self.driver.find_element_by_id('pass')

        logging.info('Entering Facebook password')
        password_input.send_keys(password)

        await asyncio.sleep(sleep_time_in_s)
        login_button = self.driver.find_element_by_id('loginbutton')
        logging.info('Clicking on login button')
        self.driver.execute_script("arguments[0].click();", login_button)

    async def sign_in_to_medium_with_facebook(self, username, password, sleep_time_in_s=0):
        await asyncio.sleep(sleep_time_in_s)
        self.navigate_to_url(medium.SIGN_IN_URL)

        await asyncio.sleep(sleep_time_in_s)
        logging.info('Waiting for Facebook sign in button')
        facebook_signin_button = self.wait.until(
            EC.presence_of_element_located(
                (By.XPATH, '//button[@data-action="facebook-auth"]')
            )
        )

        await asyncio.sleep(sleep_time_in_s)
        logging.info('Clicking on Facebook sign in button')
        facebook_signin_button.click()

        await asyncio.sleep(sleep_time_in_s)
        await self.sign_in_to_facebook(username, password, sleep_time_in_s)

        await asyncio.sleep(sleep_time_in_s)

        if env.is_production():
            logging.info('Reloading page')
            self.refresh()
            await asyncio.sleep(sleep_time_in_s)

        logging.info('Waiting for redirect to Medium')
        self.wait.until(EC.url_to_be(medium.BASE_URL))
