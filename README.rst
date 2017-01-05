A Jupyter/IPython kernel template which includes core magic functions (including help, command and file path completion, parallel and distributed processing, downloads, and much more).

.. image:: https://badge.fury.io/py/metakernel.png/
    :target: http://badge.fury.io/py/metakernel

.. image:: https://coveralls.io/repos/Calysto/metakernel/badge.png?branch=master
  :target: https://coveralls.io/r/Calysto/metakernel

.. image:: https://travis-ci.org/Calysto/metakernel.svg
  :target: https://travis-ci.org/Calysto/metakernel


See IPython's docs on `wrapper kernels
<http://ipython.org/ipython-doc/dev/development/wrapperkernels.html>`_.

Additional magics can be installed within the new kernel package under a `magics` subpackage.


Features
-------------
- Basic set of line and cell magics for all kernels.
    - Python magic for accessing python interpreter.
    - Run kernels in parallel.
    - Shell magics.
    - Classroom management magics.
- Tab completion for magics and file paths.
- Help for magics using ? or Shift+Tab.
- Plot magic for setting default plot behavior.

Kernels based on Metakernel
---------------------------

- matlab_kernel, https://github.com/Calysto/matlab_kernel
- octave_kernel, https://github.com/Calysto/octave_kernel
- calysto_scheme, https://github.com/Calysto/calysto_scheme
- calysto_processing, https://github.com/Calysto/calysto_processing
- java9_kernel, https://github.com/Bachmann1234/java9_kernel
- xonsh_kernel, https://github.com/Calysto/xonsh_kernel
- calysto_hy, https://github.com/Calysto/calysto_hy
- gnuplot_kernel, https://github.com/has2k1/gnuplot_kernel
- spylon_kernel, https://github.com/mariusvniekerk/spylon-kernel
- wolfram_kernel, https://github.com/mmatera/iwolfram
- sas_kernel, https://github.com/palmer0914/sas_kernel
- pysysh_kernel, https://github.com/Jaesin/psysh_kernel

... and many others.

Installation
----------------
You can install Metakernel through `pip`:


`pip install metakernel --upgrade`


Use MetaKernel Magics in IPython
--------------------------------

Although MetaKernel is a system for building new kernels, you can use a subset of the magics in the IPython kernel. Put the following in your (or a system-wide) ipython_config.py file:

.. code-block:: python

 # /etc/ipython/ipython_config.py
 c = get_config()
 startup = [
    'from metakernel import register_ipython_magics',
    'register_ipython_magics()',
 ]
 c.InteractiveShellApp.exec_lines = startup

Documentation
-----------------------

Example notebooks can be viewed here_.

Documentation is available online_. Magics have interactive help_ (and online).

For version information, see the Revision History_.


.. _here: http://nbviewer.ipython.org/github/Calysto/metakernel/tree/master/examples/

.. _help: https://github.com/Calysto/metakernel/blob/master/metakernel/magics/README.md

.. _online: http://Calysto.github.io/metakernel/

.. _History: https://github.com/Calysto/metakernel/blob/master/HISTORY.rst


