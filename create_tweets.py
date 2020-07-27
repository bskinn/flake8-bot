import json
import os
from collections import namedtuple
from pathlib import Path

import tweepy


osenv = os.environ

EpsPair = namedtuple("EpsPair", ["new", "old"])


def get_eps():
    eps_rep = json.loads(Path("data", "eps_rep.json").read_text())
    eps_rep_old = json.loads(Path("data", "eps_rep.json.old").read_text())
    eps_ext = json.loads(Path("data", "eps_ext.json").read_text())
    eps_ext_old = json.loads(Path("data", "eps_ext.json.old").read_text())

    return EpsPair(eps_rep, eps_rep_old), EpsPair(eps_ext, eps_ext_old)


def get_api():
    auth = tweepy.OAuthHandler(osenv["F8_TWITTER_KEY"], osenv["F8_TWITTER_SECRET_KEY"])
    auth.set_access_token(osenv["F8_TWITTER_TOKEN"], osenv["F8_TWITTER_SECRET_TOKEN"])

    return tweepy.API(auth)


def main():
    api = get_api()
    eps_p_rep, eps_p_ext = get_eps()

    print(eps_p_rep, eps_p_ext)


if __name__ == "__main__":
    main()
