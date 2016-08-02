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

def init(procs=1, multisegment=False, ixName='geoindex', force=False):
	if not os.path.exists(ixName):
		os.mkdir(ixName)
		force = True
	if force:
		print('creating the geoindex - this may take some time')
		schema = Schema(
			name=ID(stored=True),
			asci=ID,
			alias=IDLIST(expression=r"[^,]+"),
			lat=STORED,
			lon=STORED,
			cc=ID,
		)
		ix = index.create_in(ixName, schema)
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
					cc=row[8],
					_boost=boost,
				)
		writer.commit()
	
	global _ix, _parser
	_ix = index.open_dir(ixName)
	_parser =  MultifieldParser(['name', 'asci', 'alias', 'cc',], _ix.schema)

def geocode(city, cc):
	if not city:
		return None, None
	text = 'name:"{key}" OR asci:"{key}" OR alias:({key})'.format(key=city)
	if cc:
		text = '(' + text + ') AND cc:{key}'.format(key=cc)
	query = _parser.parse(text)
	with _ix.searcher() as searcher:
		results = searcher.search(query, limit=None)
		for hit in results:
			return hit['lat'], hit['lon']
	return None, None
