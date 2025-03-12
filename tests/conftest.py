import pytest

def pytest_generate_tests(metafunc):
    if "job_plugin" in metafunc.fixturenames:
        metafunc.parametrize("job_plugin", ["local", "sshhost"])
