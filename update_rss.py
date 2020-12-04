import json
import sys
from pathlib import Path

import arrow
from feedgen.feed import FeedGenerator

ID_URL = "https://github.com/bskinn/flake8-bot"


def load_rss_json():
    return json.loads(Path("data", "rss.json").read_text())


def main():
    fg = FeedGenerator()
    fg.id(ID_URL)
    fg.title("New/Updated flake8 Plugins")
    fg.author({"name": "Brian Skinn", "email": "brian.skinn@gmail.com"})
    fg.link(href="https://github.com/bskinn/flake8-bot/raw/master/feed/feed.rss", rel="self")
    fg.link(href="https://github.com/bskinn/flake8-bot", rel="alternate")
    fg.logo("https://github.com/bskinn/flake8-bot/raw/master/_static/f8_logo.jpg")
    fg.language("en")
    fg.description("Daily feed of new/updated flake8 plugins")
    fg.docs("http://www.rssboard.org/rss-specification")

    data = load_rss_json()
   
    for item in data:
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
