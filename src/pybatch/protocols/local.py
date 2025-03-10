from __future__ import annotations
import typing

from pathlib import Path
import shutil
import subprocess
import os

from ..parameter import ConnexionParameters
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
    def __init__(self, host=None, user=None, password=None, gss_auth=False):
        pass
    def __enter__(self):
        return self
    def __exit__(self, _type, _value, _traceback):
        pass


    def open(self):
        "Open session."
        pass


    def close(self):
        "Close session."
        pass


    def upload(self, local_entries, remote_path):
        for entry in local_entries:
            copy(entry, remote_path)


    def download(self, remote_entries, local_path):
        for entry in remote_entries:
            copy(entry, local_path)


    def create(self, remote_path, content):
        Path(remote_path).write_text(content)


    def run(self, command):
        proc = subprocess.run(command, capture_output=True, text=True)
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
