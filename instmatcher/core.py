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

'''Module to search for known institutes.'''

import csv
import os, os.path
from pkg_resources import resource_filename
import re

from whoosh import index
from whoosh.fields import Schema, TEXT, NUMERIC, STORED, ID
from whoosh.qparser import MultifieldParser
from whoosh.query import Term

_abbreviations = None
_ix = None
_instParser = None
_coordParser = None

def init(procs, multisegment, ixPath, force=False):
	'''
	Initialise the index and global variables.

	Create the index if it does not exist or *force* is set to True,
	load the available abbreviations from 'data/abbreviations.csv' and
	load the index along with the parsers required for the institute and
	coordinate searches.

	:param procs: maximum number of processes for the index creation
	:param multisegment: split index into at least #procs segments
	:param ixPath: path to the index
	:param force: recreate the index
	'''
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
			alpha2=ID(stored=True),
			source=TEXT(stored=True),
		)
		ix = index.create_in(ixPath, schema)
		writer = ix.writer(procs=procs, multisegment=multisegment)
		
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
					source=row['source'],
				)
		writer.commit()
	
	# load the available abbreviations from 'data/abbreviations.csv'
	global _abbreviations, _ix, _instParser, _coordParser
	_abbreviations = {}
	source = resource_filename(__name__, 'data/abbreviations.csv')
	with open(source) as csvfile:
		data = filter(lambda row: not row[0].startswith('#'), csvfile)
		reader = csv.reader(data)
		for row in reader:
			_abbreviations[row[0]] = row[1]
	
	# load the index and create the institute and coordinate query parsers
	_ix = index.open_dir(ixPath)
	_instParser = MultifieldParser(['name', 'alias',], _ix.schema)
	_coordParser = MultifieldParser(['lat', 'lon',], _ix.schema)

def query(institute, alpha2, lat, lon, offset):
	'''
	Search for institutes compatible to the search parameters sorted in
	descending order starting with the most accurate search result.
	
	Applying the ISO 3166-1 alpha-2 country code will restrict the
	search results to the given country.
	The latitude, longitude and offset (in degree of arcs) parameters
	describe a geographical box in which results are preferred. Note that
	an offset of one degree of arc corresponds to about 111 km: Using an
	offset of 1 results into a box with a width of approximately 222 km.
	
	:param institute: the institute name to search for
	:param alpha2: the country to restrict search results to
	:param lat: the latitude describing the middle of the preferred box
	:param lon: the longitude describing the middle of preferred box
	:param offset: the half-width of the preferred box in degree of arcs
	'''
	if not institute:
		return
	with _ix.searcher() as searcher:
		# search for the given institute
		instQuery = _instParser.parse(institute)
		filterTerm = Term('alpha2', alpha2) if alpha2 else None
		instResults = searcher.search(instQuery, limit=None, filter=filterTerm)
		# try to enhance the search boosting results in the vicinity of lat/lon
		try:
			latQueryText = 'lat:[{} to {}]'.format(lat - offset, lat + offset)
			lonQueryText = 'lon:[{} to {}]'.format(lon - offset, lon + offset)
			coordQuery = _coordParser.parse(latQueryText + lonQueryText)
			coordResults = searcher.search(coordQuery, limit=None)
			instResults.upgrade(coordResults)
		except TypeError:
			pass
		# yield hits along with the score
		for hit in instResults:
			yield {
				'source': hit['source'],
				'name': hit['name'],
				'isni': hit['isni'],
				'lat': hit['lat'],
				'lon': hit['lon'],
				'country': hit['country'],
				'alpha2': hit['alpha2'],
			}, hit.score

def expandAbbreviations(text):
	'''
	Expand known abbreviations in the supplied string.
	Known abbreviations may be found in data/abbreviations.csv.
	
	:param text: the text in which abbreviations should be expanded
	'''
	for abbrev, expansion in _abbreviations.items():
		text = re.sub(r"\b(?i){}\b".format(abbrev), expansion, text)
	return text
