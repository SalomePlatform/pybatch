import paramiko
import scp
from ..parameter import ConnexionParameters
from .. import PybatchException

class ParamikoProtocol():
    def __init__(self, params:ConnexionParameters):
        client = paramiko.client.SSHClient()
        client.load_system_host_keys()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.client = client
        self.params = params

    def __enter__(self):
        self.client.connect(self.params.host, username=self.params.user,
                            password=self.params.password,
                            gss_auth=self.params.gss_auth)
        return self

    def __exit__(self, type, value, traceback):
        self.client.close()

    def upload(self, local_entries, remote_path):
        with scp.SCPClient(self.client.get_transport()) as client:
            for entry in local_entries:
                client.put(entry, remote_path, recursive=True)

    def download(self, remote_entries, local_path):
        with scp.SCPClient(self.client.get_transport()) as client:
            for entry in remote_entries:
                client.get(entry, local_path, recursive=True)

    def create(self, remote_path, content):
        with self.client.open_sftp() as sftp:
            with sftp.open(remote_path, "w") as remote_file:
                remote_file.write(content)

    def run(self, command):
        # in case of issues with big stdout|stderr see
        # https://github.com/paramiko/paramiko/issues/563
        str_command = command[0]
        for arg in command[1:] :
            if " " in arg:
                str_command += ' "' + arg + '"'
            else:
                str_command += ' ' + arg
        stdin, stdout, stderr = self.client.exec_command(str_command)
        stdin.close()
        str_std = stdout.read().decode()
        str_err = stderr.read().decode()
        stdout.close()
        stderr.close()
        ret_code = stdout.channel.recv_exit_status()
        if ret_code != 0 :
            message = f"""Error {ret_code}.
  command: {str_command}
  server: {self.params.host}
  stderr: {str_err}
"""
            raise PybatchException(message)
        return str_std
