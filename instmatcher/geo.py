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

try:
	_required = ['citycoord',]
	import citycoord
	_required.remove('citycoord')
except ImportError:
	pass

def defaultArea(city, cc, radius=None):
	return None

def citycoordArea(city, cc, radius=111):
	if not city:
		return None
	for pkg in _required:
		raise ImportError('{} is required to use citycoordArea'.format(pkg))
	results = citycoord.geocode(city, cc)
	for hit in results:
		lat = hit['lat']
		lon = hit['lon']
		# one degree of arc corresponds to about 111 km
		offset = radius / 111
		return {
			'lat': {
				'min': lat - offset,
				'max': lat + offset,
			},
			'lon': {
				'min': lon - offset,
				'max': lon + offset,
			},
		}
	return None
