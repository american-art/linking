from SPARQLWrapper import SPARQLWrapper, JSON
from urllib2 import URLError
import os, sys, json, time

bases = ["aaa","acm","autry","cbm","ccma","dma","GM","ima","nmwa","npg","puam","saam","wam"]
out = {"total":{}}
f_in = open("curationStats.sparql", 'r')
base_query = f_in.read()
f_in.close()

for base in bases:
    print ("Base is "+base)
    sparql = SPARQLWrapper("http://data.americanartcollaborative.org/sparql")

    query = base_query.replace("???",base)

    #print (query)

    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    sparql.setTimeout(360)
    while True:
        #print "Querying ",base," dataset"
        try:
            results = sparql.query().convert()
            break
        except URLError:
            print("Connection to Sparql server failed! Trying again in five seconds!")
            time.sleep(5)

    TP = 0 # When raw ulan id match with curated ulan id (old-right)
    FP = 0 # When raw ulan id does not match with curated ulan id (old-wrong/new-wrong)
    FN = 0 # When raw ulan id is present but curated ulan id is missing (missed)
    TN = 0 # When raw ulan id is missing but curated ulan id is present (new-right)
    for j in results["results"]["bindings"]:
        
        if "curated_ulan" in j and "raw_ulan" in j:
            if j["raw_ulan"]["value"] == j["curated_ulan"]["value"]:
                TP += 1
            elif j["raw_ulan"]["value"] != j["curated_ulan"]["value"]:
                print ("aac uri :"+j["uri"]["value"]+" raw ulan : "+j["raw_ulan"]["value"]+" curated ulan : "+j["curated_ulan"]["value"])
                FP += 1
        elif "curated_ulan" in j and "raw_ulan" not in j:
            TN += 1
        elif "curated_ulan" not in j and "raw_ulan" in j:
            FN += 1

    if (TP + FP ) > 0:
        precision = (TP*1.0) / (TP + FP)
    else:
        precision = 0.0
        
    if (TP + FN) > 0:
        recall = (TP*1.0) / (TP + FN)
    else:
        recall = 0.0
    
    if (precision+recall) > 0:
        fscore = (2*precision*recall)/(precision+recall)
    else:
        fscore = 0.0
        
    stats = {"counts":{"old-right":TP, "old-wrong/new-wrong": FP, "missed": FN, "new-right": TN},
            "aggregates":{"Precision": precision, "Recall": recall, "F-Score": fscore}}
    
    print (json.dumps(stats, indent=4, sort_keys=True))
    
    out[base] = stats
    
    for key in stats["counts"]:
        if key in out["total"]:
            out["total"][key] += stats["counts"][key]
        else:
            out["total"][key] = stats["counts"][key]

print ("\nTotal \n")
print (json.dumps(out["total"], indent=4, sort_keys=True))