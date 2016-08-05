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
