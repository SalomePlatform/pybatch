import typing
import tempfile
import os
import shutil
from pathlib import Path


def test_protocol_paramiko(remote_args: dict[str, typing.Any]) -> None:
    import pybatch
    import pybatch.protocols.paramiko
    from pybatch.tools import path_join
    import scp

    # Test connection to a host that does not exist
    connect_param = pybatch.ConnectionParameters(host="noname_zozo")
    protocol = pybatch.protocols.paramiko.ParamikoProtocol(connect_param)
    try:
        protocol.open()
    except pybatch.PybatchException as e:
        assert str(e) == "Failed to open ssh connection to noname_zozo."
    else:
        assert 0  # Exception expected
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
    protocol = pybatch.protocols.paramiko.ParamikoProtocol(connect_param)
    local_work_dir = tempfile.mkdtemp(suffix="_pybatchtest")
    test_file_name = "paramiko_test.txt"
    remote_test_file = path_join(work_dir, test_file_name, is_posix=is_posix)
    local_test_file = os.path.join(local_work_dir, test_file_name)
    with protocol as p:
        # Test download a remote path that does not exist.
        try:
            p.download([remote_test_file], local_test_file)
        except scp.SCPException as e:
            # The remote path should be included in the error message
            # but the full message may depend on the language.
            assert remote_test_file in str(e)
        else:
            assert 0

        # Test create a file in an inaccessible place
        try:
            p.create("/no/directory/", "file content")
        except FileNotFoundError:
            pass
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
        except FileNotFoundError:
            pass
        else:
            assert 0

        # upload nonexistent file
        try:
            p.upload([local_wrong_path], work_dir)
        except FileNotFoundError as e:
            assert local_wrong_path in str(e)
        else:
            assert 0

        # upload file to an inaccessible place
        try:
            p.upload([local_test_file], "/no/directory/")
        except scp.SCPException as e:
            assert "/no/directory/" in str(e)
        else:
            assert 0

        # upload + download + check
        name_bis = "paramiko_test_bis.txt"
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
            assert "command: python3 -c 'exit(1)'" in str(e)
        else:
            assert 0

    shutil.rmtree(local_work_dir)
