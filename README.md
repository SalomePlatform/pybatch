# pybatch

Pybatch is a python module to submit jobs on a remote machine managed by a batch manager such as Slurm, PBS, etc.

# Prerequisites

libkrb5-dev

# Install

pkcon install libkrb5-dev
git clone https://gitlab.pleiade.edf.fr/I35256/pybatch.git
pip install pybatch

# Tests

tox -e test -- --user-config-file=doc/examples/config_tests.toml
