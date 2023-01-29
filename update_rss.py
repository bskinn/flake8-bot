import json
import sys
from datetime import timedelta
from pathlib import Path

import arrow
from feedgen.feed import FeedGenerator

ID_URL = "https://github.com/bskinn/flake8-bot"

MAX_RSS_ENTRIES = 50
MAX_RSS_AGE = 30

TIMESTAMP = arrow.utcnow().timestamp()


def is_stale(pkg_data):
    entry_stamp = arrow.get(pkg_data["timestamp"])
    diff = arrow.get(TIMESTAMP) - entry_stamp
    return (diff / timedelta(days=MAX_RSS_AGE)) > 1


def report_dropped_entry(pkg_data):
    datestr = arrow.get(pkg_data["timestamp"]).strftime("%Y-%m-%d")
    print(
        "Dropped {pkg} v{version}, {status} on {datestr}.".format(
            datestr=datestr, **pkg_data
        )
    )


def load_rss_json():
    return json.loads(Path("data", "rss.json").read_text())


def load_new_upd_pkgs_json():
    """Retrieve the JSON for new/updated packages."""
    return json.loads(Path("data", "new_upd_pkgs.json").read_text())


def destale_rss_data(rss_json):
    print("Checking for stale RSS entries...")
    while is_stale(rss_json[0]) and len(rss_json) > MAX_RSS_ENTRIES:
        report_dropped_entry(rss_json.pop(0))
    print("")

    return rss_json


def create_feed_generator():
    fg = FeedGenerator()
    fg.id(ID_URL)
    fg.title("New/Updated flake8 Plugins")
    fg.author({"name": "Brian Skinn", "email": "brian.skinn@gmail.com"})
    fg.link(
        href="https://github.com/bskinn/flake8-bot/raw/master/feed/feed.rss", rel="self"
    )
    fg.link(href="https://github.com/bskinn/flake8-bot", rel="alternate")
    fg.logo("https://github.com/bskinn/flake8-bot/raw/master/_static/f8_logo.jpg")
    fg.language("en")
    fg.description("Daily feed of new/updated flake8 plugins")
    fg.docs("http://www.rssboard.org/rss-specification")

    return fg


def main():
    fg = create_feed_generator()

    rss_data = load_rss_json()
    rss_data = destale_rss_data(rss_data)

    # RSS data is ordered in increasing chronological order within both lists
    rss_data.extend(load_new_upd_pkgs_json())

    for item in rss_data:
        fe = fg.add_entry()
        fe.id(ID_URL + "-".join(("", str(item["timestamp"]), item["pkg"])))
        fe.title(f"{item['status'].title()}: {item['pkg']} ({item['version']})")
        fe.link({"href": f"https://pypi.org/project/{item['pkg']}", "rel": "alternate"})
        fe.author(fg.author())
        fe.content(item["summary"])
        fe.updated(arrow.get(item["timestamp"]).datetime)
        fe.published(fe.updated())

    fg.rss_file("feed/feed.rss", pretty=True)


if __name__ == "__main__":
    sys.exit(main())
