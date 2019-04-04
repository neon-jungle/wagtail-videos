#!/usr/bin/env python
"""
Install wagtailvideos using setuptools
"""

with open('README.rst', 'r') as f:
    readme = f.read()

from setuptools import find_packages, setup

setup(
    name='wagtailvideos',
    version='2.0.1',
    description="A wagtail module for uploading and displaying videos in various codecs.",
    long_description=readme,
    author='Takeflight',
    author_email='developers@takeflight.com.au',
    url='https://github.com/takeflight/wagtailvideos',

    install_requires=[
        'wagtail>=2.2',
        'Django>=2.0,<2.2',
        'django-enumchoicefield==1.1.0',
    ],
    extras_require={
        'testing': [
            'mock==2.0.0'
        ]
    },
    zip_safe=False,
    license='BSD License',

    packages=find_packages(),

    include_package_data=True,
    package_data={},



    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Framework :: Django',
        'License :: OSI Approved :: BSD License',
    ],
)
