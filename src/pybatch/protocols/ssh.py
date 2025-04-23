from __future__ import annotations
from collections.abc import Iterable
from pathlib import Path
import subprocess
from ..parameter import ConnexionParameters

class SshProtocol():
    def __init__(self, params:ConnexionParameters):
        self._host = params.host
        self._user = params.user
        self._password = params.password #TODO not supported yet
        self._gss_auth = params.gss_auth

    def __enter__(self): # type: ignore
        return self


    def __exit__(self, _type, _value, _traceback): # type: ignore
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
        full_command = ["scp", "-r"] + list(local_entries)
        destination = ""
        if self._user:
            destination += self._user + "@"
        destination += self._host + ':"' + remote_path + '"'
        full_command.append(destination)
        proc = subprocess.run(full_command,
                              capture_output=True,
                              text=True,
                              check=True)


    def download(self,
                 remote_entries:Iterable[str],
                 local_path: str|Path
                )-> None:
        command = ["scp", "-r"]
        remote_id = "" 
        if self._user:
            remote_id += self._user + "@"
        remote_id += self._host + ":"
        for entry in remote_entries:
            full_command = command + [remote_id + '"' + entry + '"', local_path]
            subprocess.run(full_command, capture_output=True, text=True,
                           check=True)

    def create(self, remote_path:str, content:str) -> None:
        full_command = ["ssh", "-T", self._host]
        if self._user:
            full_command += ["-l", self._user]
        if self._gss_auth:
            full_command.append("-K")
        full_command.append(f"cat > '{remote_path}'")
        subprocess.run(full_command, input=content,
                       capture_output=True, text=True, check=True)


    def run(self, command:list[str]) -> str:
        full_command = ["ssh", self._host]
        if self._user:
            full_command += ["-l", self._user]
        if self._gss_auth:
            full_command.append("-K")
        full_command += command
        proc = subprocess.run(full_command,
                              capture_output=True, text=True, check=True)
        return proc.stdout


def open(params:ConnexionParameters) -> SshProtocol:
    return SshProtocol(params)
