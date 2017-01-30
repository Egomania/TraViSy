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

def bacnet_prio(collection):

    ret = queryHelperGeneral.bar_chart(collection, "Bacnet.pduNetworkPriority")
    return ret

def bacnet_pduFlags(collection):

    value = []
    elem = ('Bacnet.apduSeg', "Segmented Request")
    value.append(elem)
    elem = ('Bacnet.pduExpectingReply', "PDU Expecting Reply")
    value.append(elem)
    elem = ('Bacnet.apduMor', "More Segments")
    value.append(elem)
    elem = ('Bacnet.apduSA', "Segmented Response Accepted")
    value.append(elem)

    ret = queryHelperGeneral.bar_chart_Value(collection, value)
    return ret


def bacnet_Controller(collection, value):

    json_projects = {}
    controller = {}
    bins = {}
    bins['x'] = ['x']
    iprange = []
    lines = []

    x = {"$project": {"mac": "$EthernetHeader.source_address", "ip": "$IPHeader.source_address", "dev": "$Bacnet.iAmDeviceIdentifier", "pduSource": "$Bacnet.pduSource.addrTuple"}}
    y = {"$match": {"Bacnet.apduType": 1, "Bacnet.apduService" : 0 }}
    z = {"$group": {"_id": {"mac": "$mac", "ip": "$ip", "dev": "$dev", "pduSource": "$pduSource"}}} 
    pipeline = [y,x,z]
    try:
        projects = collection.aggregate(pipeline)['results']
    except:
        projects = collection.aggregate(pipeline)

    for project in projects:
        tmp = {}
        tmp['id'] = project.get("_id").get("dev")[1]
        tmp['ip'] = project.get("_id").get("ip")
        tmp['mac'] = project.get("_id").get("mac")
	
	if project.get("_id").get("pduSource") != None:
        	tmp['pduSource'] = project.get("_id").get("pduSource")[0]
	else:
		tmp['pduSource'] = tmp['ip']

        if (tmp['ip'] == tmp['pduSource']):
            controller[tmp['ip']] = tmp['id']
            iprange.append(tmp['ip'])
            bins[tmp['id']] = [str(tmp['id'])]

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

        x = {"$project": {"ip": "$IPHeader.source_address", "pduSource": "$Bacnet.pduSource.addrTuple"}}
        y = {"$match": {"Timestamp": {"$gt": current - value, "$lt": current}, "Bacnet.pduSource" : {"$exists": True},"IPHeader.source_address":  {"$in": iprange}}}
        z = {"$group": {"_id": {"ip": "$ip", "pduSource": "$pduSource"}, "count": {"$sum" : 1}}} 
        pipeline = [y,x,z]
        projects = collection.aggregate(pipeline)

        for project in projects:
            
            tmp['ip'] = project.get("_id").get("ip")
            if project.get("_id").get("pduSource") != None:
                tmp['pduSource'] = project.get("_id").get("pduSource")[0]
            else:
                tmp['pduSource'] = tmp['ip']
            
            
            if (tmp['ip'] == tmp['pduSource']):
                bins[controller[tmp['ip']]].append(project.get("count"))

        for (key, elem) in controller.items():
            if (len(bins[elem]) != len(bins['x'])):
                bins[elem].append(0)


    for elem in bins:
        lines.append(bins[elem])

    json_projects['lines'] = lines
    json_projects = json.dumps(json_projects, default=json_util.default)
    return json_projects

def bacnet_APDU(collection):

    json_projects = {}
    json_projects['name'] = 'init'
    Child = []
    
    Field = 'Bacnet.apduType'
    
    projects = collection.distinct(Field)
   
    for project in projects:
        if project == None:
            continue
        tmp = {}
        tmp['id'] = project
        tmp['name'] = helper.apduTypeName(project)

        x = {"$project": {"type": "$Bacnet.apduService", "len": "$UdpHeader.length"}}
        y = {"$match": {"Bacnet.apduType": project, "UdpHeader.source_port" : 47808 }}
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
            tmpNew['name'] = helper.apduServiceName(project, servID)
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

