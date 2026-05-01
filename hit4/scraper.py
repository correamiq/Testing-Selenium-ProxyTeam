import os
import subprocess

browser = os.environ.get("BROWSER", "chrome")

subprocess.call(
    [
        "pytest",
        "test_hit4.py",
        f"--browser={browser}",
    ]
)
