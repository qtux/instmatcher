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

from .core import query, init, expandAbbreviations
from .parser import grobidParse
from .geo import defaultArea, citycoordArea

init()

def match(affiliation, parse, defArea=defaultArea):
	parsedAffiliation = parse(affiliation)
	# search for a match if parsing succeeded
	try:
		area = defArea(parsedAffiliation['city'], parsedAffiliation['cc'])
		inst = expandAbbreviations(parsedAffiliation['institute'])
		return query(inst, area)
	# otherwise return None
	except TypeError:
		return None

