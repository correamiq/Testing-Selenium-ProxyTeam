from extractors import safe_find_text, extract_price, extract_bool, extract_link
from unittest.mock import MagicMock
from selenium.common.exceptions import NoSuchElementException

SEL = ("css selector", ".x")


def make_item(text=None, href=None, raises=False):
    m = MagicMock()
    if raises:
        m.find_element.side_effect = NoSuchElementException
    else:
        el = MagicMock()
        el.text = text or ""
        el.get_attribute.return_value = href
        m.find_element.return_value = el
    return m


def test_schema_completo():
    item = make_item(text="Bici", href="http://x.com")
    result = {
        "titulo": safe_find_text(item, SEL),
        "precio": extract_price(make_item(text="1500"), SEL),
        "link": extract_link(make_item(href="http://x.com"), SEL),
        "tienda_oficial": safe_find_text(make_item(raises=True), SEL),
        "envio_gratis": extract_bool(item, SEL),
        "cuotas_sin_interes": safe_find_text(make_item(raises=True), SEL),
    }
    assert isinstance(result["titulo"], str)
    assert isinstance(result["precio"], int)
    assert result["precio"] > 0
    assert result["link"].startswith("http")
    assert result["tienda_oficial"] is None
    assert result["envio_gratis"] is True
    assert result["cuotas_sin_interes"] is None


def test_schema_precio_none():
    result_precio = extract_price(make_item(raises=True), SEL)
    assert result_precio is None


def test_schema_link_none():
    result_link = extract_link(make_item(raises=True), SEL)
    assert result_link is None
