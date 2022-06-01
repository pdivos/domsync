from setuptools import setup

setup(name='domsync',
    version='0.1',
    description='Build DOM in Python, synchronise to Browser efficiently',
    author='pdivos',
    author_email='pdivos@gmail.com',
    license='MIT',
    packages=['domsync'],
    # scripts=['bin/run_tests.py'],
    test_suite="tests",
    zip_safe=False)