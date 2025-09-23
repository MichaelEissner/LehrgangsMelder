#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = fh.read().splitlines()

setup(
    name="website_monitor",
    version="1.0.0",
    author="Michael Eißner",
    author_email="CatHas4Paw@gmail.com",
    description="Ein Tool zum Überwachen von Webseiten und Senden von E-Mail-Benachrichtigungen",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/MichaelEissner/LehrgangsMelder",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "website_monitor=src.website_monitor:main",
            "setup_credentials=src.setup_credentials:main",
        ],
    },
)
