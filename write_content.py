import json
import sys
from pathlib import Path

import markdown_table

EPS_JSON = "eps.json"

CORE_TUPLES = [
    ("pydocstyle", "D"),
    ("pyflakes", "F"),
    ("pycodestyle", "E"),
    ("pycodestyle", "W"),
]


def load_data():
    with Path(EPS_JSON).open() as f:
        data = json.load(f)

    return data


def construct_tuples(data):
    result = []

    for pkg in data:
        for ep in data[pkg]["eps"]:
            result.append((pkg, ep))

    result.extend(CORE_TUPLES)

    return result


def main():
    data = load_data()

    tuples = construct_tuples(data)

    Path("test_table.md").write_text(markdown_table.render(('pkg', 'ep'), tuples))


if __name__ == "__main__":
    sys.exit(main())
