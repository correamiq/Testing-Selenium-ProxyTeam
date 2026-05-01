import os
import json
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from selectors_ml import (
    SEARCH_BOX,
    ITEMS,
    TITLE,
    PRICE,
    LINK,
    STORE,
    ENVIO_GRATIS,
    CUOTAS,
)

from extractors import (
    safe_find_text,
    extract_price,
    extract_link,
    extract_bool,
)
from logging_setup import setup_logging

URL = "https://www.mercadolibre.com.ar"
PRODUCTS = [
    "bicicleta rodado 29",
    "iPhone 16 Pro Max",
    "GeForce RTX 5090",
]

OUTPUT_DIR = Path("output")


def create_driver():
    browser = os.getenv("BROWSER", "chrome")
    headless = os.getenv("HEADLESS", "false").lower() == "true"

    if browser == "chrome":
        options = ChromeOptions()
        if headless:
            options.add_argument("--headless=new")

        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")

        options.add_argument(
            "--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
        )

        return webdriver.Chrome(options=options)

    else:
        options = FirefoxOptions()
        if headless:
            options.add_argument("--headless")

        return webdriver.Firefox(options=options)


def search(driver, product):
    driver.get(URL)

    box = WebDriverWait(driver, 10).until(EC.element_to_be_clickable(SEARCH_BOX))
    box.send_keys(product)
    box.submit()

    WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located(ITEMS))


def extract_item(item):
    return {
        "titulo": safe_find_text(item, TITLE),
        "precio": extract_price(item, PRICE),
        "link": extract_link(item, LINK),
        "tienda_oficial": safe_find_text(item, STORE),
        "envio_gratis": extract_bool(item, ENVIO_GRATIS),
        "cuotas_sin_interes": safe_find_text(item, CUOTAS),
    }


def run():
    setup_logging()
    driver = create_driver()

    OUTPUT_DIR.mkdir(exist_ok=True)

    for product in PRODUCTS:
        search(driver, product)

        items = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located(ITEMS)
        )

        results = []
        for item in items[:10]:
            data = extract_item(item)
            results.append(data)

        filename = product.replace(" ", "_").lower() + ".json"

        with open(OUTPUT_DIR / filename, "w") as f:
            json.dump(results, f, indent=2)

    driver.quit()


if __name__ == "__main__":
    run()
