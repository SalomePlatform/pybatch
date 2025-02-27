from typing import Protocol

class GenericJob(Protocol):
    " Job protocol to be implemented."
    def submit(self)-> None:
        """ Submit the job to the batch manager and return.

        If the submission fails, raise an exception.
        """
        ...

    def wait(self)-> None:
        " Wait until the end of the job."
        ...

    def state(self) -> str:
        """ Possible states : 'CREATED', 'IN_PROCESS', 'QUEUED', 'RUNNING',
        'PAUSED', 'FINISHED', 'FAILED'
        """
        ...

    def cancel(self)-> None:
        " Stop the job."
        ...

    def get(self, remote_path:str, local_path:str)-> None:
        """ Copy a file from the remote work directory.

        :param remote_path: path relative to work directory on the remote host.
        :param local_path: destination of the copy on local file system.
        """
        ...

    def batch_file(self) -> str:
        " Get the content of the batch file submited to the batch manager."
        ...

    # A réfléchir, mais il vaut peut-être mieux d'utiliser la sérialisation
    # pickle.
    def dump(self) -> str:
        " Serialization of the job in a humanly readable format."
        ...
