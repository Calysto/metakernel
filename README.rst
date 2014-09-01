A simple Jupyter/IPython kernel template which includes core magic functions.

.. image:: https://badge.fury.io/py/jupyter_kernel.png/
    :target: http://badge.fury.io/py/jupyter_kernel

.. image:: https://pypip.in/d/jupyter_kernel/badge.png
        :target: https://crate.io/packages/jupyter_kernel/

See IPython's docs on `wrapper kernels
<http://ipython.org/ipython-doc/dev/development/wrapperkernels.html>`_.

Additional magics can be installed within the new kernel package under a `magics` subpackage.


Features
-------------
- Basic set of line and cell magics for all kernels.
- Tab completion for magics and file paths.
- Help for magics using ? or Shift+Tab.
- Plot magic for setting default plot behavior.
- Python magic for accessing python interpreter.


Installation
----------------
You can install jupyter_kernel through `pip`:


`pip install jupyter_kernel --upgrade`



Documentation
-----------------------

An example notebook can be viewed here_.

Documentation is available online_.

For version information, see the Revision History_.


.. _here: http://nbviewer.ipython.org/github/blink1073/jupyter_kernel/blob/master/examples/echo_kernel.ipynb?create=1

.. _online: http://blink1073.github.io/jupyter_kernel/

.. _History: https://github.com/blink1073/jupyter_kernel/blob/master/HISTORY.rst


