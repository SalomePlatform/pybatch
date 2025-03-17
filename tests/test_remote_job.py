def test_python_script(remote_plugin, remote_protocol, remote_args):
    assert remote_plugin in ["nobatch", "slurm"]
    assert remote_protocol in ["ssh", "paramiko"]
    assert remote_args is not None
