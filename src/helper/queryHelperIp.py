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

def ip_ttl(collection):

    ret = queryHelperGeneral.bar_chart(collection, "IPHeader.ttl")
    return ret

def ip_flag(collection):

    value = []
    elem = ('IPHeader.flag_MF', "More Fragments")
    value.append(elem)
    elem = ('IPHeader.flag_DF', "Do not Fragment")
    value.append(elem)
    elem = ('IPHeader.flag_RF', "Reserved")
    value.append(elem)

    ret = queryHelperGeneral.bar_chart_Value(collection, value)
    return ret

def ip_Graph(collection, library):

    Fields = ['IPHeader.source_address', 'IPHeader.destination_address']
    ret = queryHelperGraph.plain_Graph(collection, library, Fields)
    return ret

def ip_timeline(collection, search, value):

    json_projects = {}
    bins = {}
    bins['x'] = ['x']
    lines = []
    ips = []
    Field = ""
    if search == 0:
        Field = "IPHeader.destination_address"
    elif search == 1:
        Field = "IPHeader.source_address"
    else:
        search = ""

    projects = collection.find({"EthernetHeader.type":2048}).distinct(Field)


    for project in projects:
        bins[project] = [str(project)]
        ips.append(project)

    Fields = ['Timestamp']
    projects = collection.find(projection=Fields).sort('Timestamp', pymongo.ASCENDING).limit(1)
    for project in projects:
        minimum = project.get('Timestamp')

    projects = collection.find(projection=Fields).sort('Timestamp', pymongo.DESCENDING).limit(1)
    for project in projects:
        maximum = project.get('Timestamp')

    
    current = minimum
    while (current < maximum):
        current = current + value 
        bins['x'].append(current)

        x = {}
        if search == 0:
            x = {"$project": {"ip": "$IPHeader.destination_address"}}
        elif search == 1:
            x = {"$project": {"ip": "$IPHeader.source_address"}}
        else:
            pass

        y = {"$match": {"Timestamp": {"$gt": current - value, "$lt": current}, Field : {"$exists": True}}}
        z = {"$group": {"_id": {"ip": "$ip"}, "count": {"$sum" : 1}}} 
        pipeline = [y,x,z]
        try:
            projects = collection.aggregate(pipeline)['result']
        except:
            projects = collection.aggregate(pipeline)

        for project in projects:
            
            ip = project.get("_id").get("ip")
            bins[ip].append(project.get("count"))
            

        for elem in ips:
            if (len(bins[elem]) != len(bins['x'])):
                bins[elem].append(0)


    for elem in bins:
        lines.append(bins[elem])

    json_projects['lines'] = lines
    json_projects = json.dumps(json_projects, default=json_util.default)
    return json_projects

def ip_Matrix(collection):    

    json_projects = {}
    nodes = []
    links = []
    nodes_ = []
    nodeLink = {}
    seenLinks = {}

    ident = 0

    Field = "IPHeader.destination_address"
    projects = collection.find({"EthernetHeader.type":2048}).distinct(Field)

    for project in projects:
        helper.addDistinct(nodes_, project)

    Field = "IPHeader.source_address"
    projects = collection.find({"EthernetHeader.type":2048}).distinct(Field)

    for project in projects:
        helper.addDistinct(nodes_, project)


    for node in nodes_:
        tmp = {}
        tmp["name"] = node
        tmp["id"] = ident
        nodeLink[node] = ident
        ident = ident + 1
        tmp["group"] = 1
        nodes.append(tmp)

    x = {"$project": {"srcip": "$IPHeader.source_address", "dstip": "$IPHeader.destination_address" }}
    y = {"$match": {"IPHeader.source_address" : {"$exists": True}}}
    z = {"$group": {"_id": {"srcip": "$srcip", "dstip": "$dstip"}, "count": {"$sum" : 1}}} 
    pipeline = [y,x,z]
    projects = collection.aggregate(pipeline)

    for project in projects:
        tmp = {}
        source = project.get("_id").get("srcip")
        target = project.get("_id").get("dstip")

        seenLink = source+target

        if seenLink in seenLinks:
            for singleLink in links:
                if singleLink["source"] == source and singleLink["target"] == target:
                    singleLink["value"] = singleLink["value"] + project.get("count")

        else:
            tmp["source"] = nodeLink[source]
            tmp["target"] = nodeLink[target]
            tmp["value"] = project.get("count")
            links.append(tmp)
            seenLinks[seenLink] = links.index(tmp)

    json_projects["nodes"] = nodes
    json_projects["links"] = links
    json_projects = json.dumps(json_projects, default=json_util.default)
    return json_projects


def ip_Ip(collection, library):

    Fields = ['IPHeader.source_address', 'IPHeader.destination_address']
    ret = queryHelperGraph.grouped_Graph(collection, library, Fields)
    return ret
