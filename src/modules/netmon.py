from flask import Blueprint
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for
from flask import Response
from flask import make_response
from flask import send_file

#database stuff
import pymongo
import json
from bson import json_util
from bson.json_util import dumps
from bson.son import SON

#network stuff
import dpkt
import netifaces
import pcapy

#standard stuff
import os
import random
import math
import time
import ConfigParser
import imp
import glob

# rendering stuff
import cairosvg

#threading stuff
import celery

########### OWN IMPORTS ##################

from helper import helper
from helper import queryHelper
from helper import queryHelperEthernet
from helper import queryHelperBacnet
from helper import queryHelperIp
from helper import queryHelperTcpUdp
from helper import pcapParser

name = 'netmon'
description = 'Network Monitoring and Analysis Module'

module = Blueprint(name, __name__, template_folder='templates', static_folder='static')
celery = celery.Celery('tasks', backend='rpc://', broker='amqp://')

# Global vars

ConfigDefaults = {'UPLOAD_FOLDER': './uploads', 'DefaultCollection': 'collection', 'DefaultKeyCollection':'key', 'Timer':'1000', 'Counter':'1000', 'mongoDBHost' : 'localhost', 'mongoDBPort' : 27017, 'mongoDBName' : 'travisyNetmon', 'mongoDBKeys' : 'travisyNetmonKey', 'mongoDBDescription' : 'travisynetmondescription', 'mongoDBConfiguration' : 'travisynetmonconfiguration', 'DefaultDescriptionCollection':'description', 'DefaultConfigurationCollection':'configuration'}

Config = ConfigParser.ConfigParser(defaults=ConfigDefaults)
Config.read('./config/netmon.ini')

UPLOAD_FOLDER = Config.get('AppSetting', 'UPLOAD_FOLDER')
ALLOWED_EXTENSIONS = set(['pcap'])

#database setup
MONGODB_HOST = Config.get('MongoDatabaseSetting', 'mongoDBHost')
MONGODB_PORT = int (Config.get('MongoDatabaseSetting', 'mongoDBPort'))

DB_NAME = Config.get('MongoDatabaseSetting', 'mongoDBName')
DB_NAME_KEY = Config.get('MongoDatabaseSetting', 'mongoDBKeys')
DB_NAME_DESCRIPTION = Config.get('MongoDatabaseSetting', 'mongoDBDescription')
DB_NAME_CONFIG = Config.get('MongoDatabaseSetting', 'mongoDBConfiguration')

COLLECTION_NAME = Config.get('AppSetting', 'DefaultCollection')
KEY_COLLECTION = Config.get('AppSetting', 'DefaultKeyCollection')
DESCRIPTION_COLLECTION = Config.get('AppSetting', 'DefaultDescriptionCollection')
CONFIG_COLLECTION = Config.get('AppSetting', 'DefaultConfigurationCollection')

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

# monitoring setup
GLOBAL_TIMER = Config.getint('MonitoringSetting', 'Timer')
GLOBAL_COUNTER = Config.getint('MonitoringSetting', 'Counter')


############# WEBSITE RENDERING BACKEND #############################

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@module.route('/' + name)
def netmon():
    return render_template("netmon/index.html")

@module.route("/netmon/backend")
def backend():
    return render_template("netmon/backend/backend.html")

@module.route("/netmon/listCollections", methods=['GET', 'POST'])
def listCollections():

    if request.method == "GET":
        collectionList = database.collection_names(include_system_collections=False)
        return render_template("netmon/backend/listCollections.html", collections = collectionList)
    else:
        selectedCollection = request.form['collectionList']
        global collection
        collection = connection[DB_NAME][selectedCollection]
        global COLLECTION_NAME
        COLLECTION_NAME = selectedCollection
        return render_template("netmon/backend/Success.html", action = "selected", itemType = "Collection", itemName = selectedCollection)

@module.route("/netmon/showKeyCollections", methods=['GET', 'POST'])
def showKeyCollections():

    if request.method == "GET":
        collectionList = databaseKeys.collection_names(include_system_collections=False)
        return render_template("netmon/backend/listKeyCollections.html", collections = collectionList)
    else:
        selectedCollection = request.form['collectionList']
        global key_collection
        key_collection = connection[DB_NAME_KEY][selectedCollection]
        global KEY_COLLECTION
        KEY_COLLECTION = selectedCollection
        return render_template("netmon/backend/Success.html", action = "selected", itemType = "Collection", itemName = selectedCollection)

