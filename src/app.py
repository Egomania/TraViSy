####### PYTHON LIBS ###################

# Flask imports
from flask import Flask
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for
from flask import Response
from flask import make_response
from flask import send_file
import flask

from flask_weasyprint import HTML, render_pdf

from werkzeug import secure_filename

#standard stuff
import os
import random
import math
import time
import ConfigParser
import imp
import glob

#database stuff
import pymongo
import json
from bson import json_util
from bson.json_util import dumps
from bson.son import SON

#security stuff
import ssl

#network stuff
import dpkt
import netifaces
import pcapy

#threading stuff
from celery import Celery
from kombu import serialization

# rendering stuff

import cairosvg

########### OWN IMPORTS ##################

import helper
import queryHelper
import queryHelperEthernet
import queryHelperBacnet
import queryHelperIp
import queryHelperTcpUdp
import pcapParser

################# GLOABEL STUFF ########################

# Global vars

Config = ConfigParser.ConfigParser()
Config.read('app.ini')

SERVER_PEM = Config.get('SecuritySetting', 'SERVER_PEM')
SERVER_KEY = Config.get('SecuritySetting', 'SERVER_KEY')

context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
context.load_cert_chain(SERVER_PEM, SERVER_KEY)

UPLOAD_FOLDER = Config.get('AppSetting', 'UPLOAD_FOLDER')
ALLOWED_EXTENSIONS = set(['pcap'])


#database setup
MONGODB_HOST = 'localhost'
MONGODB_PORT = 27017

DB_NAME = 'bacnet'
DB_NAME_KEY = 'key'
DB_NAME_DESCRIPTION = 'description'
DB_NAME_CONFIG = 'configuration'

COLLECTION_NAME = Config.get('AppSetting', 'DefaultCollection')
KEY_COLLECTION = Config.get('AppSetting', 'DefaultKeyCollection')
DESCRIPTION_COLLECTION = 'description'
CONFIG_COLLECTION = 'configuration'

connection = pymongo.MongoClient(MONGODB_HOST, MONGODB_PORT)
database = connection[DB_NAME]
collection = connection[DB_NAME][COLLECTION_NAME]
databaseKeys = connection[DB_NAME_KEY]
key_collection = connection[DB_NAME_KEY][KEY_COLLECTION]
description_collection = connection[DB_NAME_DESCRIPTION][DESCRIPTION_COLLECTION]
config_collection = connection[DB_NAME_CONFIG][CONFIG_COLLECTION]

#monitoring task setup
TASKS = []
taskID = 0

# app setup

app = Flask(__name__)
serialization.registry._decoders.pop("application/x-python-serialize")

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# celery setup

def make_celery(app):
    celery = Celery("app", broker=app.config['CELERY_BROKER_URL'])
    celery.conf.update(app.config)
    TaskBase = celery.Task
    class ContextTask(TaskBase):
        abstract = True
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)
    celery.Task = ContextTask
    return celery

app.config.update(
    CELERY_BROKER_URL='amqp://',
    CELERY_RESULT_BACKEND='amqp://',
    CELERY_ACCEPT_CONTENT=['application/json'],
    CELERY_TASK_SERIALIZER='json',
    CELERY_RESULT_SERIALIZER='json'
)

celery = make_celery(app)

# monitoring setup
GLOBAL_TIMER = Config.get('MonitoringSetting', 'Timer')
GLOBAL_COUNTER = Config.get('MonitoringSetting', 'Counter')

# init functions

@app.before_first_request
def before_first_request():
    pass

############# WEBSITE RENDERING #############################

@app.route("/")
def index():
    return render_template("index.html")

############# WEBSITE RENDERING BACKEND #############################

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route("/backend")
def backend():
    return render_template("backend/backend.html")

@app.route("/listCollections", methods=['GET', 'POST'])
def listCollections():

    if request.method == "GET":
        collectionList = database.collection_names(include_system_collections=False)
        return render_template("backend/listCollections.html", collections = collectionList)
    else:
        selectedCollection = request.form['collectionList']
        global collection
        collection = connection[DB_NAME][selectedCollection]
        global COLLECTION_NAME
        COLLECTION_NAME = selectedCollection
        return render_template("backend/Success.html", action = "selected", itemType = "Collection", itemName = selectedCollection)

