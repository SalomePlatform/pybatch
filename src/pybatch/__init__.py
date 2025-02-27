__all__ = [
    "GenericJob",
    "LaunchParameters",
    "create_job",
    "PybatchException",
]
from .genericjob import GenericJob
from .parameter import LaunchParameters
from .jobmanager import create_job

# WARNING `python_requires = >= 3.8`
from importlib.metadata import PackageNotFoundError, version  # pragma: no cover

try:
    # Change here if project is renamed and does not equal the package name
    dist_name = "pybatch"
    __version__ = version(dist_name)
except PackageNotFoundError:  # pragma: no cover
    __version__ = "unknown"
finally:
    del version, PackageNotFoundError

class PybatchException(Exception):
    pass
