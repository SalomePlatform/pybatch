import typing

class GenericProtocol(typing.Protocol):
    "Connection protocol (ssh, local, ...)."
    def __enter__(self):
        "Implement context manager pattern."
        ...
    def __exit__(self, _type, _value, _traceback):
        ...


    def upload(self, local_entries, remote_path):
        "Upload files and directories to the server."
        ...


    def download(self, remote_entries, local_path):
        "Download files and directories from the server."
        ...


    def create(self, remote_path, content):
        "Create a file on the server."
        ...

    def run(self, command):
        "Run a command on the server."
        ...

