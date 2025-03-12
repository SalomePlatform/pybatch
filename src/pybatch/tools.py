from __future__ import annotations
import pathlib

def path_join(base:str, *paths:list[str], is_posix:bool) -> str:
    if is_posix:
        result = pathlib.PurePosixPath(base)
    else:
        result = pathlib.PureWindowsPath(base)
    for path in paths:
        result = result / path
    return str(result)

def is_absolute(path:str, is_posix:bool) -> bool:
    if is_posix:
        return pathlib.PurePosixPath(path).is_absolute()
    else:
        return pathlib.PureWindowsPath(path).is_absolute()
