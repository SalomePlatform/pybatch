from __future__ import annotations
import typing


class GenericJob(typing.Protocol):
    "Job protocol to be implemented."

    def submit(self) -> None:
        """Submit the job to the batch manager and return.

        If the submission fails, raise an exception.
        """
        ...

    def wait(self) -> None:
        "Wait until the end of the job."
        ...

    def state(self) -> str:
        """Possible states : 'CREATED', 'IN_PROCESS', 'QUEUED', 'RUNNING',
        'PAUSED', 'FINISHED', 'FAILED'
        """
        ...

    def exit_code(self) -> int | None:
        """Get the exit code of the command if any.
        If the code is not found, for instance when the job is neither FINISHED
        nor FAILED, return None.
        """
        ...

    def cancel(self) -> None:
        "Stop the job."
        ...

    def get(self, remote_path: list[str], local_path: str) -> None:
        """Copy files from the remote work directory.

        :param remote_paths: paths relative to work directory on remote host.
        :param local_path: destination of the copy on local file system.
        """
        ...

    def batch_file(self) -> str:
        "Get the content of the batch file submited to the batch manager."
        ...

    def stdout(self) -> str:
        "Standard output of the job."
        ...

    def stderr(self) -> str:
        "Standard error of the job."
        ...

    # A réfléchir, mais il vaut peut-être mieux d'utiliser la sérialisation
    # pickle.
    def dump(self) -> str:
        "Serialization of the job in a humanly readable format."
        ...
