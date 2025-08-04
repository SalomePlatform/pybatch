from __future__ import annotations
import typing
from collections.abc import Iterable
from pathlib import Path


class GenericProtocol(typing.Protocol):
    """Connection protocol (ssh, local, ...).

    This interface defines the services expected from a connection protocol.
    """

    def upload(
        self, local_entries: Iterable[str | Path], remote_path: str
    ) -> None:
        "Upload files and directories to the server."
        ...

    def download(
        self, remote_entries: Iterable[str], local_path: str | Path
    ) -> None:
        "Download files and directories from the server."
        ...

    def create(self, remote_path: str, content: str) -> None:
        "Create a file on the server."
        ...

    def read(self, remote_path: str) -> str:
        "Get the content of a file."
        ...

    def run(self, command: list[str]) -> str:
        "Run a command on the server."
        ...
