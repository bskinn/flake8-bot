import itertools as itt
import json
import re
import sys
from pathlib import Path

import requests as rq

PAT = re.compile(b'href="/simple/([^/]+)/">')

ADDL_PKGS = ["pep8-naming", "mccabe", "pyflakes", "pycodestyle", "pydocstyle"]
SKIP_PKGS = [
    "flake8-boto3-plugin",
    "flake8-custom-indent",
    "flake8-docstrings-catnado",
    "flake8-naming",
    "flake8-setuptools",
    "flake8-time-sleep",
]


def main():
    # Retrieve the PyPI listing
    req = rq.get("https://pypi.org/simple")

    # Pull all results
    results = [mch.group(1).decode() for mch in PAT.finditer(req.content)]

    # Initial filter of results
    results = [r for r in results if "flake8" in r or r in ADDL_PKGS]

    # Save results to disk
    Path("f8.list").write_text("\n".join(results))

    return 0


if __name__ == "__main__":
    sys.exit(main())
