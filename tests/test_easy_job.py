import tempfile
from pathlib import Path
import os

def test_launch():
    import pybatch
    workdir = tempfile.mkdtemp(suffix="_pybatchtest")
    current_file_dir = os.path.dirname(__file__)
    script = str(Path(current_file_dir) / "scripts" / "hello.sh")
    params = pybatch.LaunchParameters(script, workdir)
    job = pybatch.create_job("local", params)
    job.submit()
    job.wait()
    
    output_file = Path(workdir)/"logs"/"output.log"
    assert output_file.read_text() == "Hello !\n"
