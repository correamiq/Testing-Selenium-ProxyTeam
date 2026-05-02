import os
import pytest
from selenium import webdriver


def pytest_addoption(parser):
    try:
        parser.addoption("--browser", action="store", default="chrome")
    except ValueError:
        pass


def create_driver(browser: str):
    headless = os.environ.get("HEADLESS", "false") == "true"

    if browser == "chrome":
        options = webdriver.ChromeOptions()

        if headless:
            options.add_argument("--headless=new")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")

        options.add_argument(
            "--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )

        return webdriver.Chrome(options=options)

    elif browser == "firefox":
        options = webdriver.FirefoxOptions()

        if headless:
            options.add_argument("-headless")

        return webdriver.Firefox(options=options)

    else:
        raise ValueError(f"Browser no soportado: {browser}")


@pytest.fixture
def driver(request):
    browser = request.config.getoption("--browser") or "chrome"
    d = create_driver(browser)
    yield d
    d.quit()
