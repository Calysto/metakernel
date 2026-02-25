A Jupyter kernel base class in Python which includes core magic
functions (including help, command and file path completion, parallel
and distributed processing, downloads, and much more).

See Jupyter's docs on `wrapper
kernels <http://jupyter-client.readthedocs.io/en/stable/wrapperkernels.html>`_.

Additional magics can be installed within the new kernel package under a
``magics`` subpackage.

Features
--------

- Basic set of line and cell magics for all kernels.

  - Python magic for accessing python interpreter.
  - Run kernels in parallel.
  - Shell magics.
  - Classroom management magics.

- Tab completion for magics and file paths.

- Help for magics using ? or Shift+Tab.

- Plot magic for setting default plot behavior.

.. toctree::
   :hidden:
   :maxdepth: 1

   source/installation
   source/new_kernel
   source/api
   source/info

`API Reference <source/api.html>`_
------------------------------------------------

Documentation for the functions included in Jupyter Kernel.

`Installation <source/installation.html>`_
------------------------------------------------

How to install Jupyter Kernel.


`Creating a New Kernel <source/new_kernel.html>`_
--------------------------------------------------

How to build and package a new Jupyter kernel using MetaKernel.


`Information <source/info.html>`_
-----------------------------------------

Other information about Jupyter Kernel.
