import os
import subprocess
from logging_setup import setup_logging

setup_logging()

browser = os.environ.get("BROWSER", "chrome")

subprocess.call(
    [
        "pytest",
        "test_hit5.py",
        f"--browser={browser}",
    ]
)