def bacnet_Matrix(collection, key_collection):    

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

    x = {"$project": {"srcip": "$IPHeader.source_address", "dstip": "$IPHeader.destination_address",  "pduSource": "$Bacnet.pduSource.addrTuple", "pduDest": "$Bacnet.pduDestination.addrTuple" }}
    y = {"$match": {"Bacnet.pduSource" : {"$exists": True}}}
    z = {"$group": {"_id": {"srcip": "$srcip", "dstip": "$dstip", "pduSource": "$pduSource", "pduDest": "$pduDest"}, "count": {"$sum" : 1}}} 
    pipeline = [y,x,z]
    projects = collection.aggregate(pipeline)

    for project in projects:
        tmp = {}
        if project.get("_id").get("pduSource") == None:
            source = project.get("_id").get("srcip")
        else: 
            source = project.get("_id").get("pduSource")[0]

        if project.get("_id").get("pduDest") == None:
            target = project.get("_id").get("dstip")
        else: 
            target = project.get("_id").get("pduDest")[0]

        seenLink = source+target

        if seenLink in seenLinks:
            pass
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

def bacnet_WhoIs(collection, key_collection):    

    json_projects = {}
    nodes = []
    edges = []

    x = {"$project": {"mac": "$EthernetHeader.source_address", "ip": "$IPHeader.source_address", "dev": "$Bacnet.iAmDeviceIdentifier", "pduSource": "$Bacnet.pduSource.addrTuple"}}
    y = {"$match": {"Bacnet.apduType": 1, "Bacnet.apduService" : 0 }}
    z = {"$group": {"_id": {"mac": "$mac", "ip": "$ip", "dev": "$dev", "pduSource" : "$pduSource"}}} 
    pipeline = [y,x,z]
    projects = collection.aggregate(pipeline)

    ident = 1000
    elementList = []
    elementID = {}
    elementFromTo = []
    edgeGroups = []
    edgeGroupColor = {}

    tmp ={}
    tmp['id'] = ident
    tmp['label'] = "Unknown"
    tmp['color'] = '#000000'
    nodes.append(tmp)
    elementList.append("unknown")
    elementID["unknown"] = ident
    ident = ident + 1

    for project in projects:
        etherAdr = project.get('_id').get("mac")
        ipAdr = project.get('_id').get("ip")
        bacnetAdr = int(project.get('_id').get("dev")[1])
        
        if project.get('_id').get("pduSource") != None:
            pduSource = project.get('_id').get("pduSource")[0] 
        else:
            pduSource = ipAdr
        
        if etherAdr in elementList:
            pass
        else:
            tmp ={}
            tmp['id'] = ident
            tmp['label'] = etherAdr
            tmp['color'] = '#4FAFD5'
            nodes.append(tmp)
            elementList.append(etherAdr)
            elementID[etherAdr] = ident
            ident = ident + 1
        if ipAdr in elementList:
            pass
        else:
            tmp = {}
            tmp['label'] = ipAdr
            tmp['id'] = ident
            tmp['color'] = '#FC8200'
            
            nodes.append(tmp)
            elementList.append(ipAdr)
            elementID[ipAdr] = ident
            ident = ident + 1
        if bacnetAdr in elementList:
            pass
        else:
            tmp = {}
            tmp['id'] = ident
            tmp['label'] = bacnetAdr
            tmp['group'] = 'Controller'
            tmp['NetworkFunction'] = 'Controller'
            elementList.append(bacnetAdr)
            elementID[bacnetAdr] = ident
            ident = ident + 1
            additionalInfo = key_collection.find({'physical_address.bacnet_id' : bacnetAdr})
            for info in additionalInfo:
                if info.get('physical_address').get('object_id') == bacnetAdr:
                    tmp['title'] = str(info.get('description'))                   
                    tmp['cid'] = bacnetAdr
                    tmp['Building'] = str(info.get('key_name').get('building').get('fst')) + "." + str(info.get('key_name').get('building').get('snd'))
                    tmp['Floor'] = str(info.get('key_name').get('building').get('floor'))
                    tmp['FunctionalUnit'] = str(info.get('key_name').get('function_code').get('type'))
                    tmp['key'] = info
                else:
                    infoTmp = {}
                    infoTmp['id'] = ident
                    label = str(bacnetAdr) + "." + str(info.get('physical_address').get('object_type')) + "." + str(info.get('physical_address').get('object_id'))
                    infoTmp['label'] = label
                    infoTmp['group'] = 'DataPoint'
                    infoTmp['NetworkFunction'] = 'DataPoint'
                    infoTmp['Building'] = str(info.get('key_name').get('building').get('fst')) + "." + str(info.get('key_name').get('building').get('snd'))
                    infoTmp['Floor'] = str(info.get('key_name').get('building').get('floor'))
                    infoTmp['FunctionalUnit'] = str(info.get('key_name').get('function_code').get('type'))
                    infoTmp['title'] = str(info.get('description'))
                    infoTmp['cid'] = bacnetAdr
                    infoTmp['key'] = info
                    nodes.append(infoTmp)
                    elementID[label] = ident
                    ident = ident + 1
                    infoTmp = {}
                    infoTmp['from'] = elementID[bacnetAdr]
                    infoTmp['to'] = elementID[label]
                    infoTmp['id'] = ident
                    ident = ident + 1
                    infoTmp['edge_context'] = "Controller_DataPoint"
                    edges.append(infoTmp)
                
            nodes.append(tmp)
                
        
        fromTo = {elementID[etherAdr],elementID[ipAdr]}
        if fromTo in elementFromTo:
            pass
        else:
            tmp = {}
            tmp['from'] = elementID[etherAdr]
            tmp['to'] = elementID[ipAdr]
            tmp['id'] = ident
            ident = ident + 1
            tmp['edge_context'] = "MAC_IP"
            edges.append(tmp)
            elementFromTo.append(fromTo)
        
        fromTo = {elementID[ipAdr],elementID[bacnetAdr]}    
        if fromTo in elementFromTo:
            pass
        else:
            tmp = {}
            tmp['from'] = elementID[ipAdr]
            tmp['to'] = elementID[bacnetAdr]
            tmp['id'] = ident
            ident = ident + 1
            if pduSource == ipAdr:
                tmp['edge_context'] = "IP_Bacnet"
            else:
                tmp['edge_context'] = "Router"
                tmp['color'] = '#808080'
                tmp['dashes'] = True
            edges.append(tmp)
            elementFromTo.append(fromTo)
    
    x = {"$project": {"srcmac": "$EthernetHeader.source_address", "dstmac": "$EthernetHeader.destination_address", "srcip": "$IPHeader.source_address", "dstip": "$IPHeader.destination_address", "type": "$Bacnet.apduType", "service": "$Bacnet.apduService", "ident": "$Bacnet.objectIdentifier", "pduSource": "$Bacnet.pduSource.addrTuple" }}
    y = {"$match": {"Bacnet.apduType": {"$gt": -1, "$lt": 2}}}
    z = {"$group": {"_id": {"srcmac": "$srcmac", "srcip": "$srcip", "dstmac": "$dstmac", "dstip": "$dstip", "type": "$type", "service": "$service", "ident": "$ident", "pduSource": "$pduSource"}, "count": {"$sum" : 1}}} 
    pipeline = [y,x,z]
    projects = collection.aggregate(pipeline)

    for project in projects:
        if project.get('_id').get('ident') == None:
            continue
        etherAdrSrc = project.get('_id').get('srcmac')
        ipAdrSrc = project.get('_id').get('pduSource')[0]
        etherAdrDst = project.get('_id').get('dstmac')
        ipAdrDst = project.get('_id').get('dstip')
        if etherAdrSrc in elementList:
            pass
        else:
            tmp ={}
            tmp['id'] = ident
            tmp['label'] = etherAdr
            tmp['color'] = '#4FAFD5'
            nodes.append(tmp)
            elementList.append(etherAdrSrc)
            elementID[etherAdrSrc] = ident
            ident = ident + 1
        if ipAdrSrc in elementList:
            pass
        else:
            tmp = {}
            tmp['id'] = ident
            tmp['label'] = ipAdr
            tmp['color'] = '#FC8200'
            
            nodes.append(tmp)
            elementList.append(ipAdrSrc)
            elementID[ipAdrSrc] = ident
            ident = ident + 1
            
        if etherAdrDst in elementList:
            pass
        else:
            tmp ={}
            tmp['id'] = ident
            tmp['label'] = etherAdr
            tmp['color'] = '#4FAFD5'
            nodes.append(tmp)
            elementList.append(etherAdrDst)
            elementID[etherAdrDst] = ident
            ident = ident + 1
        if ipAdrDst in elementList:
            pass
        else:
            tmp = {}
            tmp['id'] = ident
            tmp['label'] = ipAdr
            tmp['color'] = '#FC8200'
            
            nodes.append(tmp)
            elementList.append(ipAdrDst)
            elementID[ipAdrDst] = ident
            ident = ident + 1
            
        fromTo = {elementID[etherAdrSrc],elementID[ipAdrSrc]}
        if fromTo in elementFromTo:
            pass
        else:
            tmp = {}
            tmp['from'] = elementID[etherAdrSrc]
            tmp['to'] = elementID[ipAdrSrc]
            tmp['id'] = ident
            ident = ident + 1
            tmp['edge_context'] = "MAC_IP"
            edges.append(tmp)
            elementFromTo.append(fromTo)
        fromTo = {elementID[etherAdrDst],elementID[ipAdrDst]}
        if fromTo in elementFromTo:
            pass
        else:
            tmp = {}
            tmp['from'] = elementID[etherAdrDst]
            tmp['to'] = elementID[ipAdrDst]
            tmp['id'] = ident
            ident = ident + 1
            tmp['edge_context'] = "MAC_IP"
            edges.append(tmp)
            elementFromTo.append(fromTo)
        
        fromToFROM = ipAdrSrc
        physicalObjectType = helper.objectTypeName(project.get('_id').get('ident')[0])
        physicalObjectId = int(project.get('_id').get('ident')[1])
        
        
        if (int(project.get('_id').get('ident')[1]) in elementID.keys()):
            label = int(project.get('_id').get('ident')[1])
            
        else:  
            for elem in edges:
                if (elem['from'] == elementID[ipAdrDst] and elem['edge_context'] == 'IP_Bacnet'):
                    bacnetValue = elem['to']
                    for key, value in elementID.iteritems():
                        if (value == bacnetValue):
                            bacnetAdr = key
                            break;
                    label = str(bacnetAdr) + "." + str(physicalObjectType) + "." + str(physicalObjectId)
                    if (label in elementID.keys()):
                        break;
        
        if (label in elementID.keys()):
            fromToTO = label
        else:
            label = "unknown" + "." + str(physicalObjectType) + "." + str(physicalObjectId)
            if (label in elementID.keys()):
                fromToTO = label
            else:
                tmp = {}
                tmp['id'] = ident
                label = "unknown" + "." + str(physicalObjectType) + "." + str(physicalObjectId)
                tmp['label'] = label
                tmp['color'] = '#000000'
                
                nodes.append(tmp)
                elementList.append(label)
                elementID[label] = ident
                ident = ident + 1
                
                tmp = {}
                tmp['from'] = elementID["unknown"]
                tmp['to'] = elementID[label]
                tmp['id'] = ident
                ident = ident + 1
                tmp['edge_context'] = "unknown"
                edges.append(tmp)
                elementFromTo.append(fromTo)
                fromToTO = label
            
        
        
        
        tmp = {}
        tmp['from'] = elementID[fromToFROM]
        tmp['to'] = elementID[fromToTO]
        tmp['id'] = ident
        ident = ident + 1
        tmp['edge_context'] = "ACCESS"
        tmp['count'] = int(project.get('count'))
        tmp['TypeNr'] = int(project.get('_id').get('type'))
        tmp['ServiceNr'] = int(project.get('_id').get('service'))
        tmp['TypeTxt'] = helper.apduTypeName(tmp['TypeNr'])
        tmp['ServiceTxt'] = helper.apduServiceName(tmp['TypeNr'], tmp['ServiceNr'])
        tmp['label'] = str(tmp['count'])
        tmp['labelHighlightBold'] = True
        tmp['dashes'] = True
        tmp['length'] = 2000
        tmp['hidden'] = True
        tmp['group'] = tmp['TypeTxt'] + " " + tmp['ServiceTxt']
        tmp['width'] = int(math.ceil(math.log(project.get('count'))))
        
        if (tmp['group'] in edgeGroups):
            tmp['color'] = edgeGroupColor[tmp['group']]
        else:
            color = "#%06x" % random.randint(0, 0xFFFFFF)
            tmp['color'] = color
            edgeGroups.append(tmp['group'])
            edgeGroupColor[tmp['group']] = color
        edges.append(tmp)
    
    countElem = 0;
    x = -1000
    y = -1000
    for elem in edgeGroups:
        tmp = {}
        tmp['id'] = ident
        ident = ident + 1
        tmp['x'] = x
        tmp['y'] = y + 80 * countElem
        tmp['label'] = str(elem)
        tmp['title'] = "Select"
        tmp['value'] = 1
        tmp['fixed'] = True  
        tmp['physics'] = False
        tmp['group'] = 'EdgeSelectionTRUE'
        tmp['selection'] = elem
        tmp['color'] = edgeGroupColor[elem]
        nodes.append(tmp)
        
        tmp = {}
        tmp['id'] = ident
        ident = ident + 1
        tmp['x'] = x + 250
        tmp['y'] = y + 80 * countElem
        tmp['label'] = str(elem)
        tmp['title'] = "Unselect"
        tmp['value'] = 1
        tmp['fixed'] = True  
        tmp['physics'] = False
        tmp['group'] = 'EdgeSelectionFALSE'
        tmp['selection'] = elem
        tmp['color'] = edgeGroupColor[elem]
        nodes.append(tmp)
        
        countElem = countElem + 1;
    
    
    json_projects['nodes'] = nodes
    json_projects['edges'] = edges
    

    json_projects = json.dumps(json_projects, default=json_util.default)
    return json_projects

