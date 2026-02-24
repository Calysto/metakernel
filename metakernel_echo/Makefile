.PHONY: install test


install:
	pip install -e .
	jupyter kernelspec list | grep metakernel_echo

test:
	ipython console --kernel=metakernel_echo
