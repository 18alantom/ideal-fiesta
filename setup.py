# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

with open('requirements.txt') as f:
	install_requires = f.read().strip().split('\n')

# get version from __version__ variable in accounting/__init__.py
from accounting import __version__ as version

setup(
	name='accounting',
	version=version,
	description='A test accounting app.',
	author='Lin To',
	author_email='lin@to.co',
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
