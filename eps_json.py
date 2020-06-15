import argparse as ap
import importlib.metadata as ilmd
import json
from pathlib import Path

JSON_PATH = Path("eps.json")


def load_json():
    """Retrieve entry point data from disk."""
    try:
        with JSON_PATH.open("r") as f:
            data = json.load(f)
    except FileNotFoundError:
        data = {}

    return data


def dump_json(data):
    """Write entry point data to disk."""
    with JSON_PATH.open("w") as f:
        json.dump(data, f)


def update_data(data, pkg):
    """Update the entry point data with current install state.

    This update is IN PLACE.

    Uses 'pkg' as the main key for associating the data
    with the relevant package.

    """
    eps = ilmd.entry_points().get("flake8.extension", {})

    data.update(
        {
            pkg: {
                ep.name: {
                    "module": (val := ep.value.partition(":"))[0],
                    "callable": val[2],
                }
                for ep in eps
            }
        }
    )


def get_parser():
    prs = ap.ArgumentParser(
        description="Get entry points for installed flake8 extensions"
    )

    prs.add_argument("pkg", help="Name of currently installed package being probed")
    prs.add_argument("--restart", action="store_true", help="If supplied, overwrite JSON instead of updating")

    return prs


def main():
    prs = get_parser()

    ns = prs.parse_args()
    params = vars(ns)

    data = {} if params['restart'] else load_json()

    update_data(data, params["pkg"])

    dump_json(data)


if __name__ == "__main__":
    main()
