from selenium.webdriver.common.by import By

SEARCH_BOX = (By.NAME, "as_word")
ITEMS = (By.CSS_SELECTOR, "li.ui-search-layout__item")

TITLE = (By.CSS_SELECTOR, "a.poly-component__title")
PRICE = (By.CSS_SELECTOR, ".andes-money-amount__fraction")
STORE = (By.CSS_SELECTOR, ".poly-component__seller")

ENVIO_GRATIS = (By.XPATH, ".//span[contains(text(),'Envío gratis')]")
CUOTAS = (By.XPATH, ".//span[contains(text(),'cuotas')]")
