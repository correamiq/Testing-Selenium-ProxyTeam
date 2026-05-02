from unittest.mock import MagicMock, patch
from scraper import create_driver, run
from logging_setup import setup_logging


def test_setup_logging_coverage():
    with (
        patch("logging.basicConfig"),
        patch("logging.FileHandler", autospec=True),
        patch("logging.StreamHandler", autospec=True),
        patch("logging.handlers.RotatingFileHandler", autospec=True),
    ):
        setup_logging()


def test_create_driver_chrome():
    with patch("os.getenv") as mock_env:
        mock_env.side_effect = (
            lambda k, d=None: "chrome"
            if k == "BROWSER"
            else "true"
            if k == "HEADLESS"
            else d
        )
        with patch("selenium.webdriver.Chrome") as mock_chrome:
            create_driver()
            mock_chrome.assert_called_once()


def test_create_driver_firefox():
    with patch("os.getenv") as mock_env:
        mock_env.side_effect = (
            lambda k, d=None: "firefox"
            if k == "BROWSER"
            else "true"
            if k == "HEADLESS"
            else d
        )
        with patch("selenium.webdriver.Firefox") as mock_firefox:
            create_driver()
            mock_firefox.assert_called_once()


def test_run_coverage_mocked():
    with (
        patch("scraper.setup_logging"),
        patch("scraper.create_driver") as mock_create,
        patch("scraper.Path.mkdir"),
        patch("scraper.search"),
        patch("scraper.WebDriverWait"),
        patch("scraper.extract_item"),
        patch("builtins.open", create=True),
        patch("json.dump"),
    ):
        mock_driver = MagicMock()
        mock_create.return_value = mock_driver

        # Simular que encuentra items
        mock_item = MagicMock()
        with patch("selenium.webdriver.support.ui.WebDriverWait.until") as mock_until:
            mock_until.return_value = [mock_item]
            run()

        mock_driver.quit.assert_called_once()
