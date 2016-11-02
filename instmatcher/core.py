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

'''Module to search for known institutions.'''

import csv
from pkg_resources import resource_filename
import re

from whoosh import index
from whoosh.qparser import MultifieldParser
from whoosh.query import Term

# load the available abbreviations from 'data/abbreviations.csv'
abbreviations = {}
source = resource_filename(__name__, 'data/abbreviations.csv')
with open(source) as csvfile:
	data = filter(lambda row: not row[0].startswith('#'), csvfile)
	reader = csv.reader(data)
	for row in reader:
		abbreviations[row[0]] = row[1]

# load the index and create the institution and coordinate query parsers
ixPath = resource_filename(__name__, 'data/index')
ix = index.open_dir(ixPath)
instParser = MultifieldParser(['name', 'alias',], ix.schema)
coordParser = MultifieldParser(['lat', 'lon',], ix.schema)

def query(institution, alpha2, lat, lon, offset):
	'''
	Search for institutions compatible to the search parameters sorted
	in descending order starting with the most accurate search result.
	
	Applying the ISO 3166-1 alpha-2 country code will restrict the
	search results to the given country.
	The latitude, longitude and offset (in degree of arcs) parameters
	describe a geographical box in which results are preferred. Note that
	an offset of one degree of arc corresponds to about 111 km: Using an
	offset of 1 results into a box with a width of approximately 222 km.
	
	:param institution: the institution name to search for
	:param alpha2: the country to restrict search results to
	:param lat: the latitude describing the middle of the preferred box
	:param lon: the longitude describing the middle of preferred box
	:param offset: the half-width of the preferred box in degree of arcs
	'''
	if not institution:
		return
	with ix.searcher() as searcher:
		# search for the given institution
		instQuery = instParser.parse(institution)
		filterTerm = Term('alpha2', alpha2) if alpha2 else None
		instResults = searcher.search(instQuery, limit=None, filter=filterTerm)
		# try to enhance the search boosting results in the vicinity of lat/lon
		try:
			latQueryText = 'lat:[{} to {}]'.format(lat - offset, lat + offset)
			lonQueryText = 'lon:[{} to {}]'.format(lon - offset, lon + offset)
			coordQuery = coordParser.parse(latQueryText + lonQueryText)
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
				'type': hit['type'],
			}, hit.score

def expandAbbreviations(text):
	'''
	Expand known abbreviations in the supplied string.
	Known abbreviations may be found in data/abbreviations.csv.
	
	:param text: the text in which abbreviations should be expanded
	'''
	try:
		for abbrev, expansion in abbreviations.items():
			text = re.sub(r"\b(?i){}\b".format(abbrev), expansion, text)
	except TypeError:
		pass
	return text
