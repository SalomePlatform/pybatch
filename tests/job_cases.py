from pathlib import Path
import tempfile
import shutil

import pybatch


def test_hello(
    plugin: str,
    protocol: pybatch.GenericProtocol,
    job_params: pybatch.LaunchParameters,
) -> None:
    job_params.command = ["python3", "hello.py", "world"]
    job = pybatch.create_job(plugin, job_params, protocol)
    job.submit()
    job.wait()
    state = job.state()
    assert state == "FINISHED"
    resultdir = tempfile.mkdtemp(suffix="_pybatchtest")
    job.get(["logs"], resultdir)
    output_file = Path(resultdir) / "logs" / "output.log"
    assert output_file.read_text() == "Hello world !\n"
    shutil.rmtree(resultdir)


def test_sleep(
    plugin: str,
    protocol: pybatch.GenericProtocol,
    job_params: pybatch.LaunchParameters,
) -> None:
    job_params.command = ["python3", "sleep.py", "10"]
    job = pybatch.create_job(plugin, job_params, protocol)
    job.submit()

    state = job.state()
    assert state in ["RUNNING", "QUEUED"]
    job.wait()
    state = job.state()
    assert state == "FINISHED"
    resultdir = tempfile.mkdtemp(suffix="_pybatchtest")
    job.get(["wakeup.txt"], resultdir)
    result_file = Path(resultdir) / "wakeup.txt"
    assert result_file.exists()
    shutil.rmtree(resultdir)


def test_cancel(
    plugin: str,
    protocol: pybatch.GenericProtocol,
    job_params: pybatch.LaunchParameters,
) -> None:
    job_params.command = ["python3", "sleep.py", "10"]
    job = pybatch.create_job(plugin, job_params, protocol)
    job.submit()

    state = job.state()
    assert state in ["RUNNING", "QUEUED"]
    job.cancel()
    job.wait()
    state = job.state()
    assert state == "FAILED"
    resultdir = tempfile.mkdtemp(suffix="_pybatchtest")
    job.get(["."], resultdir)
    result_file = Path(resultdir) / "wakeup.txt"
    assert not result_file.exists()
    shutil.rmtree(resultdir)


def test_error(
    plugin: str,
    protocol: pybatch.GenericProtocol,
    job_params: pybatch.LaunchParameters,
) -> None:
    job_params.command = ["python3", "error.py"]
    job = pybatch.create_job(plugin, job_params, protocol)
    job.submit()
    job.wait()
    state = job.state()
    assert state == "FAILED"
