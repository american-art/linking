from flask import Flask, render_template, request, url_for, jsonify, redirect, flash, jsonify, Response, send_from_directory
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required
from flask_restful import Resource, Api
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS, cross_origin
from flask_debugtoolbar import DebugToolbarExtension
from pymongo import MongoClient, ReturnDocument, ASCENDING, DESCENDING
from pymongo.errors import ServerSelectionTimeoutError
from unidecode import unidecode
import os, json, sys, getopt, logging, logging.handlers
from optparse import OptionParser
from platform import system as system_name # Returns the system/OS name
from os import system as system_call       # Execute a shell command

devmode = False

if devmode:
    server = "http://localhost:5000/"
    dbC = MongoClient('localhost', 27017,serverSelectionTimeoutMS=10)
else:
    server = "http://linking.americanartcollaborative.org/"
    dbC = MongoClient('localhost', 12345,serverSelectionTimeoutMS=10)

try:
    dbC.server_info()
except ServerSelectionTimeoutError:
    print ("MongDb Server is down! Exiting...")
    sys.exit(1)
        
# Flask configuration
app = Flask(__name__)
app.url_map.strict_slashes = False
CORS(app)
app.config['SECRET_KEY'] = 'top secret!'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

'''
if devmode:
    app.debug = True
    toolbar = DebugToolbarExtension(app)
'''

# Handle server logging
app.logger.setLevel(logging.DEBUG)  # use the native logger of flask
app.logger.disabled = False
logging.basicConfig(filename='server.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
handler = logging.handlers.RotatingFileHandler("server.log", 'a', maxBytes=1024 * 1024 * 100, backupCount=20)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(name)s: \t%(message)s")
handler.setFormatter(formatter)
app.logger.addHandler(handler)
log = logging.getLogger('werkzeug')
log.setLevel(logging.DEBUG)
log.addHandler(handler)

# restful, usrdb and login_manager instance
api = Api(app)

usrdb = SQLAlchemy(app)

lm = LoginManager(app)
lm.login_view = 'index'
lm.session_protection = 'strong'

dname = "linkVerification"
fbrsp = ""

def append_default_dict(x):
    z = x.copy()
    # Default values, these are updated after importing config and questions
    y = {"confidenceYesNo":1,"confidenceNotSure":2,"matchedQ":0,"unmatchedQ":0,"unconcludedQ":0,"totalQ":0}
    z.update(y)
    return z

# Every museum is dictionary is defined by tag name as key and value is array containing:
# Format: <URI identifier>, <ranking for ordering - alphabetical>, <confedenceLevel yes/no - default 2>, <confedenceLevel not sure default 2>, 
    #   <matched>, <unmatched>, <total questions>
museums = {
    "aaa": append_default_dict({"uri":"/aaa/","ranking":1,"name":"Archives of American Art, Smithsonian Institution"}),
    #"aac":append_default_dict({"uri":"/aac/","ranking":2,"name","Asian Arts Council"}),
    #"aat":append_default_dict({"uri":"/aat/","ranking":3,"name":"The Getty - Art and Architecture Thesaurus Online"}),
    "acm": append_default_dict({"uri":"/acm/","ranking":4,"name":"Amon Carter Museum of American Art"}),
    "autry": append_default_dict({"uri":"/autry/","ranking":5,"name":"Autry Museum of the American West"}),
    "cbm": append_default_dict({"uri":"data.crystalbridges.org/","ranking":6,"name":"Crystal Bridges Museum of American Art"}),
    "ccma": append_default_dict({"uri":"/ccma/","ranking":7,"name":"Colby College Museum of Art"}),
    #"dbpedia":append_default_dict({"uri":"/dbpedia.org/","ranking":8,"name":"Structured information from Wikipedia"}),
    "dma": append_default_dict({"uri":"/dma/","ranking":9,"name":"Dallas Museum of Art"}),
    "gm": append_default_dict({"uri":"/GM/","ranking":10,"name":"Thomas Gilcrease Institute of American History and Art"}),
    "ima": append_default_dict({"uri":"/ima/","ranking":11,"name":"Indianapolis Museum of Art"}),
    "npg": append_default_dict({"uri":"/npg/","ranking":12,"name":"National Portrait Gallery, Smithsonian Institution"}),
    "nmwa": append_default_dict({"uri":"/nmwa/","ranking":13,"name":"National Museum of Wildlife Art"}),
    "puam": append_default_dict({"uri":"/puam/","ranking":14,"name":"Princeton University Art Museum"}),
    "saam": append_default_dict({"uri":"/saam/","ranking":15,"name":"Smithsonian American Art Museum"}),
    "ulan": append_default_dict({"uri":"/ulan/","ranking":16,"name":"The Getty Research Institute - Union List of Artist Names"}),
    #"viaf":append_default_dict({"uri":"/viaf/","ranking":17,"name":"The Virtual International Authority File"}),
    "wam": append_default_dict({"uri":"data.thewalters.org/","ranking":18,"name":"Walters Art Gallery"}),
    #"ycba":append_default_dict({"uri":"/ycba/","ranking":19,"name":"Yale Center for British Art"}),
}

statuscodes = {"NotStarted":1,"InProgress":2,"Agreement":3,"Disagreement":4,"Non-conclusive":5}

rootdir = os.path.dirname(os.path.abspath(__file__))
questiondir = os.path.join(rootdir, "linkage", "questions")

# Load API keys from file
f = open("key.json", 'r').read()
keys = json.loads(f)
if devmode:
    app.config['OAUTH_CREDENTIALS'] = keys['dev']
    curationpass = keys["dev"]["pass"]
else:
    app.config['OAUTH_CREDENTIALS'] = keys['production']
    curationpass = keys["production"]["pass"]