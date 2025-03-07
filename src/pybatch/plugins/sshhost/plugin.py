# type: ignore
from pybatch import GenericJob, LaunchParameters, GenericProtocol
from .job import Job


class Plugin:
    @property
    def description(self) -> str:
        return """Remote execution without any batch manager."""

    def create_job(self,
                   param: LaunchParameters,
                   connection_protocol: GenericProtocol
                   ) -> GenericJob:
        # TODO
        return Job()
