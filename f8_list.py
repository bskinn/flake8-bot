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

from pep503_norm import pep503_norm
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
    old_pkgs_pep503 = {pep503_norm(old_pkg) for old_pkg in old_versions}

    # Do not store a package in the new list if the version retrieval returns
    # None -- this is a signal that the JSON API 404'd for that package and
    # thus it's been deleted from PyPI.
    new_versions = {
        pkg: ver
        for pkg in results
        if (ver := get_or_default_pkg_version(pkg)) is not None
    }

    # Some (most, probably) of these will be typosquatting packages that
    # *should* end up excluded from the new stored JSON when they fail to
    # install as part of the generate_eps_json script
    new_pkgs = {
        new_pkg
        for new_pkg in new_versions
        if pep503_norm(new_pkg) not in old_pkgs_pep503
    }

    # Detect all version changes; this logic is repeated again in a slight
    # variation in extract_new_upd_pkgs.py. It might be possible to DRY it,
    # but not sure if it's worthwhile or possible.
    # This now drops from f8.list any deleted packages.
    old_key_reverse_pep503_map = {
        pep503_norm(old_key): old_key for old_key in old_versions
    }

    upd_pkgs = {
        new_pkg
        for new_pkg in new_versions
        if pep503_norm(new_pkg) in old_pkgs_pep503
        and Version(new_versions[new_pkg])
        != Version(old_versions[old_key_reverse_pep503_map[pep503_norm(new_pkg)]])
    }

    print(f"\n\nNew Packages:\n{NEWLINE.join(sorted(new_pkgs))}\n")
    print(f"Updated Packages:\n{NEWLINE.join(sorted(upd_pkgs))}\n")

    # Save new/updated packages list to disk
    Path("data", "f8_active.list").write_text("\n".join(sorted(new_pkgs | upd_pkgs)))

    return 0


if __name__ == "__main__":
    sys.exit(main())
