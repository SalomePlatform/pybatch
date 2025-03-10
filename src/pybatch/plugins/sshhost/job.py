from __future__ import annotations
from pathlib import Path

from ... import GenericJob, GenericProtocol, LaunchParameters, PybatchException

class Job(GenericJob):
    def __init__(self, param: LaunchParameters, protocol: GenericProtocol):
        self.job_params = param
        if protocol is None:
            self.protocol = LocalProtocol()
        else:
            self.protocol = protocol
        self.jobid = ""

    def submit(self) -> None:
        with self.protocol as protocol :
            try:
                manager_script = Path(__file__) / "pybatch_manager.py"
                input_files = self.job_params.input_files + [manager_script]
                protocol.upload(input_files, self.job_params.work_directory)
                # Path separator has to be present at the end of work_directory
                # because it is OS dependent!
                # The user has to know the OS of the remote server.
                work_dir = self.job_params.work_directory
                command = ["python3", work_dir + "pybatch_manager.py"]
                command += ["submit", work_dir]
                # TODO convert from slurm formats (mm, mm:ss, h:mm:ss, etc.)
                if self.job_params.wall_time:
                    command.append(self.job_params.wall_time)
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
                work_dir = self.job_params.work_directory
                command = ["python3", work_dir + "pybatch_manager.py",
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
                work_dir = self.job_params.work_directory
                command = ["python3", work_dir + "pybatch_manager.py",
                           "state", self.jobid]
                result = protocol.run(command)
            except Exception as e:
                message = "Failed to wait job."
                raise PybatchException(message) from e
        return result

    def cancel(self) -> None:
        if not self.jobid :
            return
        with self.protocol as protocol :
            try:
                work_dir = self.job_params.work_directory
                command = ["python3", work_dir + "pybatch_manager.py",
                           "cancel", self.jobid]
                protocol.run(command)
            except Exception as e:
                message = "Failed to cancel job."
                raise PybatchException(message) from e

    def get(self, remote_path: str | Path, local_path: str | Path) -> None:
        """Copy a file or directory from the remote work directory.

        :param remote_path: path relative to work directory on the remote host.
        :param local_path: destination of the copy on local file system.
        """
        with self.protocol as protocol :
            protocol.download(remote_path, local_path)

    def batch_file(self) -> str:
        return ""
