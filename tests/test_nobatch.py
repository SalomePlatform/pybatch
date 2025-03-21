from pybatch.plugins.nobatch.pybatch_manager import main as manager

import tempfile
from pathlib import Path
import os
import shutil
import inspect

def test_batch_manager(capsys):
    workdir = tempfile.mkdtemp(suffix="_pybatchtest")
    current_file_dir = os.path.dirname(__file__)
    script = Path(current_file_dir) / "scripts" / "hello.py"
    shutil.copy(script, workdir)
    shutil.copy(inspect.getfile(manager), workdir)
    args = ["submit", workdir, "python3", "hello.py"]
    manager(args)
    pid = capsys.readouterr().out
    # TODO fix defunct/ zombie
    # args = ["wait", pid]
    # manager(args)
    # captured = capsys.readouterr()
    # assert not captured.out
    # assert not captured.err
    args = ["state", pid, workdir]
    manager(args)
    state = capsys.readouterr().out
    assert state.strip() == "FINISHED"
    # params = pybatch.LaunchParameters(
    #     ["python3", "hello.py", "world"], workdir, input_files=[script]
    # )
