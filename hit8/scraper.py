import os
import json
import logging
from pathlib import Path
import pandas as pd
from tabulate import tabulate

from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions

from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from selectors_ml import (
    SEARCH_BOX,
    ITEMS,
    TITLE,
    PRICE,
    LINK,
    STORE,
    ENVIO_GRATIS,
    CUOTAS,
    NEXT_PAGE,
)

from extractors import (
    safe_find_text,
    extract_price,
    extract_link,
    extract_bool,
)
from logging_setup import setup_logging
from database import Database

URL = "https://www.mercadolibre.com.ar"
PRODUCTS = [
    "bicicleta rodado 29",
    "iPhone 16 Pro Max",
    "GeForce RTX 5090",
]

OUTPUT_DIR = Path("output")
SCREENSHOTS_DIR = Path("screenshots")


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
        
        # Bypass bot detection
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)

        driver = webdriver.Chrome(options=options)
        # Execute script to hide webdriver property
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        return driver

    else:
        options = FirefoxOptions()
        if headless:
            options.add_argument("--headless")

        return webdriver.Firefox(options=options)


def handle_overlays(driver):
    try:
        driver.execute_script("""
            const banner = document.querySelector('.cookie-consent-banner-opt-out');
            if (banner) banner.remove();
            const modal = document.querySelector('.andes-modal-stack');
            if (modal) modal.remove();
        """)
    except Exception:
        pass


def search(driver, product):
    # Navigate directly to results URL - avoids login wall triggered by search box
    import urllib.parse
    encoded = urllib.parse.quote(product)
    search_url = f"https://listado.mercadolibre.com.ar/{encoded.replace('%20', '-').lower()}"
    logging.info(f"Navigating directly to: {search_url}")

    driver.get(search_url)

    # Detect login redirect
    if "ingresa" in driver.title.lower() or "login" in driver.current_url.lower():
        SCREENSHOTS_DIR.mkdir(exist_ok=True)
        filename = f"login_wall_{product.replace(' ', '_').lower()}.png"
        driver.save_screenshot(str(SCREENSHOTS_DIR / filename))
        logging.error(f"Login wall detected for '{product}'. Screenshot: {filename}")
        raise TimeoutException(f"Login wall detected for '{product}'")

    try:
        WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located(ITEMS))
    except TimeoutException:
        SCREENSHOTS_DIR.mkdir(exist_ok=True)
        filename = f"error_{product.replace(' ', '_').lower()}.png"
        driver.save_screenshot(str(SCREENSHOTS_DIR / filename))
        logging.error(f"Timeout waiting for items for {product}. Screenshot saved to {filename}")
        raise


def extract_item(item):
    return {
        "titulo": safe_find_text(item, TITLE),
        "precio": extract_price(item, PRICE),
        "link": extract_link(item, LINK),
        "tienda_oficial": safe_find_text(item, STORE),
        "envio_gratis": extract_bool(item, ENVIO_GRATIS),
        "cuotas_sin_interes": safe_find_text(item, CUOTAS),
    }


def print_stats(product, results):
    df = pd.DataFrame(results)
    if df.empty or "precio" not in df or df["precio"].isnull().all():
        logging.warning(f"No price data available for {product}")
        return

    # Clean prices (ensure they are numeric)
    df["precio"] = pd.to_numeric(df["precio"], errors="coerce")
    df = df.dropna(subset=["precio"])

    stats = {
        "Producto": product,
        "Min": df["precio"].min(),
        "Max": df["precio"].max(),
        "Mediana": df["precio"].median(),
        "Desvío Std": df["precio"].std(),
        "Cantidad": len(df)
    }
    
    print("\n" + "="*50)
    print(f"Resumen de precios para: {product}")
    print(tabulate([stats], headers="keys", tablefmt="grid"))
    print("="*50 + "\n")


def run():
    setup_logging()
    driver = create_driver()
    db = Database()
    
    try:
        db.connect()
        db.run_migrations()
    except Exception as e:
        logging.error(f"Could not initialize DB: {e}. Proceeding without DB.")
        db = None

    OUTPUT_DIR.mkdir(exist_ok=True)

    for product in PRODUCTS:
        import time
        time.sleep(2)
        logging.info(f"Searching for: {product}")
        search(driver, product)

        results = []
        page = 1
        while len(results) < 30 and page <= 3:
            logging.info(f"Extracting results from page {page}...")
            items = WebDriverWait(driver, 20).until(
                EC.presence_of_all_elements_located(ITEMS)
            )

            for item in items:
                if len(results) >= 30:
                    break
                data = extract_item(item)
                results.append(data)

            if len(results) < 30 and page < 3:
                try:
                    next_btn = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable(NEXT_PAGE)
                    )
                    driver.execute_script("arguments[0].scrollIntoView(true);", next_btn)
                    next_btn.click()
                    page += 1
                    # Wait for new items to load
                    WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located(ITEMS))
                except (TimeoutException, NoSuchElementException):
                    logging.info("No more pages found.")
                    break
            else:
                break

        # Print stats
        print_stats(product, results)

        # Save to JSON
        filename = product.replace(" ", "_").lower() + ".json"
        with open(OUTPUT_DIR / filename, "w") as f:
            json.dump(results, f, indent=2)

        # Save to DB
        if db:
            db.save_results(product, results)

    driver.quit()
    if db:
        db.close()


if __name__ == "__main__":
    run()