@module.route("/netmon/deleteCollections", methods=['GET', 'POST'])
def deleteCollections():

    if request.method == "GET":
        collectionList = database.collection_names(include_system_collections=False)
        return render_template("netmon/backend/deleteCollection.html", collections = collectionList)
    else:
        selectedCollection = request.form['collectionList']
        database.drop_collection(selectedCollection)
        description_collection.remove({"Name": selectedCollection})
        return render_template("netmon/backend/Success.html", action = "deleted", itemType = "Collection", itemName = selectedCollection)

@module.route("/netmon/deleteKeyCollections", methods=['GET', 'POST'])
def deleteKeyCollections():

    if request.method == "GET":
        collectionList = databaseKeys.collection_names(include_system_collections=False)
        return render_template("netmon/backend/deleteKeyCollection.html", collections = collectionList)
    else:
        selectedCollection = request.form['collectionList']
        databaseKeys.drop_collection(selectedCollection)
        return render_template("netmon/backend/Success.html", action = "deleted", itemType = "Collection", itemName = selectedCollection)

@module.route("/netmon/collectionsDescription")
def collectionsDescription():

    ret = queryHelper.collectionsDescription(description_collection) 
    return ret

@module.route("/netmon/exploreCollections")
def exploreCollections():

    return render_template("netmon/backend/exploreCollections.html")

@module.route("/netmon/backend/paket")
def backend_paket():

    ret = queryHelper.pktDistribution(collection) 
    return ret

@module.route("/netmon/detailCollections")
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

    return render_template("netmon/backend/detailCollections.html", stats = stats)

@module.route("/netmon/reportCollections",methods=['GET', 'POST'])
def reportCollections():

    if request.method == 'POST':
        return render_template("netmon/backend/Success.html", action = "created", itemType = "Report", itemName = "Test")

    return render_template("netmon/backend/reportCollections.html")


@module.route('/netmon/export', methods=["POST"])
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
    

@module.route("/netmon/editCollections", methods=['GET', 'POST'])
def editCollections():

    if request.method == "GET":

        collectionDescription = queryHelper.collectionDescription(database, description_collection)

        return render_template("netmon/backend/editCollections.html", collections = collectionDescription)

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

        return render_template("netmon/backend/Success.html", action = "edited", itemType = "Collection", itemName = colname)

@module.route("/netmon/uploadFiles",methods=['GET', 'POST'])
def uploadFiles():

    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return render_template("netmon/backend/Success.html", action = "uploaded", itemType = "File", itemName = filename)

    return render_template("netmon/backend/uploadFiles.html")

@module.route("/netmon/storeKeyCollections", methods=['GET', 'POST'])
def storeKeyCollections():

    if request.method == "GET":
        moduleList = glob.glob('*Reader.py')
        return render_template("netmon/backend/storeKeyCollection.html", modules = moduleList)
    else:
        file = request.files['file']
        selectedCollection = request.form['Name']
        selectedModulePath = request.form['module']
        selectedModuleName = selectedModulePath.split('.')[0]
        my_module = imp.load_source(selectedModuleName, selectedModulePath)
        my_module.store(file, connection, selectedCollection)
        return render_template("netmon/backend/Success.html", action = "stored", itemType = "KeyCollection", itemName = selectedCollection)

@module.route("/netmon/removeFiles",methods=['GET', 'POST'])
def removeFiles():

    if request.method == 'POST':
        fileToDelete = request.form['file']
        os.remove(UPLOAD_FOLDER + "/"+fileToDelete)
        return render_template("netmon/backend/Success.html", action = "deleted", itemType = "File", itemName = fileToDelete)

    files = helper.fileNamesinUploads(UPLOAD_FOLDER)

    return render_template("netmon/backend/removeFiles.html", files = files)

@module.route("/netmon/storeFiles",methods=['GET', 'POST'])
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

        return render_template("netmon/backend/Success.html", action = "stored", itemType = "File as Collection", itemName = fileToStore, stats = stats)

    files = helper.fileNamesinUploads(UPLOAD_FOLDER)

    return render_template("netmon/backend/storeFiles.html", files = files)

@module.route("/netmon/storeFilesCelery",methods=['GET', 'POST'])
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

        return render_template("netmon/backend/Success.html", action = "stored", itemType = "File as Collection", itemName = fileToStore)

    files = helper.fileNamesinUploads(UPLOAD_FOLDER)

    return render_template("netmon/backend/storeFiles.html", files = files)

