.PHONY: all test


test:
	python setup.py install
	ipython qtconsole --kernel=bash_kernel

all:
	python setup.py register
	python setup.py sdist --formats=gztar,zip upload
