from __future__ import annotations
import typing
from pathlib import Path
import time

from pybatch import GenericJob, GenericProtocol, LaunchParameters
from pybatch import PybatchException
from pybatch.protocols.local import LocalProtocol

from pybatch.tools import path_join, is_absolute


def simplified_state(name:str) -> str:
    finished_states = ["COMPLETED"]
    running_states = ["CONFIGURI", "RUNNING"]
    queued_states = ["PENDING"]
    paused_states = ["RESV_DEL_", "REQUEUE", "RESIZING", "SUSPENDED"]
    failed_states = ["BOOT_FAIL", "CANCELLED", "DEADLINE", "FAILED",
                     "NODE_FAIL", "OUT_OF_ME", "PREEMPTED", "REVOKED",
                     "SIGNALING", "SPECIAL_E", "STAGE_OUT", "STOPPED",
                     "TIMEOUT"]
    for state in finished_states:
        if name.startswith(state):
            return "FINISHED"
    for state in running_states:
        if name.startswith(state):
            return "RUNNING"
    for state in queued_states:
        if name.startswith(state):
            return "QUEUED"
    for state in paused_states:
        if name.startswith(state):
            return "PAUSED"
    for state in failed_states:
        if name.startswith(state):
            return "FAILED"
    return ""

class Job(GenericJob):
    def __init__(self, param: LaunchParameters, protocol: GenericProtocol):
        self.job_params = param
        if protocol is None:
            self.protocol = LocalProtocol()
        else:
            self.protocol = protocol
        self.jobid = ""

    def submit(self) -> None:
        """Submit the job to the batch manager and return.

        If the submission fails, raise an exception.
        """
        with self.protocol as protocol :
            try:
                # create remote workdir
                # workdir is always a linux path
                logdir = path_join(self.job_params.work_directory, "logs",
                                   is_posix=True)
                command = ["mkdir", "-p", logdir]
                protocol.run(command)

                batch_path = path_join(self.job_params.work_directory,
                                       "batch.cmd", is_posix=True)
                protocol.create(batch_path, self.batch_file())
                protocol.upload(self.job_params.input_files,
                                self.job_params.work_directory)
                output = protocol.run(["sbatch", "--parsable",
                                       "--chdir", self.job_params.work_directory,
                                       batch_path])
                self.jobid = output.split(";")[0].strip()
                int(self.jobid) # check
            except Exception as e:
                message = "Failed to submit job."
                raise PybatchException(message) from e


    def wait(self) -> None:
        "Wait until the end of the job."
        if not self.jobid :
            return
        state = self.state()
        while state != "FINISHED" and state != "FAILED":
            time.sleep(1)
            state = self.state()

    def state(self) -> str:
        """Possible states : 'CREATED', 'QUEUED', 'RUNNING',
        'PAUSED', 'FINISHED', 'FAILED'
        """
        if not self.jobid :
            return 'CREATED'
        try:
            with self.protocol as protocol :
                # First try to query the job with "squeue" command
                command = ["squeue", "-h", "-o", "%T", "-j", self.jobid]
                output = protocol.run(command)
                state = simplified_state(output)
                squeue_state = state
                if state:
                    return state

                # If "squeue" failed, the job may be finished.
                # In this case, try to query the job with "sacct".
                command = ["sacct", "-X", "-o", "State%-10", "-n",
                           "-j", self.jobid]
                output = protocol.run(command)
                state = simplified_state(output)
                sacct_state = state
        except Exception as e:
            raise PybatchException("Failed to get the state of the job.") from e
        if state:
            return state
        else:
            raise PybatchException(f"Unknown state. squestae: {squeue_state}, sacct_state:{sacct_state}")


    def cancel(self) -> None:
        "Stop the job."
        if not self.jobid :
            return
        command = ["scancel", self.jobid]
        try:
            with self.protocol as protocol :
                protocol.run(command)
        except Exception as e:
            raise PybatchException("Failed to cancel the job.") from e


    def get(self, remote_paths: list[str], local_path: str | Path) -> None:
        """Copy a file or directory from the remote work directory.

        :param remote_paths: paths relative to work directory on remote host.
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
        "Get the content of the batch file submited to the batch manager."
        batch = """#!/bin/bash -l
#SBATCH --output=logs/output.log
#SBATCH --error=logs/error.log
"""
        if self.job_params.name :
            batch += f"#SBATCH --job-name={self.job_params.name}\n"
        if self.job_params.ntasks > 0 :
            batch += f"#SBATCH --ntasks={self.job_params.ntasks}\n"
        if self.job_params.nodes > 0 :
            batch += f"#SBATCH --nodes={self.job_params.nodes}\n"
        if self.job_params.exclusive :
            batch += f"#SBATCH --exclusive\n"
        if self.job_params.wall_time :
            batch += f"#SBATCH --time={self.job_params.wall_time}\n"
        if self.job_params.mem_per_node :
            batch += f"#SBATCH --mem={self.job_params.mem_per_node}\n"
        if self.job_params.mem_per_cpu :
            batch += f"#SBATCH --mem-per-cpu={self.job_params.mem_per_cpu}\n"
        if self.job_params.queue :
            batch += f"#SBATCH --qos={self.job_params.queue}\n"
        if self.job_params.partition :
            batch += f"#SBATCH --partition={self.job_params.partition}\n"
        if self.job_params.wckey :
            batch += f"#SBATCH --wckey={self.job_params.wckey}\n"
        for extra in self.job_params.extra_as_list :
            batch += f"#SBATCH {extra}\n"
        if self.job_params.extra_as_string :
            batch += self.job_params.extra_as_string
        batch += "\n" + " ".join(self.job_params.command) + "\n"
        batch += """EXIT_CODE=$?
echo $EXIT_CODE > logs/exit_code.log
exit $EXIT_CODE
"""
        return batch

    # A réfléchir, mais il vaut peut-être mieux utiliser la sérialisation
    # pickle.
    # def dump(self) -> str:
    # " Serialization of the job."
    # ...
