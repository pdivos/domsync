from setuptools import setup

setup(name='domsync',
    version='0.1',
    description='Python server-side DOM synchronised with Browser',
    author='pdivos',
    author_email='pdivos@gmail.com',
    license='MIT',
    packages=['domsync'],
    install_requires=[
        'websockets',
    ],
    test_suite="tests",
    zip_safe=False)