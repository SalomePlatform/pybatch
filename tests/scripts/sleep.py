import time
import sys
time.sleep(int(sys.argv[1]))
from pathlib import Path
Path("wakeup.txt").touch()
