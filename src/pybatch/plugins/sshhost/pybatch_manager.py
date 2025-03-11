#! /usr/bin/env python3
"""
This script manages the execution of a command.
"""
from __future__ import annotations
from typing import Optional
from types import FrameType

import argparse
import subprocess
import signal
import functools
import psutil
from pathlib import Path

def handler(
    proc: subprocess.Popen[bytes], signum: int, frame: Optional[FrameType]
) -> None:
    proc.terminate()

def run(command:list[str], wall_time: int | None) -> None:
    """Run a command and wait until the end.

    The command is killed after wall_time seconds.
    The current directory has been already set to the work directory and the
    command is launched without changing the directory.
    """
    log_path = Path("logs")
    stdout_log = log_path / "output.log"
    stderr_log = log_path / "error.log"
    # file descriptors are automaticaly closed by default
    # (see close_fds argument of Popen).
    stdout_file = open(stdout_log, "w")
    stderr_file = open(stderr_log, "w")
    proc = subprocess.Popen(command,
                            stdout=stdout_file, stderr=stderr_file)
    signal.signal(signal.SIGTERM, functools.partial(handler, proc))
    try:
        exit_code = proc.wait(wall_time)
    except subprocess.TimeoutExpired:
        proc.terminate()
        print("Timeout expired! Terminate child.")
        exit_code = proc.wait()
    exit_log = log_path / "exit_code.log"
    with open(exit_log, "w") as exit_file:
        exit_file.write(str(exit_code))


def submit(workdir:str, command:list[str], wall_time: int | None) -> None:
    """Launch a command and return immediatly.

    The command is launched in workdir.
    The pid of the created process is printed on stdout.
    """
    # workdir = os.path.dirname(__file__)
    log_path = Path(workdir) / "logs"
    log_path.mkdir(parents=True, exist_ok=True)
    stdout_log = log_path / "manager_output.log"
    stderr_log = log_path / "manager_error.log"
    # file descriptors are automaticaly closed by default
    # (see close_fds argument of Popen).
    stdout_file = open(stdout_log, "w")
    stderr_file = open(stderr_log, "w")
    run_command = ["python3", "pybatch_manager.py", "run"]
    if wall_time:
        run_command += ["--wall_time", str(wall_time)]
    run_command += command
    proc = subprocess.Popen(run_command, stdout=stdout_file, stderr=stderr_file,
                            cwd=workdir)
    print(proc.pid)

def wait(proc_id:int) -> None:
    "Wait for the process to finish."
    try:
        pu = psutil.Process(proc_id)
        pu.wait()
    except psutil.NoSuchProcess:
        pass


def state(proc_id:int, workdir) -> None:
    """Print the state of the process.

    The work directory of the job is supposed to be the same as the directory
    of this script.
    """
    if psutil.pid_exists(proc_id):
        print("RUNNING")
    else:
        # workdir = os.path.dirname(__file__)
        exit_log = Path(workdir) / "logs" / "exit_code.log"
        if exit_log.is_file():
            exit_value = exit_log.read_text()
            if exit_value == "0":
                print("FINISHED")
            else:
                print("FAILED")
        else:
            print("FAILED")

def cancel(proc_id:int) -> None:
    "Kill the process."
    try:
        pu = psutil.Process(proc_id)
        pu.terminate()
    except psutil.NoSuchProcess:
        pass

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Job manager for pybatch.")
    subparsers = parser.add_subparsers(dest="mode", required=True,
                                       help="Use mode.")
    parser_run = subparsers.add_parser("run",
                                 help="Execute a command and wait for the end.")
    parser_run.add_argument("--wall_time", type=int, default=None,
                            help="Maximum execution time in seconds.")
    parser_run.add_argument("command", nargs='+', help="Command to run.")

    parser_submit = subparsers.add_parser("submit",
                                          help="Start a job and print the pid.")
    parser_submit.add_argument("work_dir", help="Work directory.")
    parser_submit.add_argument("--wall_time", type=int, default=None,
                               help="Maximum execution time in seconds.")
    parser_submit.add_argument("command", nargs='+', help="Command to submit.")

    parser_wait = subparsers.add_parser("wait",
                                        help="Wait for the end of a job.")
    parser_wait.add_argument("proc", type=int, help="Process id.")

    parser_state = subparsers.add_parser("state", help="Print the state of a job.")
    parser_state.add_argument("proc", type=int, help="Process id.")
    parser_state.add_argument("work_dir", help="Work directory.")

    parser_cancel = subparsers.add_parser("cancel", help="Cancel a job.")
    parser_cancel.add_argument("proc", type=int, help="Process id.")

    args = parser.parse_args()
    if args.mode == "run":
        run(args.command, args.wall_time)
    elif args.mode == "submit":
        submit(args.work_dir, args.command, args.wall_time)
    elif args.mode == "wait":
        wait(args.proc)
    elif args.mode == "state":
        state(args.proc, args.work_dir)
    elif args.mode == "cancel":
        cancel(args.proc)


if __name__ == "__main__":
    main()
