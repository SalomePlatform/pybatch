import tempfile
from pathlib import Path
import os
import shutil


def test_python_script():
    """Launch a python script which ends without errors.

    Check files from 'logs' folder.
    """
    import pybatch

    workdir = tempfile.mkdtemp(suffix="_pybatchtest")
    current_file_dir = os.path.dirname(__file__)
    script = Path(current_file_dir) / "scripts" / "hello.py"
    params = pybatch.LaunchParameters(
        ["python3", "hello.py", "world"], workdir, input_files=[script]
    )
    job = pybatch.create_job("local", params)
    job.submit()
    job.wait()

    output_file = Path(workdir) / "logs" / "output.log"
    assert output_file.read_text() == "Hello world !\n"
    error_file = Path(workdir) / "logs" / "error.log"
    assert not error_file.read_text()  # empty file expected
    exit_code = Path(workdir) / "logs" / "exit_code.log"
    assert exit_code.read_text() == "0"
    shutil.rmtree(workdir)


def test_error_script():
    """Launch a python script which ends in error.

    Check files from 'logs' folder.
    """
    import pybatch

    workdir = tempfile.mkdtemp(suffix="_pybatchtest")
    current_file_dir = os.path.dirname(__file__)
    script = Path(current_file_dir) / "scripts" / "error.py"
    params = pybatch.LaunchParameters(
        ["python3", "error.py"], workdir, input_files=[script]
    )
    job = pybatch.create_job("local", params)
    job.submit()
    job.wait()

    output_file = Path(workdir) / "logs" / "output.log"
    assert output_file.read_text() == "Problems comming...\n"
    error_file = Path(workdir) / "logs" / "error.log"
    assert "Oups!" in error_file.read_text()
    exit_code = Path(workdir) / "logs" / "exit_code.log"
    assert exit_code.read_text() == "1"
    shutil.rmtree(workdir)


def test_state():
    """Test the state of a job."""
    import pybatch

    workdir = tempfile.mkdtemp(suffix="_pybatchtest")
    current_file_dir = os.path.dirname(__file__)
    script = Path(current_file_dir) / "scripts" / "sleep.py"
    params = pybatch.LaunchParameters(
        ["python3", "sleep.py", "1"], workdir, input_files=[script]
    )
    job = pybatch.create_job("local", params)
    assert job.state() == "CREATED"
    job.submit()
    assert job.state() == "RUNNING"
    job.wait()
    assert job.state() == "FINISHED"
    exit_code = Path(workdir) / "logs" / "exit_code.log"
    assert exit_code.read_text() == "0"
    assert (Path(workdir) / "wakeup.txt").exists()
    shutil.rmtree(workdir)


def test_cancel():
    """Cancel a running job."""
    import pybatch
    import time

    workdir = tempfile.mkdtemp(suffix="_pybatchtest")
    current_file_dir = os.path.dirname(__file__)
    script = Path(current_file_dir) / "scripts" / "sleep.py"
    params = pybatch.LaunchParameters(
        ["python3", "sleep.py", "2"], workdir, input_files=[script]
    )
    job = pybatch.create_job("local", params)
    assert job.state() == "CREATED"
    job.submit()
    time.sleep(1)
    job.cancel()
    job.wait()
    time.sleep(2)  # sleep.py would have had the time to finish if not canceled.
    assert not (Path(workdir) / "wakeup.txt").exists()
    exit_code = Path(workdir) / "logs" / "exit_code.log"
    # assert not exit_code.exists() or exit_code.read_text() != "0"
    assert exit_code.read_text() == "-15"  # not sure for Windows
    shutil.rmtree(workdir)


def test_serialization():
    """Serialization / deserialization of a submited job in the same script."""
    import pybatch
    import pickle

    workdir = tempfile.mkdtemp(suffix="_pybatchtest")
    current_file_dir = os.path.dirname(__file__)
    script = Path(current_file_dir) / "scripts" / "sleep.py"
    params = pybatch.LaunchParameters(
        ["python3", "sleep.py", "1"], workdir, input_files=[script]
    )
    job = pybatch.create_job("local", params)
    job.submit()
    pick_job = pickle.dumps(job)
    new_job = pickle.loads(pick_job)
    assert new_job.state() == "RUNNING"
    new_job.wait()
    assert new_job.state() == "FINISHED"
    shutil.rmtree(workdir)


def test_wall_time():
    """Job with wall time."""
    import pybatch

    workdir = tempfile.mkdtemp(suffix="_pybatchtest")
    current_file_dir = os.path.dirname(__file__)
    script = Path(current_file_dir) / "scripts" / "sleep.py"
    params = pybatch.LaunchParameters(
        ["python3", "sleep.py", "3"],
        workdir,
        input_files=[script],
        wall_time="1",
    )
    job = pybatch.create_job("local", params)
    job.submit()
    job.wait()
    assert not (Path(workdir) / "wakeup.txt").exists()
    exit_code = Path(workdir) / "logs" / "exit_code.log"
    # assert not exit_code.exists() or exit_code.read_text() != "0"
    assert exit_code.read_text() == "-15"  # not sure for Windows
    shutil.rmtree(workdir)


def test_files_and_directories():
    """Job that uses and produces files and directories."""
    import pybatch

    workdir = tempfile.mkdtemp(suffix="_pybatchtest")
    resultdir = tempfile.mkdtemp(suffix="_pybatchtest")
    current_file_dir = os.path.dirname(__file__)
    script = Path(current_file_dir) / "scripts" / "code.py"
    file_input = Path(current_file_dir) / "data" / "input.txt"
    dir_input = Path(current_file_dir) / "data" / "data"
    params = pybatch.LaunchParameters(
        ["python3", "code.py", "1"],
        workdir,
        input_files=[script, file_input, dir_input],
    )
    job = pybatch.create_job("local", params)
    job.submit()
    job.wait()
    error_file = Path(workdir) / "logs" / "error.log"
    assert not error_file.read_text()  # empty file expected
    exit_code = Path(workdir) / "logs" / "exit_code.log"
    assert exit_code.read_text() == "0"
    job.get("output.txt", resultdir)
    assert (Path(resultdir) / "output.txt").read_text() == "51"
    job.get("data", resultdir)
    assert (Path(resultdir) / "data" / "output.txt").read_text() == "69"
    shutil.rmtree(workdir)
    shutil.rmtree(resultdir)
