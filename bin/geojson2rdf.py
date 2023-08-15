import argparse
import json
from pathlib import Path
from urllib.parse import urljoin
from rdflib import Graph, Literal, RDF, DCTERMS, URIRef, Namespace, BNode

BEZIRKS_MAPPING = {
    '01': "Mitte",
    '02': "Friedrichshain-Kreuzberg",
    '03': "Pankow",
    '04': "Charlottenburg-Wilmersdorf",
    '05': "Spandau",
    '06': "Steglitz-Zehlendorf",
    '07': "Tempelhof-Schöneberg",
    '08': "Neukölln",
    '09': "Treptow-Köpenick",
    '10': "Marzahn-Hellersdorf",
    '11': "Lichtenberg",
    '12': "Reinickendorf"
}

LOR_LEVELS = [
    {
        "code": "bez",
        "title": "Bezirk"
    } ,
    {
        "code": "pgr",
        "title": "Prognoseraum"
    } ,
    {
        "code": "bzr",
        "title": "Bezirksregion"
    } ,
    {
        "code": "plr",
        "title": "Planungsraum"
    }
]
LOR_LEVEL_MAPPING = { level['code']: level['title'] for level  in LOR_LEVELS }

# Bezirk
# --- keine Quelle ---
#
# Prognoseraum (PGR)
#
# {
#   "gml_id": "s_lor_pgr_2021.A2B345B9-EF98-41F6-B211-3268AEB18307",
#   "PGR_ID": 370,
#   "PGR_NAME": "Südlicher Prenzlauer Berg",
#   "BEZ": 3,
#   "FINHALT": 3031116.98728661,
#   "STAND": "01.01.2021"
# }
#
# Bezirksregion (BZR)
#
# {
#   "gml_id": "s_lor_bzr_2021.AFCF580B-39F3-46EA-821D-5F0C42907CBB",
#   "BZR_ID": 112005,
#   "BZR_NAME": "Alt-Hohenschönhausen Süd",
#   "PGR_ID": 1120,
#   "PGR_NAME": "Hohenschönhausen Süd",
#   "BEZ": 11,
#   "FINHALT": 4599199.14949298,
#   "STAND": "01.01.2021"
# }
#
# Planungsraum (PLR)
#
# {
#   "gml_id": "s_lor_plr_2021.AA05BB83-33FF-4C96-8871-3959322C993D",
#   "PLR_ID": 11501341,
#   "PLR_NAME": "Karlshorst Süd",
#   "BZR_ID": 115013,
#   "BZR_NAME": "Karlshorst",
#   "PGR_ID": 1150,
#   "PGR_NAME": "Lichtenberg Süd",
#   "BEZ": 11,
#   "FINHALT": 2294053.90379473,
#   "STAND": "01.01.2021"
# }

def fix_lor_id(lor_id):
    '''
    LOR ids always begin with the id of the Bezirk, which can be "01"-"12".
    If the leading "0" is missing (can happen during transformation from source XML
    to JSON via ogr2ogr), it needs to be added again.
    '''
    if len(lor_id) % 2 != 0:
        return f"0{lor_id}"
    return lor_id

def convert_to_rdf(graph, source_folder, level):
    level_code = LOR_LEVELS[level]['code']
    container_code = LOR_LEVELS[level-1]['code']
    geojson_path = source_folder / f"{level_code}.geojson"

    with open(geojson_path) as geojson_file:
        features = json.load(geojson_file)['features']

    for feature in features:
        properties = feature['properties']
        lor_id = fix_lor_id(properties[f"{level_code.upper()}_ID"])
        feature_name = f"{level_code}_{lor_id}"
        feature_title = properties[f"{level_code.upper()}_NAME"]
        feature_res = lor[feature_name]
        feature_geometry = json.dumps(feature['geometry'])
        feature_type = unit[LOR_LEVEL_MAPPING[level_code]]

        graph.add( (feature_res, RDF.type, feature_type) )
        graph.add( (feature_res, schema.name, Literal(feature_title)) )
        graph.add( (feature_res, unit.lorCode, Literal(lor_id)) )

        container_id = lor_id[:-2]
        container_name = f"{container_code}_{container_id}"
        container_res = lor[container_name]

        graph.add( (container_res, schema.containsPlace, feature_res) )
        # graph.add( (container_res, geo.contains, feature_res) )
        graph.add( (feature_res, schema.containedInPlace, container_res) )
        # graph.add( (feature_res, geo.within, container_res) )

        bn = BNode()
        graph.add( (feature_res, geo.hasGeometry, bn) )
        graph.add( (bn, geo.asGeoJSON, Literal(feature_geometry, datatype=geo.geoJSONLiteral))  )

parser = argparse.ArgumentParser(
    description="Convert a GeoJson file with LORs to RDF.")
parser.add_argument('--source',
                    default=Path('data/temp/'),
                    type=Path,
                    help="Path to the folder containing the source files. Default is `data/temp/`.")
parser.add_argument('--output',
                    help="Path to the N-Triples output file",
                    type=Path,
                    default=Path('data/target/lors.ttl')
                    )
args = parser.parse_args()

base = "https://berlinonline.github.io/lod-berlin-lor/"
base19 = "https://berlinonline.github.io/lod-berlin-lor-2019/"
graph = Graph()
schema = Namespace("https://schema.org/")
geo = Namespace("http://www.opengis.net/ont/geosparql#")
lor = Namespace(base)
lor19 = Namespace(base19)
unit = Namespace(urljoin(base, "vocab/"))

berlin = lor['berlin']
graph.add( (berlin, RDF.type, schema.State) )
graph.add( (berlin, schema.name, Literal("Berlin")))

for code, title in BEZIRKS_MAPPING.items():
    bezirks_name = f"bez_{code}"
    bezirks_res = lor[bezirks_name]
    
    geojson_path = args.source / "bez.geojson"

    with open(geojson_path) as geojson_file:
        bez_features = json.load(geojson_file)['features']
    bez_geometries = { fix_lor_id(feature['properties']['gem']): feature['geometry'] for feature in bez_features }

    graph.add( (bezirks_res, RDF.type, unit.Bezirk) )
    graph.add( (bezirks_res, unit.lorCode, Literal(code)) )
    graph.add( (bezirks_res, schema.name, Literal(title)) )
    graph.add( (berlin, schema.containsPlace, bezirks_res) )
    # graph.add( (berlin, geo.contains, bezirks_res) )
    graph.add( (bezirks_res, schema.containedInPlace, berlin) )
    # graph.add( (bezirks_res, geo.within, berlin) )

    bn = BNode()
    graph.add( (bezirks_res, geo.hasGeometry, bn) )
    geojson = json.dumps(bez_geometries[code])
    graph.add( (bn, geo.asGeoJSON, Literal(geojson, datatype=geo.geoJSONLiteral))  )

for level in list(range(1,4)):
    convert_to_rdf(graph, args.source, level)

graph.bind("lor", lor)
graph.bind("lor19", lor19)
graph.bind("unit", unit)
graph.bind("geo", geo)
graph.bind("schema", schema)
graph.bind("dct", DCTERMS)

with open(args.output, "w") as output_file:
    output_file.write(graph.serialize(format="turtle"))
