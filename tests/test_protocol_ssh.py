import typing
import tempfile
import os
import shutil
from pathlib import Path
import pybatch
import pybatch.protocols.ssh
from pybatch.tools import path_join


def test_protocol_ssh(remote_args: dict[str, typing.Any]) -> None:
    # Test connection to a host that does not exist
    connect_param = pybatch.ConnectionParameters(host="noname_zozo")
    protocol = pybatch.protocols.ssh.SshProtocol(connect_param)
    with protocol as p:
        try:
            p.run(["python3", "-c", "exit(0)"])
        except pybatch.PybatchException as e:
            assert "noname_zozo" in str(e)
            assert (
                """command: ['ssh', 'noname_zozo', 'python3', '-c', """
                in str(e)
            )
        else:
            assert 0

    # Test configuration
    hostname = remote_args["host"]
    work_dir = remote_args["work_dir"]
    gss_auth = False
    if "gss_auth" in remote_args:
        gss_auth = remote_args["gss_auth"]
    is_posix = True
    if "is_posix" in remote_args:
        is_posix = remote_args["is_posix"]
    connect_param = pybatch.ConnectionParameters(
        host=hostname, gss_auth=gss_auth
    )
    protocol = pybatch.protocols.ssh.SshProtocol(connect_param)
    local_work_dir = tempfile.mkdtemp(suffix="_pybatchtest")
    test_file_name = "ssh_test.txt"
    remote_test_file = path_join(work_dir, test_file_name, is_posix=is_posix)
    local_test_file = os.path.join(local_work_dir, test_file_name)
    with protocol as p:
        # Test download a remote path that does not exist.
        try:
            p.download([remote_test_file], local_test_file)
        except pybatch.PybatchException as e:
            # The remote path should be included in the error message
            # but the full message may depend on the language.
            assert remote_test_file in str(e)
        else:
            assert 0

        # Test create a file in an inaccessible place
        try:
            p.create("/no/directory/", "file content")
        except pybatch.PybatchException as e:
            assert "/no/directory" in str(e)
        else:
            assert 0

        # Test create + download
        file_content = "Servus!"
        p.create(remote_test_file, file_content)
        remote_content = p.read(remote_test_file)
        assert remote_content == file_content
        p.download([remote_test_file], local_test_file)
        assert Path(local_test_file).read_text() == file_content

        # download in an inaccessible place
        local_wrong_path = os.path.join(local_work_dir, "nodir", "nofile")
        try:
            p.download([remote_test_file], local_wrong_path)
        except pybatch.PybatchException as e:
            assert local_wrong_path in str(e)
        else:
            assert 0

        # upload nonexistent file
        try:
            p.upload([local_wrong_path], work_dir)
        except pybatch.PybatchException as e:
            assert local_wrong_path in str(e)
        else:
            assert 0

        # upload file to an inaccessible place
        try:
            p.upload([local_test_file], "/no/directory/")
        except pybatch.PybatchException as e:
            assert "/no/directory/" in str(e)
        else:
            assert 0

        # upload + download + check
        name_bis = "ssh_test_bis.txt"
        remote_test_file_bis = path_join(work_dir, name_bis, is_posix=is_posix)
        local_test_file_bis = os.path.join(local_work_dir, name_bis)
        p.upload([local_test_file], remote_test_file_bis)
        p.download([remote_test_file_bis], local_test_file_bis)
        assert Path(local_test_file_bis).read_text() == file_content

        # run
        command = ["python3", "-c", 'print("Cool!")']
        res = p.run(command)
        assert res.strip() == "Cool!"

        # run error
        command = ["python3", "-c", "exit(1)"]
        try:
            res = p.run(command)
        except pybatch.PybatchException as e:
            assert "Error 1" in str(e)
        else:
            assert 0

        # remove remote files
        pycommand = f'import os; os.remove("{remote_test_file}")'
        p.run(["python3", "-c", pycommand])
        pycommand = f'import os; os.remove("{remote_test_file_bis}")'
        p.run(["python3", "-c", pycommand])

    shutil.rmtree(local_work_dir)
