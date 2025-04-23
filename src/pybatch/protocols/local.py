from __future__ import annotations
import typing
from collections.abc import Iterable
from pathlib import Path
import shutil
import subprocess
import os

from .. import PybatchException

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
            f"Copy error. Path {src} is neither a file, nor a directory."
        )

class LocalProtocol():
    "Protocol for localhost."
    def __init__(self, params:typing.Any=None):
        pass
    def __enter__(self):# type: ignore
        return self
    def __exit__(self, _type, _value, _traceback):# type: ignore
        pass


    def open(self)->None:
        "Open session."
        pass


    def close(self)->None:
        "Close session."
        pass


    def upload(self,
               local_entries:Iterable[str|Path],
               remote_path:str
               )->None:
        for entry in local_entries:
            copy(entry, remote_path)


    def download(self,
                 remote_entries:Iterable[str],
                 local_path: str|Path
                )-> None:
        for entry in remote_entries:
            copy(entry, local_path)


    def create(self, remote_path:str, content:str) -> None:
        Path(remote_path).write_text(content)


    def run(self, command:list[str]) -> str:
        proc = subprocess.run(command, capture_output=True, text=True,
                              check=True)
        ret_code = proc.returncode
        if ret_code != 0 :
            message = f"""Error {ret_code}.
  command: {command}.
  stderr: {proc.stderr}
"""
            raise PybatchException(message)
        return proc.stdout


def open() -> LocalProtocol:
    return LocalProtocol()