@app.route("/showKeyCollections", methods=['GET', 'POST'])
def showKeyCollections():

    if request.method == "GET":
        collectionList = databaseKeys.collection_names(include_system_collections=False)
        return render_template("backend/listKeyCollections.html", collections = collectionList)
    else:
        selectedCollection = request.form['collectionList']
        global key_collection
        key_collection = connection[DB_NAME_KEY][selectedCollection]
        global KEY_COLLECTION
        KEY_COLLECTION = selectedCollection
        return render_template("backend/Success.html", action = "selected", itemType = "Collection", itemName = selectedCollection)

@app.route("/deleteCollections", methods=['GET', 'POST'])
def deleteCollections():

    if request.method == "GET":
        collectionList = database.collection_names(include_system_collections=False)
        return render_template("backend/deleteKeyCollection.html", collections = collectionList)
    else:
        selectedCollection = request.form['collectionList']
        database.drop_collection(selectedCollection)
        description_collection.remove({"Name": selectedCollection})
        return render_template("backend/Success.html", action = "deleted", itemType = "Collection", itemName = selectedCollection)

@app.route("/deleteKeyCollections", methods=['GET', 'POST'])
def deleteKeyCollections():

    if request.method == "GET":
        collectionList = databaseKeys.collection_names(include_system_collections=False)
        return render_template("backend/deleteKeyCollection.html", collections = collectionList)
    else:
        selectedCollection = request.form['collectionList']
        databaseKeys.drop_collection(selectedCollection)
        return render_template("backend/Success.html", action = "deleted", itemType = "Collection", itemName = selectedCollection)

@app.route("/collectionsDescription")
def collectionsDescription():

    ret = queryHelper.collectionsDescription(description_collection) 
    return ret

@app.route("/exploreCollections")
def exploreCollections():

    return render_template("backend/exploreCollections.html")

@app.route("/backend/paket")
def backend_paket():

    ret = queryHelper.pktDistribution(collection) 
    return ret

@app.route("/detailCollections")
def detailCollections():

    statsTMP = database.command("collstats", COLLECTION_NAME)
    
    stats = []
    stats.append(["Namespace", statsTMP['ns']])
    stats.append(["Paket Count", statsTMP['count']])
    stats.append(["Size", statsTMP['size']])
    stats.append(["AVG Object Size", statsTMP['avgObjSize']])
    stats.append(["Storage Size", statsTMP['storageSize']])
    stats.append(["Number of indizes", statsTMP['nindexes']])
    stats.append(["Total Index Size", statsTMP['totalIndexSize']])

    return render_template("backend/detailCollections.html", stats = stats)

@app.route("/reportCollections",methods=['GET', 'POST'])
def reportCollections():

    if request.method == 'POST':
        return render_template("backend/Success.html", action = "created", itemType = "Report", itemName = "Test")

    return render_template("backend/reportCollections.html")


@app.route('/export', methods=["POST"])
def export():
    svg_xml = request.form.get("data", "Invalid data")
    filename = request.form.get("filename")
    type_foo = request.form['format']
    if (type_foo == 'svg'):
        response = Response(svg_xml, mimetype="image/svg+xml")
        response.headers["Content-Disposition"] = "attachment; filename=%s"%filename
        return response
    elif (type_foo == 'pdf'):
        pdfOut = cairosvg.svg2pdf(svg_xml)
        ret = make_response(pdfOut)
        ret.headers['Content-Type'] = 'application/pdf'
        ret.headers['Content-Disposition'] = \
            'inline; filename=%s.pdf'
        return ret 
    elif (type_foo == 'png'):
        pngOut = cairosvg.svg2png(svg_xml)
        ret = make_response(pngOut)
        ret.headers['Content-Type'] = 'image/png'
        ret.headers['Content-Disposition'] = 'attachment; filename='+filename
        return ret
    else:
        return render_template("error.html")
    

@app.route("/editCollections", methods=['GET', 'POST'])
def editCollections():

    if request.method == "GET":

        collectionDescription = queryHelper.collectionDescription(database, description_collection)

        return render_template("backend/editCollections.html", collections = collectionDescription)

    else:
        colname = request.form['Name']
        colowner = request.form['Owner']
        coldesc = request.form['Description']
        colid = request.form['Id']
        colstart = request.form['Start']
        colend = request.form['Ende']
        colloc = request.form['Location']

        if colowner:
            description_collection.update_one({'Name': colname},{"$set": {"Owner": colowner}})

        if coldesc:
            description_collection.update_one({'Name': colname},{"$set": {"Description": coldesc}})

        if colstart:
            description_collection.update_one({'Name': colname},{"$set": {"Start": colstart}})

        if colend:
            description_collection.update_one({'Name': colname},{"$set": {"Ende": colend}})

        if colloc:
            description_collection.update_one({'Name': colname},{"$set": {"Location": colloc}})

        return render_template("backend/Success.html", action = "edited", itemType = "Collection", itemName = colname)

