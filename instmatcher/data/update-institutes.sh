#!/bin/bash

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

QUERY="
SELECT
  (SAMPLE(?name) AS ?name)
  (GROUP_CONCAT(DISTINCT(?altLabel); separator = '; ') AS ?alias)
  (SAMPLE(?country) AS ?country)
  (SAMPLE(?region) AS ?region)
  (SAMPLE(?lat) AS ?lat)
  (SAMPLE(?lon) AS ?lon)
  (SAMPLE(?insi) AS ?isni)
WHERE {
  ?item (wdt:P31/wdt:P279*) wd:Q3918.
  ?item rdfs:label ?name FILTER (lang(?name) = 'en')
  OPTIONAL {
    ?item skos:altLabel ?altLabel
  }
  OPTIONAL {
    ?item wdt:P17 ?countryName.
    ?countryName rdfs:label ?country FILTER (lang(?country) = 'en')
  }
  OPTIONAL {
    ?item wdt:P131 ?_located_in_the_administrative_territorial_entity.
    ?_located_in_the_administrative_territorial_entity rdfs:label ?region FILTER (lang(?region) = 'en')
  }
  ?item p:P625 ?coordinate .
  ?coordinate psv:P625 ?coordinate_node .
  ?coordinate_node wikibase:geoLatitude ?lat .
  ?coordinate_node wikibase:geoLongitude ?lon .
  OPTIONAL {
    ?item wdt:P213 ?insi.
  }
}
GROUP BY ?item
ORDER BY ASC(?name)
"

URL=https://query.wikidata.org/bigdata/namespace/wdq/sparql

curl -G -H "Accept: text/csv" ${URL} --data-urlencode query="${QUERY}" > institutes.csv
