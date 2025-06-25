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


def test_nodefile(
    plugin: str,
    protocol: pybatch.GenericProtocol,
    job_params: pybatch.LaunchParameters,
) -> None:
    job_params.ntasks = 4
    job_params.create_nodefile = True
    job_params.command = ["python3", "check_nodefile.py", "4"]
    job = pybatch.create_job(plugin, job_params, protocol)
    job.submit()
    job.wait()
    state = job.state()
    assert state == "FINISHED"
    resultdir = tempfile.mkdtemp(suffix="_pybatchtest")
    job.get(["batch_nodefile.txt"], resultdir)
    result_file = Path(resultdir) / "batch_nodefile.txt"
    assert result_file.exists()
    shutil.rmtree(resultdir)


def test_reconnect(
    plugin: str,
    protocol: pybatch.GenericProtocol,
    job_params: pybatch.LaunchParameters,
) -> None:
    job_params.command = ["python3", "sleep.py", "10"]
    job = pybatch.create_job(plugin, job_params, protocol)
    job.submit()
    import pickle

    dumps = pickle.dumps(job)
    new_job = pickle.loads(dumps)
    state = new_job.state()
    assert state in ["RUNNING", "QUEUED"]
    new_job.wait()
    state = new_job.state()
    assert state == "FINISHED"
    resultdir = tempfile.mkdtemp(suffix="_pybatchtest")
    new_job.get(["wakeup.txt"], resultdir)
    result_file = Path(resultdir) / "wakeup.txt"
    assert result_file.exists()
    shutil.rmtree(resultdir)
