from expected_conditions import element_appears_n_times, url_is
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

import asyncio
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
        self.driver.get(url)

    async def scroll_to_bottom_n_times(self, num_scrolls, sleep_time_in_s=0):
        INITIAL_NUM_STREAM_ITEMS = 3
        num_stream_items = INITIAL_NUM_STREAM_ITEMS
        for _ in range(num_scrolls):
            await asyncio.sleep(sleep_time_in_s)
            self.wait.until(
                element_appears_n_times(
                    (By.CLASS_NAME, 'js-streamItem'), num_stream_items)
            )
            self.driver.execute_script(
                'window.scrollTo(0, document.body.scrollHeight);'
            )
            num_stream_items += 1

    async def sign_in_to_google(self, username, password, sleep_time_in_s=0):
        await asyncio.sleep(sleep_time_in_s)
        email_input = self.wait.until(
            EC.presence_of_element_located((By.NAME, 'identifier'))
        )
        email_input.send_keys(username)

        await asyncio.sleep(sleep_time_in_s)
        next_button = self.driver.find_element_by_id('identifierNext')
        next_button.click()

        await asyncio.sleep(sleep_time_in_s)
        password_input = self.wait.until(
            EC.visibility_of_element_located((By.NAME, 'password'))
        )
        password_input.send_keys(password)

        await asyncio.sleep(sleep_time_in_s)
        next_button = self.wait.until(
            EC.presence_of_element_located((By.ID, 'passwordNext'))
        )
        self.driver.execute_script("arguments[0].click();", next_button)

    async def sign_in_to_medium_with_google(self, username, password, sleep_time_in_s=0):
        await asyncio.sleep(sleep_time_in_s)
        self.driver.get(medium.SIGN_IN_URL)

        await asyncio.sleep(sleep_time_in_s)
        google_signin_button = self.wait.until(
            EC.presence_of_element_located(
                (By.XPATH, '//button[@data-action="google-auth"]')
            )
        )

        await asyncio.sleep(sleep_time_in_s)
        google_signin_button.click()

        await asyncio.sleep(sleep_time_in_s)
        await self.sign_in_to_google(username, password, sleep_time_in_s)

        await asyncio.sleep(sleep_time_in_s)
        self.wait.until(url_is(medium.BASE_URL))
