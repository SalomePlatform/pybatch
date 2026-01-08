# Copyright (C) 2025-2026  CEA, EDF
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307 USA
#
# See http://www.salome-platform.org/ or email : webmaster.salome@opencascade.com
#
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
        help="User configuration file for custom tests.",
    )
