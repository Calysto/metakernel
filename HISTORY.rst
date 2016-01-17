.. :changelog:

Release History
------------------------

0.12.0 (2016-01-17)
+++++++++++++++++++
- Fixes for process metakernel

0.11.0 (2015-09-28)
+++++++++++++++++++
- Added activity and jigsaw magics
- MetaKernel Magics can be used from IPython
- Renamed Spell Magics to Macro Magics

0.10.0 (2015-08-24)
+++++++++++++++++++
- Improved kernel spec install for kernels

0.9.0 (2015-03-03)
++++++++++++++++++
- Improved support for ProcessKernel on Windows
- Improved %plot magic
- Added metakernel.makSubKernel* helper methods


0.8.0 (2015-01-31)
++++++++++++++++++
- Added support for IPython.display.Image for metakernels
- Improved support for Display formatting

0.7.0 (2015-01-29)
++++++++++++++++++
- BUG: Fixed handling of icon resource on install


0.6.0 (2015-01-23)
++++++++++++++++++
- New home for MetaKernel in Calysto
- Brought source up to date with current IPython master
- Kernelspec installation issues resolved
- New help_links and language in kernelspecs
- get_help cursor fix
- Handling of mixed args and options in magics
- WIP: %install magic
- New %set and %get magics
- Added Dynamic process kernels
- Added kernel logos
- replwrap fixes


0.5.1 (2014-12-03)
++++++++++++++++++
- Add ProcessMetaKernel for subprocess-based kernels
- Renamed XXX_kernel to metakernel_XXX
- Reworked completion infrastructure
- Reworked arg parser
- Lots of bug fixes and updates to keep up with IPython 3.0.0-dev


0.3.0 (2014-09-01)
++++++++++++++++++
- Add gh-pages website: http://calysto.github.io/metakernel
- Add example notebook for echo_kernel.
- Add %python magic to interact with python shell.


0.2.0 (2014-09-01)
++++++++++++++++++

- Completely refactored API for MagicKernel and Magic
- Added %plot magic
- Added test suite with Travis CI
- Implemented all base Kernel methods with sane defaults.


0.1.0 (2014-08-24)
++++++++++++++++++

- Initial Release
