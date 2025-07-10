import pybatch.plugins.nobatch.pybatch_manager as manager

import tempfile
from pathlib import Path
import os
import shutil
import inspect
import subprocess
import time


def test_hello():
    workdir = tempfile.mkdtemp(suffix="_pybatchtest")
    current_file_dir = os.path.dirname(__file__)
    script = Path(current_file_dir) / "scripts" / "hello.py"
    shutil.copy(script, workdir)
    manager_script = shutil.copy(inspect.getfile(manager), workdir)

    # submit
    args = [
        "python3",
        manager_script,
        "submit",
        workdir,
        "python3",
        "hello.py",
        "zozo",
    ]
    proc = subprocess.run(args, capture_output=True, text=True)
    assert proc.returncode == 0
    pid = proc.stdout.strip()
    assert int(pid) > 0

    # wait
    args = ["python3", manager_script, "wait", pid]
    proc = subprocess.run(args, capture_output=True, text=True)
    assert proc.returncode == 0

    # check
    args = ["python3", manager_script, "state", pid, workdir]
    proc = subprocess.run(args, capture_output=True, text=True)
    assert proc.returncode == 0
    state = proc.stdout.strip()
    assert state == "FINISHED"
    output_file = Path(workdir) / "logs" / "output.log"
    assert output_file.read_text().strip() == "Hello zozo !"

    # clean
    shutil.rmtree(workdir)


def test_sleep():
    workdir = tempfile.mkdtemp(suffix="_pybatchtest")
    current_file_dir = os.path.dirname(__file__)
    script = Path(current_file_dir) / "scripts" / "sleep.py"
    shutil.copy(script, workdir)
    manager_script = shutil.copy(inspect.getfile(manager), workdir)

    # submit long job
    args = [
        "python3",
        manager_script,
        "submit",
        workdir,
        "python3",
        "sleep.py",
        "1",
    ]
    proc = subprocess.run(args, capture_output=True, text=True)
    assert proc.returncode == 0
    pid = proc.stdout.strip()
    assert int(pid) > 0

    # state
    args = ["python3", manager_script, "state", pid, workdir]
    proc = subprocess.run(args, capture_output=True, text=True)
    assert proc.returncode == 0
    state = proc.stdout.strip()
    assert state == "RUNNING"

    # wait
    args = ["python3", manager_script, "wait", pid]
    proc = subprocess.run(args, capture_output=True, text=True)
    assert proc.returncode == 0

    # check
    args = ["python3", manager_script, "state", pid, workdir]
    proc = subprocess.run(args, capture_output=True, text=True)
    assert proc.returncode == 0
    state = proc.stdout.strip()
    assert state == "FINISHED"
    result_file = Path(workdir) / "wakeup.txt"
    assert result_file.exists()

    # clean
    shutil.rmtree(workdir)


def test_cancel():
    workdir = tempfile.mkdtemp(suffix="_pybatchtest")
    current_file_dir = os.path.dirname(__file__)
    script = Path(current_file_dir) / "scripts" / "sleep.py"
    shutil.copy(script, workdir)
    manager_script = shutil.copy(inspect.getfile(manager), workdir)

    # submit long job
    args = [
        "python3",
        manager_script,
        "submit",
        workdir,
        "python3",
        "sleep.py",
        "1",
    ]
    proc = subprocess.run(args, capture_output=True, text=True)
    assert proc.returncode == 0
    pid = proc.stdout.strip()
    assert int(pid) > 0

    # state
    args = ["python3", manager_script, "state", pid, workdir]
    proc = subprocess.run(args, capture_output=True, text=True)
    assert proc.returncode == 0
    state = proc.stdout.strip()
    assert state == "RUNNING"

    # cancel
    args = ["python3", manager_script, "cancel", pid]
    proc = subprocess.run(args, capture_output=True, text=True)
    assert proc.returncode == 0

    time.sleep(2)

    # check
    args = ["python3", manager_script, "state", pid, workdir]
    proc = subprocess.run(args, capture_output=True, text=True)
    assert proc.returncode == 0
    state = proc.stdout.strip()
    assert state == "FAILED"
    time.sleep(2)
    result_file = Path(workdir) / "wakeup.txt"
    assert not result_file.exists()

    # clean
    shutil.rmtree(workdir)


def test_timeout():
    """Wall time shorter than execution time."""
    workdir = tempfile.mkdtemp(suffix="_pybatchtest")
    current_file_dir = os.path.dirname(__file__)
    script = Path(current_file_dir) / "scripts" / "sleep.py"
    shutil.copy(script, workdir)
    manager_script = shutil.copy(inspect.getfile(manager), workdir)

    # submit long job
    args = [
        "python3",
        manager_script,
        "submit",
        workdir,
        "--wall_time",
        "1",
        "python3",
        "sleep.py",
        "3",
    ]
    proc = subprocess.run(args, capture_output=True, text=True)
    assert proc.returncode == 0
    pid = proc.stdout.strip()
    assert int(pid) > 0

    # state
    args = ["python3", manager_script, "state", pid, workdir]
    proc = subprocess.run(args, capture_output=True, text=True)
    assert proc.returncode == 0
    state = proc.stdout.strip()
    assert state == "RUNNING"

    time.sleep(2)

    # check
    args = ["python3", manager_script, "state", pid, workdir]
    proc = subprocess.run(args, capture_output=True, text=True)
    assert proc.returncode == 0
    state = proc.stdout.strip()
    assert state == "FAILED"
    time.sleep(2)
    result_file = Path(workdir) / "wakeup.txt"
    assert not result_file.exists()

    # clean
    shutil.rmtree(workdir)


