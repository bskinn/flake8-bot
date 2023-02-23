import argparse as ap
import importlib.metadata as ilmd
import json
import sys
from pathlib import Path

from packaging.utils import canonicalize_version

from pep503_norm import pep503_norm
from skip_pkgs import SKIP_PKGS


EXT_JSON_PATH = Path("data", "eps_ext.json")
REP_JSON_PATH = Path("data", "eps_rep.json")


def load_json():
    """Retrieve entry point data from disk.

    Return is a two-tuple of dicts.
    First element is the flake8.extensions data.
    Second element is the flake8.report data.

    """
    try:
        with EXT_JSON_PATH.open("r") as f:
            data_ext = json.load(f)
    except FileNotFoundError:
        data_ext = {}

    try:
        with REP_JSON_PATH.open("r") as f:
            data_rep = json.load(f)
    except FileNotFoundError:
        data_rep = {}

    return data_ext, data_rep


def dump_json(data_ext, data_rep):
    """Write entry point data to disk."""
    with EXT_JSON_PATH.open("w") as f:
        json.dump(data_ext, f)
    with REP_JSON_PATH.open("w") as f:
        json.dump(data_rep, f)


def update_data(data_ext, data_rep, pkg):
    """Update the entry point data with current install state.

    This update is IN PLACE for both data_ext and data_rep.

    Uses 'pkg' as the main key for associating the data
    with the relevant package.

    """

    # Purge any existing packages in both data hives that match the
    # indicated package to within PEP 503 normalization. This will flush
    # any old package data after a rename invisible after PEP 503
    # normalization. (Primarily to get flufl-flake8 out of there...)
    for ext_pkg in [k for k in data_ext.keys()]:
        if pep503_norm(pkg) == pep503_norm(ext_pkg):
            data_ext.pop(ext_pkg)

    for rep_pkg in [k for k in data_rep.keys()]:
        if pep503_norm(pkg) == pep503_norm(rep_pkg):
            data_rep.pop(rep_pkg)

    # Purge any packages matching items in SKIP_PKGS. If a package is
    # being skipped, we should make sure it no longer appears in the
    # Markdown tables, even if it once *was* included and thus is being
    # carried along in the JSON.
    for ext_pkg in [k for k in data_ext.keys()]:
        if ext_pkg in SKIP_PKGS:
            data_ext.pop(ext_pkg)

    for rep_pkg in [k for k in data_rep.keys()]:
        if rep_pkg in SKIP_PKGS:
            data_rep.pop(rep_pkg)

    # TODO: Update with modern API for importlib.metadata entry points
    eps_ext = ilmd.entry_points().get("flake8.extension", {})
    eps_rep = ilmd.entry_points().get("flake8.report", {})

    try:
        version = canonicalize_version(ilmd.version(pkg))
        summary = ilmd.metadata(pkg).get("Summary")
    except ilmd.PackageNotFoundError:
        version = canonicalize_version("0.0")
        summary = "[no summary]"

    for data, eps in zip((data_ext, data_rep), (eps_ext, eps_rep)):
        data.update(
            {
                pkg: {
                    "version": version,
                    "summary": summary,
                    "eps": {
                        ep.name: {
                            "module": (val := ep.value.partition(":"))[0],
                            "callable": val[2],
                        }
                        for ep in eps
                    },
                }
            }
        )


def get_parser():
    prs = ap.ArgumentParser(
        description="Get entry points for installed flake8 extensions"
    )

    prs.add_argument("pkg", help="Name of currently installed package being probed")
    prs.add_argument(
        "--restart",
        action="store_true",
        help="If supplied, overwrite JSON instead of updating",
    )

    return prs


def main():
    prs = get_parser()

    ns = prs.parse_args()
    params = vars(ns)

    data_ext, data_rep = ({}, {}) if params["restart"] else load_json()

    update_data(data_ext, data_rep, params["pkg"])

    dump_json(data_ext, data_rep)

    return 0


if __name__ == "__main__":
    sys.exit(main())
