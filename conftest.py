import argparse
import sys

if sys.version_info[:2] >= (3, 11):
    import tomllib
else:
    import tomli as tomllib


class MyAction(argparse.Action):
    "Load the configuration file once for the whole test session."
    def __call__(self, parser, namespace, values, option_string=None):
        with open(values, "rb") as toml_file:
            setattr(namespace, self.dest, tomllib.load(toml_file))


def pytest_addoption(parser):
    parser.addoption(
        "--user-config-file",
        default=None,
        action=MyAction,
        help="User configuration file for custom tests."
    )
