from retry_ml import with_retry
from selenium.common.exceptions import TimeoutException


def test_retry():
    calls = {"n": 0}

    def fn():
        calls["n"] += 1
        if calls["n"] < 3:
            raise TimeoutException()
        return "ok"

    assert with_retry(fn) == "ok"
