import paramiko
import scp
from ..parameter import ConnexionParameters

class ParamikoProtocol():
    def __init__(self, params:ConnexionParameters):
        client = paramiko.client.SSHClient()
        client.load_system_host_keys()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(params.host, username=params.user,
                       password=params.password, gss_auth=params.gss_auth)
        self.client = client
    def __enter__(self):
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

    def run(self, command):
        # in case of issues with big stdout|stderr see
        # https://github.com/paramiko/paramiko/issues/563
        stdin, stdout, stderr = self.client.exec_command(command)
        stdin.close()
        str_std = stdout.read().decode()
        str_err = stderr.read().decode()
        stdout.close()
        stderr.close()
        ret_code = stdout.channel.recv_exit_status()
        return ret_code, str_std, str_err