@module.route("/netmon/realTimeMonitoring",methods=['GET', 'POST'])
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

        return render_template("netmon/backend/Success.html", action = "activated", itemType = "Realtime-Monitoring on Interface", itemName = interfaceToActivate, stats = stats)

    interfaces = netifaces.interfaces()

    return render_template("netmon/backend/realTimeMonitoring.html", interfaces = interfaces)

@module.route("/netmon/realTimeMonitoringStatus",methods=['GET', 'POST'])
def realTimeMonitoringStatus():

    global TASKS

    if request.method == 'POST':

        action = "none"
        task = "none"

        if len(request.form.keys()) < 2: 
            return render_template("netmon/backend/Success.html", action = action, itemType = "Task", itemName = task)

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
                    

        return render_template("netmon/backend/Success.html", action = action, itemType = "Task", itemName = task)
    
    cancelTask = []
    deleteTask = []

    for task in TASKS:
        
        if (str(task['task'].state) == "SUCCESS" and str(task['task'].status) == "SUCCESS") or (str(task['task'].state) == "REVOKED" and str(task['task'].status) == "REVOKED") or (str(task['task'].state) == "FAILURE" and str(task['task'].status) == "FAILURE"):
            deleteTask.append(task['id'])
        else:
            cancelTask.append(task['id'])

    return render_template("netmon/backend/realTimeMonitoringStatus.html", TasksToCancel = cancelTask, TasksToDelete = deleteTask)

@module.route("/netmon/realTimeMonitoringStatusData")
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

@module.route("/netmon/realTimeMonitoringRemoteConfigure",methods=['GET', 'POST'])
def realTimeMonitoringRemoteConfigure():

    if request.method == 'GET':

        configurations = queryHelper.collectionConfig(config_collection)

        if configurations == None:
            configurations = []

        return render_template("netmon/backend/realTimeMonitoringRemoteConfigure.html", configurations = configurations)

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
            
        return render_template("netmon/backend/Success.html", action = action, itemType = "Configuration", itemName = config)

@module.route("/netmon/realTimeMonitoringRemote",methods=['GET', 'POST'])
def realTimeMonitoringRemote():

    if request.method == 'GET':

        interfaces = queryHelper.getConfigurations(config_collection)

        return render_template("netmon/backend/realTimeMonitoringRemote.html", interfaces = interfaces)

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

        return render_template("netmon/backend/Success.html", action = "activated", itemType = "Remote Realtime-Monitoring on Interface", itemName = device, stats = stats)


############# WEBSITE RENDERING  APPLICATION #############################

@module.route("/netmon/ethernet")
def ethernet():
    return render_template("netmon/frontend/ethernet.html")

@module.route("/netmon/ip")
def ip():
    return render_template("netmon/frontend/ip.html")

@module.route("/netmon/ipGraphs")
def ipGraphs():
    return render_template("netmon/frontend/ipGraphs.html")

@module.route("/netmon/tcpGraphs")
def tcpGraphs():
    ips = json.loads(transport_IPPortsConnectionCyto())['nodes']
    return render_template("netmon/frontend/tcpGraphs.html", ips=ips)

@module.route("/netmon/tcp_udp")
def tcp_udp():
    return render_template("netmon/frontend/tcp_udp.html")

@module.route("/netmon/bacnet")
def bacnet():
    return render_template("netmon/frontend/bacnet.html")

@module.route("/netmon/bacnetSpec")
def bacnetSpec():
    return render_template("netmon/frontend/bacnetSpec.html")

############# JSON FILES for Application #############################

############# ETHERNET STUFF #########################################

@module.route("/netmon/ethernet/Timeline/<int:start>/<int:end>")
def ethernet_Timeline(start, end):
    
    ret = queryHelperEthernet.ethernet_Timeline(collection, start, end)
    return ret

@module.route("/netmon/ethernet/Ethertype")
def ethernet_Ethertype():

    ret = queryHelperEthernet.ethernet_Ethertype(collection)
    return ret

@module.route("/netmon/ethernet/MacSrc")
def ethernet_MacSrc():
    
    ret = queryHelperEthernet.ethernet_MacSrc(collection)
    return ret

@module.route("/netmon/ethernet/ForcedGraph")
def ethernet_Ethernet():
    
    ret = queryHelperEthernet.ethernet_Ethernet(collection, "forced")
    return ret

@module.route("/netmon/ethernet/Mac")
def ethernet_Mac():

    ret = queryHelperEthernet.ethernet_Mac(collection)
    return ret

############# IP STUFF #########################################
@module.route("/netmon/ip/Node")
def ip_Ip():
    
    ret = queryHelperIp.ip_Ip(collection, "forced")
    return ret

