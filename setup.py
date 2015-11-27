#!/usr/bin/env python

from setuptools import setup, find_packages
from os import path

# www.pythonhosted.org/setuptools/setuptools.html

setup(
    name="lines",
    version="1.1.0",
    description="Program for plotting powder diffraction patterns and background subtraction",

    author="Stef Smeets",
    author_email="stef.smeets@mat.ethz.ch",
    license="GPL",
    url="https://github.com/stefsmeets/lines",

    classifiers=[
        'Programming Language :: Python :: 2.7',
    ],

    packages=["lines", "zeolite_database"],

    install_requires=["numpy", "matplotlib", "scipy"],

    package_data={
        "": ["LICENCE",  "readme.md", "setup.py"],
        "zeolite_database": ["*.cif"],
    },

    entry_points={
        'console_scripts': [
            'lines = lines.lines:main',
            'cif2xy = lines.cif2xy:main'
        ]
    }

)