@app.route("/uploadFiles",methods=['GET', 'POST'])
def uploadFiles():

    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return render_template("backend/Success.html", action = "uploaded", itemType = "File", itemName = filename)

    return render_template("backend/uploadFiles.html")

@app.route("/storeKeyCollections", methods=['GET', 'POST'])
def storeKeyCollections():

    if request.method == "GET":
        moduleList = glob.glob('*Reader.py')
        return render_template("backend/storeKeyCollection.html", modules = moduleList)
    else:
        file = request.files['file']
        selectedCollection = request.form['Name']
        selectedModulePath = request.form['module']
        selectedModuleName = selectedModulePath.split('.')[0]
        my_module = imp.load_source(selectedModuleName, selectedModulePath)
        my_module.store(file, selectedCollection)
        return render_template("backend/Success.html", action = "stored", itemType = "KeyCollection", itemName = selectedCollection)

@app.route("/removeFiles",methods=['GET', 'POST'])
def removeFiles():

    if request.method == 'POST':
        fileToDelete = request.form['file']
        os.remove(UPLOAD_FOLDER + "/"+fileToDelete)
        return render_template("backend/Success.html", action = "deleted", itemType = "File", itemName = fileToDelete)

    files = helper.fileNamesinUploads(UPLOAD_FOLDER)

    return render_template("backend/removeFiles.html", files = files)

@app.route("/storeFiles",methods=['GET', 'POST'])
def storeFiles():

    if request.method == 'POST':
        fileToStore = str(request.form['file'])
        nameToStore = str(request.form['Name'])
        ownerToStore = str(request.form['Owner'])
        descToStore = str(request.form['Description'])
        startToStore = str(request.form['Start'])
        endeToStore = str(request.form['Ende'])
        locToStore = str(request.form['Location'])
        
        if not nameToStore:
            nameToStore = fileToStore[:len(fileToStore)-5]

        erg = pcapParser.storeFileIntoDataBase(UPLOAD_FOLDER + "/" + fileToStore, nameToStore)

        description_collection.insert_one({"Description": descToStore, "Ende": endeToStore, "Location": locToStore, "Name": nameToStore, "Owner": ownerToStore, "Start": startToStore})

        queryHelper.makeIndizes(database, nameToStore)

        stats = []
        stats.append(["Anzahl benoetigter Pakete", erg['pak']])
        stats.append(["Benoetigte Laufzeit", erg['run']])

        return render_template("backend/Success.html", action = "stored", itemType = "File as Collection", itemName = fileToStore, stats = stats)

    files = helper.fileNamesinUploads(UPLOAD_FOLDER)

    return render_template("backend/storeFiles.html", files = files)

@app.route("/storeFilesCelery",methods=['GET', 'POST'])
def storeFilesCelery():

    if request.method == 'POST':
        fileToStore = str(request.form['file'])
        nameToStore = str(request.form['Name'])
        ownerToStore = str(request.form['Owner'])
        descToStore = str(request.form['Description'])
        startToStore = str(request.form['Start'])
        endeToStore = str(request.form['Ende'])
        locToStore = str(request.form['Location'])
        
        if not nameToStore:
            nameToStore = fileToStore[:len(fileToStore)-5]

        task = {}
        global taskID
        task['id'] = taskID
        task['iface'] = "Local Storage Process"
        requestTask = CeleryStoringTask.apply_async(args=[fileToStore, nameToStore, descToStore, endeToStore, locToStore, ownerToStore, startToStore],serializer='json')
        task['task'] = requestTask

        taskID = taskID + 1
        global TASKS
        TASKS.append(task)

        return render_template("backend/Success.html", action = "stored", itemType = "File as Collection", itemName = fileToStore)

    files = helper.fileNamesinUploads(UPLOAD_FOLDER)

    return render_template("backend/storeFiles.html", files = files)

