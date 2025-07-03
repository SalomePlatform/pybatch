import typing
from pathlib import Path
import os

import pybatch
import pybatch.tools

import tests.job_cases


def create_launch_parameters(
    config: dict[str, typing.Any],
) -> pybatch.LaunchParameters:
    params = pybatch.LaunchParameters([], config["work_dir"])
    if "wckey" in config:
        params.wckey = config["wckey"]
    if "is_posix" in config:
        params.is_posix = config["is_posix"]
    params.wall_time = "1"  # one minute
    return params


def create_protocol(
    protocol_name: str, config: dict[str, typing.Any]
) -> pybatch.GenericProtocol:
    import pybatch

    params = pybatch.ConnectionParameters(config["host"])
    if "user" in config:
        params.user = config["user"]
    if "password" in config:
        params.password = config["password"]
    if "gss_auth" in config:
        params.gss_auth = config["gss_auth"]
    if protocol_name == "ssh":
        import pybatch.protocols.ssh

        protocol = pybatch.protocols.ssh.SshProtocol(params)
    elif protocol_name == "paramiko":
        import pybatch.protocols.paramiko

        protocol = pybatch.protocols.paramiko.ParamikoProtocol(params)
    else:
        raise Exception(f"Unknown protocol {protocol_name}")
    return protocol


def remote_case_config(
    remote_plugin: str,
    remote_protocol: str,
    remote_args: dict[str, typing.Any],
    case_name: str,
    script_name: str,
) -> tuple[pybatch.LaunchParameters, pybatch.GenericProtocol]:
    is_posix = True
    if "is_posix" in remote_args:
        is_posix = remote_args["is_posix"]
    job_params = create_launch_parameters(remote_args)
    case_dir = case_name + "_" + remote_plugin + "_" + remote_protocol
    job_params.work_directory = pybatch.tools.path_join(
        job_params.work_directory,
        case_dir,
        is_posix=is_posix,
    )
    job_params.ntasks = 1
    current_file_dir = os.path.dirname(__file__)
    script = Path(current_file_dir) / "scripts" / script_name

    job_params.input_files = [script]
    protocol = create_protocol(remote_protocol, remote_args)
    return job_params, protocol


def clean(protocol: pybatch.GenericProtocol, remote_dir: str) -> None:
    pycommand = f'import shutil; shutil.rmtree("{remote_dir}")'
    protocol.run(["python3", "-c", pycommand])


def test_hello(
    remote_plugin: str, remote_protocol: str, remote_args: dict[str, typing.Any]
) -> None:
    job_params, protocol = remote_case_config(
        remote_plugin, remote_protocol, remote_args, "hello", "hello.py"
    )
    tests.job_cases.test_hello(remote_plugin, protocol, job_params)
    clean(protocol, job_params.work_directory)


def test_sleep(
    remote_plugin: str, remote_protocol: str, remote_args: dict[str, typing.Any]
) -> None:
    job_params, protocol = remote_case_config(
        remote_plugin, remote_protocol, remote_args, "sleep", "sleep.py"
    )
    tests.job_cases.test_sleep(remote_plugin, protocol, job_params)
    clean(protocol, job_params.work_directory)


def test_cancel(
    remote_plugin: str, remote_protocol: str, remote_args: dict[str, typing.Any]
) -> None:
    job_params, protocol = remote_case_config(
        remote_plugin, remote_protocol, remote_args, "cancel", "sleep.py"
    )
    tests.job_cases.test_cancel(remote_plugin, protocol, job_params)
    clean(protocol, job_params.work_directory)


def test_error(
    remote_plugin: str, remote_protocol: str, remote_args: dict[str, typing.Any]
) -> None:
    job_params, protocol = remote_case_config(
        remote_plugin, remote_protocol, remote_args, "error", "error.py"
    )
    tests.job_cases.test_error(remote_plugin, protocol, job_params)
    clean(protocol, job_params.work_directory)


def test_nodefile(
    remote_plugin: str, remote_protocol: str, remote_args: dict[str, typing.Any]
) -> None:
    job_params, protocol = remote_case_config(
        remote_plugin,
        remote_protocol,
        remote_args,
        "nodefile",
        "check_nodefile.py",
    )
    tests.job_cases.test_nodefile(remote_plugin, protocol, job_params)
    clean(protocol, job_params.work_directory)


def test_reconnect(
    remote_plugin: str, remote_protocol: str, remote_args: dict[str, typing.Any]
) -> None:
    job_params, protocol = remote_case_config(
        remote_plugin, remote_protocol, remote_args, "reconnect", "sleep.py"
    )
    tests.job_cases.test_reconnect(remote_plugin, protocol, job_params)
    clean(protocol, job_params.work_directory)
