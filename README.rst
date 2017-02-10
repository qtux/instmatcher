===========
instmatcher
===========
This library provides means to find an institution matching an affiliation string, a string consisting of for example a name, an address or similar information associated with the institution.
Its main features are:

1. Search for an institution by its name in a list based on `Wikidata`_ and `GeoNames`_.
2. Parse affiliation strings using `grobid`_ to retrieve the corresponding name and address.
3. Geocode the parsed data to enrich it with geographical coordinates based on `GeoNames`_.

============
Installation
============
To install instmatcher simply clone the git repository and install it using pip: ::

  git clone https://github.com/qtux/instmatcher.git
  cd instmatcher
  pip install .

=============
Usage Example
=============
The ``match`` function may be used to search for a matching institution for a given affiliation string.
Note that this example assumes a `grobid`_ server listening on **http://0.0.0.0:8080**.

.. code:: python

    import instmatcher
    response = instmatcher.match('TU Berlin, Institute of Mathematics, Berlin, Germany')
    print(response)

Depending on how well `grobid`_ is trained, executing the code above will most likely print:

.. code:: python

    {'name': 'Technical University of Berlin', 'lat': '52.511944444444', 'lon': '13.326388888889',...

===========
Development
===========
In order to run the tests execute::

  python setup.py test

In order to build the documentation install the required packages ::

  pip install .[docs]

and use the Makefile in the **docs** folder to build the documentation.

===========
Attribution
===========
1. The list of `institutions`_ is queried from `Wikidata`_ (available under `CC0`_).
2. The list of `institutions`_ is enhanced using the `reverse-geocoder`_ library which contains `GeoNames`_ data (available under `CC BY 3.0`_).
3. The list of `cities`_ and the list of `countries`_ are taken from `GeoNames`_  (available under `CC BY 3.0`_).

.. image:: https://raw.githubusercontent.com/qtux/instmatcher/master/attribution.png

=======
License
=======
This software is licensed under the `Apache License, Version 2.0`_.

.. LICENSES
.. _Apache License, Version 2.0: https://www.apache.org/licenses/LICENSE-2.0.html
.. _CC0: https://creativecommons.org/publicdomain/zero/1.0/
.. _CC BY 3.0: http://creativecommons.org/licenses/by/3.0/

.. DATASETS
.. _cities: https://github.com/qtux/instmatcher/blob/master/instmatcher/data/cities1000.txt
.. _countries: https://github.com/qtux/instmatcher/blob/master/instmatcher/data/countryInfo.txt
.. _institutions: https://github.com/qtux/instmatcher/blob/master/instmatcher/data/institutions.csv

.. DATASOURCES:
.. _Wikidata: https://www.wikidata.org
.. _GeoNames: http://download.geonames.org/export/dump/

.. OTHER
.. _grobid: https://github.com/kermitt2/grobid
.. _reverse-geocoder: https://github.com/thampiman/reverse-geocoder
