def test_slurm_time_to_seconds():
    from pybatch.tools import slurm_time_to_seconds as converter
    from pybatch import PybatchException
    assert converter(" ") == ""
    assert converter("10") == "600"
    assert converter("10:30") == "630"
    assert converter("100:30") == "6030"
    assert converter("2:10:5") == "7805"
    assert converter("2:10:05") == "7805"
    assert converter("2-2:10:30") == "180630"
    assert converter("2-2") == "180000"
    assert converter("2-2:10") == "180600"
    try:
        converter("2-0-4")
    except PybatchException:
        pass
    else:
        assert 0 # Exception expected
    try:
        converter("xvi")
    except PybatchException:
        pass
    else:
        assert 0 # Exception expected
    try:
        converter("1:2:3:4")
    except PybatchException:
        pass
    else:
        assert 0 # Exception expected
