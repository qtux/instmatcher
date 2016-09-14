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
import logging
import datetime

def getCountry(lat, lon, codes, countries, hint=None):
	# try to find the hint as a country name (geonames.org data)
	try:
		alpha2 = codes[hint]
		country = hint
		logging.info('Found alpha-2 code of {}'.format(hint))
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
				logging.info('Found country name of: {}'.format(hint))
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
				logging.info('Found location of ({}, {})'.format(lat, lon))
				return country, alpha2
	
	# return None if no country could be associated
	logging.info('Did not find ({}, {}, {})'.format(lat, lon, hint))
	return None, None

def enhance(src, dest, fail, countryInfo, cacheFile):
	# load cache
	cache = {}
	with open(cacheFile, 'r+') as c:
		reader = csv.reader(c)
		for row in reader:
			cache[(row[0],row[1])] = (row[2], row[3])
	
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
	with open(src, 'r') as s, open(dest, 'w') as d, open(fail, 'w') as f, open(cacheFile, 'a') as c:
		source = csv.reader(s)
		destination = csv.writer(d)
		failures = csv.writer(f)
		cacheMiss = csv.writer(c)
		
		fieldnames = next(source)
		failures.writerow(fieldnames)
		fieldnames.append('alpha2')
		index = {}
		for field in fieldnames:
			index[field] = fieldnames.index(field)
		destination.writerow(fieldnames)
		
		for row in source:
			rawLat, rawLon = row[index['lat']], row[index['lon']]
			try:
				country, alpha2 = cache[(rawLat, rawLon)]
			except KeyError:
				hint = row[index['country']]
				lat, lon = float(rawLat), float(rawLon)
				country, alpha2 = getCountry(lat, lon, codes, countries, hint)
				cacheMiss.writerow([rawLat, rawLon, country, alpha2])
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
	parser.add_argument(
		'--cache',
		default='cache.csv',
		help='the lat/lon to country/alpha2 cache file (default: %(default)s)'
	)
	args = parser.parse_args()
	logging.basicConfig(filename='enhance.log',level=logging.INFO)
	logging.info('Started enhancing institutes at {}'.format(datetime.datetime.now()))
	enhance(args.src, args.dest, args.fails, args.countries, args.cache)

if __name__ == '__main__':
	main()
