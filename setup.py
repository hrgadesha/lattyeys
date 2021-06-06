# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

with open('requirements.txt') as f:
	install_requires = f.read().strip().split('\n')

# get version from __version__ variable in latteys/__init__.py
from latteys import __version__ as version

setup(
	name='latteys',
	version=version,
	description='Customisation',
	author='B2Grow',
	author_email='mail@b2grow.com',
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
