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
import argparse
import sys
import reverse_geocoder as rg

def enhance(src, dest, fail, countryInfo):
	# load country names indexed by the corresponding ISO 3166-1 alpha-2 code
	countries = {}
	with open(countryInfo) as csvfile:
		data = filter(lambda row: not row[0].startswith('#'), csvfile)
		reader = csv.reader(data, delimiter='\t', quoting=csv.QUOTE_NONE)
		for row in reader:
			countries[row[0]] = row[4]
	
	# enhance the data
	i = 0
	with open(src, 'r') as s, open(dest, 'w') as d:
		source = csv.reader(s)
		destination = csv.writer(d)
		
		fieldnames = next(source)
		fieldnames.append('alpha2')
		index = {}
		for field in fieldnames:
			index[field] = fieldnames.index(field)
		destination.writerow(fieldnames)
		
		for row in source:
			lat = float(row[index['lat']])
			lon = float(row[index['lon']])
			result = rg.get((lat, lon))
			alpha2 = result['cc']
			country = countries[alpha2]
			row[index['country']] = country
			row.append(alpha2)
			destination.writerow(row)
			i += 1
			if i % 100 == 0:
				print('processed {} rows'.format(i))

def main():
	# parse arguments
	parser = argparse.ArgumentParser(
		description='Enhance institute data using reverse-geocoder.'
	)
	parser.add_argument(
		'--src',
		default='query.csv',
		help='the source list (default: %(default)s)'
	)
	parser.add_argument(
		'--dest',
		default='institutions.csv',
		help='the target (enhanced) list (default: %(default)s)'
	)
	parser.add_argument(
		'--fails',
		default='failures.csv',
		help='a list of failed target (enhanced) list (default: %(default)s)'
	)
	parser.add_argument(
		'--countries',
		default='countryInfo.txt',
		help='the geonames list of country details (default: %(default)s)'
	)
	args = parser.parse_args()
	
	# start enhancing
	enhance(args.src, args.dest, args.fails, args.countries)

if __name__ == '__main__':
	main()
