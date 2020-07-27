import itertools as itt
import json
import re
import sys
from pathlib import Path

import requests as rq

PAT = re.compile(b'href="/simple/([^/]+)/">')

ADDL_PKGS = [
    "cohesion",
    "darglint",
    "dlint",
    "flakehell",
    "hacking",
    "mccabe",
    "pandas-vet",
    "pep8-naming",
    "pycodestyle",
    "pyflakes",
    "wemake-python-styleguide",
]

SKIP_PKGS = ["dh2flake8"]


def safe_match(bstr):
    if mch := PAT.search(bstr):
        return mch.group(1).decode()
    else:
        return ""


def main():
    # Retrieve the PyPI listing
    req = rq.get("https://pypi.org/simple")

    # Iterate through and filter results
    results = [
        r
        for line in req.iter_lines()
        if any(map((r := safe_match(line)).startswith, "a"))
        and "flake8" not in r
    ]

    # Save results to disk
    Path("data", "f8.list").write_text("\n".join(results))

    return 0


if __name__ == "__main__":
    sys.exit(main())
