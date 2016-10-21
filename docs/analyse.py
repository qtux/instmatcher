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
			'alpha2',
			'country',
			'lat',
			'lon',
		])
		writer.writerow(fieldnames)
		for row in reader:
			result = instmatcher.extract(row[0])
			writer.writerow([
				row[0],
				result['institution'],
				result['settlement'],
				result['alpha2'],
				result['country'],
				result.get('lat'),
				result.get('lon'),
			])

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Analyse classification.')
	parser.add_argument('-s', '--sample', help='path to the sample file')
	parser.add_argument('-u', '--url', default='http://0.0.0.0:8080',
		help='url of the grobid server (default: %(default)s)')
	parser.add_argument('-c', '--classify', action='store_true',
		help='manually classify matcing results')
	parser.add_argument('-e', '--extract', action='store_true',
		help='extract information from affiliation strings')
	args = parser.parse_args()
	if args.classify:
		classify(args.sample, args.url)
	if args.extract:
		extract(args.sample, args.url)
