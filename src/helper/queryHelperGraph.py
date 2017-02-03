from bson import json_util
from bson.json_util import dumps
from bson.son import SON
import json

import random
import math

import pymongo

from API import nodeApi
from API import linkApi
from API import libApi

# Create a plain graph showing traffic realtions
def plain_Graph(collection, library, values):

    json_projects = {}
    Fields = values
    
    nodeIndentMapper = {}
    naming = ()
    json_nodes = []
    json_links = []
    ident = 0

    for elem in Fields:
        projects = collection.find(projection=[elem]).distinct(elem)

        for project in projects:
            
            if nodeIndentMapper.get(project) == None:
                node = {}

                node = nodeApi.makeNode(library, project, ident)
                
                json_nodes.append(node)
                nodeIndentMapper[project] = ident
                ident = ident + 1


    x = {"$project": {"source": "$IPHeader.source_address", "destination": "$IPHeader.destination_address"}}
    z = {"$group": {"_id": {"source": "$source", "destination": "$destination"}, "count": {"$sum" : 1}}} 
    pipeline = [x,z]

    try:
        projects = collection.aggregate(pipeline)['result']
    except:
        projects = collection.aggregate(pipeline)

    for project in projects: 

        if project.get('_id').get('source') != None and project.get('_id').get('destination') != None:
            link = {}

            link = linkApi.makeLink(library, project, ident, nodeIndentMapper)

            ident = ident + 1            
            
            json_links.append(link)

    json_projects = libApi.createDataSet(library, json_nodes, json_links)
    json_projects = json.dumps(json_projects, default=json_util.default)
    return json_projects

#Create a more complex Graph with "associated" and "communication" relations
def complex_Graph(collection, library, Fields, labels, firstLevelNodeColor, secondLevelNodeColor, commRelationColor, openRelationColor):

    ident = 0
    json_projects = {}
    nodeIndentMapper = {}
    ident = 0
    seenLinks = []
    json_nodes = []
    json_links = []

    for FieldElem in Fields:
        Src = FieldElem[0]
        Dst = FieldElem[1]
        SrcSpec = FieldElem[2]
        DstSpec = FieldElem[3]

        SrcExt = "$" + FieldElem[0]
        DstExt = "$" + FieldElem[1]
        SrcSpecExt = "$" + FieldElem[2]
        DstSpecExt = "$" + FieldElem[3]

        x = {"$project": {"source": SrcExt, "destination": DstExt, "source_spec" : SrcSpecExt, "destination_spec" : DstSpecExt}}
        z = {"$group": {"_id": {"source": "$source", "destination": "$destination", "source_spec": "$source_spec", "destination_spec": "$destination_spec"}, "count": {"$sum" : 1}}} 
        pipeline = [x,z]
        try:
            projects = collection.aggregate(pipeline)['result']
        except:
            projects = collection.aggregate(pipeline)

        for project in projects:
            
            # add first level nodes
            src = project.get("_id").get("source")
            dst = project.get("_id").get("destination")
            srcS = project.get("_id").get("source_spec")
            dstS = project.get("_id").get("destination_spec")

            if src != None and dst != None and srcS != None and dstS != None:
           
                # add nodes
                src_special = src + "_" + str(srcS)
                dst_special = dst + "_" + str(dstS)

                NodeStringList = [src, dst]

                for elem in NodeStringList:

                    if nodeIndentMapper.get(elem) == None:
                        node = {}
                        node = nodeApi.makeNode(library, elem, ident, group=labels[0],color=firstLevelNodeColor)
                        json_nodes.append(node)
                        nodeIndentMapper[elem] = ident
                        ident = ident + 1

                NodeStringList = [src_special, dst_special]

                for elem in NodeStringList:

                    if nodeIndentMapper.get(elem) == None:
                        node = {}
                        node = nodeApi.makeNode(library, elem, ident, group=labels[1], showedName=elem.split('_')[1], color=secondLevelNodeColor)
                        json_nodes.append(node)
                        nodeIndentMapper[elem] = ident
                        ident = ident + 1
                
                # add connection between first and seconLevelNode
                FirstLevelNodes = [[src, src_special], [dst, dst_special]]

                for elem in FirstLevelNodes:

                    linkName = elem[0] + elem[1]

                    if linkName not in seenLinks:
                        
                        link = {}
                        projectTmp = {}
                        idTmp = {}
                        idTmp['source'] = elem[0]
                        idTmp['destination'] = elem[1]
                        projectTmp['_id'] = idTmp
                        projectTmp['count'] = 1
                        link = linkApi.makeLink(library, projectTmp, ident, nodeIndentMapper, color=openRelationColor, context='open', directed=False)
                        ident = ident + 1                    
                        json_links.append(link) 
                        seenLinks.append(linkName)

                # add communication
                link = {}
                projectTmp = {}
                idTmp = {}
                idTmp['source'] = src_special
                idTmp['destination'] = dst_special
                projectTmp['_id'] = idTmp
                projectTmp['count'] = project['count']
                link = linkApi.makeLink(library, projectTmp, ident, nodeIndentMapper, color=commRelationColor, context='communicate')
                ident = ident + 1                    
                json_links.append(link) 
            

    json_projects = libApi.createDataSet(library, json_nodes, json_links)

    json_projects = json.dumps(json_projects, default=json_util.default)
    return json_projects

# Values have to be provided by: source, destination
def grouped_Graph(collection, library, values):

    json_projects = {}
    nodeIndentMapper = {}
    ident = 0

    Field1 = values[0]
    Field2 = values[1]

    Field1Ext = "$" + Field1
    Field2Ext = "$" + Field2
    
    projects = collection.find(projection=[Field1]).distinct(Field1)
    json_nodes = []
    for project in projects:
        if nodeIndentMapper.get(project) == None:
            node = {}
            node = nodeApi.makeNode(library, project, ident, group=1)
            json_nodes.append(node)
            ident = ident + 1
            nodeIndentMapper[project] = ident

    projects = collection.find(projection=[Field2]).distinct(Field2)
    for project in projects:
        for entry in json_nodes:
            found = False
            if entry.get('name') == project:
                entry = libApi.changeValue(library, entry, 'group', 3)
                found = True
                break
        if found == False:
            if nodeIndentMapper.get(project) == None:
                node = {}
                node = nodeApi.makeNode(library, project, ident, group=2)
                json_nodes.append(node)
                ident = ident + 1
                nodeIndentMapper[project] = ident
    
    x = {"$project": {"source": Field1Ext, "destination": Field2Ext}}
    z = {"$group": {"_id": {"source": "$source", "destination": "$destination"}, "count": {"$sum" : 1}}} 
    pipeline = [x,z]
    try:
        projects = collection.aggregate(pipeline)['result']
    except:
        projects = collection.aggregate(pipeline)

    json_links = []
    for project in projects: 
        link = {}
        link = linkApi.makeLink(library, project, ident, nodeIndentMapper)
        if project.get('_id').get('source') != None and project.get('_id').get('destination') != None:
            json_links.append(link)
            ident = ident + 1
        
    json_projects = libApi.createDataSet(library, json_nodes, json_links)
    json_projects = json.dumps(json_projects, default=json_util.default)
    return json_projects
