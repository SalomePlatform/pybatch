#! /usr/bin/env python3
"""
This script manages the execution of a command.
It is meant to be run on the remote server side.
This script should avoid the utilisation of non standard python modules for
better compatibility, because pybatch is not necessary installed on the remote
server.
"""

# No typing for better compatibility with older python versions.
# (edf gaia - python 3.5)
# mypy: ignore-errors
import argparse
import subprocess
import signal
import functools
import os
from pathlib import Path
import sys
import logging


def handler(proc, signum, frame):
    proc.terminate()


def submit(workdir, command, wall_time):
    """Launch a command and return immediatly.

    The command is launched in workdir.
    The pid of the created process is printed on stdout.
    """
    message = "submit workdir={}, command={}, walltime={}".format(
        workdir, command, wall_time
    )
    logging.info(message)
    # check access to workdir before fork.
    log_path = Path(workdir) / "logs"
    log_path.mkdir(parents=True, exist_ok=True)
    stdout_log = log_path / "output.log"
    stderr_log = log_path / "error.log"
    manager_log = log_path / "manager.log"
    stdout_log.touch()
    stderr_log.touch()
    manager_log.touch()

    # execute in detached mode
    pid = os.fork()
    if pid > 0:
        # father side
        logging.info("Jobid " + str(pid))
        print(pid)
        return
    # child side
    os.setsid()
    signal.signal(signal.SIGHUP, signal.SIG_IGN)

    log = open(str(manager_log), "w")  # python 3.5
    # std redirection
    os.dup2(log.fileno(), sys.stdout.fileno())
    os.dup2(log.fileno(), sys.stderr.fileno())
    os.dup2(os.open(os.devnull, os.O_RDWR), sys.stdin.fileno())

    # file descriptors are automaticaly closed by default
    # (see close_fds argument of Popen).
    stdout_file = open(str(stdout_log), "w")  # python 3.5
    stderr_file = open(str(stderr_log), "w")  # python 3.5
    proc = subprocess.Popen(
        command, stdout=stdout_file, stderr=stderr_file, cwd=workdir
    )
    signal.signal(signal.SIGTERM, functools.partial(handler, proc))
    try:
        exit_code = proc.wait(wall_time)
    except subprocess.TimeoutExpired:
        proc.terminate()
        print("Timeout expired! Terminate child.")
        exit_code = proc.wait()
    exit_log = str(log_path / "exit_code.log")  # python 3.5
    with open(exit_log, "w") as exit_file:
        exit_file.write(str(exit_code))


def wait(proc_id):
    "Wait for the process to finish."
    logging.info("Wait jobid " + str(proc_id))
    import time

    proc_exists = True
    while proc_exists:
        try:
            os.kill(proc_id, 0)
        except ProcessLookupError:
            proc_exists = False
        else:
            time.sleep(0.1)
    logging.info("Wait finished.")


def state(proc_id, workdir):
    """Print the state of the process.

    The work directory of the job is supposed to be the same as the directory
    of this script.
    """
    logging.info("state jobid " + str(proc_id))
    proc_exists = True
    try:
        os.kill(proc_id, 0)
    except ProcessLookupError:
        proc_exists = False
    if proc_exists:
        logging.info("state RUNNING")
        print("RUNNING")
    else:
        exit_log = Path(workdir) / "logs" / "exit_code.log"
        if exit_log.is_file():
            exit_value = exit_log.read_text().strip()
            if exit_value == "0":
                logging.info("state FINISHED")
                print("FINISHED")
            else:
                logging.info("state FAILED")
                print("FAILED")
        else:
            logging.info("state FAILED")
            print("FAILED")


def cancel(proc_id):
    "Kill the process."
    logging.info("cancel jobid " + str(proc_id))
    try:
        os.kill(proc_id, signal.SIGTERM)
    except Exception:
        # TODO
        logging.info("cancel kill failed!")


def main(args_list=None):
    parser = argparse.ArgumentParser(description="Job manager for pybatch.")
    subparsers = parser.add_subparsers(
        dest="mode",  # required=True,#python>=3.7
        help="Use mode.",
    )

    parser_submit = subparsers.add_parser(
        "submit", help="Start a job and print the pid."
    )
    parser_submit.add_argument("work_dir", help="Work directory.")
    parser_submit.add_argument(
        "--wall_time",
        type=int,
        default=None,
        help="Maximum execution time in seconds.",
    )
    parser_submit.add_argument("command", nargs="+", help="Command to submit.")

    parser_wait = subparsers.add_parser(
        "wait", help="Wait for the end of a job."
    )
    parser_wait.add_argument("proc", type=int, help="Process id.")

    parser_state = subparsers.add_parser(
        "state", help="Print the state of a job."
    )
    parser_state.add_argument("proc", type=int, help="Process id.")
    parser_state.add_argument("work_dir", help="Work directory.")

    parser_cancel = subparsers.add_parser("cancel", help="Cancel a job.")
    parser_cancel.add_argument("proc", type=int, help="Process id.")

    args = parser.parse_args(args_list)
    if args.mode == "submit":
        submit(args.work_dir, args.command, args.wall_time)
    elif args.mode == "wait":
        wait(args.proc)
    elif args.mode == "state":
        state(args.proc, args.work_dir)
    elif args.mode == "cancel":
        cancel(args.proc)


def log_config():
    workdir = os.path.dirname(sys.argv[0])
    log_file = os.path.join(workdir, "pybatch.log")
    logging.basicConfig(
        filename=log_file,
        level=logging.DEBUG,
        format="%(asctime)s - %(message)s",
    )


if __name__ == "__main__":
    log_config()
    main()
