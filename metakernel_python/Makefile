.PHONY: all test

test:
	python setup.py install --user
	ipython console --kernel=metakernel_python

all:
	python setup.py register
	python setup.py sdist --formats=gztar,zip upload
