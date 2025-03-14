import pytest

def pytest_generate_tests(metafunc):
    if "job_plugin" in metafunc.fixturenames:
        metafunc.parametrize("job_plugin", ["local", "nobatch"])
    # TODO parametrization by configuration file.
    if "local_plugin" in metafunc.fixturenames:
        metafunc.parametrize("local_plugin", [])
    if "local_args" in metafunc.fixturenames:
        metafunc.parametrize("local_args", [])
    if "remote_plugin" in metafunc.fixturenames:
        metafunc.parametrize("remote_plugin", [])
    if "remote_args" in metafunc.fixturenames:
        metafunc.parametrize("remote_args", [])
