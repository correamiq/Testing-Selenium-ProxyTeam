from selenium.common.exceptions import NoSuchElementException


def safe_find_text(parent, selector):
    try:
        return parent.find_element(*selector).text.strip()
    except NoSuchElementException:
        return None


def extract_price(parent, selector):
    try:
        text = parent.find_element(*selector).text.replace(".", "")
        return int(text)
    except Exception:
        return None


def extract_link(parent, selector):
    try:
        return parent.find_element(*selector).get_attribute("href")
    except Exception:
        return None


def extract_bool(parent, selector):
    try:
        parent.find_element(*selector)
        return True
    except Exception:
        return False
