import argparse as ap
import importlib.metadata as ilmd
import json
import sys
from pathlib import Path

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
    eps_ext = ilmd.entry_points().get("flake8.extension", {})
    eps_rep = ilmd.entry_points().get("flake8.report", {})

    try:
        version = ilmd.version(pkg)
        summary = ilmd.metadata(pkg).get("Summary")
    except ilmd.PackageNotFoundError:
        version = "0.0"
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
