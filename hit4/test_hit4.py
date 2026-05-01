import json
from pathlib import Path

import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

URL = "https://www.mercadolibre.com.ar"

PRODUCTS = [
    "bicicleta rodado 29",
    "iPhone 16 Pro Max",
    "GeForce RTX 5090",
]

OUTPUT_DIR = Path(__file__).parent / "output"


def handle_overlays(d):
    d.execute_script("""
        const banner = document.querySelector('.cookie-consent-banner-opt-out');
        if (banner) banner.remove();
    """)


def search(d, term):
    d.get(URL)
    handle_overlays(d)

    box = WebDriverWait(d, 10).until(EC.element_to_be_clickable((By.NAME, "as_word")))
    box.send_keys(term)
    box.send_keys(Keys.RETURN)

    WebDriverWait(d, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "li.ui-search-layout__item"))
    )


def extract(item):
    try:
        title_el = item.find_element(By.CSS_SELECTOR, "a.poly-component__title")
        title = title_el.text
        link = title_el.get_attribute("href")
    except Exception:
        return None

    try:
        price_el = item.find_element(By.CSS_SELECTOR, ".andes-money-amount__fraction")
        price = int(price_el.text.replace(".", ""))
    except Exception:
        price = None

    try:
        store = item.find_element(By.CSS_SELECTOR, ".poly-component__seller").text
    except Exception:
        store = None

    try:
        item.find_element(By.XPATH, ".//span[contains(text(),'Envío gratis')]")
        envio = True
    except Exception:
        envio = False

    try:
        cuotas = item.find_element(By.XPATH, ".//span[contains(text(),'cuotas')]").text
    except Exception:
        cuotas = None

    return {
        "titulo": title,
        "precio": price,
        "link": link,
        "tienda_oficial": store,
        "envio_gratis": envio,
        "cuotas_sin_interes": cuotas,
    }


@pytest.mark.parametrize("product", PRODUCTS)
def test_hit4_scraper(driver, product):
    d = driver

    search(d, product)

    items = WebDriverWait(d, 10).until(
        EC.presence_of_all_elements_located(
            (By.CSS_SELECTOR, "li.ui-search-layout__item")
        )
    )

    results = []

    for item in items[:10]:
        data = extract(item)
        if data:
            results.append(data)

    OUTPUT_DIR.mkdir(exist_ok=True)

    filename = product.replace(" ", "_").lower() + ".json"

    with open(OUTPUT_DIR / filename, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    assert len(results) >= 1
