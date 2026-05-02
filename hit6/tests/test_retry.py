import pytest
from unittest.mock import MagicMock, patch
from selenium.common.exceptions import TimeoutException
from retry_ml import with_retry


def test_retry_success_first_attempt():
    fn = MagicMock(return_value="ok")
    result = with_retry(fn, max_attempts=3, base_delay=0)
    assert result == "ok"
    assert fn.call_count == 1


def test_retry_success_after_failures():
    fn = MagicMock(side_effect=[TimeoutException, TimeoutException, "ok"])
    with patch("retry_ml.time.sleep"):
        result = with_retry(fn, max_attempts=3, base_delay=0)
    assert result == "ok"
    assert fn.call_count == 3


def test_retry_raises_after_max_attempts():
    fn = MagicMock(side_effect=TimeoutException)
    with patch("retry_ml.time.sleep"):
        with pytest.raises(TimeoutException):
            with_retry(fn, max_attempts=3, base_delay=0)
    assert fn.call_count == 3


def test_retry_delay_increases():
    sleeps = []
    fn = MagicMock(side_effect=[TimeoutException, TimeoutException, "ok"])
    with patch("retry_ml.time.sleep", side_effect=lambda s: sleeps.append(s)):
        with_retry(fn, max_attempts=3, base_delay=2)
    assert sleeps == [2, 4]