@app.route("/realTimeMonitoring",methods=['GET', 'POST'])
def realTimeMonitoring():

    if request.method == 'POST':
        interfaceToActivate = str(request.form['interface'])
        timerToUse = request.form['timer']
        counterToUse = request.form['counter']
        collectionNameToUse = request.form['collection']

        if not timerToUse:
            timerToUse = GLOBAL_TIMER

        if not counterToUse:
            counterToUse = GLOBAL_COUNTER

        if not collectionNameToUse:
            collectionNameToUse = str(interfaceToActivate) + str(random.randint(0,1000))

        task = {}
        global taskID
        task['id'] = taskID
        task['iface'] = interfaceToActivate
        requestTask = CeleryMonitoringTask.apply_async(args=[interfaceToActivate, counterToUse, timerToUse, collectionNameToUse],serializer='json')
        task['task'] = requestTask

        taskID = taskID + 1
        global TASKS
        TASKS.append(task)

        if requestTask.state != 'FAILURE':

            description_collection.insert_one({"Description": "Local trace on interface:" + str(interfaceToActivate) + "with Timer set to:" + str(timerToUse) + " and Counter to set: " + str(counterToUse), "Location": "Local Server Instance", "Name": collectionNameToUse, "Owner": "system", "Start": time.clock()})

        stats = []
        stats.append(["Paket-Counter gesetzt auf:", counterToUse])
        stats.append(["Timer gesetzt auf:", timerToUse])

        return render_template("backend/Success.html", action = "activated", itemType = "Realtime-Monitoring on Interface", itemName = interfaceToActivate, stats = stats)

    interfaces = netifaces.interfaces()

    return render_template("backend/realTimeMonitoring.html", interfaces = interfaces)

@app.route("/realTimeMonitoringStatus",methods=['GET', 'POST'])
def realTimeMonitoringStatus():

    global TASKS

    if request.method == 'POST':

        action = "none"
        task = "none"

        if len(request.form.keys()) < 2: 
            return render_template("backend/Success.html", action = action, itemType = "Task", itemName = task)

        task = int(request.form['task'])
       

        if request.form['action'] == "delete":
            action = "deleted"
            
            for taskElem in TASKS:
                
                if taskElem['id'] == task:
                    TASKS.remove(taskElem)

        if request.form['action'] == "cancel":
            action = "canceled"   

            for taskElem in TASKS:
                
                if taskElem['id'] == task:
                    taskElem['task'].revoke(terminate=True)
                    

        return render_template("backend/Success.html", action = action, itemType = "Task", itemName = task)
    
    cancelTask = []
    deleteTask = []

    for task in TASKS:
        
        if (str(task['task'].state) == "SUCCESS" and str(task['task'].status) == "SUCCESS") or (str(task['task'].state) == "REVOKED" and str(task['task'].status) == "REVOKED") or (str(task['task'].state) == "FAILURE" and str(task['task'].status) == "FAILURE"):
            deleteTask.append(task['id'])
        else:
            cancelTask.append(task['id'])

    return render_template("backend/realTimeMonitoringStatus.html", TasksToCancel = cancelTask, TasksToDelete = deleteTask)

@app.route("/realTimeMonitoringStatusData")
def realTimeMonitoringStatusData():
    global TASKS
    ret = []
    for task in TASKS:
        retTask = {}
        retTask['id'] = task['id']
        retTask['iface'] = task['iface']
        retTask['stat'] = str(task['task'].state)
        retTask['status'] = str(task['task'].status)
        retTask['intID'] = str(task['task'].id)
        ret.append(retTask)        

    ret = json.dumps(ret, default=json_util.default)
    return ret

@app.route("/realTimeMonitoringRemoteConfigure",methods=['GET', 'POST'])
def realTimeMonitoringRemoteConfigure():

    if request.method == 'GET':

        configurations = queryHelper.collectionConfig(config_collection)

        if configurations == None:
            configurations = []

        return render_template("backend/realTimeMonitoringRemoteConfigure.html", configurations = configurations)

    if request.method == 'POST':
        if request.form['action'] == "new":

            confname = request.form['name']
            confadr = request.form['address']
            confport = int(request.form['port'])
            confuser = request.form['user']
            confiface = request.form['iface']
            confdev = "./tmp/" + confname + str(random.randint(0,100))

            os.system("mkfifo " + confdev)

            config_collection.insert_one({"name": confname, "address": confadr, "port": confport, "user": confuser, "dev": confdev, "iface": confiface})

            action = "added"
            config = confname

        if request.form['action'] == "edit":

            confname = request.form['name']
            confadr = request.form['address']
            confport = request.form['port']
            confuser = request.form['user']
            confiface = request.form['iface']

            if confport:
                config_collection.update_one({'name': confname},{"$set": {"port": int(confport)}})

            if confadr:
                config_collection.update_one({'name': confname},{"$set": {"address": confadr}})

            if confuser:
                config_collection.update_one({'name': confname},{"$set": {"user": confuser}})

            if confiface:
                config_collection.update_one({'name': confname},{"$set": {"iface": confiface}})


            action = "edit"
            config = confname

        if request.form['action'] == "delete":

            confname = request.form['config']
            devs = config_collection.find({"name": confname})
            for dev in devs:
                confdev = dev.get("dev")
            config_collection.remove({"name": confname})

            os.system("rm " + confdev)

            action = "deleted"
            config = confname
            
        return render_template("backend/Success.html", action = action, itemType = "Configuration", itemName = config)

