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

from .core import query, expandAbbreviations
from .geo import geocode
from .parser import parse
from .version import __version__

def _appendDoc(docstring):
	def decorator(function):
		function.__doc__ += docstring
		return function
	return decorator

################################ init function ################################

def init(grobidUrl='http://localhost:8080'):
	'''
	Set the URL pointing to the grobid service.
	
	:param grobidUrl: the URL to the grobid service
	'''
	parser.init(grobidUrl)

############################### find functions ################################
_find_doc = '''
	Applying the ISO 3166-1 alpha-2 country code will restrict the
	search results to the given country.
	The latitude, longitude and offset (in degree of arcs) parameters
	describe a geographical box in which results are preferred. Note that
	an offset of one degree of arc corresponds to about 111 km: Using an
	offset of 1 results into a box with a width of approximately 222 km.
	
	:param institution: the list of institutions to search for
	:param alpha2: the country to restrict search results to
	:param lat: the latitude describing the middle of the preferred box
	:param lon: the longitude describing the middle of preferred box
	:param offset: the half-width of the preferred box in degree of arcs
	:param ignore: ignored keyword arguments
'''

@_appendDoc(_find_doc)
def findAll(institution, alpha2=None, lat=None, lon=None, offset=1, **ignore):
	'''
	Yield all institutions compatible to the search parameters sorted in
	descending order starting with the most accurate search result.
	'''
	if not isinstance(institution, list):
		return
	for inst in institution:
		fullName = expandAbbreviations(inst)
		for result in query(fullName, alpha2, lat, lon, offset):
			yield result[0]

@_appendDoc(_find_doc)
def find(institution, alpha2=None, lat=None, lon=None, offset=1, **ignore):
	'''
	Find the most accurate institution described by the search parameters.
	'''
	try:
		return next(findAll(institution, alpha2, lat, lon, offset))
	except StopIteration:
		return

############################## extract functions ##############################
_extract_doc = '''
	:param string: the affiliation string to be extracted
	:param parse: a function to parse the affiliation string
	:param geocode: a function to retrieve coordinates of a settlement
'''

@_appendDoc(_extract_doc)
def extractAll(string, parse=parse, geocode=geocode):
	'''
	Yield the data extracted from the affiliation string augmented with
	each compatible geographical location. The generator is sorted in a
	descending order starting with the most likely coordinate.
	'''
	affiDict = parse(string)
	emptyGenerator = True
	for settlement in affiDict['settlement']:
		for position in geocode(settlement, affiDict['alpha2']):
			emptyGenerator = False
			result = affiDict.copy()
			result.update(position)
			yield result
	if emptyGenerator:
		yield affiDict

@_appendDoc(_extract_doc)
def extract(string, parse=parse, geocode=geocode):
	'''
	Extract the data from the given affiliation string and augment it
	with the most likely geographical location.
	'''
	return next(extractAll(string, parse, geocode))

############################### match function ################################

def match(string, parse=parse, geocode=geocode, offset=1):
	'''
	Find the most accurate institution matching the affiliation string.
	
	:param string: the affiliation string to be extracted
	:param parse: a function to parse the string into a structure
	:param geocode: a function to retrieve coordinates of a settlement
	'''
	return find(offset=offset, **extract(string, parse, geocode))
