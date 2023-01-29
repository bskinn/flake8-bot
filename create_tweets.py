import argparse as ap
import json
import os
import sys

# from datetime import timedelta
from pathlib import Path
from textwrap import dedent
from time import sleep

# import arrow
import tweepy


osenv = os.environ.get

NEW_PKG_MSG = dedent(
    """\
    *** New Package ***

    {pkg} v{version}

    {summary}

    https://pypi.org/project/{pkg}
    """
)

UPD_PKG_MSG = dedent(
    """\
    *** Updated Package ***

    {pkg} v{version}

    {summary}

    https://pypi.org/project/{pkg}
    """
)

SLEEP_DELAY = 10.0
MAX_RSS_ENTRIES = 50
MAX_RSS_AGE = 30

AP_ARG_POST = "post"


# def is_stale(entry):
#     entry_stamp = arrow.get(entry["timestamp"])
#     diff = arrow.get(TIMESTAMP) - entry_stamp
#     return (diff / timedelta(days=MAX_RSS_AGE)) > 1


# def report_dropped_entry(entry):
#     datestr = arrow.get(entry["timestamp"]).strftime("%Y-%m-%d")
#     print(
#         "Dropped {pkg} v{version}, {status} on {datestr}.".format(
#             datestr=datestr, **entry
#         )
#     )


def get_params():
    prs = ap.ArgumentParser(description="Helper for creating/posting tweets")

    prs.add_argument(
        f"--{AP_ARG_POST}",
        action="store_true",
        help="Pass this flag to actually post the tweets to Twitter",
    )

    ns = prs.parse_args()
    return vars(ns)


# def get_rss_json():
#     """Retrieve the JSON of the RSS data.

#     INCLUDES a cull of stale RSS feed entries.

#     """
#     rss_json = json.loads(Path("data", "rss.json").read_text())

#     print("Checking for stale RSS entries...")
#     while is_stale(rss_json[0]) and len(rss_json) > MAX_RSS_ENTRIES:
#         report_dropped_entry(rss_json.pop(0))
#     print("")

#     return rss_json


def get_new_upd_pkgs_json():
    """Retrieve the JSON for new/updated packages."""
    return json.loads(Path("data", "new_upd_pkgs.json").read_text())


def get_api():
    auth = tweepy.OAuthHandler(osenv("F8_TWITTER_KEY"), osenv("F8_TWITTER_SECRET_KEY"))
    auth.set_access_token(osenv("F8_TWITTER_TOKEN"), osenv("F8_TWITTER_SECRET_TOKEN"))

    return tweepy.API(auth)


def tweet_new_package(api, *, pkg, version, summary):
    api.update_status(NEW_PKG_MSG.format(pkg=pkg, version=version, summary=summary))


def tweet_upd_package(api, *, pkg, version, summary):
    api.update_status(UPD_PKG_MSG.format(pkg=pkg, version=version, summary=summary))


def main():
    params = get_params()

    should_post = params[AP_ARG_POST]

    api = get_api() if should_post else None

    pkgs_data = get_new_upd_pkgs_json()

    if len(pkgs_data) < 1:
        print("No packages to tweet about.")
        return 0

    for pkg_data in pkgs_data:
        if pkg_data["status"] == "new":
            print(f"**** Tweeting new package: {pkg_data['pkg']} ****")

            if should_post:
                tweet_new_package(
                    api,
                    pkg=pkg_data["pkg"],
                    version=pkg_data["version"],
                    summary=pkg_data["summary"],
                )
                sleep(SLEEP_DELAY)
            else:
                print(f"Would tweet {pkg_data['pkg']} v{pkg_data['version']}")

            print()

        elif pkg_data["status"] == "updated":
            print(f"**** Tweeting updated package: {pkg_data['pkg']} ****")

            if should_post:
                tweet_upd_package(
                    api,
                    pkg=pkg_data["pkg"],
                    version=pkg_data["version"],
                    summary=pkg_data["summary"],
                )
                sleep(SLEEP_DELAY)
            else:
                print(f"Would tweet {pkg_data['pkg']} v{pkg_data['version']}")

            print()

        else:
            print(f"!!!! ERROR: Invalid package status ({pkg_data['status']}) !!!!")
            print(f"  {pkg_data['pkg']} v{pkg_data['version']}")
            print()

    return 0


if __name__ == "__main__":
    sys.exit(main())
