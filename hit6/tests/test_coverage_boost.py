from unittest.mock import patch, MagicMock
import os


def test_setup_logging_runs(tmp_path):
    with patch("logging_setup.RotatingFileHandler") as mock_handler:
        mock_handler.return_value = MagicMock()
        mock_handler.return_value.level = 0
        from logging_setup import setup_logging

        setup_logging()


def test_create_driver_chrome():
    with patch("scraper.webdriver.Chrome") as mock_chrome:
        mock_chrome.return_value = MagicMock()
        os.environ["BROWSER"] = "chrome"
        os.environ["HEADLESS"] = "true"
        import scraper
        scraper.create_driver()
        assert mock_chrome.called


def test_create_driver_firefox():
    with patch("scraper.webdriver.Firefox") as mock_firefox:
        mock_firefox.return_value = MagicMock()
        os.environ["BROWSER"] = "firefox"
        os.environ["HEADLESS"] = "false"
        import scraper
        scraper.create_driver()
        assert mock_firefox.called


def test_extract_item_structure():
    from unittest.mock import MagicMock
    from selenium.common.exceptions import NoSuchElementException
    import scraper

    item = MagicMock()
    item.find_element.side_effect = NoSuchElementException

    result = scraper.extract_item(item)
    assert "titulo" in result
    assert "precio" in result
    assert "link" in result
    assert "envio_gratis" in result
    assert result["envio_gratis"] is False
