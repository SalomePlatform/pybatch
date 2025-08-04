import pybatch
from pybatch.protocols.paramiko import ParamikoProtocol

# define the remote connection protocol
# It is possible to specify user & password if not gss_auth.
con_param = pybatch.ConnectionParameters(
    host="gaia",   # remote host address
    gss_auth=True  # use kerberos authentication, user & password not needed
)
protocol = ParamikoProtocol(con_param)

# define job parameters
job_params = pybatch.LaunchParameters(
    ["touch", "result.txt"], # command to execute with arguments
    "job_test",              # remote work directory
    name="myjob",            # job name
    nodes=1,                 # number of nodes for the job
    ntasks=1,                # number of tasks for the job
    wall_time="10",          # wall time for the job. Available formats:
                             # "minutes", "minutes:seconds",
                             # "hours:minutes:seconds", "days-hours",
                             # "days-hours:minutes" and
                             # "days-hours:minutes:seconds"
    wckey="P120K:SALOME"
)
# Other possible parameters:
#  total_jobs - number of jobs in a job array. When the command to execute is
#     called, the index of the current job is added as the last argument.
#  max_simul_jobs - max number of simultaneous jobs in a job array.
#  exclusive - activate exclusive mode.
#  mem_per_node - memory required per node (ex. "32G").
#  mem_per_cpu - minimum memory required per usable allocated CPU.
#  queue - required queue.
#  partition - required partition.
#  extra_as_string - extra parameters as a string
#     (ex. "#SBATCH --cpus-per-task=4").
#  extra_as_list - extra parameters as a list (ex. ["--cpus-per-task=4"]).
#  input_files - list of local files to be copied to remote work_directory.
#  is_posix - Unix like server (True) or Windows server (False).
#  create_nodefile - create LIBBATCH_NODEFILE which contains the list of
#     allocated nodes.

# job creation
myjob = pybatch.create_job("slurm", job_params, protocol)

# Another way to create the job:
#from pybatch.plugins.slurm.plugin import Job
#myjob = Job(job_params, protocol)

# submit the job
myjob.submit()

# get the state of the job
myjob.state()

# wait for the end of the job
myjob.wait()

# get the exit code of the job if the job is finished
myjob.exit_code()

# get a list of files from the remote working directory to a local directory
myjob.get(["result.txt"], ".")

# dump the job and reload it later in order to reconnect to a long running job.
import pickle
job_dump = pickle.dumps(myjob)
new_job = pickle.loads(job_dump)
