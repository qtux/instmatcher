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

def enhance(src, dest, countryInfo):
	# load country names indexed by the corresponding ISO 3166-1 alpha-2 code
	countryOf = {}
	with open(countryInfo) as csvfile:
		data = filter(lambda row: not row[0].startswith('#'), csvfile)
		reader = csv.reader(data, delimiter='\t', quoting=csv.QUOTE_NONE)
		for row in reader:
			countryOf[row[0]] = row[4]
	
	# store fieldnames and organisations
	with open(src, 'r') as s:
		source = csv.reader(s)
		fieldnames = next(source)
		fieldnames.append('alpha2')
		organisations = list(source)
	
	# create the index of the fieldnames
	index = {}
	for name in fieldnames:
		index[name] = fieldnames.index(name)
	
	# store the coordinates of every organisation in a separate list
	coords = []
	for row in organisations:
		latLon = float(row[index['lat']]), float(row[index['lon']])
		coords.append(latLon)
	
	# reverse geocode the coordinates and store the ISO 3166-1 alpha-2 code
	codes = [item['cc'] for item in rg.search(coords)]
	# retrieve the country name based on the ISO 3166-1 alpha-2 code
	countries = [countryOf[item] for item in codes]
	# combine the results
	for org, country, code in zip(organisations, countries, codes):
		org[index['country']] = country
		org.append(code)
	
	# write the results
	with open(dest, 'w') as d:
		destination = csv.writer(d)
		destination.writerow(fieldnames)
		destination.writerows(organisations)

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
		'--countries',
		default='countryInfo.txt',
		help='the geonames list of country details (default: %(default)s)'
	)
	args = parser.parse_args()
	
	# start enhancing
	enhance(args.src, args.dest, args.countries)

if __name__ == '__main__':
	main()
