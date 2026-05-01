import time
import logging

logger = logging.getLogger(__name__)


def with_retry(fn, attempts=3, delays=(2, 4, 8)):
    for i in range(attempts):
        try:
            return fn()
        except Exception:
            if i == attempts - 1:
                logger.error("Fallo final tras reintentos", exc_info=True)
                raise

            delay = delays[i]
            logger.warning(f"Reintento {i+1}/{attempts} en {delay}s")
            time.sleep(delay)
