import os
import sys
import json

from dotenv import load_dotenv
from SPARQLWrapper import SPARQLWrapper, JSON
from rdflib import Graph, URIRef, Literal, Namespace

def get_reified_statements(wd_entity):
    wd_endpoint = "https://query.wikidata.org/sparql"
    user_agent = 'CoolBot/0.0 (https://example.org/coolbot/; coolbot@example.org)'
    sparql = SPARQLWrapper(wd_endpoint, agent=user_agent)
    query = f"""
    SELECT ?property ?propertyLabel ?value ?valueLabel WHERE {{
      wd:{wd_entity} ?prop ?value .
      ?property wikibase:directClaim ?prop .
      SERVICE wikibase:label {{ bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }}
    }}
    """
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    return results

def save_statements_as_ttl(entity_id, results, output_path):
    g = Graph()

    WD = Namespace("http://www.wikidata.org/entity/")

    for result in results["results"]["bindings"]:
        s = WD[entity_id]
        p = URIRef(result["property"]["value"])
        o_val = result["value"]["value"]
        o = URIRef(o_val) if o_val.startswith("http") else Literal(o_val)
        g.add((s, p, o))

    g.serialize(destination=output_path, format="turtle")
    return

def main(wd_entity, output_dir):
    output_path = os.path.join(output_dir, f"{wd_entity}_reified.ttl")
    results = get_reified_statements(wd_entity)
    save_statements_as_ttl(wd_entity, results, output_path)

if __name__ == "__main__":

    load_dotenv()

    wd_entity = os.getenv("WIKIDATA_ENTITY")
    wp_title = os.getenv("WIKIPEDIA_TITLE")
    output_dir = os.path.join("../data", wp_title)

    main(wd_entity, output_dir)