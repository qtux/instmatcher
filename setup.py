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

'''A Python library to match an affiliation string to a known institution'''

import os, os.path
import csv
import math
import multiprocessing
from setuptools import setup
from setuptools.command.develop import develop
from setuptools.command.install import install
from setuptools.command.test import test

codes = {}
countryInfo = os.path.join('instmatcher', 'data', 'countryInfo.txt')
with open(countryInfo) as csvfile:
	data = filter(lambda row: not row[0].startswith('#'), csvfile)
	reader = csv.reader(data, delimiter='\t', quoting=csv.QUOTE_NONE)
	for row in reader:
		codes[row[0]] = row[4]

def create_index(procs, multisegment, ixPath):
	from whoosh import index
	from whoosh.fields import Schema, TEXT, NUMERIC, STORED, ID
	from whoosh.analysis import CharsetFilter, StemmingAnalyzer, LowercaseFilter
	from whoosh.support.charset import accent_map
	
	ana = StemmingAnalyzer() | CharsetFilter(accent_map) | LowercaseFilter()
	schema = Schema(
		name=STORED,
		tokens=TEXT(analyzer=ana),
		alias=TEXT(analyzer=ana),
		lat=NUMERIC(numtype=float, stored=True),
		lon=NUMERIC(numtype=float, stored=True),
		isni=STORED,
		country=STORED,
		alpha2=ID(stored=True),
		source=ID(stored=True, unique=True),
		type=STORED,
	)
	ix = index.create_in(ixPath, schema)
	writer = ix.writer(procs=procs, multisegment=multisegment)
	institutions = os.path.join('instmatcher', 'data', 'institutions.csv')
	visited = set()
	with open(institutions) as csvfile:
		reader = csv.DictReader(csvfile)
		for row in reader:
			if row['source'] not in visited:
				try:
					row['country'] = codes[row['alpha2']]
				except KeyError:
					continue
				if not row['lat'] or not row['lon']:
					row['lat'], row['lon'] = float('nan'), float('nan')
				row['tokens'] = row['name']
				writer.add_document(**row)
				visited.add(row['source'])
	writer.commit()

def create_geoindex(procs, multisegment, ixPath):
	from whoosh import index
	from whoosh.fields import Schema, STORED, ID, IDLIST
	
	schema = Schema(
		name=STORED,
		lower=ID,
		asci=ID,
		alias=IDLIST(expression=r'[^,]+'),
		lat=STORED,
		lon=STORED,
		alpha2=ID(stored=True),
		country=ID(stored=True),
	)
	ix = index.create_in(ixPath, schema)
	writer = ix.writer(procs=procs, multisegment=multisegment)
	cities = os.path.join('instmatcher', 'data', 'cities1000.txt')
	with open(cities) as f:
		reader = csv.reader(f, delimiter='\t', quoting=csv.QUOTE_NONE)
		for row in reader:
			population = int(row[14])
			writer.add_document(
				name=row[1],
				lower=row[1].lower(),
				asci=row[2].lower(),
				alias=row[3].lower(),
				lat=row[4],
				lon=row[5],
				alpha2=row[8],
				country=codes[row[8]],
				_boost=math.log(max(math.e, population)),
			)
	writer.commit()

def create_indices(force):
	def decorator(command_subclass):
		orig_run = command_subclass.run
		def new_run(self):
			procs =  multiprocessing.cpu_count()
			multisegment = procs > 1
			
			forceInst = force
			ixPath = os.path.join('instmatcher', 'data', 'index')
			if not os.path.exists(ixPath):
				forceInst = True
				os.mkdir(ixPath)
			if forceInst:
				print('creating the institution index, this may take some time')
				create_index(procs, multisegment, ixPath)
			
			forceGeo = force
			ixPath = os.path.join('instmatcher', 'data', 'geoindex')
			if not os.path.exists(ixPath):
				forceGeo = True
				os.mkdir(ixPath)
			if forceGeo:
				print('creating the geoindex, this may take some time')
				create_geoindex(procs, multisegment, ixPath)
			
			orig_run(self)
		command_subclass.run = new_run
		return command_subclass
	return decorator

@create_indices(force=True)
class CustomDevelopCommand(develop):
	pass

@create_indices(force=True)
class CustomInstallCommand(install):
	pass

@create_indices(force=False)
class CustomTestCommand(test):
	pass

def readme():
	with open('README.rst') as f:
		return f.read()

with open(os.path.join('instmatcher', 'version.py'), 'rt') as f:
	exec(f.read())

setup(
	cmdclass={
		'install': CustomInstallCommand,
		'develop': CustomDevelopCommand,
		'test': CustomTestCommand,
	},
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
			'data/abbreviations.csv',
			'data/alternativeCountryNames.csv',
			'data/countryInfo.txt',
			'data/index/*',
			'data/geoindex/*',
		]
	},
	install_requires=[
		'Whoosh>=2.7.4',
		'requests>=2.10.0',
	],
	extras_require={
		'docs':[
			'Sphinx>=1.4.5',
			'sphinx_rtd_theme>=0.1.10a0',
		],
		'examples-neo4j':[
			'PyYAML>=3.11',
			'py2neo>=3.1.1',
		],
	},
	include_package_data=True,
	zip_safe=False,
	keywords='institute institution affiliation organisation search match',
	platforms='any',
	classifiers=[
		'Development Status :: 4 - Beta',
		'License :: OSI Approved :: Apache Software License',
		'Intended Audience :: Developers',
		'Programming Language :: Python :: 3.5',
		'Programming Language :: Python :: 3.4',
		'Topic :: Text Processing :: General',
		'Topic :: Software Development :: Libraries :: Python Modules',
	],
	test_suite="tests",
)
