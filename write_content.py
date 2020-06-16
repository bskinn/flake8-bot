import json
import re
import sys
from collections import namedtuple
from pathlib import Path

import markdown_table

PkgEntryPt = namedtuple("PkgEntryPt", ["pkg", "ep"])


EPS_JSON = "eps.json"
MD_PYPI_LINK = "[{pkg}](https://pypi.org/project/{pkg})"

CORE_TUPLES = [
    PkgEntryPt("pyflakes", "F"),
    PkgEntryPt("pycodestyle", "E"),
    PkgEntryPt("pycodestyle", "W"),
]

P_ERRCODE = re.compile(r"^(?P<alpha>[A-Z]{1,3})(?P<num>\d{0,3})$", re.I)


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
            result.append(PkgEntryPt(pkg, ep))

    result.extend(CORE_TUPLES)

    return result


def main():
    data = load_data()

    tuples = construct_tuples(data)

    # Remove base flake8
    tuples = [t for t in tuples if t.pkg != "flake8"]

    # Split out ones with improperly formatted entry_point names
    ok_tups = [t for t in tuples if P_ERRCODE.match(t.ep)]
    bad_tups = [t for t in tuples if not P_ERRCODE.match(t.ep)]

    Path("test_table.md").write_text(
        markdown_table.render(
            ("Package", "`entry_point` Name"),
            ((md_pypi_link(p), e) for p, e in sorted(ok_tups, key=(lambda t: t.ep))),
        )
    )

    Path("bad_errcodes.md").write_text(
        "Broken `entry_points`\n============\n\n"
        + markdown_table.render(
            ("Package", "`entry_point` Name"),
            ((md_pypi_link(p), e) for p, e in bad_tups),
        )
    )


if __name__ == "__main__":
    sys.exit(main())
