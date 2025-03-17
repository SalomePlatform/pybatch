
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