def test_notimeout():
    """Walltime longer than execution time."""
    workdir = tempfile.mkdtemp(suffix="_pybatchtest")
    current_file_dir = os.path.dirname(__file__)
    script = Path(current_file_dir) / "scripts" / "sleep.py"
    shutil.copy(script, workdir)
    manager_script = shutil.copy(inspect.getfile(manager), workdir)

    # submit
    args = [
        "python3",
        manager_script,
        "submit",
        workdir,
        "--wall_time",
        "3",
        "python3",
        "sleep.py",
        "1",
    ]
    proc = subprocess.run(args, capture_output=True, text=True)
    assert proc.returncode == 0
    pid = proc.stdout.strip()
    assert int(pid) > 0

    # state
    args = ["python3", manager_script, "state", pid, workdir]
    proc = subprocess.run(args, capture_output=True, text=True)
    assert proc.returncode == 0
    state = proc.stdout.strip()
    assert state == "RUNNING"

    time.sleep(2)

    # check
    args = ["python3", manager_script, "state", pid, workdir]
    proc = subprocess.run(args, capture_output=True, text=True)
    assert proc.returncode == 0
    state = proc.stdout.strip()
    assert state == "FINISHED"
    result_file = Path(workdir) / "wakeup.txt"
    assert result_file.exists()

    # clean
    shutil.rmtree(workdir)


def test_array():
    "Simulation of a job array Slurm"
    workdir = tempfile.mkdtemp(suffix="_pybatchtest")
    current_file_dir = os.path.dirname(__file__)
    script = Path(current_file_dir) / "scripts" / "array.py"
    shutil.copy(script, workdir)
    manager_script = shutil.copy(inspect.getfile(manager), workdir)
    args = [
        "python3",
        manager_script,
        "submit",
        workdir,
        "--total_jobs",
        "4",
        "python3",
        "array.py",
    ]
    proc = subprocess.run(args, capture_output=True, text=True)
    assert proc.returncode == 0
    pid = proc.stdout.strip()
    assert int(pid) > 0

    # state
    args = ["python3", manager_script, "state", pid, workdir]
    proc = subprocess.run(args, capture_output=True, text=True)
    assert proc.returncode == 0
    state = proc.stdout.strip()
    assert state == "RUNNING"

    # wait
    args = ["python3", manager_script, "wait", pid]
    proc = subprocess.run(args, capture_output=True, text=True)
    assert proc.returncode == 0

    # check
    args = ["python3", manager_script, "state", pid, workdir]
    proc = subprocess.run(args, capture_output=True, text=True)
    assert proc.returncode == 0
    state = proc.stdout.strip()
    assert state == "FINISHED"
    for idx in range(4):
        result = Path(workdir) / f"result_{idx}.txt"
        assert result.read_text() == str(idx)

    # clean
    shutil.rmtree(workdir)


def test_array_ko():
    "Job array with a failed job"
    workdir = tempfile.mkdtemp(suffix="_pybatchtest")
    current_file_dir = os.path.dirname(__file__)
    script = Path(current_file_dir) / "scripts" / "array_ko.py"
    shutil.copy(script, workdir)
    manager_script = shutil.copy(inspect.getfile(manager), workdir)
    args = [
        "python3",
        manager_script,
        "submit",
        workdir,
        "--total_jobs",
        "4",
        "python3",
        "array_ko.py",
    ]
    proc = subprocess.run(args, capture_output=True, text=True)
    assert proc.returncode == 0
    pid = proc.stdout.strip()
    assert int(pid) > 0

    # state
    args = ["python3", manager_script, "state", pid, workdir]
    proc = subprocess.run(args, capture_output=True, text=True)
    assert proc.returncode == 0
    state = proc.stdout.strip()
    assert state == "RUNNING"

    # wait
    args = ["python3", manager_script, "wait", pid]
    proc = subprocess.run(args, capture_output=True, text=True)
    assert proc.returncode == 0

    # check
    args = ["python3", manager_script, "state", pid, workdir]
    proc = subprocess.run(args, capture_output=True, text=True)
    assert proc.returncode == 0
    state = proc.stdout.strip()
    assert state == "FAILED"
    for idx in range(4):
        result = Path(workdir) / f"result_{idx}.txt"
        assert result.read_text() == str(idx)
    exit_code = Path(workdir) / "logs" / "exit_code.log"
    assert "42" == exit_code.read_text()

    # clean
    shutil.rmtree(workdir)


def test_array_cancel():
    "Cancel on a job array."
    workdir = tempfile.mkdtemp(suffix="_pybatchtest")
    current_file_dir = os.path.dirname(__file__)
    script = Path(current_file_dir) / "scripts" / "array.py"
    shutil.copy(script, workdir)
    manager_script = shutil.copy(inspect.getfile(manager), workdir)
    args = [
        "python3",
        manager_script,
        "submit",
        workdir,
        "--total_jobs",
        "4",
        "python3",
        "array.py",
    ]
    proc = subprocess.run(args, capture_output=True, text=True)
    assert proc.returncode == 0
    pid = proc.stdout.strip()
    assert int(pid) > 0

    # state
    args = ["python3", manager_script, "state", pid, workdir]
    proc = subprocess.run(args, capture_output=True, text=True)
    assert proc.returncode == 0
    state = proc.stdout.strip()
    assert state == "RUNNING"

    # cancel
    args = ["python3", manager_script, "cancel", pid]
    proc = subprocess.run(args, capture_output=True, text=True)
    assert proc.returncode == 0

    # state
    args = ["python3", manager_script, "state", pid, workdir]
    proc = subprocess.run(args, capture_output=True, text=True)
    assert proc.returncode == 0
    state = proc.stdout.strip()
    assert state == "FAILED"

    # clean
    shutil.rmtree(workdir)
