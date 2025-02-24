# type: ignore
from pybatch import GenericJob, LaunchParameters
from .job import Job

class Plugin:
    @property
    def description(self) -> str:
        return """Local execution without any batch manager."""
    
    def create_job(self, param: LaunchParameters) -> GenericJob :
        return Job(param)
