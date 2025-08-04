from __future__ import annotations
from importlib.metadata import entry_points
from .genericjob import GenericJob
from .generic_protocol import GenericProtocol
from .parameter import LaunchParameters


def create_job(
    plugin_name: str,
    params: LaunchParameters,
    connection_protocol: GenericProtocol | None = None,
) -> GenericJob:
    """Create the job with the chosen plugin.

    :param plugin_name: name of the plugin to use for the job creation.
    :param params: job parameters.
    :param connection_protocol: protocol for remote connection. None for local
     use.
    """

    # for entry_point in entry_points().get("pybatch.plugins"):
    for entry_point in entry_points()["pybatch.plugins"]:
        if entry_point.name == plugin_name:
            plugin = entry_point.load()()
            job: GenericJob = plugin.create_job(params, connection_protocol)
            return job
    raise Exception(f"Plugin {plugin_name} not found.")


def reload_job(dump: str) -> GenericJob:  # type: ignore
    """Reload a job from a dumped string - for future use, not implemented.

    :param dump: representation of the job.
    """
    ...  # TODO
