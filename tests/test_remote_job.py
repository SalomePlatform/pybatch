import typing
from pathlib import Path
import tempfile
import os
import shutil

import pybatch
import pybatch.protocols.paramiko
import pybatch.protocols.ssh
import pybatch.tools

def create_launch_parameters(config:dict[str, typing.Any]
                             ) -> pybatch.LaunchParameters:
    params = pybatch.LaunchParameters([], config["work_dir"])
    if "wckey" in config:
        params.wckey = config["wckey"]
    if "is_posix" in config:
        params.is_posix = config["is_posix"]
    return params


def create_protocol(protocol_name:str, config:dict[str, typing.Any]
                    ) -> pybatch.GenericProtocol:
    params = pybatch.ConnexionParameters(config["host"])
    if "user" in config:
        params.user = config["user"]
    if "password" in config:
        params.password = config["password"]
    if "gss_auth" in config:
        params.gss_auth = config["gss_auth"]
    if protocol_name == "ssh":
        protocol = pybatch.protocols.ssh.SshProtocol(params)
    elif protocol_name == "paramiko":
        protocol = pybatch.protocols.paramiko.ParamikoProtocol(params)
    else:
        raise Exception(f"Unknown protocol {protocol_name}")
    return protocol


def test_python_script(remote_plugin:str,
                       remote_protocol:str,
                       remote_args:dict[str, typing.Any]) -> None:
    assert remote_plugin in ["nobatch", "slurm"]
    assert remote_protocol in ["ssh", "paramiko"]
    assert remote_args
    is_posix = True
    if "is_posix" in remote_args:
        is_posix = remote_args["is_posix"]
    job_params = create_launch_parameters(remote_args)
    job_params.command = ["python3", "hello.py", "world"]
    job_params.work_directory = pybatch.tools.path_join(
                                                job_params.work_directory,
                                                "python_script",
                                                remote_plugin,
                                                remote_protocol,
                                                is_posix=is_posix)
    job_params.ntasks = 1
    current_file_dir = os.path.dirname(__file__)
    script = Path(current_file_dir) / "scripts" / "hello.py"

    job_params.input_files = [script]
    protocol = create_protocol(remote_protocol, remote_args)
    job = pybatch.create_job(remote_plugin, job_params, protocol)
    job.submit()
    job.wait()
    resultdir = tempfile.mkdtemp(suffix="_pybatchtest")
    job.get(["logs"], resultdir)
    output_file = Path(resultdir) / "logs" / "output.log"
    assert output_file.read_text() == "Hello world !\n"
    shutil.rmtree(resultdir)

