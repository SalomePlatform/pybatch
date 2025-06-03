from __future__ import annotations
import typing

from ... import GenericJob, LaunchParameters, PybatchException
from ...tools import slurm_time_to_seconds
from pathlib import Path
import shutil
import subprocess
import psutil
import json
import os


def copy(src: str | Path, dest: str | Path) -> None:
    """Recursively copy files and directories."""
    if os.path.isfile(src):
        shutil.copy(src, dest)
    elif os.path.isdir(src):
        src_basename = os.path.basename(src)
        dest_dir = Path(dest) / src_basename
        shutil.copytree(src, dest_dir, dirs_exist_ok=True)
    else:
        raise PybatchException(
            f"Path {src} is neither a file, nor a directory."
        )


class Job(GenericJob):
    def __init__(self, param: LaunchParameters):
        self.command = param.command
        self.work_directory = param.work_directory
        self.input_files = param.input_files
        self.wall_time = slurm_time_to_seconds(param.wall_time)
        self.pid = -1  # job not launched
        self.ntasks = 0
        if param.create_nodefile:
            self.ntasks = param.ntasks
        # TODO We could also use ntasks and mem_per_node to set
        # limits using resource module.

    def submit(self) -> None:
        """Submit the job to the batch manager and return.

        If the submission fails, raise an exception.
        """
        Path(self.work_directory).mkdir(parents=True, exist_ok=True)
        for fi in self.input_files:
            copy(fi, self.work_directory)
        config = self.config()
        config_path = Path(self.work_directory) / "pybatch_conf.json"
        with open(config_path, "w") as config_file:
            json.dump(config, config_file)
        proc = subprocess.Popen(["pybatch_run", config_path])
        self.pid = proc.pid

    def wait(self) -> None:
        "Wait until the end of the job."
        if self.pid > 0:
            try:
                pu = psutil.Process(self.pid)
                pu.wait()
            except psutil.NoSuchProcess:
                pass

    def state(self) -> str:
        """Possible states : 'CREATED', 'IN_PROCESS', 'QUEUED', 'RUNNING',
        'PAUSED', 'FINISHED', 'FAILED'
        """
        if self.pid == -1:
            return "CREATED"
        if psutil.pid_exists(self.pid):
            return "RUNNING"
        else:
            exit_log = Path(self.work_directory) / "logs" / "exit_code.log"
            if exit_log.is_file():
                exit_value = exit_log.read_text()
                if exit_value == "0":
                    return "FINISHED"
                else:
                    return "FAILED"
            else:
                return "FAILED"

    def exit_code(self) -> int | None:
        exit_log = Path(self.work_directory) / "logs" / "exit_code.log"
        result = None
        try:
            if exit_log.is_file():
                exit_value = exit_log.read_text().strip()
                result = int(exit_value)
        except Exception:
            result = None
        return result

    def cancel(self) -> None:
        "Stop the job."
        pu = psutil.Process(self.pid)
        pu.terminate()

    def get(self, remote_paths: list[str], local_path: str | Path) -> None:
        """Copy a file or directory from the remote work directory.

        :param remote_path: path relative to work directory on the remote host.
        :param local_path: destination of the copy on local file system.
        """
        for path in remote_paths:
            if os.path.isabs(path):
                abs_remote_path = path
            else:
                tmp_path = Path(self.work_directory) / path
                abs_remote_path = os.path.realpath(tmp_path)
            copy(abs_remote_path, local_path)

    def config(self) -> dict[str, typing.Any]:
        cfg: dict[str, typing.Any] = {
            "command": self.command,
        }
        if self.wall_time:
            cfg["wall_time"] = self.wall_time
        if self.ntasks > 0:
            cfg["ntasks"] = self.ntasks
        return cfg

    def batch_file(self) -> str:
        "Get the content of the batch file submited to the batch manager."
        return json.dumps(self.config())

    # A réfléchir, mais il vaut peut-être mieux utiliser la sérialisation
    # pickle.
    # def dump(self) -> str:
    # " Serialization of the job."
    # ...
