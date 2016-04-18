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
- Tab completion for magics and file paths.
- Help for magics using ? or Shift+Tab.
- Plot magic for setting default plot behavior.
- Python magic for accessing python interpreter.


Installation
----------------
You can install Metakernel through `pip`:


`pip install metakernel --upgrade`



Documentation
-----------------------

Example notebooks can be viewed here_.

Documentation is available online_. Magics have interactive help_ (and online).

For version information, see the Revision History_.


.. _here: http://nbviewer.ipython.org/github/Calysto/metakernel/tree/master/examples/

.. _help: https://github.com/Calysto/metakernel/blob/master/metakernel/magics/README.md

.. _online: http://Calysto.github.io/metakernel/

.. _History: https://github.com/Calysto/metakernel/blob/master/HISTORY.rst


