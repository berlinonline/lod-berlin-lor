berlinonline_url = https://raw.githubusercontent.com/berlinonline/lod-berlin-bo/main/data/static/berlinonline.ttl
lors19_url = https://raw.githubusercontent.com/berlinonline/lod-berlin-lor-2019/main/data/target/lors.ttl
wfs_base = https://fbinter.stadt-berlin.de/fb/wfs/data/senstadt/
bez_layer = s_wfs_alkis_bezirk
bez_wfs_url = $(wfs_base)$(bez_layer)

data/temp/void.nt: data/temp
	@echo "converting void.ttl to $@ ..."
	@rdfpipe -o ntriples void.ttl > $@

data/temp/berlinonline.ttl: data/temp
	@echo "downloading $(berlinonline_url) ..."
	@echo "writing to $@ ..."
	@curl -s -o $@ "$(berlinonline_url)"

data/temp/lors19.ttl: data/temp
	@echo "download $(lors19_url) ..."
	@echo "writing to $@ ..."
	@curl -s -o $@ "$(lors19_url)"

data/temp/all19.nt: data/temp data/temp/lors19.ttl data/vocab/units.ttl
	@echo "combining $(filter-out $<,$^) to $@ ..."
	@rdfpipe -o ntriples $(filter-out $<,$^) > $@

data/temp/all19-21.nt: data/target/lors.ttl data/temp/lors19.ttl data/vocab/units.ttl
	@echo "combining $^ to $@ ..."
	@rdfpipe -o ntriples $^ > $@

data/target/links19-21.ttl: data/temp/all19-21.nt
	@echo "computing links between LOR19 and LOR21 ..."
	@echo "writing to $@ ..."
	@arq --data $< --query query/link19-21.sparql | rdfpipe -o turtle - > $@

# This target creates the RDF file that serves as the input to the static site generator.
# All data should be merged in this file. This should include at least the VOID dataset
# description and the actual data.
# The target works by merging all prerequisites 
data/temp/all.nt: data/temp void.ttl data/temp/berlinonline.ttl data/target/lors.ttl data/vocab/units.ttl data/target/links19-21.ttl
	@echo "combining $(filter-out $<,$^) to $@ ..."
	@rdfpipe -o ntriples $(filter-out $<,$^) > $@

cbds: _includes/cbds data/temp/all.nt
	@echo "computing concise bounded descriptions for all subjects in input data"
	@python bin/compute_cbds.py --base="https://berlinonline.github.io/lod-berlin-lor/"

# LOR-related targets

# Conversion of source data to RDF
data/target/lors.ttl: data/temp/bez.geojson data/temp/pgr.geojson data/temp/bzr.geojson data/temp/plr.geojson
	@echo "writing Turtle to $@ ..."
	@python bin/geojson2rdf.py --output=$@

# getting the source data for Bezirke
data/temp/bez.xml: data/temp
	@echo "getting layer $(bez_layer) from $(bez_wfs_url) ..."
	@echo "writing to $@ ..."
	@curl --output $@ "$(bez_wfs_url)?service=wfs&version=2.0.0&request=GetFeature&typeNames=$(bez_layer)"

# getting the source data for Prognoseraum, Bezirksregion, Planungsraum
.PRECIOUS: data/temp/%.xml
data/temp/%.xml: data/temp
	$(eval LAYER := "s_lor_$(basename $(notdir $@))_2021")
	@echo "getting layer $(LAYER) from $(wfs_base)$(LAYER) ..."
	@echo "writing to $@ ..."
	@curl --output $@ "$(wfs_base)$(LAYER)?service=wfs&version=2.0.0&request=GetFeature&typeNames=$(LAYER)"

# Conversion of source data to GeoJSON and projecting to WGS84
data/temp/%.geojson: data/temp/%.xml
	@echo "converting $< to geojson"
	@ogr2ogr -fieldTypeToString All -f "GeoJSON" $@ -s_srs EPSG:25833 -t_srs WGS84 $<

# Just for looking: formatting the source data
data/temp/%.formatted.xml: data/temp/%.xml
	@echo "formatting $<, writing to $@ ..."
	@xmllint --format $< > $@

# Housekeeping

.PHONY: serve-local
serve-local: data/temp/all.nt cbds
	@echo "serving local version of static LOD site ..."
	@bundle exec jekyll serve

clean: clean-temp clean-cbds clean-jekyll

clean-temp:
	@echo "deleting temp folder ..."
	@rm -rf data/temp

data/temp:
	@echo "creating temp directory ..."
	@mkdir -p data/temp

_includes/cbds:
	@echo "creating $@ directory ..."
	@mkdir -p $@

clean-cbds:
	@echo "deleting cbd folder ..."
	@rm -rf _includes/cbds

clean-jekyll:
	@echo "deleting jekyll artifacts ..."
	@rm -rf _site
	@rm -rf .jekyll-cache