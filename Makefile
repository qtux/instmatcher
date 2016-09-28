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

.SUFFIXES:
.PHONY: all clean clean-all

# Wikidata query related variables
QUERY_URL		:= https://query.wikidata.org/bigdata/namespace/wdq/sparql
QUERIES			:= $(wildcard query/*.sparql)
QUERY_RESULTS	:= $(patsubst %.sparql,%.csv, $(QUERIES))
JOINED_RESULT	:= query/query.csv

# Natural Earth shapefiles related variables
NAT_EARTH_URL	:= http://www.naturalearthdata.com/http//www.naturalearthdata.com/download/10m/cultural
SHAPE_PREFIX	:= query/ne_10m_admin_0_countries
SHAPE_ZIP		:= $(addprefix $(SHAPE_PREFIX), .zip)
SHAPE_FILES		:= $(addprefix $(SHAPE_PREFIX), .cpg .dbf .prj .shp .shx)

TARGET_FILE		:= instmatcher/data/institutes.csv
COUNTRY_INFO	:= instmatcher/data/countryInfo.txt
FAILURE_FILE	:= query/failures.csv

# create the target file containing a list of organisations
all: $(TARGET_FILE)

# enhance the queried items adding country information
$(TARGET_FILE): $(JOINED_RESULT) $(SHAPE_FILES)
	python3 query/enhance.py \
	--src $< \
	--dest $@ \
	--fails $(FAILURE_FILE) \
	--countries $(COUNTRY_INFO)

# join the retrieved csv files into a single file
$(JOINED_RESULT): $(QUERY_RESULTS)
	head -1 $< > $@
	tail -n +2 -q $+ >> $@

# retrieve data from WikiData as a csv file
%.csv: %.sparql
	curl -G -H "Accept: text/csv" $(QUERY_URL) --data-urlencode query@$< > $@

# extract the shapefiles
%.cpg %.dbf %.prj %.shp %.shx: %.zip
	unzip -u $< -d $(dir $<)

# download the shapefiles
$(SHAPE_ZIP):
	wget $(NAT_EARTH_URL)/$(notdir $@) -P $(dir $@)

clean:
	rm -rf $(SHAPE_FILES)
	rm -rf $(QUERY_RESULTS)

clean-all:
	rm -rf $(SHAPE_PREFIX).*
	rm -rf $(QUERY_RESULTS)
	rm -rf $(FAILURE_FILE)
