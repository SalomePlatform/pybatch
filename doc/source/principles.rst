Module pybatch
===============

This module provides an interface to manage jobs on computing resources managed
by a batch manager such as Slurm.

It can be used remotely from a work station connected to a computing cluster by
ssh, but it can also be used on the frontal of a computing cluster.

Today, the interface is implemented for
`Slurm <https://slurm.schedmd.com/overview.html>`_ and future implementations
are possible for other batch managers.
There is also an implementation for work stations without any batch manager.

This is a standard example of use of the module:

.. literalinclude:: ../examples/use_case.py

Protocols
==========

The protocols manage the connection to a remote server.
The interface is defined in a generic class.

.. autoclass:: pybatch.GenericProtocol
    :member-order: bysource
    :no-special-members:


The protocols available today are :

  - pybatch.protocols.paramiko.ParamikoProtocol - ssh protocol implemented using
    `paramiko <https://www.paramiko.org/index.html>`_
  - pybatch.protocols.ssh.SshProtocol - ssh protocol implemented using the
    commands *ssh* and *scp*.
  - pybatch.protocols.local.LocalProtocol - protocol that can be used locally,
    for instance when we are already connected on the cluster frontal and we
    don't need to connect to a remote server.

The parameters needed to create a protocol are defined in the class
'ConnectionParameters'.

.. autoclass:: pybatch.ConnectionParameters
    :member-order: bysource
    :no-special-members:

This is an exemple how to create a protocol object :

.. code-block:: python
 
   from pybatch.protocols.paramiko import ParamikoProtocol
   con_param = pybatch.ConnectionParameters(
     host="gaia",   # remote host address
     gss_auth=True  # use kerberos authentication, user & password not needed
   )
   protocol = ParamikoProtocol(con_param)


One big difference between *SshProtocol* and *ParamikoProtocol* is that the
*SshProtocol* protocol opens an ssh connection with authentication at every
operation, because there is a call to the command *ssh* at every opertaion.
The *ParamikoProtocol* opens a ssh connection when the object is created and all
the operations are made in the same ssh session, with only one authentication.
This makes *ParamikoProtocol* faster.

Jobs
=====

The generic interface for a job is :

.. autoclass:: pybatch.GenericJob
    :member-order: bysource
    :no-special-members:

Implementations available today are :

  - pybatch.plugins.slurm.job.Job - for Slurm,
  - pybatch.plugins.nobatch.job.Job - without batch manager.

The parameters of a job are defined by LaunchParameters :

.. autoclass:: pybatch.LaunchParameters
    :member-order: bysource
    :no-special-members:

Job factory and plugins
========================

Jobs can be created by the function *create_job* which offers the possibility to
choose among different job implementations available within the python
environment.

.. autofunction:: pybatch.create_job

Each job implementation is wrapped in a plugin which can be added to the python
environment using the `python entry points specification
<https://packaging.python.org/en/latest/specifications/entry-points/>`_.
The key of these entry points is "pybatch.plugins".

The plugin names defined by the module *pybatch* are :

  - "slurm" - implementation for Slurm batch manager which creates an object of
    type *pybatch.plugins.slurm.job.Job*.
  - "nobatch" - implementation that doesn't use any batch manager which creates
    an object of type *pybatch.plugins.nobatch.job.Job*.
  - "local" - implementation that doesn't use any batch manager and that can be
    only used on the local machine, because it doesn't use the GenericProtocol
    for communication. The object created is of type
    *pybatch.plugins.local.job.Job*.

Other plugins can be created and added to the entry point "pybatch.plugins" in
order to make them available to the function *create_job*.
