import pytest
from selenium import webdriver


@pytest.fixture
def driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    d = webdriver.Chrome(options=options)
    yield d
    d.quit()
