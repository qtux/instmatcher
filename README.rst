instmatcher
===========
A tool to match an affiliation string to a list of known institutes.

Installation
============
To install instmatcher simply clone the git repository and install it using pip: ::

  git clone https://github.com/qtux/instmatcher.git
  cd instmatcher
  pip install .

Basic Usage Example
===================
This library must be initialised with the ``init`` function before using any other functions.
This will create an index if it does not exist yet and initialise internal variables.

The ``find`` function can be used to find an institute searching for a given name:

.. code:: python

    import instmatcher
    
    instmatcher.init()
    institute = instmatcher.find('TU Berlin')
    print(institute)

Executing the code above will print the following dictionary: ::

    {
        'name': 'Technical University of Berlin',
        'isni': '0000 0001 2195 9817',
        'lat': '52.511944444444',
        'lon': '13.326388888889',
        'country': 'Germany',
        'alpha2': 'DE'
    }

Note that using the ``findAll`` function instead allows to retrieve a generator of all the matching institutes sorted by their score.

Advanced Usage Example
======================
It is also possible to search for an institute supplying an affiliation string, a string containing the organisation name, subdivision and/or the full address.
The library provides the ``extract`` function which tries to return a dictionary retrieving the

- institute
- city
- country
- ISO 3166-1 alpha 2 code
- latitude
- longitude

Note that this function requires a `grobid`_ instance running for example at **http://localhost:8080**.

.. code:: python

    from instmatcher import init, extract, find
    import os
    
    init(
        procs=os.cpu_count(),
        initGeo=True,
        grobidUrl='http://localhost:8080'
    )
    string = 'TU Berlin, Berlin, Germany'
    structured = extract(string)
    institute = find(**structured)
    print(institute)

It might produce the same output as the previous example depending on how `grobid`_ is trained.
Note that this example shows on how to use every available CPU core to reduce the time
for initialising the main index and especially the index for the geographical coordinates.

Additionally, there is also an ``extractAll`` function which provides a generator of all possible geographic locations sorted by their likelihood.
Note that the library has a bias towards cities with a higher population in order to retrieve the matching geographical coordinate.

Using self-defined parser and/or geocoder
=========================================
It is also possible to supply self-defined parsing and geocoding functions to the ``extract`` and ``extractAll`` functions
instead of using the default ``parser.grobid`` and ``geo.geocode`` functions.

The parser function takes an affiliation string and returns a generator providing dictionaries consisting of the

- institute
- city
- country
- ISO 3166-1 alpha 2 code

The geocoding function takes a city name and the ISO 3166-1 alpha 2 code and returns a generator providing the most likely

- latitude
- longitude
- country
- ISO 3166-1 alpha 2 code

.. code:: python

    from instmatcher import init, extract, find
    
    def dummyParse(affiliation):
        if affiliation.startswith('TU Berlin'):
            return {
                'institute': 'TU Berlin',
                'city': 'Berlin',
                'country': 'Germany',
                'alpha2': 'DE',
        }
        return None
    
    def dummyGeocode(city, alpha2, **ignore):
        if city == 'Berlin' and alpha2 == 'DE':
            yield {
                'lat': 52.52437,
                'lon': 13.41053,
                'alpha2': 'DE',
                'country': 'Germany',
            }
    
    init()
    string = 'TU Berlin, Berlin, Germany'
    structured = extract(string, dummyParse, dummyGeocode)
    institute = find(**structured)
    print(institute)

In this specific case this will print the same as in the examples above.

Run Tests
=========
Run ::

  python setup.py test

to execute the tests.

Build Documentation
===================
Install the required packages using ::

  pip install .[doc]

and use the Makefile in the docs folder to build a documentation.

Query and Enhance Institute List
================================
Install the optional dependencies required to run the Python script: ::

  pip install .[data]

and use the Makefile in the 
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
