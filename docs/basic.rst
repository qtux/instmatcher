-----------
Basic Usage
-----------
This library provides four different interaction options:

1. Match affiliation strings to institutions inside the database.
2. Parse affiliation strings using grobid to gain structured data.
3. Geocode previously parsed affiliation strings to retrieve coordinates.
4. Find possible institutions compatible to the search criterions.

Note that matching an affiliation string consists of parsing and geocoding the
affiliation string followed by using the gained information to find an
compatible institution.

In general, every interaction option provides two functions. One to return the
most compatible result and one to return a generator containing every possible
result. In detail, the first result of the generator equals the result of the
function returning only a single item.

============================
1. Match Affiliation Strings
============================
The :func:`instmatcher.match` and :func:`instmatcher.matchAll` functions
retrieve institutions matching the given affiliation string.
Note that both functions require a valid URL to a running grobid server.

.. testcode::

	from pprint import pprint
	from instmatcher import match
	url = 'http://localhost:8080'
	inst = match('TU Berlin, Inst of Math, Berlin, Germany', url)
	pprint(inst)

Executing the code from above will return:

.. testoutput::
	:options: +NORMALIZE_WHITESPACE

	{'alpha2': 'DE',
	 'country': 'Germany',
	 'isni': '0000 0001 2195 9817',
	 'lat': 52.511944444444,
	 'lon': 13.326388888889,
	 'name': 'Technical University of Berlin',
	 'source': 'http://www.wikidata.org/entity/Q51985',
	 'type': 'university'}

============================
2. Parse Affiliation Strings
============================
The :func:`instmatcher.parse` and :func:`instmatcher.parseAll` functions
retrieve structured data from an affiliation string.
Note that both functions require a valid URL to a running grobid server.

.. testcode::

	from pprint import pprint
	from instmatcher import parse
	data = parse('TU Berlin, Inst of Math, Berlin, Germany', 'http://localhost:8080')
	pprint(data)

Executing the code from above will return:

.. testoutput::
	:options: +NORMALIZE_WHITESPACE

	{'alpha2': 'DE',
	 'country': 'Germany',
	 'countrySource': 'regex',
	 'department': 'Inst of Math',
	 'institution': 'TU Berlin',
	 'institutionSource': 'regexReplace',
	 'settlement': ['Inst of Math', 'Berlin']}

Parsed Data Details
-------------------
The parsed data consists of ``alpha2``, ``country``, ``department``,
``institution`` and ``settlement``. The naming schmeme is chosen to conform with
the naming scheme of grobid. Therefore, ``department`` and ``institution`` are
an array of departments and institutions respectively ordered by grobid.

The ``settlement`` array consists of strings assumed to be an settlement name.
It combines the results of grobid and a set of regular expressions.

Note that ``countrySource`` stores whether the country information was retrieved
using the data provided by grobid or by internal regular expressions.
It is set either to the string ``grobid`` or to ``regex``.

======================
3. Geocode Settlements
======================
The :func:`instmatcher.geocode` and :func:`instmatcher.geocodeAll` functions
retrieve the geographical location (``lat`` and ``lon``) along with the main
name (``locality``) of the settlement searched for.

.. testcode::

	from pprint import pprint
	from instmatcher import geocode
	data = geocode('Berlin','DE')
	pprint(data)

Executing the code from above will return:

.. testoutput::
	:options: +NORMALIZE_WHITESPACE

	{'lat': 52.52437,
	 'locality': 'Berlin',
	  'lon': 13.41053}

Note that the ISO 3166-1 alpha-2 country code is an optional parameter.

====================
4. Find Institutions
====================
The :func:`instmatcher.find` and :func:`instmatcher.findAll` functions retrieve
compatible institutions found in the internal database.

.. testcode::

	from pprint import pprint
	from instmatcher import find
	lat, lon = 52.52437, 13.41053
	inst = find('TU Berlin', 'DE', lat, lon)
	pprint(inst)

.. testoutput::
	:options: +NORMALIZE_WHITESPAC

	{'alpha2': 'DE',
	 'country': 'Germany',
	 'isni': '0000 0001 2195 9817',
	 'lat': 52.511944444444,
	 'lon': 13.326388888889,
	 'name': 'Technical University of Berlin',
	 'source': 'http://www.wikidata.org/entity/Q51985',
	 'type': 'university'}

Note that the ISO 3166-1 alpha-2 country code and the geographical coordinates
are optional parameters.
