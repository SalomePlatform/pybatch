import tempfile
import os
import shutil
from pathlib import Path
import pybatch
import pybatch.protocols.local


def test_protocol_local() -> None:
    # Test configuration
    test_dir = tempfile.mkdtemp(suffix="_pybatchtest")
    work_dir = os.path.join(test_dir, "remote_dir")
    local_work_dir = os.path.join(test_dir, "local_dir")
    os.mkdir(work_dir)
    os.mkdir(local_work_dir)
    p = pybatch.protocols.local.LocalProtocol()
    test_file_name = "local_test.txt"
    remote_test_file = os.path.join(work_dir, test_file_name)
    local_test_file = os.path.join(local_work_dir, test_file_name)
    # Test download a remote path that does not exist.
    try:
        p.download([remote_test_file], local_test_file)
    except pybatch.PybatchException as e:
        assert remote_test_file in str(e)
    else:
        assert 0

    ## Test create a file in an inaccessible place
    try:
        p.create("/no/directory/", "file content")
    except FileNotFoundError as e:
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
    except FileNotFoundError as e:
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
    except FileNotFoundError as e:
        assert "/no/directory/" in str(e)
    else:
        assert 0

    # upload + download + check
    name_bis = "local_test_bis.txt"
    remote_test_file_bis = os.path.join(work_dir, name_bis)
    local_test_file_bis = os.path.join(local_work_dir, name_bis)
    p.upload([local_test_file], remote_test_file_bis)
    assert Path(remote_test_file_bis).read_text() == file_content
    p.download([remote_test_file_bis], local_test_file_bis)
    assert Path(local_test_file_bis).read_text() == file_content

    # run
    command = ["python3", "-c", 'print("Cool!")']
    res = p.run(command)
    assert res.strip() == "Cool!"

    ## run error
    command = ["python3", "-c", "exit(1)"]
    try:
        res = p.run(command)
    except pybatch.PybatchException as e:
        assert "Error 1" in str(e)
    else:
        assert 0

    shutil.rmtree(test_dir)