@module.route("/netmon/ip/NodeVIS")
def ip_IpExtended():
    
    ret = queryHelperIp.ip_Graph(collection, "vis")
    return ret

@module.route("/netmon/ip/NodeSigma")
def ip_IpExtendedString():
    
    ret = queryHelperIp.ip_Graph(collection, "sigma")
    return ret

@module.route("/netmon/ip/NodeAlchemy")
def ip_Alchemy():
    
    ret = queryHelperIp.ip_Graph(collection, "alchemy")
    return ret

@module.route("/netmon/ip/NodeForcedGraph")
def ip_NodeForcedGraph():
    
    ret = queryHelperIp.ip_Graph(collection, "forced")
    return ret

@module.route("/netmon/ip/Matrix")
def ip_Matrix():
    
    ret = queryHelperIp.ip_Matrix(collection)
    return ret

@module.route("/netmon/ip/ttl")
def ip_ttl():
    
    ret = queryHelperIp.ip_ttl(collection)
    return ret

@module.route("/netmon/ip/flags")
def ip_flags():
    
    ret = queryHelperIp.ip_flag(collection)
    return ret

@module.route("/netmon/ip/timeline/<int:search>/<int:value>")
def ip_timeline(search, value):

    ret = queryHelperIp.ip_timeline(collection, search, value)
    return ret

############# Transport STUFF #########################################
@module.route("/netmon/transport/IPPortsConnection")
def transport_TransportExtended():
    
    ret = queryHelperTcpUdp.transport_IPPortsConnection(collection, "vis")
    return ret

@module.route("/netmon/transport/IPPortsConnectionCyto")
def transport_IPPortsConnectionCyto():
    
    ret = queryHelperTcpUdp.transport_IPPortsConnection(collection, "cytoscape",firstLevelNodeColor='#0000FF', secondLevelNodeColor='#009900', commRelationColor='#CC0000', openRelationColor='#808080')
    return ret

@module.route("/netmon/transport/sourcePortDistribution")
def transport_sourcePortDistribution():
    
    ret = queryHelperTcpUdp.transport_distribution(collection, "source_port")
    return ret

############# BACNET STUFF #########################################

@module.route("/netmon/bacnet/Prio")
def bacnet_prio():

    ret = queryHelperBacnet.bacnet_prio(collection)
    return ret 

@module.route("/netmon/bacnet/pduFlags")
def bacnet_pduFlags():

    ret = queryHelperBacnet.bacnet_pduFlags(collection)
    return ret

@module.route("/netmon/bacnet/Controller/<int:value>")
def bacnet_Controller(value):

    ret = queryHelperBacnet.bacnet_Controller(collection, value)
    return ret

@module.route("/netmon/bacnet/APDU")
def bacnet_APDU():
    ret = queryHelperBacnet.bacnet_APDU(collection)
    return ret

@module.route("/netmon/bacnet/Matrix")
def bacnet_Matrix():    

    ret = queryHelperBacnet.bacnet_Matrix(collection, key_collection)
    return ret

@module.route("/netmon/bacnet/WhoIs")
def bacnet_WhoIs():
    ret = queryHelperBacnet.bacnet_WhoIs(collection, key_collection)
    return ret

########################################### CELERY - TASKS ###########################################

@celery.task(serializer='json')
def CeleryMonitoringTask(interface, counter, timer, collectionNameToUse):
    
    requestTask = pcapParser.liveMonitoring(interface, int(counter), int(timer), collectionNameToUse, connection, DB_NAME)
    
    queryHelper.makeIndizes(database, collectionNameToUse)

@celery.task(serializer='json')
def CeleryMonitoringTaskRemote(interface, counter, timer, collectionNameToUse, address, port, user, iface):

    requestTask = pcapParser.liveMonitoringRemote(interface, int(counter), int(timer), collectionNameToUse, address, port, user, iface, connection, DB_NAME)

    queryHelper.makeIndizes(database, collectionNameToUse)

@celery.task(serializer='json')
def CeleryStoringTask(fileToStore, nameToStore, descToStore, endeToStore, locToStore, ownerToStore, startToStore):
    
    erg = pcapParser.storeFileIntoDataBase(UPLOAD_FOLDER + "/" + fileToStore, nameToStore, connection, DB_NAME)

    description_collection.insert_one({"Description": descToStore, "Ende": endeToStore, "Location": locToStore, "Name": nameToStore, "Owner": ownerToStore, "Start": startToStore})

    queryHelper.makeIndizes(database, nameToStore)
