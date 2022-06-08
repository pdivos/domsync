.PHONY: default style test coverage build clean

export PYTHONASYNCIODEBUG=1
export PYTHONPATH=.
export PYTHONWARNINGS=default

test:
	python -m unittest

build:
	python setup.py build_ext --inplace

clean:
	find . -name '*.pyc' -o -name '*.so' -delete
	find . -name __pycache__ -delete
	rm -rf .coverage .mypy_cache build compliance/reports dist docs/_build htmlcov MANIFEST src/websockets.egg-info
