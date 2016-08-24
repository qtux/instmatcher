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

'''Module to retrieve coordinates of a given city'''

import csv
import os, os.path
import math
from pkg_resources import resource_filename
from whoosh.fields import Schema, STORED, ID, IDLIST
from whoosh import index
from whoosh.qparser import MultifieldParser
from whoosh.query import Term
from . import countries

_ix = None
_parser = None

def init(procs, multisegment, ixPath, force=False):
	'''
	Initialise the index and global variables
	
	Create the index if it does not exist or force is set to True and
	load it along with the parser required for the coordinate search.
	
	:param procs: maximum number of processes for index creation
	:param multisegment: split index into at least #procs segments
	:param ixPath: path to the index
	:param force: recreate the index
	'''
	# create the geoindex if it does not exist or force is enabled
	if not os.path.exists(ixPath):
		os.mkdir(ixPath)
		force = True
	if force:
		print('creating the geoindex - this may take some time')
		schema = Schema(
			name=ID(stored=True),
			asci=ID,
			alias=IDLIST(expression=r"[^,]+"),
			lat=STORED,
			lon=STORED,
			alpha2=ID(stored=True),
			country=ID(stored=True)
		)
		ix = index.create_in(ixPath, schema)
		writer = ix.writer(procs=procs, multisegment=multisegment)
		cities = resource_filename(__name__, 'data/cities1000.txt')
		with open(cities) as f:
			reader = csv.reader(f, delimiter='\t', quoting=csv.QUOTE_NONE)
			for row in reader:
				population = int(row[14])
				boost = math.log(max(math.e, population))
				writer.add_document(
					name=row[1],
					asci=row[2],
					alias=row[3],
					lat=row[4],
					lon=row[5],
					alpha2=row[8],
					country=countries.get(alpha2=row[8]).name,
					_boost=boost,
				)
		writer.commit()
	
	# load the index and create the city/alpha2 query parser
	global _ix, _parser
	_ix = index.open_dir(ixPath)
	_parser = MultifieldParser(['name', 'asci', 'alias',], _ix.schema)

def geocode(city, alpha2, **ignore):
	'''
	Search for geographical coordinates of a given city name, optionally
	restricting search results to a specified country.
	
	:param city: the city name to search for
	:param alpha2: the country to restrict search results to
	:param ignore: ignored keyword arguments
	'''
	if not city:
		return
	text = 'name:"{key}" OR asci:"{key}" OR alias:({key})'.format(key=city)
	query = _parser.parse(text)
	filterTerm = Term('alpha2', alpha2) if alpha2 else None
	with _ix.searcher() as searcher:
		results = searcher.search(query, limit=None, filter=filterTerm)
		for hit in results:
			yield {
				'lat': float(hit['lat']),
				'lon': float(hit['lon']),
				'alpha2': hit['alpha2'],
				'country': hit['country'],
			}
