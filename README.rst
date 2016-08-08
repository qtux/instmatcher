instmatcher
===========
A tool to match an affiliation string to a list of known institutes.

Installation
============
To install instmatcher simply clone the git repository and install it using pip: ::

  git clone https://github.com/qtux/instmatcher.git
  cd instmatcher
  pip install .

Run Tests
=========
In order to run the test execute: ::

  python setup.py test

Usage Example
=============
This example assumes that a `grobid`_ instance is running at **http://localhost:8080**.
Additionally, the example shows on how to use every available CPU core to reduce the time
for initialising the indices in the ``core`` and especially in the ``geo`` module.

.. code:: python

    from instmatcher import core, geo, parser
    import os

    # init desired modules using every core available
    core.init(os.cpu_count(), True)
    geo.init(os.cpu_count(), True)
    parser.init('http://localhost:8080')

    # match an affiliation using a grobid instance and the integrated geocoder
    affiliation = 'TU Berlin, Berlin, Germany'
    institute = core.match(affiliation, parse=parser.grobid, geocode=geo.geocode)
    print(institute)

This might (it depends on the parser result) print the following: ::

    {
        'name': 'Technical University of Berlin',
        'isni': '0000 0001 2195 9817',
        'lat': '52.511944444444',
        'lon': '13.326388888889',
        'country': 'Germany',
        'alpha2': 'DE'
    }

Advanced Usage Example
======================
It is possible to supply self-defined parsing and geocoding functions instead of using ``parser.grobid`` and ``geo.geocode``.

The parser function takes an affiliation string and returns a dictionary consisting of the

- institute name
- city name
- country name
- ISO 3166-1 alpha 2 code

or ``None`` if the string is not parseable.

The geocoding function takes a city name and the ISO 3166-1 alpha 2 code and returns the corresponding coordinates or ``None, None`` if the city could not be found.

.. code:: python

    from instmatcher import core

    def dummyParse(affiliation):
        if affiliation.startswith('TU Berlin'):
            return {
                'institute': 'TU Berlin',
                'city': 'Berlin',
                'country': 'Germany',
                'cc': 'DE',
        }
        return None

    def dummyGeocode(city, cc):
        if city == 'Berlin' and cc == 'DE':
            return 52.52437, 13.41053
        return None, None

    # init index and internal variables
    core.init()

    # match the affiliation to a known institute
    affiliation = 'TU Berlin, Berlin, Germany'
    institute = core.match(affiliation, dummyParse, dummyGeocode)
    print(institute)

In this specific case this will print the same as before: ::

    {
        'name': 'Technical University of Berlin',
        'isni': '0000 0001 2195 9817',
        'lat': '52.511944444444',
        'lon': '13.326388888889',
        'country': 'Germany',
        'alpha2': 'DE'
    }

Query and Enhance Institute List
================================
Install the optional dependencies required to run the Python script: ::

  pip install .[data]

To update the institute list execute ::

  make

in the data folder inside the Python module to query institutes from `Wikidata`_ and complete it with the country name and ISO 3166-1 alpha 2 code.
This process yields two lists:

1. **institutes.csv** which contains the successfully enhanced data
2. **failures.csv** which contains the data missing information

The data from the second list has to be manually supplied with the missing information and added to the first list.

Attribution
===========
1. The list of `institutes`_ is queried from `Wikidata`_ (available under `CC0`_).
2. The list of `institutes`_ is enhanced using the country shapes from `Natural Earth`_ (in public domain).
3. The list of `cities`_ to upgrade search results is taken from `GeoNames`_  (available under `CC BY 3.0`_).

.. image:: https://raw.githubusercontent.com/qtux/instmatcher/master/attribution.png

License
=======
This software is licensed under the `Apache License, Version 2.0`_.

.. LICENSES
.. _Apache License, Version 2.0: https://www.apache.org/licenses/LICENSE-2.0.html
.. _CC0: https://creativecommons.org/publicdomain/zero/1.0/
.. _CC BY 3.0: http://creativecommons.org/licenses/by/3.0/

.. DATASETS
.. _cities: https://github.com/qtux/instmatcher/blob/master/instmatcher/data/cities1000.txt
.. _institutes: https://github.com/qtux/instmatcher/blob/master/instmatcher/data/institutes.csv

.. DATASOURCES:
.. _Wikidata: https://www.wikidata.org
.. _Natural Earth: http://www.naturalearthdata.com/
.. _GeoNames: http://download.geonames.org/export/dump/

.. OTHER
.. _grobid: https://github.com/kermitt2/grobid
