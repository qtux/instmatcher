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

import csv
import os, os.path
from pkg_resources import resource_filename
import re

from whoosh import index
from whoosh.fields import Schema, TEXT, NUMERIC, STORED
from whoosh.qparser import MultifieldParser

_abbreviations = None
_ix = None
_instParser = None
_coordParser = None

def init(procs=1, multisegment=False, ixPath='index', force=False):
	# create the index if it does not exist or force is enabled
	if not os.path.exists(ixPath):
		os.mkdir(ixPath)
		force = True
	if force:
		print('creating the index - this may take some time')
		schema = Schema(
			name=TEXT(stored=True),
			alias=TEXT,
			lat=NUMERIC(numtype=float, stored=True),
			lon=NUMERIC(numtype=float, stored=True),
			isni=STORED,
			country=STORED,
			alpha2=STORED,
		)
		ix = index.create_in(ixPath, schema)
		writer = ix.writer(procs=os.cpu_count(), multisegment=True)
		
		institutes = resource_filename(__name__, 'data/institutes.csv')
		with open(institutes) as csvfile:
			reader = csv.DictReader(csvfile)
			for row in reader:
				writer.add_document(
					name=row['name'],
					alias=row['alias'],
					lat=row['lat'],
					lon=row['lon'],
					isni=row['isni'],
					country=row['country'],
					alpha2=row['alpha2'],
				)
		writer.commit()
	
	# load the available abbreviations from 'data/abbreviations.csv'
	global _abbreviations, _ix, _instParser, _coordParser
	_abbreviations = {}
	source = resource_filename(__name__, 'data/abbreviations.csv')
	with open(source) as csvfile:
		reader = csv.reader(csvfile)
		for row in reader:
			_abbreviations[row[0]] = row[1]
	
	# load the index and create the institute and coordinate query parsers
	_ix = index.open_dir(ixPath)
	_instParser = MultifieldParser(['name', 'alias',], _ix.schema)
	_coordParser = MultifieldParser(['lat', 'lon'], _ix.schema)

def query(inst, lat, lon, offset=1):
	with _ix.searcher() as searcher:
		# search for the given institute
		try:
			instQuery = _instParser.parse(inst)
		except AttributeError:
			return None
		instResults = searcher.search(instQuery, limit=None)
		# try to enhance the search boosting results in the vicinity of lat/lon
		try:
			# one degree of arc corresponds to about 111 km
			latQueryText = 'lat:[{} to {}]'.format(lat - offset, lat + offset)
			lonQueryText = 'lon:[{} to {}]'.format(lon - offset, lon + offset)
			coordQuery = _coordParser.parse(latQueryText + lonQueryText)
			coordResults = searcher.search(coordQuery, limit=None)
			instResults.upgrade(coordResults)
		except TypeError:
			pass
		# return the best hit
		for hit in instResults:
			return {
				'name': hit['name'],
				'isni': hit['isni'],
				'lat': hit['lat'],
				'lon': hit['lon'],
				'country': hit['country'],
				'alpha2': hit['alpha2'],
			}

def expandAbbreviations(text):
	for abbrev, expansion in _abbreviations.items():
		text = re.sub(r"\b(?i){}\b".format(abbrev), expansion, text)
	return text
