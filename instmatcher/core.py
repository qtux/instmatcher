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

def createIndex(force=False):
	if not os.path.exists('index'):
		os.mkdir('index')
	elif not force:
		return
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
	ix = index.create_in('index', schema)
	writer = ix.writer()
	
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

def init():
	global _abbreviations
	_abbreviations = {}
	source = resource_filename(__name__, 'data/abbreviations.csv')
	with open(source) as csvfile:
		reader = csv.reader(csvfile)
		for row in reader:
			_abbreviations[row[0]] = row[1]
	
	createIndex()
	
	global _ix, _instParser, _coordParser
	_ix = index.open_dir('index')
	_instParser = MultifieldParser(['name', 'alias',], _ix.schema)
	_coordParser = MultifieldParser(['lat', 'lon'], _ix.schema)

def query(inst, area):
	with _ix.searcher() as searcher:
		# search for the given institute
		instQuery = _instParser.parse(inst)
		instResults = searcher.search(instQuery, limit=None)
		# try to enhance the search results boosting ones in the given area
		try:
			latQueryText = 'lat:[{min} to {max}]'.format(**area['lat'])
			lonQueryText = 'lon:[{min} to {max}]'.format(**area['lon'])
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
