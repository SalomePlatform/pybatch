from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class LaunchParameters:
    """Parameters of a job to be launched.

    List of parameters :

      * command - full command to run with arguments as a list.
      * work_directory - remote work directory.
      * host - remote host where the job will be launched
      * user - user name if needed.
      * name - name of the job
      * nodes - number of required nodes, 0 for undefined.
      * ntasks - number of required tasks, 0 for undefined
      * exclusive - activate exclusive mode.
      * wall_time - maximum time of the job.
        Acceptable time formats include "minutes", "minutes:seconds",
        "hours:minutes:seconds", "days-hours", "days-hours:minutes" and
        "days-hours:minutes:seconds".
      * mem_per_node - memory required per node (ex. "32G")
      * mem_per_cpu - minimum memory required per usable allocated CPU.
      * queue - required queue.
      * partition - required partition
      * wckey
      * extra_as_string - extra parameters as a string
        (ex. "#SBATCH --cpus-per-task=4")
      * extra_as_list - extra parameters as a list (ex. ["--cpus-per-task=4"])
      * preprocess - local path of a script to be launched remotely before the
        job.
      * input_files - list of local files to be copied to remote work_directory
    """

    command: list[str]
    work_directory: str
    name: str = ""
    nodes: int = 0
    ntasks: int = 0
    exclusive: bool = False
    wall_time: str = ""
    mem_per_node: str = ""
    mem_per_cpu: str = ""
    queue: str = ""
    partition: str = ""
    wckey: str = ""
    extra_as_string: str = ""
    extra_as_list: list[str] = field(default_factory=list)
    preprocess: str = ""
    input_files: list[str | Path] = field(default_factory=list)

@dataclass
class ConnexionParameters:
    """Parameters needed to connect to a remote server.

    List of parameters :

    * host
    * user
    * password
    * gss_auth - use the gss api for authentication. It has to be True when
      using Kerberos protocole.
    """
    host: str = ""
    user: str = ""
    password: str = ""
    gss_auth: bool = False
