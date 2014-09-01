# Note: This is meant for Jupyter Kernel developer use only
.PHONY: all clean test cover release

export TEST_ARGS=--exe -v --with-doctest
export NAME=jupyter_kernel
export VERSION=`python -c "import $(NAME); print($(NAME).__version__)"`

all: clean
	python setup.py install

clean:
	rm -rf build
	rm -rf dist
	find . -name "*.pyc" -o -name "*.py,cover"| xargs rm -f
	python -c $(KILL_PROC)
	killall -9 nosetests; true

test: clean
	python setup.py build
	export PYTHONWARNINGS="all"; cd build; nosetests $(TEST_ARGS)
	make clean

cover: clean
	pip install nose-cov
	nosetests $(TEST_ARGS) --with-cov --cov $(NAME) $(NAME)
	coverage annotate

release: test
	python setup.py register
	python setup.py sdist --formats=gztar,zip upload
	git tag v$(VERSION)
	git push origin --all
