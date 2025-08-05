# Copyright (C) 2025  CEA, EDF
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307 USA
#
# See http://www.salome-platform.org/ or email : webmaster.salome@opencascade.com
#
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
    assert "Hello world !" in job.stdout()
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


def test_array(
    plugin: str,
    protocol: pybatch.GenericProtocol,
    job_params: pybatch.LaunchParameters,
) -> None:
    "Test of a job array without errors."
    job_params.command = ["python3", "array.py"]
    job_params.total_jobs = 4
    job_params.max_simul_jobs = 2
    job = pybatch.create_job(plugin, job_params, protocol)
    job.submit()
    state = job.state()
    assert state in ["RUNNING", "QUEUED"]
    exit_code = job.exit_code()
    assert exit_code is None
    job.wait()
    state = job.state()
    assert state == "FINISHED"
    exit_code = job.exit_code()
    assert exit_code == 0
    resultdir = tempfile.mkdtemp(suffix="_pybatchtest")
    result_files = [f"result_{i}.txt" for i in range(job_params.total_jobs)]
    job.get(result_files, resultdir)
    for i in range(job_params.total_jobs):
        r_name = f"result_{i}.txt"
        r_file = Path(resultdir) / r_name
        assert r_file.read_text() == str(i)
    shutil.rmtree(resultdir)


def test_array_ko(
    plugin: str,
    protocol: pybatch.GenericProtocol,
    job_params: pybatch.LaunchParameters,
) -> None:
    "Test of a job array with a failed job."
    job_params.command = ["python3", "array_ko.py"]
    job_params.total_jobs = 6
    job_params.max_simul_jobs = 2
    job = pybatch.create_job(plugin, job_params, protocol)
    job.submit()
    state = job.state()
    assert state in ["RUNNING", "QUEUED"]
    exit_code = job.exit_code()
    assert exit_code is None
    job.wait()
    state = job.state()
    assert state == "FAILED"
    exit_code = job.exit_code()
    assert exit_code == 42
    resultdir = tempfile.mkdtemp(suffix="_pybatchtest")
    result_files = [f"result_{i}.txt" for i in range(job_params.total_jobs)]
    job.get(result_files, resultdir)
    for i in range(job_params.total_jobs):
        r_name = f"result_{i}.txt"
        r_file = Path(resultdir) / r_name
        assert r_file.read_text() == str(i)
    shutil.rmtree(resultdir)


def test_array_cancel(
    plugin: str,
    protocol: pybatch.GenericProtocol,
    job_params: pybatch.LaunchParameters,
) -> None:
    "Test of a canceled job array."
    job_params.command = ["python3", "array.py"]
    job_params.total_jobs = 4
    job_params.max_simul_jobs = 2
    job = pybatch.create_job(plugin, job_params, protocol)
    job.submit()
    state = job.state()
    assert state in ["RUNNING", "QUEUED"]
    job.cancel()
    job.wait()
    state = job.state()
    assert state == "FAILED"
    # exit_code is not relevant in this case
