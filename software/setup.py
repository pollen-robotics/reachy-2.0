#!/usr/bin/env python

import re

from setuptools import setup, find_packages
from os import path


def version():
    with open('reachy/_version.py') as f:
        return re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", f.read()).group(1)


here = path.abspath(path.dirname(__file__))

with open(path.join(here, '..', 'README.md'), encoding='utf-8') as f:
    long_description = f.read()


setup(
    name='reachy',
    version=version(),
    packages=find_packages(exclude=['tests']),

    install_requires=[
        'pyluos @ git+ssh://git@github.com/Luos-Robotics/pyluos@37687a67a14686a640b7d69a9218a671cef7eb65',
        'numpy',
        'scipy',
        'orbita',
        'pyquaternion',
    ],

    extras_require={
        'head': ['opencv-python'],
        'log': ['zzlog'],
    },

    author='Pollen Robotics',
    author_email='contact@pollen-robotics.com',
    url='https://github.com/pollen-robotics/reachy-2.0',

    description='A multi-purposed robotic arm',
    long_description=long_description,
    long_description_content_type='text/markdown',
)
