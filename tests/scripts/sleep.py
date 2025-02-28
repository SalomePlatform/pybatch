import time
import sys
from pathlib import Path

time.sleep(int(sys.argv[1]))
Path("wakeup.txt").touch()
