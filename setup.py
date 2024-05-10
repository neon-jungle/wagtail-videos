#!/usr/bin/env python
"""
Install wagtailvideos using setuptools
"""

with open("README.rst", "r") as f:
    readme = f.read()

from setuptools import find_packages, setup  # noqa: E4

setup(
    name="wagtailvideos",
    version="5.2.2",
    description="A wagtail module for uploading and displaying videos in various codecs.",
    long_description=readme,
    author="Neon Jungle",
    author_email="developers@neonjungle.studio",
    url="https://github.com/neon-jungle/wagtailvideos",
    install_requires=[
        "wagtail>=5.2",
        "Django>=3.2",
        "django-enumchoicefield>=1.1.0",
        "bcp47==0.0.4",
        "wagtail-modeladmin>=2.0.0"
    ],
    zip_safe=False,
    license="BSD License",
    packages=find_packages(),
    include_package_data=True,
    package_data={},
    classifiers=[
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Framework :: Django",
        "License :: OSI Approved :: BSD License",
    ],
)
