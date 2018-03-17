from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


def log_in(driver, username, password):
    wait = WebDriverWait(driver, 10)

    email_input = wait.until(
        EC.presence_of_element_located((By.NAME, 'identifier'))
    )
    email_input.send_keys(username)

    next_button = driver.find_element_by_id('identifierNext')
    next_button.click()

    password_input = wait.until(
        EC.visibility_of_element_located((By.NAME, 'password'))
    )
    password_input.send_keys(password)

    next_button = wait.until(
        EC.presence_of_element_located((By.ID, 'passwordNext'))
    )
    driver.execute_script("arguments[0].click();", next_button)
