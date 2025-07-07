import sys
from pathlib import Path
import time

job_id = sys.argv[1]

time.sleep(2)
Path("result_" + job_id + ".txt").write_text(job_id)
if job_id == "2":
    exit(42)
