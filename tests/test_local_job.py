def test_python_script(local_plugin, local_args):
    assert local_plugin in ["nobatch", "slurm"]
    assert local_args is not None
