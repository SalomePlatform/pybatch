def test_version():
    import pybatch

    assert pybatch.__version__ == "0.0"


def test_plugin():
    import pybatch

    params = pybatch.LaunchParameters("script", "dir")
    import pybatch.plugins.local.job
    job = pybatch.create_job("local", params)
    assert isinstance(job, pybatch.plugins.local.job.Job)

    import pybatch.plugins.slurm.job
    job = pybatch.create_job("slurm", params)
    assert isinstance(job, pybatch.plugins.slurm.job.Job)

    import pybatch.plugins.nobatch.job
    job = pybatch.create_job("nobatch", params)
    assert isinstance(job, pybatch.plugins.nobatch.job.Job)
