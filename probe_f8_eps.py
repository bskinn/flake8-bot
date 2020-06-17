import importlib.metadata as ilmd
from textwrap import dedent


def main():
    for key in ["flake8.extension", "flake8.report"]:
        print(
            dedent(
                f"""
    {key}
    {'=' * len(key)}
    {ilmd.entry_points().get(key, "(none)")}
"""
            )
        )


if __name__ == "__main__":
    main()
