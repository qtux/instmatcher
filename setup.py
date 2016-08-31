# Copyright 2016 Matthias Gazzari
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

'''A Python library to match an affiliation string to a known institute'''

import os
from setuptools import setup

def readme():
	with open('README.rst') as f:
		return f.read()

with open(os.path.join('instmatcher', 'version.py'), 'rt') as f:
	exec(f.read())

setup(
	name='instmatcher',
	version=__version__,
	description=__doc__,
	long_description=readme(),
	author='Matthias Gazzari',
	author_email='matthias.gazzar@cern.ch',
	url='https://github.com/qtux/instmatcher',
	license='Apache License 2.0',
	packages=['instmatcher',],
	package_data={
		'instmatcher': [
			'data/institutes.csv',
			'data/abbreviations.csv',
			'data/cities1000.txt',
			'data/countryInfo.txt',
		]
	},
	install_requires=[
		'Whoosh>=2.7.4',
		'requests>=2.10.0',
	],
	extras_require={
		'data':[
			'fiona>=1.7.0',
			'shapely>=1.5.16',
		],
		'docs':[
			'Sphinx>=1.4.5',
			'sphinx_rtd_theme>=0.1.10a0',
		]
	},
	include_package_data=True,
	zip_safe=False,
	keywords='institute affiliation organisation search match',
	platforms='any',
	classifiers=[
		'Development Status :: 3 - Alpha',
		'License :: OSI Approved :: Apache Software License',
		'Intended Audience :: Developers',
		'Programming Language :: Python :: 3.5',
		'Programming Language :: Python :: 3.4',
		'Topic :: Text Processing :: General',
		'Topic :: Software Development :: Libraries :: Python Modules',
	],
	test_suite="tests",
)
