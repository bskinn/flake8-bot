import re


def pep503_norm(pkg_name):
    """Apply PEP503 normalization to the given package name.

    Recipe per PEP 503:

    https://peps.python.org/pep-0503/#normalized-names

    """
    return re.sub("[-_.]+", "-", pkg_name).lower()