@app.route("/realTimeMonitoringRemote",methods=['GET', 'POST'])
def realTimeMonitoringRemote():

    if request.method == 'GET':

        interfaces = queryHelper.getConfigurations(config_collection)

        return render_template("backend/realTimeMonitoringRemote.html", interfaces = interfaces)

    if request.method == 'POST':

        configToUse = str(request.form['interface'])
        timerToUse = request.form['timer']
        counterToUse = request.form['counter']
        collectionNameToUse = request.form['collection']

        if not timerToUse:
            timerToUse = GLOBAL_TIMER

        if not counterToUse:
            counterToUse = GLOBAL_COUNTER

        if not collectionNameToUse:
            collectionNameToUse = str(configToUse) + str(random.randint(0,1000))

        conf = config_collection.find({"name": configToUse})

        for col in conf:
            address = col.get("address")
            port = col.get("port")
            user = col.get("user")
            device = col.get("dev")
            iface = col.get("iface")
        
        description_collection.insert_one({"Description": "Remote trace on interface:" + str(iface) + "with Timer set to:" + str(timerToUse) + " and Counter to set: " + str(counterToUse), "Location": "Remote Machine: " + str(address) + ":" + str(port), "Name": collectionNameToUse, "Owner": user, "Start": time.clock()})

        task = {}
        global taskID
        task['id'] = taskID
        task['iface'] = device
        requestTask = CeleryMonitoringTaskRemote.apply_async(args=[device, counterToUse, timerToUse, collectionNameToUse, address, port, user, iface],serializer='json')
        task['task'] = requestTask

        taskID = taskID + 1
        global TASKS
        TASKS.append(task)

        stats = []
        stats.append(["Paket-Counter gesetzt auf:", counterToUse])
        stats.append(["Timer gesetzt auf:", timerToUse])

        return render_template("backend/Success.html", action = "activated", itemType = "Remote Realtime-Monitoring on Interface", itemName = device, stats = stats)


############# WEBSITE RENDERING  APPLICATION #############################

@app.route("/ethernet")
def ethernet():
    return render_template("frontend/ethernet.html")

@app.route("/ip")
def ip():
    return render_template("frontend/ip.html")

@app.route("/ipGraphs")
def ipGraphs():
    return render_template("frontend/ipGraphs.html")

@app.route("/tcpGraphs")
def tcpGraphs():
    ips = json.loads(transport_IPPortsConnectionCyto())['nodes']
    return render_template("frontend/tcpGraphs.html", ips=ips)

@app.route("/tcp_udp")
def tcp_udp():
    return render_template("frontend/tcp_udp.html")

@app.route("/bacnet")
def bacnet():
    return render_template("frontend/bacnet.html")

@app.route("/bacnetSpec")
def bacnetSpec():
    return render_template("frontend/bacnetSpec.html")

############# JSON FILES for Application #############################

############# ETHERNET STUFF #########################################

@app.route("/ethernet/Timeline/<int:start>/<int:end>")
def ethernet_Timeline(start, end):
    
    ret = queryHelperEthernet.ethernet_Timeline(collection, start, end)
    return ret

@app.route("/ethernet/Ethertype")
def ethernet_Ethertype():

    ret = queryHelperEthernet.ethernet_Ethertype(collection)
    return ret

@app.route("/ethernet/MacSrc")
def ethernet_MacSrc():
    
    ret = queryHelperEthernet.ethernet_MacSrc(collection)
    return ret

@app.route("/ethernet/ForcedGraph")
def ethernet_Ethernet():
    
    ret = queryHelperEthernet.ethernet_Ethernet(collection, "forced")
    return ret

@app.route("/ethernet/Mac")
def ethernet_Mac():

    ret = queryHelperEthernet.ethernet_Mac(collection)
    return ret

