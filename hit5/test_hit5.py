import json
import logging
from pathlib import Path

import pytest
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from selectors_ml import (
    SEARCH_BOX,
    ITEMS,
    TITLE,
    PRICE,
    STORE,
    ENVIO_GRATIS,
    CUOTAS,
)

from retry_ml import with_retry

logger = logging.getLogger(__name__)

URL = "https://www.mercadolibre.com.ar"

PRODUCTS = [
    "bicicleta rodado 29",
    "iPhone 16 Pro Max",
    "GeForce RTX 5090",
]

OUTPUT_DIR = Path(__file__).parent / "output"


def search(d, term):
    def _action():
        d.get(URL)

        box = WebDriverWait(d, 10).until(EC.element_to_be_clickable(SEARCH_BOX))
        box.send_keys(term)
        box.submit()

        WebDriverWait(d, 10).until(EC.presence_of_element_located(ITEMS))

    return with_retry(_action)


def safe_find(item, selector, field_name, product):
    try:
        return item.find_element(*selector)
    except Exception:
        logger.warning(f"{field_name} no encontrado", extra={"producto": product})
        return None


def extract(item, product):
    try:
        title_el = safe_find(item, TITLE, "titulo", product)
        title = title_el.text if title_el else None
        link = title_el.get_attribute("href") if title_el else None

        price_el = safe_find(item, PRICE, "precio", product)
        price = int(price_el.text.replace(".", "")) if price_el else None

        store_el = safe_find(item, STORE, "tienda", product)
        store = store_el.text if store_el else None

        envio = False
        try:
            item.find_element(*ENVIO_GRATIS)
            envio = True
        except Exception:
            pass

        cuotas_el = safe_find(item, CUOTAS, "cuotas", product)
        cuotas = cuotas_el.text if cuotas_el else None

        return {
            "titulo": title,
            "precio": price,
            "link": link,
            "tienda_oficial": store,
            "envio_gratis": envio,
            "cuotas_sin_interes": cuotas,
        }

    except Exception:
        logger.error("Error extrayendo item", exc_info=True)
        return None


@pytest.mark.parametrize("product", PRODUCTS)
def test_hit5_scraper(driver, product):
    d = driver

    search(d, product)

    items = WebDriverWait(d, 10).until(EC.presence_of_all_elements_located(ITEMS))

    results = []

    for item in items[:10]:
        data = extract(item, product)
        if data:
            results.append(data)

    OUTPUT_DIR.mkdir(exist_ok=True)

    filename = product.replace(" ", "_").lower() + ".json"

    with open(OUTPUT_DIR / filename, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    assert len(results) >= 1
