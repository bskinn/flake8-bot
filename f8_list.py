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

SKIP_PKGS = ["dh2flake8", "flake82"]
NEWLINE = "\n"


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
    retry_on_exceptions=(Exception,),
)
def get_pkg_pypi_version(pkg):
    resp = rq.get(f"https://pypi.org/pypi/{pkg}/json")

    print(f"Retrieving '{pkg}' version...", end="")

    ver = canonicalize_version(resp.json()["info"]["version"])

    print("OK.")

    return ver


def get_or_default_pkg_version(pkg):
    try:
        return get_pkg_pypi_version(pkg)
    except Exception:
        print("Not found, using dummy v0.0")
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

    new_versions = {p: get_or_default_pkg_version(p) for p in results}

    # Some (most, probably) of these will be typosquatting packages that
    # *should* end up excluded from the new stored JSON when they fail to
    # install as part of the generate_eps_json script
    new_pkgs = set(new_versions.keys()) - set(old_versions.keys())

    # Detect all version changes; the decision to tweet only based upon
    # new versions is made in the later write_content.py script.
    # The new_versions.get() handles cases where projects are deleted
    # from PyPI.
    upd_pkgs = {
        pkg
        for pkg in old_versions
        if Version(new_versions.get(pkg, "0")) != Version(old_versions[pkg])
    }

    print(f"\n\nNew Packages:\n{NEWLINE.join(sorted(new_pkgs))}\n")
    print(f"Updated Packages:\n{NEWLINE.join(sorted(upd_pkgs))}\n")

    # Save new/updated packages list to disk
    Path("data", "f8_active.list").write_text("\n".join(sorted(new_pkgs | upd_pkgs)))

    return 0


if __name__ == "__main__":
    sys.exit(main())
