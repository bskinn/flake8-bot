import itertools as itt
import json
import re
import sys
from contextlib import suppress
from pathlib import Path

import requests as rq
from opnieuw import retry
from packaging.utils import canonicalize_version
from packaging.version import Version

from skip_pkgs import SKIP_PKGS

PAT_SEARCH_SIMPLE = re.compile(b'href="/simple/([^/]+)/">')

ADDL_PKGS = [
    "cohesion",
    "darglint",
    "dlint",
    "flakehell",
    "good-smell",
    "hacking",
    "mccabe",
    "nitpick",
    "pandas-vet",
    "pep8-naming",
    "pycodestyle",
    "pyflakes",
    "tryceratops",
    "wemake-python-styleguide",
]


NEWLINE = "\n"


class Status404Error(Exception):
    """Marker exception for when a 404 happens."""

    pass


def match_pep503_normalization(pkg1, pkg2):
    """Indicate whether two packages names match w/in Simple API normalization.

    https://peps.python.org/pep-0503/#normalized-names

    PEP provides this regex-based normalization approach.

    """

    def pep503_norm(pkg):
        return re.sub(r"[-_.]+", "-", pkg).lower()

    return pep503_norm(pkg1) == pep503_norm(pkg2)


@retry(
    max_calls_total=5,
    retry_window_after_first_call_in_seconds=60,
    retry_on_exceptions=(Exception,),
)
def get_simple_listing_response():
    print("Retrieving PyPI simple listing...", end="")

    resp = rq.get(
        "https://pypi.org/simple",
        headers={"Accept": "application/vnd.pypi.simple.v1+json"},
    )

    print("OK.\n")

    return resp


def safe_match(bstr):
    if mch := PAT_SEARCH_SIMPLE.search(bstr):
        return mch.group(1).decode()
    else:
        return ""


def get_old_versions():
    # Load one JSON
    # Update the dict with the other JSON
    # Return a mapping of package to version string
    with Path("data", "eps_ext.json").open() as f:
        data = json.load(f)
    with Path("data", "eps_rep.json").open() as f:
        data.update(json.load(f))

    # Don't want the stub 'init' entry in there
    with suppress(KeyError):
        data.pop("init")

    return {pkg: data[pkg]["version"] for pkg in data}


@retry(
    max_calls_total=5,
    retry_window_after_first_call_in_seconds=20,
    retry_on_exceptions=(rq.RequestException,),
)
def get_pkg_pypi_version(pkg):
    resp = rq.get(f"https://pypi.org/pypi/{pkg}/json")

    print(f"Retrieving '{pkg}' version...", end="")

    if resp.status_code == 404:
        raise Status404Error()

    ver = canonicalize_version(resp.json()["info"]["version"])

    print("OK.")

    return ver


def get_or_default_pkg_version(pkg):
    """Return PyPI project version, or None for 404, or v0.0 for other errors."""
    try:
        return get_pkg_pypi_version(pkg)
    except Status404Error:
        print("404 response at package JSON endpoint, package deleted: skipping.")
        return None
    except rq.RequestException:
        print("Repeated error during attempt to reach JSON endpoint, using dummy v0.0")
        return canonicalize_version("0.0")
    except KeyError:
        print("Invalid version in JSON response, using dummy v0.0")
        return canonicalize_version("0.0")
    except Exception:
        print("Unexpected error, using dummy v0.0")
        return canonicalize_version("0.0")


def main():
    # Retrieve the PyPI listing
    resp = get_simple_listing_response()

    # Iterate through and filter results
    results = list(
        sorted(
            {
                proj_name
                for proj in resp.json()["projects"]
                if ("flake8" in (proj_name := proj["name"]) or proj_name in ADDL_PKGS)
                and proj_name not in SKIP_PKGS
            }
        )
    )

    # Save complete results to disk
    Path("data", "f8.list").write_text("\n".join(results))

    old_versions = get_old_versions()

    new_versions = {
        pkg: ver
        for pkg in results
        if (ver := get_or_default_pkg_version(pkg)) is not None
    }

    # Some (most, probably) of these will be typosquatting packages that
    # *should* end up excluded from the new stored JSON when they fail to
    # install as part of the generate_eps_json script
    new_pkgs = {
        new_key
        for new_key in new_versions.keys()
        if not any(
            match_pep503_normalization(new_key, old_key)
            for old_key in old_versions.keys()
        )
    }

    # Detect all version changes; the decision to tweet only based upon
    # new versions is made in the later extract_new_upd_pkgs.py script.
    # The old_versions.get() handles cases where projects are deleted
    # from PyPI. This now drops from f8.list any deleted packages.
    # TODO: Update to match normalized packages, not string-equal (via the .get(...))
    upd_pkgs = {
        pkg
        for pkg in new_versions
        if Version(new_versions[pkg]) != Version(old_versions.get(pkg, "0"))
    }

    print(f"\n\nNew Packages:\n{NEWLINE.join(sorted(new_pkgs))}\n")
    print(f"Updated Packages:\n{NEWLINE.join(sorted(upd_pkgs))}\n")

    # Save new/updated packages list to disk
    Path("data", "f8_active.list").write_text("\n".join(sorted(new_pkgs | upd_pkgs)))

    return 0


if __name__ == "__main__":
    sys.exit(main())
