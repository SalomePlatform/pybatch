from pybatch import GenericJob, LaunchParameters
from pathlib import Path
import shutil
import subprocess
import psutil
import json
#import os

class Job(GenericJob):
    def __init__(self,  param: LaunchParameters):
        self.batch_script = param.batch_script
        self.work_directory = param.work_directory
        self.batch_args = param.batch_args
        self.preprocess = param.preprocess
        self.input_files = param.input_files
        self.pid = -1 # job not launched
        # TODO We could also use ntasks, wall_time and mem_per_node to set
        # limits using resource module.

    " Job protocol to be implemented."
    def submit(self)-> None:
        """ Submit the job to the batch manager and return.

        If the submission fails, raise an exception.
        """
        # create work directory
        Path(self.work_directory).mkdir(parents=True, exist_ok=True)
        # copy files
        for fi in self.input_files:
            # TODO deal with directories & relative paths
            shutil.copy(fi, self.work_directory)
        shutil.copy(self.batch_script, self.work_directory)
        # create job config file
        config = {
            "batch_script":self.batch_script,
            "batch_args":self.batch_args,
            }
        config_path = Path(self.work_directory) / "pybatch_conf.json"
        with open(config_path, "w") as config_file:
            json.dump(config, config_file)
        ## copy launcher
        #current_file_dir = os.path.dirname(__file__)
        #current_file_dir = os.path.realpath(current_file_dir)
        #launcher_file = Path(current_file_dir) / "pybatch_run.py"
        #shutil.copy(launcher_file, self.work_directory)
        #os.chmod(
        # launch batch script
        proc = subprocess.Popen(["pybatch_run", config_path])
        # set pid
        self.pid = proc.pid

    def wait(self)-> None:
        " Wait until the end of the job."
        if self.pid > 0 :
            pu = psutil.Process(self.pid)
            pu.wait()

    def state(self) -> str:
        """ Possible states : 'CREATED', 'IN_PROCESS', 'QUEUED', 'RUNNING',
        'PAUSED', 'FINISHED', 'FAILED'
        """
        if self.pid == -1:
            return 'CREATED'
        if psutil.pid_exists(self.pid):
            return 'RUNNING'
        else:
            return 'FINISHED'

    def cancel(self)-> None:
        " Stop the job."
        pu = psutil.Process(self.pid)
        pu.kill()

    def get_file(self, remote_path:str, local_path:str)-> None:
        """ Copy a file from the remote work directory.

        :param remote_path: path relative to work directory on the remote host.
        :param local_path: destination of the copy on local file system.
        """
        if os.path.isabs(remote_path) :
            abs_remote_path = remote_path
        else:
            abs_remote_path = Path(self.work_directory) / remote_path
            abs_remote_path = os.path.realpath(abs_remote_path)
            shutil.copy(abs_remote_path, local_path)

    def batch_file(self) -> str:
        " Get the content of the batch file submited to the batch manager."
        config = {
            "batch_script":self.batch_script,
            "batch_args":self.batch_args,
            }
        return json.dumps(config)

    # A réfléchir, mais il vaut peut-être mieux utiliser la sérialisation
    # pickle.
    def dump(self) -> str:
        " Serialization of the job."
        ...
