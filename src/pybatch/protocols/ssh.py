import subprocess
from ..parameter import ConnexionParameters

class SshProtocol():
    def __init__(self, params:ConnexionParameters):
        self._host = params.host
        self._user = params.user
        self._password = params.password
        self._gss_auth = params.gss_auth

    def __enter__(self):
        return self


    def __exit__(self, _type, _value, _traceback):
        pass


    def upload(self, local_entries, remote_path):
        full_command = ["scp", "-r"] + local_entries
        destination = ""
        if self._user:
            destination += self._user + "@"
        destination += self._host + ':"' + remote_path + '"'
        full_command.append(destination)
        proc = subprocess.run(full_command,
                              capture_output=True,
                              text=True,
                              check=True)


    def download(self, remote_entries, local_path):
        command = ["scp", "-r"]
        remote_id = "" 
        if self._user:
            remote_id += self._user + "@"
        remote_id += self._host + ":"
        for entry in remote_entries:
            full_command = command + [remote_id + '"' + entry + '"', local_path]
            proc = subprocess.run(full_command,
                                  capture_output=True,
                                  text=True,
                                  check=True)


    def run(self, command):
        full_command = ["ssh", self._host]
        if self._user:
            full_command += ["-l", self._user]
        if self._gss_auth:
            full_command.append("-K")
        full_command += command
        proc = subprocess.run(full_command, capture_output=True, text=True)
        return proc.returncode, proc.stdout, proc.stderr
