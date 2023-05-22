flake8 Plugins Bot
==================

While the initial purpose of this repository was implementing the lists of flake8 plugin entry points
described below, the machinery is also well suited for reporting when flake8 plugins are
added to or updated on PyPI. Accordingly, whenever these entrypoints lists are updated,
information on new/updated packages is:

 - Tweeted at [@Flake8Plugins](https://twitter.com/Flake8Plugins)
   (via [tweepy](https://github.com/tweepy/tweepy))
 - Pushed to the RSS feed at https://github.com/bskinn/flake8-bot/raw/master/feed/feed.rss
   (via [python-feedgen](https://github.com/lkiesow/python-feedgen))

The data used to persist historical package data for the RSS feed is curated
[here](data/rss.json.zip); if documentation of the schema used there would be helpful,
please open an issue.


Lists of flake8 Plugin Entry Points
===================================

flake8 uses the Python packaging [`entry_points` mechanism](https://setuptools.readthedocs.io/en/latest/setuptools.html#dynamic-discovery-of-services-and-plugins)
as its hook for [registering plugins](https://flake8.pycqa.org/en/latest/plugin-development/registering-plugins.html).
It supports two types of plugins:
"[checkers](https://flake8.pycqa.org/en/latest/plugin-development/plugin-parameters.html)"
 and "[formatters](https://flake8.pycqa.org/en/latest/plugin-development/formatters.html),"
which are registered via the `flake8.extension` and `flake8.report` entry points, respectively.

For both types of plugins, if multiple plugins try to register with the same
entry-point name (the portion of the value before the equals sign),
all but one of the plugins will ~silently not be loaded.

Thus, the goal of this repository is to automatically assemble as complete
and current a list as possible of the entry-point names claimed by plugins on PyPI,
to allow authors of new plugins to confidently choose entry-point names
that will not conflict with other, pre-existing plugins. It also seeks
to identify those checker plugins whose entry-point names do not
conform to the valid format (see the lower half of
[this page](https://flake8.pycqa.org/en/latest/plugin-development/registering-plugins.html)).

The set of PyPI projects surveyed to create these lists can be retrieved
[here](data/f8.list), and the intermediate datasets used to create
the lists are available in JSON format, zipped in
[this file](data/eps.json.zip).
If there is interest (please open an issue if so),
I can add documentation of the JSON schema used in these two files.
If there are any flake8 plugins missing from these lists,
please open an issue (or PR) as well.


*Last Updated: 22 May 2023*

----

**Checker (`flake8.extension`) Entry Points**

- [Valid entry point names, sorted by entry point](mdbuild/ec_sort.md)

- [Valid entry point names, sorted by package](mdbuild/pkg_sort.md)

- [Invalid entry point names](mdbuild/bad_errorcodes.md)



**Formatter (`flake8.report`) Entry Points**

- [Separate lists, sorted by package and entry point](mdbuild/report.md)
