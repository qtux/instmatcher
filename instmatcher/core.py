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

from whoosh import index, qparser
from whoosh.fields import Schema, TEXT, NUMERIC, STORED
from whoosh.qparser import MultifieldParser

def createIndex():
	print('creating the index - this may take some time')
	if not os.path.exists('index'):
		os.mkdir('index')
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

def query(inst, area):
	ix = index.open_dir('index')
	
	instParser = MultifieldParser(['name', 'alias',], ix.schema)
	queryInst = expandAbbreviations(inst)
	instQuery = instParser.parse(queryInst)
	
	coordParser = MultifieldParser(['lat', 'lon'], ix.schema)
	latQueryText = 'lat:[{min} to {max}]'.format(**area['lat'])
	lonQueryText = 'lon:[{min} to {max}]'.format(**area['lon'])
	coordQuery = coordParser.parse(latQueryText + lonQueryText)
	
	with ix.searcher() as searcher:
		instResults = searcher.search(instQuery)
		coordResults = searcher.search(coordQuery, limit=None)
		instResults.upgrade(coordResults)
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
	result = text
	abbreviations = resource_filename(__name__, 'data/abbreviations.csv')
	with open(abbreviations) as csvfile:
		reader = csv.DictReader(csvfile)
		for row in reader:
			result = re.sub(
				r"\b(?i){}\b".format(row['short']),
				row['long'],
				result,
			)
	return result
