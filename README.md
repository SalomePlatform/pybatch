# pybatch

Pybatch is a python module to submit jobs on a remote machine managed by a batch manager such as Slurm, PBS, etc.

# Prerequisites

libkrb5-dev

# Tests

tox -e test -- --user-config-file=doc/examples/config_tests.toml
