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

from whoosh.fields import Schema, TEXT, NUMERIC, STORED
from whoosh import index
from whoosh.qparser import MultifieldParser

def createIndex():
	schema = Schema(
		name=TEXT(stored=True),
		alias=TEXT,
		lat=NUMERIC(numtype=float, stored=True),
		lon=NUMERIC(numtype=float, stored=True),
		isni=STORED,
	)
	
	if not os.path.exists('index'):
		os.mkdir('index')
	ix = index.create_in('index', schema)
	writer = ix.writer()
	
	with open('data/institutes.csv') as csvfile:
		reader = csv.DictReader(csvfile)
		for row in reader:
			writer.add_document(
				name=row['name'],
				alias=row['alias'],
				lat=row['lat'],
				lon=row['lon'],
				isni=row['isni'],
			)
	writer.commit()

def query(searchString):
	fields = ['name', 'alias',]
	ix = index.open_dir('index')
	with ix.searcher() as searcher:
		query = MultifieldParser(fields, ix.schema).parse(searchString)
		results = searcher.search(query, terms=True)
		print(results)
		for hit in results:
			print(hit)
