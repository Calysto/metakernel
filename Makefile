# Note: This is meant for Metaernel developer use only
.PHONY: all clean test test_warn cover release gh-pages

export TEST_ARGS=--exe -v --with-doctest
export NAME=metakernel
export VERSION=`python -c "import $(NAME); print($(NAME).__version__)"`
export GHP_MSG="Generated gh-pages for `git log master -1 --pretty=short --abbrev-commit`"

all: install

install: clean
	python setup.py install
	cd metakernel_python; python setup.py install
	cd metakernel_echo; python setup.py install
	cd metakernel_bash; python setup.py install

install3: clean
	python3 setup.py install
	cd metakernel_python; python3 setup.py install
	cd metakernel_echo; python3 setup.py install
	cd metakernel_bash; python3 setup.py install

clean:
	rm -rf build
	rm -rf dist
	/usr/bin/find . -name "*.pyc" -o -name "*.py,cover"| xargs rm -f

test: clean
	python setup.py build
	ipcluster2 start -n=3 &
	cd build; nosetests $(TEST_ARGS); ipcluster2 stop
	make clean

test_warn: clean
	python setup.py build
	ipcluster2 start -n=3 &
	export PYTHONWARNINGS="all"; cd build; nosetests $(TEST_ARGS); ipcluster2 stop
	make clean

cover: clean
	pip install nose-cov
	ipcluster2 start -n=3 &
	nosetests $(TEST_ARGS) --with-cov --cov $(NAME) $(NAME); ipcluster2 stop
	coverage annotate

release: gh-pages
	pip install wheel
	python setup.py register
	python setup.py bdist_wheel upload
	python setup.py sdist --formats=gztar,zip upload
	git tag v$(VERSION)
	git push origin --all

gh-pages: clean
	pip install sphinx-bootstrap-theme numpydoc sphinx ghp-import
	git checkout master
	git pull origin master
	make -C docs html
	ghp-import -n -p -m $(GHP_MSG) docs/_build/html

help: 
	ipython console --kernel metakernel_python < generate_help.py
