from selenium.webdriver.common.by import By

SEARCH_BOX = (By.NAME, "as_word")
ITEMS = (By.CSS_SELECTOR, "li.ui-search-layout__item")

TITLE = (By.CSS_SELECTOR, "a.poly-component__title")
PRICE = (By.CSS_SELECTOR, ".andes-money-amount__fraction")
LINK = (By.CSS_SELECTOR, "a.poly-component__title")

STORE = (By.CSS_SELECTOR, ".poly-component__seller")
ENVIO_GRATIS = (By.XPATH, ".//span[contains(text(),'Envío gratis')]")
CUOTAS = (By.CSS_SELECTOR, ".poly-price__installments")
NEXT_PAGE = (By.CSS_SELECTOR, "a[aria-label='Siguiente']")
