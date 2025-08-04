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


One big difference between SshProtocol and ParamikoProtocol is that the
SshProtocol protocol opens an ssh connection with authentication at every
operation, because there is a call to the command *ssh* at every opertaion.
The ParamikoProtocol opens a ssh connection when the object is created and all
the operations are made in the same ssh session, with only one authentication.
This makes ParamikoProtocol faster.

Jobs
=====

The generic interface for a job is :

.. autoclass:: pybatch.GenericJob
    :member-order: bysource
    :no-special-members:

Implementations available today are :

  - pybatch.plugins.slurm.plugin.Job - for Slurm,
  - pybatch.plugins.nobatch.plugin.Job - without batch manager.

The parameters of a job are defined by LaunchParameters :

.. autoclass:: pybatch.LaunchParameters
    :member-order: bysource
    :no-special-members:

Job factory and plugins
========================

.. autofunction:: pybatch.create_job
