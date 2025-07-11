from __future__ import annotations
import typing
from typing import Optional
from types import FrameType

from ... import GenericJob, LaunchParameters, PybatchException
from ...tools import slurm_time_to_seconds
from pathlib import Path
import shutil
import subprocess
import psutil
import json
import os
import signal
import socket
import functools


def handler(
    proc: subprocess.Popen[bytes], signum: int, frame: Optional[FrameType]
) -> None:
    proc.terminate()


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
        seconds_str = slurm_time_to_seconds(param.wall_time)
        if not seconds_str:
            self.wall_time = None
        else:
            self.wall_time = int(seconds_str)
        self.pid = -1  # job not launched
        self.ntasks = 0
        if param.create_nodefile:
            self.ntasks = param.ntasks
        # TODO We could also use ntasks and mem_per_node to set
        # limits using resource module.

    def submit(self) -> None:
        """Submit the job to the batch manager and return.

        The command is executed in a process detached from the current one, in
        a daemon mode.
        """
        self._prepare_run()
        r_pipe, w_pipe = os.pipe()
        pid = os.fork()
        if pid > 0:
            # father side - get pid of the grand child
            self.pid = int(os.fdopen(r_pipe).readline().strip())
            return
        # double fork for daemon creation
        try:
            pid = os.fork()
            if pid > 0:
                # child side
                try:
                    os.write(w_pipe, f"{pid}\n".encode())
                finally:
                    os._exit(0)  # ensure child ends here!
            # actual daemon
            self._run()
        finally:
            os._exit(0)  # ensure grand child ends here!

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

    def stdout(self) -> str:
        output_file = Path(self.work_directory, "logs", "output.log")
        return output_file.read_text()

    def stderr(self) -> str:
        output_file = Path(self.work_directory, "logs", "error.log")
        return output_file.read_text()

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

    def _prepare_run(self) -> None:
        Path(self.work_directory).mkdir(parents=True, exist_ok=True)
        for fi in self.input_files:
            copy(fi, self.work_directory)
        if self.ntasks > 0:
            nodelist = (socket.gethostname() + "\n") * self.ntasks
            nodefile = Path(self.work_directory) / "batch_nodefile.txt"
            nodefile.write_text(nodelist)
        log_path = Path(self.work_directory) / "logs"
        log_path.mkdir(parents=True, exist_ok=True)

    def _run(self) -> None:
        # daemonize process
        os.setsid()
        signal.signal(signal.SIGHUP, signal.SIG_IGN)

        log_path = Path(self.work_directory) / "logs"
        stdout_log = log_path / "output.log"
        stderr_log = log_path / "error.log"
        # file descriptors are automaticaly closed by default
        # (see close_fds argument of Popen).
        stdout_file = open(stdout_log, "w")
        stderr_file = open(stderr_log, "w")
        proc = subprocess.Popen(
            self.command,
            cwd=self.work_directory,
            stdout=stdout_file,
            stderr=stderr_file,
        )
        signal.signal(signal.SIGTERM, functools.partial(handler, proc))
        try:
            exit_code = proc.wait(self.wall_time)
        except subprocess.TimeoutExpired:
            proc.terminate()
            exit_code = proc.wait()
        exit_log = log_path / "exit_code.log"
        with open(exit_log, "w") as exit_file:
            exit_file.write(str(exit_code))

    # A réfléchir, mais il vaut peut-être mieux utiliser la sérialisation
    # pickle.
    # def dump(self) -> str:
    # " Serialization of the job."
    # ...
