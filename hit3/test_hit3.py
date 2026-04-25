import pytest
from pathlib import Path
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

URL = "https://www.mercadolibre.com.ar"
PRODUCTS = ["bicicleta rodado 29", "iPhone 16 Pro Max", "GeForce RTX 5090"]
SCREENSHOTS_DIR = Path(__file__).parent.parent / "screenshots"


# Helpers

def handle_overlays(d):
    d.execute_script("""
        const banner = document.querySelector('.cookie-consent-banner-opt-out');
        if (banner) banner.remove();
    """)


def search(d, term):
    d.get(URL)
    handle_overlays(d)

    box = WebDriverWait(d, 10).until(
        EC.element_to_be_clickable((By.NAME, "as_word"))
    )
    box.send_keys(term)
    box.send_keys(Keys.RETURN)

    WebDriverWait(d, 10).until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, "li.ui-search-layout__item")
        )
    )

    handle_overlays(d)


def safe_click(d, xpath):
    try:
        el = WebDriverWait(d, 8).until(
            EC.presence_of_element_located((By.XPATH, xpath))
        )
        d.execute_script(
            "arguments[0].scrollIntoView({block: 'center'});", el
        )
        WebDriverWait(d, 2).until(lambda d: el.is_displayed())
        try:
            el.click()
        except Exception:
            d.execute_script("arguments[0].click();", el)
        WebDriverWait(d, 10).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "li.ui-search-layout__item")
            )
        )
        handle_overlays(d)
        return True

    except TimeoutException:
        return False
    

# Test

@pytest.mark.parametrize("product", PRODUCTS)
def test_search_with_filters_and_screenshot(driver, product):
    d, browser = driver

    search(d, product)

    safe_click(d, "//span[normalize-space()='Nuevo']/ancestor::a")
    safe_click(d, "//span[normalize-space()='Tienda oficial']/ancestor::a")
    safe_click(d, "//button[contains(@class,'andes-dropdown__trigger')]")
    safe_click(
        d,
        "//li[contains(@class,'andes-dropdown__item')]//span[normalize-space()='Más relevantes']"
    )

    items = WebDriverWait(d, 10).until(
        EC.presence_of_all_elements_located(
            (By.CSS_SELECTOR, "li.ui-search-layout__item")
        )
    )

    titles = []
    for item in items[:5]:
        try:
            title_el = item.find_element(
                By.CSS_SELECTOR, "a.poly-component__title"
            )
            text = title_el.text.strip()
            if text:
                titles.append(text)
        except:
            continue

    # screenshot
    safe_name = product.replace(" ", "_").lower()
    SCREENSHOTS_DIR.mkdir(exist_ok=True)
    d.save_screenshot(str(SCREENSHOTS_DIR / f"{safe_name}_{browser}.png"))

    # asserts
    assert len(titles) >= 3
    assert all(isinstance(t, str) and len(t) > 0 for t in titles)