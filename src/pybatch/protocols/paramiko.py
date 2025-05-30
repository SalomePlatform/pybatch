from __future__ import annotations
from collections.abc import Iterable
from pathlib import Path
import paramiko
import scp  # type: ignore
from ..parameter import ConnectionParameters
from .. import PybatchException
from ..tools import escape_str


class ParamikoProtocol:
    def __init__(self, params: ConnectionParameters):
        client = paramiko.client.SSHClient()
        client.load_system_host_keys()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.client = client
        self.params = params

    def __enter__(self):  # type: ignore
        self.open()
        return self

    def __exit__(self, type, value, traceback):  # type: ignore
        self.close()

    def open(self) -> None:
        try:
            self.client.connect(
                self.params.host,
                username=self.params.user,
                password=self.params.password,
                gss_auth=self.params.gss_auth,
            )
        except Exception as e:
            message = f"Failed to open ssh connection to {self.params.host}."
            raise PybatchException(message) from e

    def close(self) -> None:
        "Close session."
        self.client.close()

    def upload(
        self, local_entries: Iterable[str | Path], remote_path: str
    ) -> None:
        with scp.SCPClient(self.client.get_transport()) as client:
            for entry in local_entries:
                client.put(entry, remote_path, recursive=True)

    def download(
        self, remote_entries: Iterable[str], local_path: str | Path
    ) -> None:
        with scp.SCPClient(self.client.get_transport()) as client:
            for entry in remote_entries:
                client.get(entry, local_path, recursive=True)

    def create(self, remote_path: str, content: str) -> None:
        with self.client.open_sftp() as sftp:
            with sftp.open(remote_path, "w") as remote_file:
                remote_file.write(content)

    def run(self, command: list[str]) -> str:
        # in case of issues with big stdout|stderr see
        # https://github.com/paramiko/paramiko/issues/563
        if len(command) == 0:
            raise PybatchException("Empty command.")
        str_command = command[0]
        for arg in command[1:]:
            str_command += " " + escape_str(arg)
        stdin, stdout, stderr = self.client.exec_command(str_command)
        stdin.close()
        str_std = stdout.read().decode()
        str_err = stderr.read().decode()
        stdout.close()
        stderr.close()
        ret_code = stdout.channel.recv_exit_status()
        if ret_code != 0:
            message = f"""Error {ret_code}.
  command: {str_command}
  server: {self.params.host}
  stderr: {str_err}
"""
            raise PybatchException(message)
        return str_std


def open(params: ConnectionParameters) -> ParamikoProtocol:
    return ParamikoProtocol(params)
