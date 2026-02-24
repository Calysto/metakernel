.PHONY: install test


install:
	pip install -e .
	jupyter kernelspec list | grep metakernel_python

test:
	ipython console --kernel=metakernel_python
