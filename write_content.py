import json
import re
import sys
import time
from collections import namedtuple
from pathlib import Path

from jinja2 import Template
import markdown_table

PkgEntryPt = namedtuple("PkgEntryPt", ["pkg", "ep"])


DATE = time.strftime("%e %b %Y".lstrip())
EXT_EPS_JSON_PATH = Path("data", "eps_ext.json")
REP_EPS_JSON_PATH = Path("data", "eps_rep.json")
MD_PYPI_LINK = "[{pkg}](https://pypi.org/project/{pkg})"

CORE_TUPLES = [
    PkgEntryPt("pyflakes", "F"),
    PkgEntryPt("pycodestyle", "E"),
    PkgEntryPt("pycodestyle", "W"),
]

P_ERRCODE = re.compile(r"^(?P<alpha>[A-Z]{1,3})(?P<num>\d{0,3})$", re.I)

REP_TEMPLATE = Template(Path("templates", "report.md_t").read_text())
BAD_TEMPLATE = Template(Path("templates", "bad_errorcodes.md_t").read_text())
PKG_SORT_TEMPLATE = Template(Path("templates", "ok_pkgsort.md_t").read_text())
EC_SORT_TEMPLATE = Template(Path("templates", "ok_ecsort.md_t").read_text())

BUILD_DIR = "mdbuild"
REP_PATH = Path(BUILD_DIR, "report.md")
BAD_CODE_PATH = Path(BUILD_DIR, "bad_errorcodes.md")
PKG_SORT_PATH = Path(BUILD_DIR, "pkg_sort.md")
EC_SORT_PATH = Path(BUILD_DIR, "ec_sort.md")


def md_pypi_link(pkg):
    return MD_PYPI_LINK.format(pkg=pkg)


def load_data():
    with EXT_EPS_JSON_PATH.open() as f:
        data_ext = json.load(f)
    with REP_EPS_JSON_PATH.open() as f:
        data_rep = json.load(f)

    return data_ext, data_rep


def construct_tuples(data):
    result = []

    for pkg in data:
        for ep in data[pkg]["eps"]:
            result.append(PkgEntryPt(pkg, ep))

    result.extend(CORE_TUPLES)

    return result


def write_report_md(tuples_rep):
    table_pkg = markdown_table.render(
        ("Package", "Entry Point Name"), ((md_pypi_link(p), e) for p, e in tuples_rep)
    )
    table_ep = markdown_table.render(
        ("Entry Point Name", "Package"),
        ((e, md_pypi_link(p)) for p, e in sorted(tuples_rep, key=(lambda t: t.ep))),
    )
    REP_PATH.write_text(
        REP_TEMPLATE.render(table_pkg=table_pkg, table_ep=table_ep, date=DATE)
    )


def main():
    data_ext, data_rep = load_data()

    tuples_ext = construct_tuples(data_ext)
    tuples_rep = construct_tuples(data_rep)

    # Remove base flake8 for extensions; leave for report
    tuples_ext = [t for t in tuples_ext if t.pkg != "flake8"]

    # Write flake8.report .md
    write_report_md(tuples_rep)

    # Split out ones with improperly formatted entry_point names
    ok_tups = [t for t in tuples_ext if P_ERRCODE.match(t.ep)]
    bad_tups = [t for t in tuples_ext if not P_ERRCODE.match(t.ep)]

    PKG_SORT_PATH.write_text(
        PKG_SORT_TEMPLATE.render(
            table=markdown_table.render(
                ("Package", "`entry_point` Name"),
                ((md_pypi_link(p), e) for p, e in ok_tups),
            ),
            date=DATE,
        )
    )
    EC_SORT_PATH.write_text(
        EC_SORT_TEMPLATE.render(
            table=markdown_table.render(
                ("`entry_point` Name", "Package"),
                (
                    (e, md_pypi_link(p))
                    for p, e in sorted(ok_tups, key=(lambda t: t.ep))
                ),
            ),
            date=DATE,
        )
    )

    BAD_CODE_PATH.write_text(
        BAD_TEMPLATE.render(
            table=markdown_table.render(
                ("Package", "`entry_point` Name"),
                ((md_pypi_link(p), e) for p, e in bad_tups),
            ),
            date=DATE,
        ),
    )


if __name__ == "__main__":
    sys.exit(main())
