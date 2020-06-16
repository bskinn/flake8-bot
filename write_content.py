import json
import sys
from pathlib import Path

import markdown_table

EPS_JSON = "eps.json"
MD_PYPI_LINK = "[{pkg}](https://pypi.org/project/{pkg})"

CORE_TUPLES = [
    ("pydocstyle", "D"),
    ("pyflakes", "F"),
    ("pycodestyle", "E"),
    ("pycodestyle", "W"),
]


def md_pypi_link(pkg):
    return MD_PYPI_LINK.format(pkg=pkg)


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

    Path("test_table.md").write_text(
        markdown_table.render(("Package", "`entry_point` Name"), ((md_pypi_link(p), e) for p, e in tuples))
    )


if __name__ == "__main__":
    sys.exit(main())
