# type: ignore
from pybatch import GenericJob, LaunchParameters
from .job import Job


class Plugin:
    @property
    def description(self) -> str:
        return """Job submission using slurm batch manager."""

    def create_job(self, param: LaunchParameters) -> GenericJob:
        # TODO
        return Job()
