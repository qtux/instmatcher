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
import fiona
from shapely import geometry
import argparse

def getCountry(lat, lon, codes, countries, hint=None):
	# try to find the hint as a country name (geonames.org data)
	try:
		alpha2 = codes[hint]
		country = hint
		return country, alpha2
	except KeyError:
		pass
	
	# try to find the hint as a country name (Natural Earth data)
	with fiona.open('ne_10m_admin_0_countries.shp', 'r') as source:
		for record in source:
			name = record['properties']['NAME']
			longName = record['properties']['NAME_LONG']
			if name == hint or longName == hint:
				alpha2 = record['properties']['ISO_A2']
				try:
					country = countries[alpha2]
				except KeyError:
					alpha2 = None
					country = longName
				return country, alpha2

	# search for a country using the coordinates (Natural Earth data)
	point = geometry.Point(lon, lat)
	with fiona.open('ne_10m_admin_0_countries.shp', 'r') as source:
		for record in source:
			shape = geometry.asShape(record['geometry'])
			if shape.contains(point):
				alpha2 = record['properties']['ISO_A2']
				try:
					country = countries[alpha2]
				except KeyError:
					country = record['properties']['NAME_LONG']
					try:
						alpha2 = codes[country]
					except KeyError:
						alpha2 = None
				return country, alpha2
	
	# return None if no country could be associated
	return None, None

def enhance(src, dest, fail, countryInfo):
	# load country names and the corresponding ISO 3166-1 alpha-2 code
	codes, countries = {}, {}
	with open(countryInfo) as csvfile:
		data = filter(lambda row: not row[0].startswith('#'), csvfile)
		reader = csv.reader(data, delimiter='\t', quoting=csv.QUOTE_NONE)
		for row in reader:
			countries[row[0]] = row[4]
			codes[row[4]] = row[0]
	# enhance the data
	i = 0
	with open(src, 'r') as s, open(dest, 'w') as d, open(fail, 'w') as f:
		source = csv.reader(s)
		destination = csv.writer(d)
		failures = csv.writer(f)
		
		fieldnames = next(source)
		failures.writerow(fieldnames)
		fieldnames.append('alpha2')
		index = {}
		for field in fieldnames:
			index[field] = fieldnames.index(field)
		destination.writerow(fieldnames)
		
		for row in source:
			hint = row[index['country']]
			lat = float(row[index['lat']])
			lon = float(row[index['lon']])
			country, alpha2 = getCountry(lat, lon, codes, countries, hint)
			if not country:
				failures.writerow(row)
				continue
			row[index['country']] = country
			row.append(alpha2)
			destination.writerow(row)
			
			i += 1
			if i % 100 == 0:
				print('processed {} rows'.format(i))

def main():
	parser = argparse.ArgumentParser(
		description='Enhance institute data using pyCountry and Natural Earth.'
	)
	parser.add_argument(
		'-src',
		'--source',
		default='query.csv',
		help='the source list (default: %(default)s)'
	)
	parser.add_argument(
		'-dest',
		'--destination',
		default='institutions.csv',
		help='the target (enhanced) list (default: %(default)s)'
	)
	parser.add_argument(
		'-fail',
		'--failures',
		default='failures.csv',
		help='a list of failed target (enhanced) list (default: %(default)s)'
	)
	parser.add_argument(
		'-cntr',
		'--country',
		default='countryInfo.txt',
		help='the geonames list of country details (default: %(default)s)'
	)
	args = parser.parse_args()
	enhance(args.source, args.destination, args.failures, args.country)

if __name__ == '__main__':
	main()
