import pymongo

from bson import json_util
from bson.json_util import dumps
from bson.son import SON
import json
import random
import math
import time

import helper

def collectionsDescription(description_collection):

    coll = description_collection.find({})  
    collections = []

    for collection in coll:
        collectionDescriptionEntry = {}
        collectionDescriptionEntry['id'] = str(collection.get("_id"))
        collectionDescriptionEntry['name'] = collection.get("Name")
        collectionDescriptionEntry['owner'] = collection.get("Owner")
        collectionDescriptionEntry['descr'] = collection.get("Description")
        collectionDescriptionEntry['start'] = collection.get("Start")
        collectionDescriptionEntry['ende'] = collection.get("Ende")
        collectionDescriptionEntry['location'] = collection.get("Location")
        collections.append(collectionDescriptionEntry)
    

    collections = json.dumps(collections, default=json_util.default)
    return collections

def pktDistribution(collection):
    collections = []
    protos = ["EthernetHeader","ArpHeader", "IPHeader", "IcmpHeader", "IP6Header", "Icmp6Header",  "TcpHeader", "UdpHeader", "Bacnet"]

    for item in protos:
        col = {}
        num = collection.count({item:{"$exists":True}})
        col = {"count":num, "type":item}
        collections.append(col)
    
    collections = json.dumps(collections, default=json_util.default)
    return collections

def collectionDescription(database, description_collection):
    collectionList = database.collection_names(include_system_collections=False)

    collectionDescription = []
        
    for listElem in collectionList:

        collectionDescriptionEntry = {}
        collectionDescriptionEntry['name'] = listElem
        desc = description_collection.find({'Name' : listElem})
        for descEntry in desc:
            collectionDescriptionEntry['_id'] = descEntry.get("_id")
            collectionDescriptionEntry['owner'] = descEntry.get("Owner")
            collectionDescriptionEntry['descr'] = descEntry.get("Description")
            collectionDescriptionEntry['start'] = descEntry.get("Start")
            collectionDescriptionEntry['ende'] = descEntry.get("Ende")
            collectionDescriptionEntry['location'] = descEntry.get("Location")
        collectionDescription.append(collectionDescriptionEntry)

    return collectionDescription

def collectionConfig(config_collection):

    collect = config_collection.find({})

    collections = []

    for col in collect:
        entry = {}
        entry["id"] = col.get("_id")
        entry["name"] = col.get("name")
        entry["address"] = col.get("address")
        entry["port"] = col.get("port")
        entry["user"] = col.get("user")
        entry["pwd"] = col.get("pwd")
        entry["dev"] = col.get("dev")
        entry["iface"] = col.get("iface")
        collections.append(entry)

    return collections

def getConfigurations(config_collection):

    collect = config_collection.find({})

    collections = []

    for col in collect:
        collections.append(col.get("name"))

    return collections


def makeIndizes(database, collectionName):

    collection = database[collectionName]
    collection.create_index([("Timestamp", pymongo.DESCENDING)], background = True)
    collection.create_index([("Timestamp", pymongo.ASCENDING)], background = True)
    collection.create_index([("EthernetHeader.source_address", pymongo.ASCENDING)], background = True)
    collection.create_index([("EthernetHeader.type", pymongo.ASCENDING)], background = True)
    collection.create_index([("EthernetHeader.destination_address", pymongo.ASCENDING)], background = True)
    collection.create_index([("EthernetHeader.source_address", pymongo.ASCENDING), ("EthernetHeader.destination_address", pymongo.ASCENDING)], background = True)
    collection.create_index([("Bacnet.pduNetworkPriority", pymongo.ASCENDING)], background = True)
    collection.create_index([("Bacnet.apduSeg", pymongo.ASCENDING)], background = True)
    collection.create_index([("Bacnet.apduMor", pymongo.ASCENDING)], background = True)
    collection.create_index([("Bacnet.apduSA", pymongo.ASCENDING)], background = True)
    collection.create_index([("Bacnet.apduExpectingReply", pymongo.ASCENDING)], background = True)
    collection.create_index([("Bacnet.apduType", pymongo.ASCENDING)], background = True)
    collection.create_index([("Bacnet.apduService", pymongo.ASCENDING)], background = True)
    collection.create_index([("EthernetHeader.source_address", pymongo.ASCENDING), ("IPHeader.source_address", pymongo.ASCENDING), ("Bacnet.iAmDeviceIdentifier", pymongo.ASCENDING)], background = True)
