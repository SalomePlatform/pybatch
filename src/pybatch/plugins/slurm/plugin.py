# type: ignore
from __future__ import annotations
from pybatch import GenericJob, LaunchParameters, GenericProtocol
from .job import Job


class Plugin:
    @property
    def description(self) -> str:
        return """Job submission using slurm batch manager."""

    def create_job(
        self, param: LaunchParameters, connection_protocol: GenericProtocol
    ) -> GenericJob:
        return Job(param, connection_protocol)
