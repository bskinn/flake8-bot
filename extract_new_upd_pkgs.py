import json
import re
from collections import namedtuple
from pathlib import Path

import arrow
from packaging.version import Version


EpsPair = namedtuple("EpsPair", ["new", "old"])

TIMESTAMP = arrow.utcnow().timestamp()


def pep503_norm(pkg_name):
    """Apply PEP503 normalization to the given package name.

    Recipe per PEP 503:

    https://peps.python.org/pep-0503/#normalized-names

    """
    return re.sub("[-_.]+", "-", pkg_name).lower()


def get_eps():
    eps_rep = json.loads(Path("data", "eps_rep.json").read_text())
    eps_rep_old = json.loads(Path("data", "eps_rep.json.old").read_text())
    eps_ext = json.loads(Path("data", "eps_ext.json").read_text())
    eps_ext_old = json.loads(Path("data", "eps_ext.json.old").read_text())

    return EpsPair(eps_rep, eps_rep_old), EpsPair(eps_ext, eps_ext_old)


# For these two functions, we assert that if a maintainer *deletes*
# a package from PyPI, they are communicating an intent to abandon
# any flake8 error codes they project had once claimed.
def make_set_new_packages(eps_pair):
    return {
        pkg
        for pkg in eps_pair.new
        if pep503_norm(pkg) not in {pep503_norm(old_pkg) for old_pkg in eps_pair.old}
    }


def make_set_upd_packages(eps_pair):
    eps_pair_old_reverse_pep503_map = {
        pep503_norm(old_pkg): old_pkg for old_pkg in eps_pair.old
    }

    return {
        new_pkg
        for new_pkg in eps_pair.new
        if pep503_norm(new_pkg) in {pep503_norm(old_pkg) for old_pkg in eps_pair.old}
        and (
            Version(eps_pair.new[new_pkg]["version"])
            > Version(
                eps_pair.old[eps_pair_old_reverse_pep503_map[pep503_norm(new_pkg)]][
                    "version"
                ]
            )
        )
    }


def write_new_upd_json(pkg_json):
    Path("data", "new_upd_pkgs.json").write_text(json.dumps(pkg_json))


def main():

    new_upd_pkg_json = []

    eps_pair_rep, eps_pair_ext = get_eps()

    new_pkgs = set.union(*map(make_set_new_packages, (eps_pair_rep, eps_pair_ext)))
    upd_pkgs = set.union(*map(make_set_upd_packages, (eps_pair_rep, eps_pair_ext)))

    for pkg in new_pkgs:
        pkg_data = eps_pair_rep.new.get(pkg, eps_pair_ext.new[pkg])

        new_upd_pkg_json.append(
            {
                "timestamp": TIMESTAMP,
                "pkg": pkg,
                "version": pkg_data["version"],
                "summary": pkg_data["summary"],
                "status": "new",
            }
        )

    for pkg in upd_pkgs:
        pkg_data = eps_pair_rep.new.get(pkg, eps_pair_ext.new[pkg])

        new_upd_pkg_json.append(
            {
                "timestamp": TIMESTAMP,
                "pkg": pkg,
                "version": pkg_data["version"],
                "summary": pkg_data["summary"],
                "status": "updated",
            }
        )

    write_new_upd_json(new_upd_pkg_json)


if __name__ == "__main__":
    main()
