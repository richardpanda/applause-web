class element_appears_n_times():
    def __init__(self, locator, n):
        self.locator = locator
        self.n = n

    def __call__(self, driver):
        elements = driver.find_elements(*self.locator)
        return len(elements) == self.n


class url_is():
    def __init__(self, url):
        self.url = url

    def __call__(self, driver):
        return driver.current_url == self.url
