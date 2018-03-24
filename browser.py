from expected_conditions import element_appears_n_times, url_is
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

import asyncio
import logging
import medium


class Browser():
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(self.driver, 10)

    def close(self):
        self.driver.close()

    def extract_post_urls_from_current_page(self):
        a_tags = self.driver.find_elements_by_tag_name('a')
        return set([a.get_property('href') for a in a_tags if '?source=topic_page' in a.get_property('href')])

    def navigate_to_url(self, url):
        logging.info('Navigating to {}'.format(url))
        self.driver.get(url)

    async def scroll_to_bottom_n_times(self, num_scrolls, sleep_time_in_s=0):
        logging.info('Scrolling to bottom {} times'.format(num_scrolls))
        INITIAL_NUM_STREAM_ITEMS = 3
        num_stream_items = INITIAL_NUM_STREAM_ITEMS
        for _ in range(num_scrolls):
            await asyncio.sleep(sleep_time_in_s)
            logging.info(
                'Waiting for number of stream items to be {}'.format(
                    num_stream_items)
            )
            self.wait.until(
                element_appears_n_times(
                    (By.CLASS_NAME, 'js-streamItem'), num_stream_items)
            )
            logging.info('Scrolling to bottom')
            self.driver.execute_script(
                'window.scrollTo(0, document.body.scrollHeight);'
            )
            num_stream_items += 1
            logging.info('Scrolled to bottom {} times'.format(
                num_stream_items - INITIAL_NUM_STREAM_ITEMS)
            )

    async def sign_in_to_facebook(self, username, password, sleep_time_in_s=0):
        await asyncio.sleep(sleep_time_in_s)
        logging.info('Waiting for username input to be present')
        email_input = self.wait.until(
            EC.presence_of_element_located((By.ID, 'email'))
        )
        logging.info('Entering Facebook username')
        email_input.send_keys(username)

        # await asyncio.sleep(sleep_time_in_s)
        # logging.info('Clicking on next button')
        # next_button = self.driver.find_element_by_id('identifierNext')
        # next_button.click()

        # await asyncio.sleep(sleep_time_in_s)
        # logging.info('Waiting for password input to be present')
        # password_input = self.wait.until(
        #     EC.visibility_of_element_located((By.NAME, 'password'))
        # )
        await asyncio.sleep(sleep_time_in_s)
        password_input = self.driver.find_element_by_id('pass')
        # password_input = self.wait.until(
        #     EC.presence_of_element_located((By.ID, 'pass'))
        # )
        logging.info('Entering Facebook password')
        password_input.send_keys(password)

        await asyncio.sleep(sleep_time_in_s)
        login_button = self.driver.find_element_by_id('loginbutton')
        # logging.info('Waiting for next button to be present')
        # next_button = self.wait.until(
        #     EC.presence_of_element_located((By.ID, 'passwordNext'))
        # )
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
        logging.info('Waiting for redirect to Medium')
        self.wait.until(url_is(medium.BASE_URL))

    async def sign_in_to_google(self, username, password, sleep_time_in_s=0):
        await asyncio.sleep(sleep_time_in_s)
        logging.info('Waiting for username input to be present')
        email_input = self.wait.until(
            EC.presence_of_element_located((By.NAME, 'identifier'))
        )
        logging.info('Entering Google username')
        email_input.send_keys(username)

        await asyncio.sleep(sleep_time_in_s)
        logging.info('Clicking on next button')
        next_button = self.driver.find_element_by_id('identifierNext')
        next_button.click()

        await asyncio.sleep(sleep_time_in_s)
        logging.info('Waiting for password input to be present')
        password_input = self.wait.until(
            EC.visibility_of_element_located((By.NAME, 'password'))
        )
        logging.info('Entering Google password')
        password_input.send_keys(password)

        await asyncio.sleep(sleep_time_in_s)
        logging.info('Waiting for next button to be present')
        next_button = self.wait.until(
            EC.presence_of_element_located((By.ID, 'passwordNext'))
        )
        logging.info('Clicking on next button')
        self.driver.execute_script("arguments[0].click();", next_button)

    async def sign_in_to_medium_with_google(self, username, password, sleep_time_in_s=0):
        await asyncio.sleep(sleep_time_in_s)
        self.navigate_to_url(medium.SIGN_IN_URL)

        await asyncio.sleep(sleep_time_in_s)
        logging.info('Waiting for Google sign in button')
        google_signin_button = self.wait.until(
            EC.presence_of_element_located(
                (By.XPATH, '//button[@data-action="google-auth"]')
            )
        )

        await asyncio.sleep(sleep_time_in_s)
        logging.info('Clicking on Google sign in button')
        google_signin_button.click()

        await asyncio.sleep(sleep_time_in_s)
        await self.sign_in_to_google(username, password, sleep_time_in_s)

        await asyncio.sleep(sleep_time_in_s)
        logging.info('Waiting for redirect to Medium')
        self.wait.until(url_is(medium.BASE_URL))
