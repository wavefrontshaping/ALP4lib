#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from setuptools import setup
import os

long_description = (
    "Please read the documentation on Github and official Vialux documentation."
)
if os.path.exists("README.txt"):
    long_description = open("README.txt").read()

setup(
    name="ALP4lib",
    version="1.0.2",
    author="Sebastien Popoff",
    author_email="sebastien.popoff@espci.fr",
    description=(
        "A module to control Vialux DMDs based on ALP4.X API."
        "It uses the .ddl files provided by Vialux."
    ),
    license="MIT",
    keywords="DMD Vialux",
    url="https://github.com/wavefronthsaping/ALP4lib",
    package_dir={"": "src"},
    py_modules=["ALP4"],
    long_description=long_description,
    classifiers=[
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Education",
        "Topic :: Scientific/Engineering",
        "License :: OSI Approved :: MIT License",
    ],
    install_requires=["numpy", "matplotlib", "scipy", "numba", "joblib"],
)
