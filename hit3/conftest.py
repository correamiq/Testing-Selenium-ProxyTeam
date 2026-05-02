import os
import pytest
from selenium import webdriver


def pytest_addoption(parser):
    try:
        parser.addoption("--browser", action="store", default="chrome")
    except ValueError:
        pass


def create_driver(browser: str):
    if browser == "chrome":
        options = webdriver.ChromeOptions()
        options.add_argument("--start-maximized")
        return webdriver.Chrome(options=options)
    elif browser == "firefox":
        options = webdriver.FirefoxOptions()
        return webdriver.Firefox(options=options)
    else:
        raise ValueError(f"Browser no soportado: {browser}")


@pytest.fixture
def driver(request):
    browser = request.config.getoption("--browser") or os.environ.get(
        "BROWSER", "chrome"
    )
    d = create_driver(browser)
    yield d, browser
    d.quit()
