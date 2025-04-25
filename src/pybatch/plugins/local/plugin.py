# type: ignore
from __future__ import annotations

from pybatch import GenericJob, LaunchParameters, GenericProtocol
from .job import Job


class Plugin:
    @property
    def description(self) -> str:
        return """Local execution without any batch manager."""

    def create_job(
        self, param: LaunchParameters, _: GenericProtocol | None
    ) -> GenericJob:
        return Job(param)
