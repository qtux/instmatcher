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

'''Module to retrieve coordinates of a given settlement'''

from pkg_resources import resource_filename

from whoosh import index
from whoosh.qparser import MultifieldParser
from whoosh.query import Term

# load the index and create the settlement/alpha2 query parser
ixPath = resource_filename(__name__, 'data/geoindex')
ix = index.open_dir(ixPath)
parser = MultifieldParser(['lower', 'asci', 'alias',], ix.schema)

def geocodeAll(settlement, alpha2=None):
	'''
	Yield all geographical coordinates of a given settlement name,
	optionally restricting search results to a specified country.
	
	:param settlement: the settlement name to search for
	:param alpha2: the country to restrict search results to
	'''
	if not settlement:
		return
	lower = settlement.lower()
	text = "'" + lower + "' OR '" + lower.replace(' ', '-') + "'"
	query = parser.parse(text)
	filterTerm = Term('alpha2', alpha2) if alpha2 else None
	with ix.searcher() as searcher:
		results = searcher.search(query, limit=None, filter=filterTerm)
		for hit in results:
			yield {
				'lat': float(hit['lat']),
				'lon': float(hit['lon']),
				'locality': hit['name'],
			}

def geocode(settlement, alpha2=None):
	'''
	Get the most accurate geographical coordinate of a given settlement
	name, optionally restricting search results to a specified country.
	
	:param settlement: the settlement name to search for
	:param alpha2: the country to restrict search results to
	'''
	try:
		return next(geocodeAll(settlement, alpha2))
	except StopIteration:
		return
