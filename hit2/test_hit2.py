from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

URL = "https://www.mercadolibre.com.ar"
SEARCH_TERM = "bicicleta rodado 29"


def test_search_works_on_selected_browser(driver):
    driver.get(URL)

    search_box = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.NAME, "as_word"))
    )
    search_box.send_keys(SEARCH_TERM)
    search_box.send_keys(Keys.RETURN)

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "li.ui-search-layout__item"))
    )

    items = driver.find_elements(By.CSS_SELECTOR, "li.ui-search-layout__item")
    titles = [
        item.find_element(By.CSS_SELECTOR, "a.poly-component__title").text
        for item in items[:5]
    ]

    for i, title in enumerate(titles, 1):
        print(f"{i}. {title}")

    assert len(titles) == 5
    assert all(isinstance(t, str) and len(t) > 0 for t in titles)
