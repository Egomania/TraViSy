import pymongo

from bson import json_util
from bson.json_util import dumps
from bson.son import SON
import json
import random
import math
import time

import helper
import queryHelperGeneral
import queryHelperGraph

def ethernet_Timeline(collection, start, end):

    Fields = ['EthernetHeader.source_address', 'Timestamp', 'EthernetHeader.type']
    
    projects = collection.find(projection=Fields).sort('Timestamp', pymongo.ASCENDING)[start:end]
    
    json_projects = []
    
    for project in projects:
        tmp = {}
        tmp['timestamp'] = project.get('Timestamp')
        tmp[project.get('EthernetHeader').get('source_address')] = hex(int(project.get('EthernetHeader').get('type')))
        json_projects.append(tmp)
    
    json_projects = json.dumps(json_projects, default=json_util.default)
    
    return json_projects

def ethernet_Ethertype(collection):

    ret = queryHelperGeneral.bar_chart(collection, "EthernetHeader.type")
    return ret

def ethernet_Mac(collection):

    Field1 = 'EthernetHeader.source_address'
    Field2 = 'EthernetHeader.destination_address'
    
    projects = collection.find(projection=[Field1]).distinct(Field1)
    json_projects = []
    for project in projects:
        json_projects.append(project)
    projects = collection.find(projection=[Field2]).distinct(Field2)
    for project in projects:
        helper.addDistinct(json_projects, project)
    json_projects = json.dumps(json_projects, default=json_util.default)
    return json_projects

def ethernet_MacSrc(collection):
    
    Field1 = 'EthernetHeader.source_address'
    
    projects = collection.find(projection=[Field1]).distinct(Field1)
    json_projects = []
    for project in projects:
        json_projects.append(project)
    json_projects = json.dumps(json_projects, default=json_util.default)
    return json_projects


def ethernet_Ethernet(collection, library):

    Fields = ['EthernetHeader.source_address', 'EthernetHeader.destination_address']
    ret = queryHelperGraph.grouped_Graph(collection, library, Fields)
    return ret
    
