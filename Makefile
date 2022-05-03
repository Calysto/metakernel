# Note: This is meant for Metakernel developer use only
.PHONY: all clean test test_warn cover release help


all: install

install: clean
	pip install  --upgrade --upgrade-strategy eager -e .[parallel,activity,test]
	pip install ./metakernel_python
	python -m metakernel_python install --user
	pip install ./metakernel_echo
	python -m metakernel_echo install --user

clean:
	rm -rf build dist
	/usr/bin/find . -name "*.pyc" -o -name "*.py,cover"| xargs rm -f

test: clean
	ipcluster start -n=3 &
	python -m pytest || python -m pytest --lf
	ipcluster stop
	python metakernel_python/test_metakernel_python.py
	make clean

test_warn: clean
	ipcluster start -n=3 &
	export PYTHONWARNINGS="all"
	python -m pytest || python -m pytest --lf
	ipcluster stop
	python metakernel_python/test_metakernel_python.py
	make clean

cover: clean
	ipcluster start -n=3 &
	python -m pytest --cov=metakernel || python -m pytest --lf --cov=metakernel
	ipcluster stop
	python metakernel_python/test_metakernel_python.py
	coverage annotate

docs: clean
	pip install -r docs/requirements.txt
	make -C docs html SPHINXOPTS="-W"

help:
	python docs/generate_help.py
