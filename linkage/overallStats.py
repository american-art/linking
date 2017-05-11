from SPARQLWrapper import SPARQLWrapper, JSON
from urllib2 import URLError
import os, sys, json, time

classes = ["E39_Actor","E22_Man-Made_Object","E12_Production","E53_Place","triples","labels"]
bases = ["aaa","acm","autry","cbm","ccma","dma","GM","ima","nmwa","npg","puam","saam","wam"]
out = {"total":{}}
f_in = open("overallStats.sparql", 'r')
base_query = f_in.read()
f_in.close()

for b in bases:
    print ("Base is "+b)
    graph_query = base_query.replace("<graph>",b)
    sparql = SPARQLWrapper("http://data.americanartcollaborative.org/sparql")
    out_c = {}
    
    for c in classes:
        if c == "triples":
            query = graph_query.replace("?s a crm:<class>","?s ?o ?p")
        elif c == "labels":
            query = graph_query.replace("?s a crm:<class>;","?s a crm:E39_Actor;\n skos:exactMatch ?lod.")
        else:
            query = graph_query.replace("<class>",c)

        #print (query)

        sparql.setQuery(query)
        sparql.setReturnFormat(JSON)
        sparql.setTimeout(360)
        while True:
            try:
                results = sparql.query().convert()
                break
            except URLError:
                print("Connection to Sparql server failed! Trying again in five seconds!")
                time.sleep(5)

        out_c[c] = results["results"]["bindings"][0]["c"]["value"]

    out[b] = out_c
    print (json.dumps(out_c, indent=4, sort_keys=True))
    
    for key in out_c:
        if key in out["total"]:
            out["total"][key] += int(out_c[key])
        else:
            out["total"][key] = int(out_c[key])

print ("\nTotal \n")
print (json.dumps(out["total"], indent=4, sort_keys=True))