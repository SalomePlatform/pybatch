from __future__ import annotations
from pathlib import Path
import os

from ... import GenericJob, GenericProtocol, LaunchParameters, PybatchException
from ...protocols.local import LocalProtocol
from ...tools import path_join, is_absolute

class Job(GenericJob):
    def __init__(self, param: LaunchParameters, protocol: GenericProtocol):
        self.job_params = param
        if protocol is None:
            self.protocol = LocalProtocol()
        else:
            self.protocol = protocol
        self.jobid = ""
        self.remote_manager_path = path_join(param.work_directory,
                                             "pybatch_manager.py",
                                             is_posix=param.is_posix)


    def submit(self) -> None:
        with self.protocol as protocol :
            try:
                # TODO deal with no posix
                if self.job_params.is_posix:
                    logdir = path_join(self.job_params.work_directory, "logs",
                                    is_posix=True)
                    command = ["mkdir", "-p", logdir]
                    protocol.run(command)

                file_dir = Path(os.path.dirname(__file__))
                manager_script = file_dir / "pybatch_manager.py"
                input_files = self.job_params.input_files + [manager_script]
                protocol.upload(input_files, self.job_params.work_directory)
                command = ["python3",
                           self.remote_manager_path,
                           "submit", self.job_params.work_directory]
                # TODO convert from slurm formats (mm, mm:ss, h:mm:ss, etc.)
                if self.job_params.wall_time:
                    command += ["--wall_time", self.job_params.wall_time]
                command += self.job_params.command
                self.jobid = protocol.run(command)
            except Exception as e:
                message = "Failed to submit job."
                raise PybatchException(message) from e


    def wait(self) -> None:
        "Wait until the end of the job."
        if not self.jobid :
            return
        with self.protocol as protocol :
            try:
                command = ["python3", self.remote_manager_path,
                           "wait", self.jobid]
                protocol.run(command)
            except Exception as e:
                message = "Failed to wait job."
                raise PybatchException(message) from e


    def state(self) -> str:
        if not self.jobid :
            return 'CREATED'
        with self.protocol as protocol :
            try:
                command = ["python3", self.remote_manager_path,
                           "state", self.jobid, self.job_params.work_directory]
                result = protocol.run(command).strip()

            except Exception as e:
                message = "Failed to wait job."
                raise PybatchException(message) from e
        return result

    def cancel(self) -> None:
        if not self.jobid :
            return
        with self.protocol as protocol :
            try:
                command = ["python3", self.remote_manager_path,
                           "cancel", self.jobid]
                protocol.run(command)
            except Exception as e:
                message = "Failed to cancel job."
                raise PybatchException(message) from e

    def get(self, remote_paths: list[str], local_path: str | Path) -> None:
        """Copy a file or directory from the remote work directory.

        :param remote_path: path relative to work directory on the remote host.
        :param local_path: destination of the copy on local file system.
        """
        with self.protocol as protocol :
            checked_paths = []
            for path in remote_paths:
                if is_absolute(path, self.job_params.is_posix):
                    checked_paths.append(path)
                else:
                    p = path_join(self.job_params.work_directory,
                                  path,
                                  is_posix=self.job_params.is_posix)
                    checked_paths.append(p)
            protocol.download(checked_paths, local_path)

    def batch_file(self) -> str:
        return ""
