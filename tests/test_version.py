def test_version():
    import pybatch
    assert pybatch.__version__ == "0.0"

def test_plugin():
    import pybatch
    params = pybatch.LaunchParameters("script", "dir")
    job = pybatch.create_job("local", params)
    import pybatch.plugins.local.job
    assert isinstance(job, pybatch.plugins.local.job.Job)
    import pybatch.plugins.slurm.job
    job = pybatch.create_job("slurm", params)
    assert isinstance(job, pybatch.plugins.slurm.job.Job)
    import pybatch.plugins.sshhost.job
    job = pybatch.create_job("sshhost", params)
    assert isinstance(job, pybatch.plugins.sshhost.job.Job)
