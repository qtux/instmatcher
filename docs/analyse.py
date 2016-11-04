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
import instmatcher
import argparse
import pprint
import json

def classify(sample, url):
	pp = pprint.PrettyPrinter(indent=4)
	instmatcher.init(url)
	
	result = sample + '_classified'
	with open(sample, 'r') as s, open(result, 'w') as r:
		reader = csv.reader(s)
		writer = csv.writer(r)
		
		fieldnames = next(reader)
		fieldnames.append('classification')
		writer.writerow(fieldnames)
		
		affiStrings = []
		institutions = []
		
		print('processing affiliation strings...')
		for row in reader:
			affiStrings.append(row[0])
			institutions.append(instmatcher.match(row[0]))
		
		i = 1
		size = len(institutions)
		for affiString, institution in zip(affiStrings, institutions):
			row = [affiString]
			print(chr(27) + "[2J")
			print(affiString, '({} of {})'.format(i, size))
			pp.pprint(institution)
			
			# retrieve an valid input
			answer = input('Is this correct? [y/n] ')
			while answer not in ('y', 'n'):
				answer = input('enter either y or n')
			
			# check for true/false postive and negatives
			classification = 'negative' if not institution else 'positive'
			if answer == 'y':
				row.append('true_' + classification)
			elif answer == 'n':
				row.append('false_' + classification)
			
			# write result
			writer.writerow(row)
			i += 1

def extract(sample, url):
	instmatcher.init(url)
	with open(sample, 'r') as s, open(sample + '_extracted', 'w') as r:
		reader = csv.reader(s)
		writer = csv.writer(r)
		fieldnames = next(reader)
		fieldnames.extend([
			'institution',
			'settlement',
			'postCode',
			'region',
			'alpha2',
			'country',
			'countrySource',
			'lat',
			'lon',
		])
		writer.writerow(fieldnames)
		for row in reader:
			result = instmatcher.extract(row[0])
			writer.writerow([
				row[0],
				json.dumps(result['institution']),
				result['settlement'],
				result.get('postCode'),
				result.get('region'),
				result['alpha2'],
				result.get('country'),
				result.get('countrySource'),
				result.get('lat'),
				result.get('lon'),
			])

def match(sample, url):
	instmatcher.init(url)
	with open(sample, 'r') as s, open(sample + '_matched', 'w') as r:
		reader = csv.reader(s)
		writer = csv.writer(r)
		fieldnames = next(reader)
		fieldnames.extend([
			'name',
			'type',
			'alpha2',
			'country',
		])
		writer.writerow(fieldnames)
		for row in reader:
			result = instmatcher.match(row[0])
			if result:
				writer.writerow([
					row[0],
					result['name'],
					result['type'],
					result['alpha2'],
					result['country'],
				])
			else:
				writer.writerow([row[0],])

def find(sample):
	with open(sample, 'r') as s, open(sample + '_found', 'w') as r:
		reader = csv.DictReader(s)
		fieldnames = reader.fieldnames.copy()
		fieldnames.extend([
			'inst_name',
			'inst_type',
			'inst_alpha2',
			'inst_country',
			'inst_lat',
			'inst_lon',
			'inst_isni',
			'inst_source',
		])
		writer = csv.DictWriter(r, fieldnames=fieldnames)
		writer.writeheader()
		for row in reader:
			result = instmatcher.find(
				json.loads(row['institution']),
				row['alpha2'],
				None if row['lat'] == '' else row['lat'],
				None if row['lon'] == '' else row['lon']
			)
			if result:
				prefixedResult = {}
				for k,v in result.items():
					prefixedResult['inst_' + k] = v
				row.update(prefixedResult)
			writer.writerow(row)

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Analyse classification.')
	parser.add_argument('-s', '--sample', help='path to the sample file')
	parser.add_argument('-u', '--url', default='http://0.0.0.0:8080',
		help='url of the grobid server (default: %(default)s)')
	parser.add_argument('-c', '--classify', action='store_true',
		help='manually classify matcing results')
	parser.add_argument('-e', '--extract', action='store_true',
		help='extract information from affiliation strings')
	parser.add_argument('-m', '--match', action='store_true',
		help='find matching organisations for address nodes')
	parser.add_argument('-f', '--find', action='store_true',
		help='find organisations for extracted information')
	args = parser.parse_args()
	if args.classify:
		classify(args.sample, args.url)
	if args.extract:
		extract(args.sample, args.url)
	if args.match:
		match(args.sample, args.url)
	if args.find:
		find(args.sample)
