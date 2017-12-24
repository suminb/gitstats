#!/usr/bin/env python

from distutils.core import setup

import gitstats


def readme():
    try:
        with open('README.rst') as f:
            return f.read()
    except:
        return '(Could not read from README.rst)'


with open('requirements.txt') as fin:
    install_reqs = fin.readlines()


setup(
    name='gitstats',
    py_modules=['gitstats', 'gitstats.__main__', 'gitstats.utils'],
    version=gitstats.__version__,
    description='Generating overall statistics for multiple git repositories',
    long_description=readme(),
    author=gitstats.__author__,
    author_email=gitstats.__email__,
    url='http://github.com/suminb/gitstats',
    license='BSD',
    packages=[],
    install_requires=install_reqs,
    entry_points={
        'console_scripts': [
            'gitstats = gitstats.__main__:cli'
        ]
    },
)
