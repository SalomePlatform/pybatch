from __future__ import annotations
import pathlib
from . import PybatchException
import subprocess
import typing


def path_join(base: str, *paths: str, is_posix: bool) -> str:
    result: pathlib.PurePath
    if is_posix:
        result = pathlib.PurePosixPath(base)
    else:
        result = pathlib.PureWindowsPath(base)
    for path in paths:
        result = result / path
    return str(result)


def is_absolute(path: str, is_posix: bool) -> bool:
    if is_posix:
        return pathlib.PurePosixPath(path).is_absolute()
    else:
        return pathlib.PureWindowsPath(path).is_absolute()


def slurm_time_to_seconds(val: str) -> str:
    """Convert a slurm time format string to seconds.

    See https://slurm.schedmd.com/sbatch.html#OPT_time
    Acceptable time formats:
       "minutes", "minutes:seconds", "hours:minutes:seconds",
       "days-hours", "days-hours:minutes" and "days-hours:minutes:seconds"
    """
    val = val.strip()
    if not val:
        return val
    try:
        day_split = val.split("-")
        if len(day_split) == 2:
            days = int(day_split[0])
            rem = day_split[1]
        elif len(day_split) == 1:
            days = 0
            rem = day_split[0]
        else:
            raise PybatchException(f"Invalid time format: {val}.")
        hour_split = rem.split(":")
        if len(hour_split) == 3:
            hours = int(hour_split[0])
            minutes = int(hour_split[1])
            seconds = int(hour_split[2])
        elif len(hour_split) == 2:
            if days > 0:  # days-hours:minutes
                hours = int(hour_split[0])
                minutes = int(hour_split[1])
                seconds = 0
            else:  # minutes:seconds
                hours = 0
                minutes = int(hour_split[0])
                seconds = int(hour_split[1])
        elif len(hour_split) == 1:
            if days > 0:  # days-hours
                hours = int(hour_split[0])
                minutes = 0
                seconds = 0
            else:  # minutes
                hours = 0
                minutes = int(hour_split[0])
                seconds = 0
        else:
            raise PybatchException(f"Invalid time format: {val}.")
    except Exception as e:
        raise PybatchException(f"Invalid time format: {val}.") from e
    result = seconds + 60 * minutes + 3600 * hours + 24 * 3600 * days
    return str(result)


def run_check(
    command: list[str], **extra: typing.Any
) -> subprocess.CompletedProcess[str]:
    proc = subprocess.run(command, capture_output=True, text=True, **extra)
    ret_code = proc.returncode
    if ret_code != 0:
        message = f"""Error {ret_code}.
  command: {command}.
  stderr: {proc.stderr}
"""
        raise PybatchException(message)
    return proc


def escape_str(val: str) -> str:
    """Escape characters with special meaning in bash.
    a'b -> 'a'\''b'
    a b -> 'a b'
    """
    special_chars = " ()[]{}*?$#'\\"
    special_found = False
    for c in special_chars:
        if c in val:
            special_found = True
            break
    if special_found:
        result = "'" + val.replace("'", "'\\''") + "'"
    else:
        result = val
    return result
