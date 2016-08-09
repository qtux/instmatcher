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
import math
from pkg_resources import resource_filename
from whoosh.fields import Schema, STORED, ID, IDLIST
from whoosh import index
from whoosh.qparser import MultifieldParser

_ix = None
_parser = None

def init(procs=1, multisegment=False, ixPath='geoindex', force=False):
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
			alpha2=ID,
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
					_boost=boost,
				)
		writer.commit()
	
	# load the index and create the city/alpha2 query parser
	global _ix, _parser
	_ix = index.open_dir(ixPath)
	_parser = MultifieldParser(['name', 'asci', 'alias', 'alpha2',], _ix.schema)

def geocodeAll(city, alpha2):
	if not city:
		return
	text = 'name:"{key}" OR asci:"{key}" OR alias:({key})'.format(key=city)
	if alpha2:
		text = '(' + text + ') AND alpha2:{key}'.format(key=alpha2)
	query = _parser.parse(text)
	with _ix.searcher() as searcher:
		results = searcher.search(query, limit=None)
		for hit in results:
			yield float(hit['lat']), float(hit['lon'])

def geocode(city, alpha2):
	try:
		return next(geocodeAll(city, alpha2))
	except StopIteration:
		return None, None
