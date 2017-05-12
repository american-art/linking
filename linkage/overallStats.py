from SPARQLWrapper import SPARQLWrapper, JSON
from urllib2 import URLError
import os, sys, json, time

classes = ["triples","labels"]
bases = ["aaa","acm","autry","cbm","ccma","dma","GM","ima","nmwa","npg","puam","saam","wam","YCBA"]

constituents = ["E21_Person","E39_Actor","E40_Legal_Body","E74_Group"]
objects = ["E22_Man-Made_Object","E84_Information_Carrier"]
events = ["E5_Event","E6_Destruction","E7_Activity","E8_Acquisition","E9_Move","E10_Transfer_of_Custody",
                "E11_Modification","E12_Production","E13_Attribute_Assignment","E14_Condition_Assessment",
                "E15_Identifier_Assignment","E16_Measurement","E17_Type_Assignment","E79_Part_Addition",
                "E80_Part_Removal","E63_Beginning_of_Existence","E64_End_of_Existence","E65_Creation",
                "E66_Formation","E67_Birth","E68_Dissolution","E69_Death","E81_Transformation","E83_Type_Creation",
                "E85_Joining","E86_Leaving","E87_Curation_Activity"]
places = ["E53_Place"]

# All classes
all_classes = []
all_classes = classes + all_classes + constituents + objects + events + places

out = {"total":{}}
f_in = open("overallStats.sparql", 'r')
base_query = f_in.read()
f_in.close()

for b in bases:
    print ("Base is "+b)
    graph_query = base_query.replace("<graph>",b)
    sparql = SPARQLWrapper("http://data.americanartcollaborative.org/sparql")
    out_c = {"constituents":0,"objects":0,"events":0,"places":0}
    
    for c in all_classes:
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

        if c in constituents:
            out_c["constituents"] += int(results["results"]["bindings"][0]["c"]["value"])
        elif c in objects:
            out_c["objects"] += int(results["results"]["bindings"][0]["c"]["value"])
        elif c in events:
            out_c["events"] += int(results["results"]["bindings"][0]["c"]["value"])
        elif c in places:
            out_c["places"] += int(results["results"]["bindings"][0]["c"]["value"])
        else:
            out_c[c] = int(results["results"]["bindings"][0]["c"]["value"])

    out[b] = out_c
    print (json.dumps(out_c, indent=4, sort_keys=True))
    
    for key in out_c:
        if key in out["total"]:
            out["total"][key] += out_c[key]
        else:
            out["total"][key] = out_c[key]

print ("\nTotal \n")
print (json.dumps(out["total"], indent=4, sort_keys=True))