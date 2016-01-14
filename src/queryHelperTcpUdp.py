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

def transport_IPPortsConnection(collection, library, firstLevelNodeColor=None, secondLevelNodeColor=None, commRelationColor=None, openRelationColor=None):

    Fields = [['IPHeader.source_address', 'IPHeader.destination_address', 'UdpHeader.source_port', 'UdpHeader.destination_port'],['IPHeader.source_address', 'IPHeader.destination_address', 'TcpHeader.source_port', 'TcpHeader.destination_port']]
    labels = ['IP', 'Port']
    ret = queryHelperGraph.complex_Graph(collection, library, Fields, labels, firstLevelNodeColor, secondLevelNodeColor, commRelationColor, openRelationColor)
    return ret

#ToDo
#Barcharts for TCP Flags 

def transport_distribution(collection, port):

    json_projects = {}
    json_projects['name'] = 'init'
    Child = []
    
    projects = ["UdpHeader", "TcpHeader"];
    
    for project in projects:
        if project == None:
            continue
        tmp = {}
        tmp['id'] = project
        tmp['name'] = str(project)

        x = {"$project": {"type": "$"+project+"."+port, "len": "$"+project+".length"}}
        y = {"$match": {project: {"$exists": True}}}
        z = {"$group": {"_id": "$type", "count": {"$sum" : 1}, "sum": {"$sum" : "$len"}}} 
        pipeline = [y,x,z]
        projectsNew = collection.aggregate(pipeline)

        children = []
        
        sumGes = 0
        countGes = 0
        
        for projectNew in projectsNew:
            if projectNew.get('_id') == None:
                continue
            tmpNew = {}
            servID = int(projectNew.get('_id'))
            tmpNew['id'] = servID
            tmpNew['count'] = int(projectNew.get('count'))
            tmpNew['sum'] = int(projectNew.get('sum'))
            tmpNew['name'] = str(servID)
            children.append(tmpNew)
            sumGes = sumGes + tmpNew['sum']
            countGes = countGes + tmpNew['count']
            
        tmp['children'] = children
        tmp['count'] = countGes
        tmp['sum'] = sumGes
        
        Child.append(tmp)
           
    json_projects['children'] = Child
        
    
    json_projects = json.dumps(json_projects, default=json_util.default)
    return json_projects
