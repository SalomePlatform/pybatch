from __future__ import annotations
from collections.abc import Iterable
from pathlib import Path
from ..parameter import ConnectionParameters
from ..tools import run_check, escape_str
from .. import PybatchException


class SshProtocol:
    def __init__(self, params: ConnectionParameters):
        self._host = params.host
        self._user = params.user
        self._password = params.password  # TODO not supported yet
        self._gss_auth = params.gss_auth

    def __enter__(self):  # type: ignore
        return self

    def __exit__(self, _type, _value, _traceback):  # type: ignore
        pass

    def open(self) -> None:
        "Open session."
        pass

    def close(self) -> None:
        "Close session."
        pass

    def upload(
        self, local_entries: Iterable[str | Path], remote_path: str
    ) -> None:
        # conversion Path to str for mypy
        full_command = ["scp", "-r"] + list(str(x) for x in local_entries)
        destination = ""
        if self._user:
            destination += self._user + "@"
        destination += self._host + ':"' + remote_path + '"'
        full_command.append(destination)
        run_check(full_command)

    def download(
        self, remote_entries: Iterable[str], local_path: str | Path
    ) -> None:
        command = ["scp", "-r"]
        remote_id = ""
        if self._user:
            remote_id += self._user + "@"
        remote_id += self._host + ":"
        for entry in remote_entries:
            full_command = command + [
                remote_id + '"' + entry + '"',
                str(local_path),
            ]
            run_check(full_command)

    def create(self, remote_path: str, content: str) -> None:
        full_command = ["ssh", "-T", self._host]
        if self._user:
            full_command += ["-l", self._user]
        if self._gss_auth:
            full_command.append("-K")
        full_command.append(f"cat > '{remote_path}'")
        run_check(full_command, input=content)

    def read(self, remote_path: str) -> str:
        full_command = ["ssh", self._host]
        if self._user:
            full_command += ["-l", self._user]
        if self._gss_auth:
            full_command.append("-K")
        full_command.append(f"cat '{remote_path}'")
        proc = run_check(full_command)
        return proc.stdout

    def run(self, command: list[str]) -> str:
        if len(command) == 0:
            raise PybatchException("Empty command.")
        full_command = ["ssh", self._host]
        if self._user:
            full_command += ["-l", self._user]
        if self._gss_auth:
            full_command.append("-K")
        full_command.append(command[0])
        for arg in command[1:]:
            full_command.append(escape_str(arg))
        proc = run_check(full_command)
        return proc.stdout


def open(params: ConnectionParameters) -> SshProtocol:
    return SshProtocol(params)
