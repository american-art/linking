from SPARQLWrapper import SPARQLWrapper, JSON
from urllib2 import URLError
import os, sys, json, time

map = {'ulan':"http://vocab.getty.edu/sparql",
       'aac':"http://data.americanartcollaborative.org/sparql"}

files = os.listdir( os.path.join(os.path.dirname(os.path.realpath(__file__)),'sparql'))

if not os.path.exists('dataset'):
    os.makedirs('dataset')

# Iterate over all SPARQL files
for f in files:
    # Extract museum name
    base = f[:f.index('.')] # ulan, npg etc.
    f_in = open(os.path.join('sparql',f), 'r')
    
    if len(sys.argv) > 1 and base not in sys.argv[1].split():
        continue
    
    # Send SPARQL query
    if base == 'ulan':
        sparql = SPARQLWrapper(map['ulan'])
    else:
        sparql = SPARQLWrapper(map['aac'])
        
    sparql.setQuery(f_in.read())
    sparql.setReturnFormat(JSON)
    sparql.setTimeout(360)
    while True:
        print "Downloading ",base," dataset"
        try:
            results = sparql.query().convert()
            break
        except URLError:
            print("Connection to Sparql server failed! Trying again in five seconds!")
            time.sleep(5)
    
    f_in.close()
                
    # Save the results
    out = open(os.path.join('dataset',base+'.json'),'w')
    for entity in results["results"]["bindings"]:
        out.write(json.dumps(entity))
        out.write("\n")
    out.close()
    
    time.sleep(10)