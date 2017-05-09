from SPARQLWrapper import SPARQLWrapper, JSON
from urllib2 import URLError
import os, sys, json, time

bases = ["autry","ccma","GM","ima","wam"]

for base in bases:
    print ("Base is "+base)
    f_in = open("curationStats.sparql", 'r')
    sparql = SPARQLWrapper("http://data.americanartcollaborative.org/sparql")

    query = f_in.read().replace("???",base)

    #print (query)

    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    sparql.setTimeout(360)
    while True:
        print "Querying ",base," dataset"
        try:
            results = sparql.query().convert()
            break
        except URLError:
            print("Connection to Sparql server failed! Trying again in five seconds!")
            time.sleep(5)
        
    f_in.close()
    
    TP = 0 # When raw ulan id match with curated ulan id
    FP = 0 # When raw ulan id does not match with curated ulan id
    FN = 0 # When raw ulan id is present but curated ulan id is missing
    TN = 0 # When raw ulan id is missing but curated ulan id is present
    for j in results["results"]["bindings"]:
        
        if "curated_ulan" in j and "raw_ulan" in j:
            if j["raw_ulan"]["value"] == j["curated_ulan"]["value"]:
                TP += 1
            elif j["raw_ulan"]["value"] != j["curated_ulan"]["value"]:
                FP += 1
        elif "curated_ulan" in j and "raw_ulan" not in j:
            TN += 1
        else:
            FN += 1

    precision = (TP*1.0) / (TP + FP)
    recall = (TP*1.0) / (TP + FN)
    fscore = (2*precision*recall)/(precision+recall)
    stats = {"counts":{"TP":TP, "FP": FP, "FN": FN, "TN": TN},
            "aggregates":{"Precision": precision, "Recall": recall, "F-Score": fscore}}
    print (json.dumps(stats, indent=4, sort_keys=True))
                    
    # Save the results
    '''
    out = open('curationStats_'+base+'.json','w')
    for j in results["results"]["bindings"]:
        
        o = {"uri":j["uri"]["value"]}
        
        if "raw_ulan" in j:
            o["raw_ulan"] = j["raw_ulan"]["value"]
        
        if "curated_ulan" in j:
            o["curated_ulan"] = j["curated_ulan"]["value"]
        
        out.write(json.dumps(o))
        out.write("\n")
        
    out.close()
    '''