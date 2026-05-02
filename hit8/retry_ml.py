import time
import logging
from selenium.common.exceptions import TimeoutException

logger = logging.getLogger(__name__)


def with_retry(fn, max_attempts=3, base_delay=2):
    for attempt in range(1, max_attempts + 1):
        try:
            return fn()
        except TimeoutException:
            if attempt == max_attempts:
                logger.error("Timeout tras reintentos", exc_info=True)
                raise
            delay = base_delay * (2 ** (attempt - 1))
            logger.warning(f"Retry {attempt}/{max_attempts} en {delay}s")
            time.sleep(delay)
