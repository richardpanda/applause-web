import medium

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from time import sleep

SLEEP_TIME = 2


class Browser:
    def __init__(self, driver):
        self._driver = driver
        self._wait = WebDriverWait(self._driver, 10)

    def build_cookie_str(self):
        return ";".join(
            [f"{c['name']}={c['value']}" for c in self._driver.get_cookies()]
        )

    def close(self):
        self._driver.close()

    def navigate_to_url(self, url):
        print("Navigating to {}".format(url))
        self._driver.get(url)

    def refresh(self):
        self._driver.get(self._driver.current_url)

    def sign_in_to_facebook(self, username, password):
        email_input = self._wait.until(EC.presence_of_element_located((By.ID, "email")))
        print("Entering Facebook username")
        email_input.send_keys(username)
        sleep(SLEEP_TIME)

        password_input = self._driver.find_element_by_id("pass")
        print("Entering Facebook password")
        password_input.send_keys(password)
        sleep(SLEEP_TIME)

        login_button = self._driver.find_element_by_id("loginbutton")
        print("Clicking on login button")
        self._driver.execute_script("arguments[0].click();", login_button)
        sleep(SLEEP_TIME)

    def sign_in_to_medium_with_facebook(self, username, password):
        self.navigate_to_url(medium.SIGN_IN_URL)
        sleep(SLEEP_TIME)

        print("Waiting for Facebook sign in button")
        facebook_signin_button = self._wait.until(
            EC.presence_of_element_located(
                (By.XPATH, '//button[@data-action="facebook-auth"]')
            )
        )
        sleep(SLEEP_TIME)

        print("Clicking on Facebook sign in button")
        facebook_signin_button.click()
        sleep(SLEEP_TIME)

        self.sign_in_to_facebook(username, password)

        print("Reloading page")
        self.refresh()
        sleep(SLEEP_TIME)

        print("Waiting for redirect to Medium")
        self._wait.until(EC.url_to_be(medium.BASE_URL))
        sleep(SLEEP_TIME)
