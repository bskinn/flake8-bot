List of flake8 Plugin Entry Points
==================================

flake8 uses the Python packaging [`entry_points` mechanism](https://setuptools.readthedocs.io/en/latest/setuptools.html#dynamic-discovery-of-services-and-plugins)
as its hook for [registering plugins](https://flake8.pycqa.org/en/latest/plugin-development/registering-plugins.html).
It supports two types of plugins: "checkers," which **BLAH**, and
"formatters," which **BLOOH**.

Formatters use the `flake8.report` entry point ...

Checkers user the `flake8.extension` entry point ...



(at minimum) the scope of the error codes raised
by a code-checking plugin.

If multiple plugins try to claim the same error code
namespace, one or the other plugin will silently(?)
just not be loaded.

Goal here is to automatically assemble a list of the
full claimed namespace of flake8 error codes,
to allow authors of new plugins to confidently
choose error codes that are likely to be as-yet unclaimed.

*Last Updated: 19 Jun 2020*


**`flake8.extension` Entry Points**





**`flake8.report` Entry Points**

[Separate lists, sorted by package and entry point](mdbuild/report.md)
