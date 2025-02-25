#! /usr/bin/env python3
"""
This script wraps the execution of a script and it can add controls over the
resources used by the script (wall time, number of cpus, memory).
All the arguments are passed through a configuration file.
This is written in python for portability.
"""
import json
import argparse
import os
import subprocess
from pathlib import Path
import signal
import functools

def handler(proc, signum, frame):
    proc.terminate()

def main():
    parser = argparse.ArgumentParser(description="Run a local job.")
    parser.add_argument("config", help="Configuration file of the job.")
    args = parser.parse_args()

    with open(args.config, "r") as config_file:
        options = json.load(config_file)
    work_directory = os.path.realpath(os.path.dirname(args.config))

    # TODO deal with wall time, memory & number of cpus
    command = options["command"]
    if "wall_time" in options:
        wall_time = int(options["wall_time"])
    else:
        wall_time = None
    log_path = Path(work_directory) / "logs"
    log_path.mkdir(parents=True, exist_ok=True)
    stdout_log = log_path / "output.log"
    stderr_log = log_path / "error.log"
    # file descriptors are automaticaly closed by default
    # (see close_fds argument of Popen).
    stdout_file = open(stdout_log, "w")
    stderr_file = open(stderr_log, "w")
    proc = subprocess.Popen(command,
                            cwd=work_directory,
                            stdout=stdout_file, stderr=stderr_file)
    signal.signal(signal.SIGTERM, functools.partial(handler, proc))
    try:
        exit_code = proc.wait(wall_time)
    except subprocess.TimeoutExpired:
        proc.terminate()
        exit_code = proc.wait()
    exit_log = log_path / "exit_code.log"
    with open(exit_log, "w") as exit_file:
        exit_file.write(str(exit_code))

if __name__ == "__main__":
    main()
