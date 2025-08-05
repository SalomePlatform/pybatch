# Copyright (C) 2025  CEA, EDF
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
def pytest_generate_tests(metafunc):
    if "job_plugin" in metafunc.fixturenames:
        metafunc.parametrize("job_plugin", ["local", "nobatch"])

    user_options = metafunc.config.getoption("--user-config-file")
    if "local_plugin" in metafunc.fixturenames:
        if user_options is not None and "local" in user_options:
            conf = user_options["local"]["plugins"]
        else:
            conf = []
        metafunc.parametrize("local_plugin", conf)

    if "local_args" in metafunc.fixturenames:
        if user_options is not None and "local" in user_options:
            conf = [user_options["local"]]
        else:
            conf = []
        metafunc.parametrize("local_args", conf)

    if "remote_plugin" in metafunc.fixturenames:
        if user_options is not None and "remote" in user_options:
            conf = user_options["remote"]["plugins"]
        else:
            conf = []
        metafunc.parametrize("remote_plugin", conf)

    if "remote_protocol" in metafunc.fixturenames:
        if user_options is not None and "remote" in user_options:
            conf = user_options["remote"]["protocols"]
        else:
            conf = []
        metafunc.parametrize("remote_protocol", conf)

    if "remote_args" in metafunc.fixturenames:
        if user_options is not None and "remote" in user_options:
            conf = [user_options["remote"]]
        else:
            conf = []
        metafunc.parametrize("remote_args", conf)
