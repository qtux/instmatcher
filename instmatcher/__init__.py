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

from . import core
from . import geo
from . import parser

def init(procs=1, initGeo=False, grobidUrl='http://localhost:8080'):
	multisegment = procs > 1
	core.init(procs, multisegment, './index')
	parser.init(grobidUrl)
	if initGeo:
		geo.init(procs, multisegment, './geoindex')

def findAll(institute, alpha2=None, lat=None, lon=None, offset=1, **ignore):
	if not institute:
		return
	fullName = core.expandAbbreviations(institute)
	for result in core.query(fullName, alpha2, lat, lon, offset):
		yield result[0]

def find(institute, alpha2=None, lat=None, lon=None, offset=1, **ignore):
	try:
		return next(findAll(institute, alpha2, lat, lon, offset))
	except StopIteration:
		return None

def extractAll(string, parse=parser.grobid, geocode=geo.geocode):
	affiDict = parse(string)
	emptyGenerator = True
	for position in geocode(**affiDict):
		emptyGenerator = False
		result = affiDict.copy()
		result.update(position)
		yield result
	if emptyGenerator:
		yield affiDict

def extract(string, parse=parser.grobid, geocode=geo.geocode):
	return next(extractAll(string, parse, geocode))
