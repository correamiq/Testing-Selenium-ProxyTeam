from unittest.mock import MagicMock
from selenium.common.exceptions import NoSuchElementException
from extractors import safe_find_text, extract_price, extract_link, extract_bool

FAKE_SELECTOR = ("css selector", ".fake")


def make_parent(text=None, href=None, raises=False):
    parent = MagicMock()
    if raises:
        parent.find_element.side_effect = NoSuchElementException
    else:
        el = MagicMock()
        el.text = text or ""
        el.get_attribute.return_value = href
        parent.find_element.return_value = el
    return parent


def test_safe_find_text_found():
    parent = make_parent(text="  Hola  ")
    assert safe_find_text(parent, FAKE_SELECTOR) == "Hola"


def test_safe_find_text_not_found():
    parent = make_parent(raises=True)
    assert safe_find_text(parent, FAKE_SELECTOR) is None


def test_extract_price_valid():
    parent = make_parent(text="1.500")
    assert extract_price(parent, FAKE_SELECTOR) == 1500


def test_extract_price_invalid():
    parent = make_parent(raises=True)
    assert extract_price(parent, FAKE_SELECTOR) is None


def test_extract_link_found():
    parent = make_parent(href="https://test.com")
    assert extract_link(parent, FAKE_SELECTOR) == "https://test.com"


def test_extract_link_not_found():
    parent = make_parent(raises=True)
    assert extract_link(parent, FAKE_SELECTOR) is None


def test_extract_bool_true():
    parent = make_parent(text="algo")
    assert extract_bool(parent, FAKE_SELECTOR) is True


def test_extract_bool_false():
    parent = make_parent(raises=True)
    assert extract_bool(parent, FAKE_SELECTOR) is False