############# IP STUFF #########################################
@app.route("/ip/Node")
def ip_Ip():
    
    ret = queryHelperIp.ip_Ip(collection, "forced")
    return ret

@app.route("/ip/NodeVIS")
def ip_IpExtended():
    
    ret = queryHelperIp.ip_Graph(collection, "vis")
    return ret

@app.route("/ip/NodeSigma")
def ip_IpExtendedString():
    
    ret = queryHelperIp.ip_Graph(collection, "sigma")
    return ret

@app.route("/ip/NodeAlchemy")
def ip_Alchemy():
    
    ret = queryHelperIp.ip_Graph(collection, "alchemy")
    return ret

@app.route("/ip/NodeForcedGraph")
def ip_NodeForcedGraph():
    
    ret = queryHelperIp.ip_Graph(collection, "forced")
    return ret

@app.route("/ip/Matrix")
def ip_Matrix():
    
    ret = queryHelperIp.ip_Matrix(collection)
    return ret

@app.route("/ip/ttl")
def ip_ttl():
    
    ret = queryHelperIp.ip_ttl(collection)
    return ret

@app.route("/ip/flags")
def ip_flags():
    
    ret = queryHelperIp.ip_flag(collection)
    return ret

@app.route("/ip/timeline/<int:search>/<int:value>")
def ip_timeline(search, value):

    ret = queryHelperIp.ip_timeline(collection, search, value)
    return ret

############# Transport STUFF #########################################
@app.route("/transport/IPPortsConnection")
def transport_TransportExtended():
    
    ret = queryHelperTcpUdp.transport_IPPortsConnection(collection, "vis")
    return ret

@app.route("/transport/IPPortsConnectionCyto")
def transport_IPPortsConnectionCyto():
    
    ret = queryHelperTcpUdp.transport_IPPortsConnection(collection, "cytoscape",firstLevelNodeColor='#0000FF', secondLevelNodeColor='#009900', commRelationColor='#CC0000', openRelationColor='#808080')
    return ret

@app.route("/transport/sourcePortDistribution")
def transport_sourcePortDistribution():
    
    ret = queryHelperTcpUdp.transport_distribution(collection, "source_port")
    return ret

############# BACNET STUFF #########################################

@app.route("/bacnet/Prio")
def bacnet_prio():

    ret = queryHelperBacnet.bacnet_prio(collection)
    return ret 

@app.route("/bacnet/pduFlags")
def bacnet_pduFlags():

    ret = queryHelperBacnet.bacnet_pduFlags(collection)
    return ret

@app.route("/bacnet/Controller/<int:value>")
def bacnet_Controller(value):

    ret = queryHelperBacnet.bacnet_Controller(collection, value)
    return ret

@app.route("/bacnet/APDU")
def bacnet_APDU():
    ret = queryHelperBacnet.bacnet_APDU(collection)
    return ret

@app.route("/bacnet/Matrix")
def bacnet_Matrix():    

    ret = queryHelperBacnet.bacnet_Matrix(collection, key_collection)
    return ret

@app.route("/bacnet/WhoIs")
def bacnet_WhoIs():
    ret = queryHelperBacnet.bacnet_WhoIs(collection, key_collection)
    return ret
        
########################################### CELERY - TASKS ###########################################

@celery.task(serializer='json')
def CeleryMonitoringTask(interface, counter, timer, collectionNameToUse):
    
    requestTask = pcapParser.liveMonitoring(interface, int(counter), int(timer), collectionNameToUse)
    
    queryHelper.makeIndizes(database, collectionNameToUse)

@celery.task(serializer='json')
def CeleryMonitoringTaskRemote(interface, counter, timer, collectionNameToUse, address, port, user, iface):

    requestTask = pcapParser.liveMonitoringRemote(interface, int(counter), int(timer), collectionNameToUse, address, port, user, iface)

    queryHelper.makeIndizes(database, collectionNameToUse)

@celery.task(serializer='json')
def CeleryStoringTask(fileToStore, nameToStore, descToStore, endeToStore, locToStore, ownerToStore, startToStore):
    
    erg = pcapParser.storeFileIntoDataBase(UPLOAD_FOLDER + "/" + fileToStore, nameToStore)

    description_collection.insert_one({"Description": descToStore, "Ende": endeToStore, "Location": locToStore, "Name": nameToStore, "Owner": ownerToStore, "Start": startToStore})

    queryHelper.makeIndizes(database, nameToStore)

########################################### MAIN ###########################################

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True, threaded=True, ssl_context=context)


    
