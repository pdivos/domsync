from setuptools import setup

import pathlib
import re

root_dir = pathlib.Path(__file__).parent

long_description = (root_dir / 'README.md').read_text(encoding='utf-8')

# PyPI disables the "raw" directive.
long_description = re.sub(
    r"^\.\. raw:: html.*?^(?=\w)",
    "",
    long_description,
    flags=re.DOTALL | re.MULTILINE,
)

setup(
    name='domsync',
    version='0.1.1',
    description='Python server-side DOM synchronised with Browser',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='pdivos',
    author_email='pdivos@gmail.com',
    license='BSD',
    packages=['domsync'],
    package_dir={'':'src'},
    install_requires=[
        'websockets',
    ],
    test_suite="tests",
    zip_safe=False,
)