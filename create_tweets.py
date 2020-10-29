import argparse as ap
import json
import os
from collections import namedtuple
from pathlib import Path
from textwrap import dedent
from time import sleep

import arrow
import tweepy
from packaging.version import Version


osenv = os.environ.get

EpsPair = namedtuple("EpsPair", ["new", "old"])

TIMESTAMP = arrow.utcnow().timestamp

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


def get_params():
    prs = ap.ArgumentParser(description="Helper for creating/posting tweets")

    prs.add_argument(
        "--post",
        action="store_true",
        help="Pass this flag to actually post the tweets to Twitter",
    )

    ns = prs.parse_args()
    return vars(ns)


def get_eps():
    eps_rep = json.loads(Path("data", "eps_rep.json").read_text())
    eps_rep_old = json.loads(Path("data", "eps_rep.json.old").read_text())
    eps_ext = json.loads(Path("data", "eps_ext.json").read_text())
    eps_ext_old = json.loads(Path("data", "eps_ext.json.old").read_text())

    return EpsPair(eps_rep, eps_rep_old), EpsPair(eps_ext, eps_ext_old)


def get_rss_json():
    rss_json = json.loads(Path("data", "rss.json").read_text())

    # TODO: Cull old entries

    return rss_json


def write_rss_json(rss_json):
    Path("data", "rss.json").write_text(json.dumps(rss_json))


def get_api():
    auth = tweepy.OAuthHandler(osenv("F8_TWITTER_KEY"), osenv("F8_TWITTER_SECRET_KEY"))
    auth.set_access_token(osenv("F8_TWITTER_TOKEN"), osenv("F8_TWITTER_SECRET_TOKEN"))

    return tweepy.API(auth)


def tweet_new_package(api, *, pkg, version, summary):
    api.update_status(NEW_PKG_MSG.format(pkg=pkg, version=version, summary=summary))


def tweet_upd_package(api, *, pkg, version, summary):
    api.update_status(UPD_PKG_MSG.format(pkg=pkg, version=version, summary=summary))


def set_new_packages(eps_pair):
    return {pkg for pkg in eps_pair.new if pkg not in eps_pair.old}


def set_upd_packages(eps_pair):
    return {
        pkg
        for pkg in eps_pair.old
        if pkg in eps_pair.new
        and (
            Version(eps_pair.new[pkg]["version"])
            > Version(eps_pair.old[pkg]["version"])
        )
    }


def main():
    params = get_params()

    api = get_api()

    eps_pair_rep, eps_pair_ext = get_eps()

    rss_json = get_rss_json()

    new_pkgs = set.union(*map(set_new_packages, (eps_pair_rep, eps_pair_ext)))
    upd_pkgs = set.union(*map(set_upd_packages, (eps_pair_rep, eps_pair_ext)))

    if len(new_pkgs | upd_pkgs) < 1:
        print("No packages to tweet about.")

    for pkg in new_pkgs:
        print(f"**** Tweeting new package: {pkg} ****")
        pkg_data = eps_pair_rep.new.get(pkg, eps_pair_ext.new[pkg])

        if params["post"]:
            tweet_new_package(
                api, pkg=pkg, version=pkg_data["version"], summary=pkg_data["summary"]
            )
            sleep(SLEEP_DELAY)
        else:
            print(f"Would tweet {pkg} v{pkg_data['version']}")

        rss_json.append(
            {
                "timestamp": TIMESTAMP,
                "pkg": pkg,
                "version": pkg_data["version"],
                "summary": pkg_data["summary"],
            }
        )

    for pkg in upd_pkgs:
        print(f"**** Tweeting updated package: {pkg} ****")
        pkg_data = eps_pair_rep.new.get(pkg, eps_pair_ext.new[pkg])

        if params["post"]:
            tweet_upd_package(
                api, pkg=pkg, version=pkg_data["version"], summary=pkg_data["summary"]
            )
            sleep(SLEEP_DELAY)
        else:
            print(f"Would tweet {pkg} v{pkg_data['version']}")

        rss_json.append(
            {
                "timestamp": TIMESTAMP,
                "pkg": pkg,
                "version": pkg_data["version"],
                "summary": pkg_data["summary"],
            }
        )

    write_rss_json(rss_json)


if __name__ == "__main__":
    main()
