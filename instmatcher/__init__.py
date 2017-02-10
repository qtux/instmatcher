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

'''
A library to match an affiliation string to a known institution.

This library provides means to search for an institution by its name and
means to extract information using either the internal geocoder along
with an external grobid server or by providing self-defined functions.
'''

from .core import findAll, find
from .geo import geocodeAll, geocode
from .parser import parseAll, parse
from .version import __version__

def matchAll(string, url='http://0.0.0.0:8080', offset=1):
	'''
	Yield all institutions matching the affiliation string using a
	grobid service to parse the string.
	
	:param string: the affiliation string to be extracted
	:param url: the URL to the grobid service
	:param offset: the half-width of the preferred box in degree of arcs
	'''
	for parsed in parseAll(string, url):
		alpha2 = parsed.get('alpha2')
		for settlement in parsed['settlement']:
			for coord in geocodeAll(settlement, alpha2):
				institutions = findAll(
					institution=parsed.get('institution'),
					alpha2=alpha2,
					lat=coord.get('lat'),
					lon=coord.get('lon'),
					offset=offset
				)
				for instit in institutions:
					yield instit

def match(string, url='http://0.0.0.0:8080', offset=1):
	'''
	Find the most accurate institution matching the affiliation string
	using a grobid service to parse the string.
	
	:param string: the affiliation string to be extracted
	:param url: the URL to the grobid service
	:param offset: the half-width of the preferred box in degree of arcs
	'''
	try:
		return next(matchAll(string, url, offset))
	except StopIteration:
		return
