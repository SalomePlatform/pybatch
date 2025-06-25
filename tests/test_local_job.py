import typing

import pybatch
import pybatch.protocols.local

import tempfile
from pathlib import Path
import shutil
import os

import tests.job_cases


def local_case_config(
    plugin: str, config: dict[str, typing.Any], case_name: str, script_name: str
) -> tuple[pybatch.LaunchParameters, pybatch.GenericProtocol, str]:
    if "work_dir" in config:
        work_dir = os.path.join(config["work_dir"], case_name + "_" + plugin)
    else:
        work_dir = tempfile.mkdtemp(suffix="_pybatchtest")
    params = pybatch.LaunchParameters([], work_dir)
    if "wckey" in config:
        params.wckey = config["wckey"]
    params.ntasks = 1

    current_file_dir = os.path.dirname(__file__)
    script = Path(current_file_dir) / "scripts" / script_name
    params.input_files = [script]
    protocol = pybatch.protocols.local.LocalProtocol()
    return params, protocol, work_dir


def test_hello(local_plugin: str, local_args: dict[str, typing.Any]) -> None:
    job_params, protocol, work_dir = local_case_config(
        local_plugin, local_args, "hello", "hello.py"
    )
    tests.job_cases.test_hello(local_plugin, protocol, job_params)
    shutil.rmtree(work_dir)


def test_sleep(local_plugin: str, local_args: dict[str, typing.Any]) -> None:
    job_params, protocol, work_dir = local_case_config(
        local_plugin, local_args, "sleep", "sleep.py"
    )
    tests.job_cases.test_sleep(local_plugin, protocol, job_params)
    shutil.rmtree(work_dir)


def test_cancel(local_plugin: str, local_args: dict[str, typing.Any]) -> None:
    job_params, protocol, work_dir = local_case_config(
        local_plugin, local_args, "cancel", "sleep.py"
    )
    tests.job_cases.test_cancel(local_plugin, protocol, job_params)
    shutil.rmtree(work_dir)


def test_error(local_plugin: str, local_args: dict[str, typing.Any]) -> None:
    job_params, protocol, work_dir = local_case_config(
        local_plugin, local_args, "error", "error.py"
    )
    tests.job_cases.test_error(local_plugin, protocol, job_params)
    shutil.rmtree(work_dir)


def test_nodefile(local_plugin: str, local_args: dict[str, typing.Any]) -> None:
    job_params, protocol, work_dir = local_case_config(
        local_plugin, local_args, "nodefile", "check_nodefile.py"
    )
    tests.job_cases.test_nodefile(local_plugin, protocol, job_params)
    shutil.rmtree(work_dir)


def test_reconnect(
    local_plugin: str, local_args: dict[str, typing.Any]
) -> None:
    job_params, protocol, work_dir = local_case_config(
        local_plugin, local_args, "reconnect", "sleep.py"
    )
    tests.job_cases.test_reconnect(local_plugin, protocol, job_params)
    shutil.rmtree(work_dir)
