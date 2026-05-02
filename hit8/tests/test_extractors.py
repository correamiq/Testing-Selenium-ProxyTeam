from selenium.webdriver.common.by import By
from extractors import extract_price


class Fake:
    def find_element(self, *args):
        class E:
            text = "12.345"

        return E()


def test_price():
    selector = (By.CSS_SELECTOR, "fake")
    assert extract_price(Fake(), selector) == 12345
