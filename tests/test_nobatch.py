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
    args = ["python3", manager_script, "submit", workdir,
            "python3", "hello.py", "zozo"]
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
    args = ["python3", manager_script, "submit", workdir,
            "python3", "sleep.py", "1"]
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
    args = ["python3", manager_script, "submit", workdir,
            "python3", "sleep.py", "1"]
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
