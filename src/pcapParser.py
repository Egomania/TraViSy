'''
Created on Jun 23, 2015

@author: ansii
'''


import socket
import dpkt
import sys
import time 
import datetime
import struct
import os
import subprocess

import pcapy
import json
import pymongo
import bacpypes
from base64 import b64encode,b64decode

MONGODB_HOST = 'localhost'
MONGODB_PORT = 27017
DB_NAME = 'bacnet'

def todict(obj, classkey=None):
    if isinstance(obj, dict):
        data = {}
        for (k, v) in obj.items():
            data[k] = todict(v, classkey)
        return data
    elif hasattr(obj, "_ast"):
        return todict(obj._ast())
    elif hasattr(obj, "__iter__"):
        return [todict(v, classkey) for v in obj]
    elif hasattr(obj, "__dict__"):
        data = dict([(key, todict(value, classkey)) 
            for key, value in obj.__dict__.iteritems() 
            if not callable(value) and not key.startswith('_')])
        if classkey is not None and hasattr(obj, "__class__"):
            data[classkey] = obj.__class__.__name__
        return data
    else:
        return obj

def decoderList(list):
    
    if list == None: return
    
    for entry in list:
        if (entry == None):
            pass
        else:
            if (type(entry) is dict):
                decoder(entry)
            elif (type(entry) is list):
                decoderList(entry)
            else:
                if ((type(entry) is str) and (entry == 'addrAddr')):
                    entry =  entry.encode('hex')
                elif ((type(entry) is str) and (entry == 'tagData')):
                    entry = entry.encode('hex')
                elif ((type(entry) is str) and (entry == 'pduData')):
                    entry = entry.encode('hex')    
                
                else:
                    pass

def decoder(dictionary):
    
    if dictionary == None: return
    
    for entry in dictionary:
        
        if entry != None and dictionary[entry] != None:
            if (type(dictionary[entry]) is dict):
                decoder(dictionary[entry])
            elif (type(dictionary[entry]) is list):
                decoderList(dictionary[entry])
            else:
                
                if ((type(entry) is str) and (entry == 'addrAddr')):
                    dictionary[entry] =  dictionary[entry].encode('hex')
                elif ((type(entry) is str) and (entry == 'tagData')):
                    dictionary[entry] =  dictionary[entry].encode('hex')
                elif ((type(entry) is str) and (entry == 'pduData')):
                    dictionary[entry] =  dictionary[entry].encode('hex')
                   
                else:
                    pass
                    
            
    return dictionary

def mac_addr(mac_string):
    return ':'.join('%02x' % ord(b) for b in mac_string)

def ip_to_str(address):
    return socket.inet_ntop(socket.AF_INET, address)

def parseExtensionHeader(extHeader):
    
    header = {}

    if type(extHeader) == dpkt.ip6.IP6OptsHeader:
        header.update({'name':'optionHeader'})
        header.update({'len':extHeader.len})

    if type(extHeader) == dpkt.ip6.IP6HopOptsHeader:
        header.update({'name':'hopOptionHeader'})
        header.update({'len':extHeader.len})

    if type(extHeader) == dpkt.ip6.IP6DstOptsHeader:
        header.update({'name':'dstOptionHeader'})
        header.update({'len':extHeader.len})

    if type(extHeader) == dpkt.ip6.IP6RoutingHeader:
        header.update({'name':'routingHeader'})
        header.update({'len':extHeader.len})
        header.update({'sl_bits':extHeader.sl_bits})
        header.update({'rsdv_sl_bits':extHeader.rsdv_sl_bits})
        header.update({'segs_left':extHeader.segd_left})
        header.update({'type':extHeader.type})

    if type(extHeader) == dpkt.ip6.IP6FragmentHeader:
        header.update({'name':'fragmentHeader'})
        header.update({'frag_off':extHeader.frag_off})
        header.update({'m_flag':extHeader.m_flag})
        header.update({'frag_off_resv_m':extHeader.frag_off_resv_m})
        header.update({'id':extHeader.id})
        header.update({'resv':extHeader.resv})

    if type(extHeader) == dpkt.ip6.IP6AHHeader:
        header.update({'name':'ahHeader'})
        header.update({'len':extHeader.len})
        header.update({'seq':extHeader.seq})
        header.update({'spi':extHeader.spi})
        header.update({'resv':extHeader.resv})

    if type(extHeader) == dpkt.ip6.IP6ESPHeader:
        header.update({'name':'espHeader'})
        header.update({'seq':extHeader.seq})
        header.update({'spi':extHeader.spi})

    return header
       

def parseIP6(data):

    ip6Loc = data
    ip6 = {}

    ip6.update({'version':ip6Loc.v})
    ip6.update({'destination_address':socket.inet_ntop(socket.AF_INET6, ip6Loc.dst)})
    ip6.update({'source_address':socket.inet_ntop(socket.AF_INET6, ip6Loc.src)})
    ip6.update({'hop_limit':ip6Loc.hlim})
    ip6.update({'payload_length':ip6Loc.plen})
    ip6.update({'next':ip6Loc.nxt})
    ip6.update({'flow_label':ip6Loc.flow})
    
    next = ip6['next']
    extHeader = []

    while next in [0, 43, 44, 51, 50, 60, 135, 59]:
        header = parseExtensionHeader(ip6Loc.data)
        extHeader.append(header)

        if type(ip6Loc.data) not in [dpkt.ip6.IP6OptsHeader,dpkt.ip6.IP6HopOptsHeader,  dpkt.ip6.IP6DstOptsHeader, dpkt.ip6.IP6RoutingHeader, dpkt.ip6.IP6FragmentHeader, dpkt.ip6.IP6AHHeader, dpkt.ip6.IP6ESPHeader]:
            break

        ip6Loc = ip6Loc.data
        next = ip6Loc.nxt

    if len(extHeader) > 0:
        ip6.update({'extensionHeader':extHeader})

    ip6.update({'data':ip6Loc.data})

    return ip6

def parseTCP(data):
    
    tcpLoc = data

    tcp = {}
    tcp.update({'source_port':tcpLoc.sport})
    tcp.update({'destination_port':tcpLoc.dport})
    tcp.update({'sequence_number':tcpLoc.seq})
    tcp.update({'window':tcpLoc.win})
    tcp.update({'offset':tcpLoc.off})

    optionsLoc = dpkt.tcp.parse_opts(tcpLoc.opts)
    options = {}
    for option in optionsLoc:
        options.update({str(option[0]):option[1].encode('hex')})
    tcp.update({'options':options})

    urg_flag = (tcpLoc.flags & dpkt.tcp.TH_URG) != 0
    tcp.update({'urg_flag':urg_flag})
    ack_flag = (tcpLoc.flags & dpkt.tcp.TH_ACK) != 0
    tcp.update({'ack_flag':ack_flag})
    psh_flag = (tcpLoc.flags & dpkt.tcp.TH_PUSH) != 0
    tcp.update({'psh_flag':psh_flag}) 
    rst_flag = (tcpLoc.flags & dpkt.tcp.TH_RST) != 0
    tcp.update({'rst_flag':rst_flag})
    syn_flag = (tcpLoc.flags & dpkt.tcp.TH_SYN) != 0
    tcp.update({'syn_flag':syn_flag}) 
    fin_flag = (tcpLoc.flags & dpkt.tcp.TH_FIN) != 0
    tcp.update({'fin_flag':fin_flag})     

    tcp.update({'data':tcpLoc.data})

    return tcp

def parseARP(data):
    
    arpLoc = data

    arp = {}

    arp.update({'hlen':arpLoc.hln})
    arp.update({'plen':arpLoc.pln})
    arp.update({'operation':arpLoc.op})
    arp.update({'htype':arpLoc.hrd})
    arp.update({'ptype':arpLoc.pro})

    if (arpLoc.hrd == 1) and (arpLoc.pro == dpkt.ethernet.ETH_TYPE_IP):

        arp.update({'sender_hw_address':mac_addr(arpLoc.sha)})
        arp.update({'target_hw_address':mac_addr(arpLoc.tha)})
        arp.update({'sender_proto_address':ip_to_str(arpLoc.spa)})
        arp.update({'target_proto_address':ip_to_str(arpLoc.tpa)})
    
    else: 
        return {}

    return arp

def parseUDP(data):
    
    udpLoc = data

    udp = {}

    udp.update({'source_port':udpLoc.sport})
    udp.update({'destination_port':udpLoc.dport})
    udp.update({'length':udpLoc.ulen})
    udp.update({'checksum':udpLoc.sum})

    udp.update({'data':udpLoc.data})

    return udp

def parseICMP(data):
    
    icmpLoc = data

    icmp = {}

    icmp.update({'type':icmpLoc.type})
    icmp.update({'code':icmpLoc.code})
    icmp.update({'checksum':icmpLoc.sum})

    if (icmpLoc.type == 0) or (icmpLoc.type == 8):
        
        icmp.update({'id': icmpLoc.data.id})
        icmp.update({'seq': icmpLoc.data.seq})

    if (icmpLoc.type == 3):

        icmp.update({'mtu': icmpLoc.data.mtu})
        header = parseIP(icmpLoc.data.data)
        del header['data']
        icmp.update({'header': header})

    if (icmpLoc.type == 11):
  
        header = parseIP(icmpLoc.data.data)
        del header['data']
        icmp.update({'header': header})

    return icmp

def parseICMP6(data):
    
    icmp6Loc = data

    icmp6 = {}

    icmp6.update({'type':icmp6Loc.type})
    icmp6.update({'code':icmp6Loc.code})
    icmp6.update({'checksum':icmp6Loc.sum})

    if (icmp6Loc.type == 128) or (icmp6Loc.type == 129):
        
        icmp6.update({'id': icmp6Loc.data.id})
        icmp6.update({'seq': icmp6Loc.data.seq})

    if (icmp6Loc.type == 1) or (icmp6Loc.type == 3) or (icmp6Loc.type == 4):
  
        header = parseIP6(icmp6Loc.data.data)
        del header['data']
        icmp6.update({'header': header})

    if (icmp6Loc.type == 2):
  
        icmp6.update({'mtu': icmp6Loc.data.mtu})
        header = parseIP6(icmp6Loc.data.data)
        del header['data']
        icmp6.update({'header': header})


    return icmp6

def parseIP(data):
    
    ipLoc = data

    ip = {}
    
    ip.update({'total_len':ipLoc.len})
    ip.update({'protocol':ipLoc.p})
    ip.update({'tos':ipLoc.tos})
    ip.update({'header_len':ipLoc.hl})
    ip.update({'options':ipLoc.opts.encode('hex')})    
    ip.update({'version':ipLoc.v})
    ip.update({'ttl':ipLoc.ttl})
    ip.update({'flag_RF':(ipLoc.off >> 15) & 0x1})
    ip.update({'flag_DF':(ipLoc.off >> 14) & 0x1})
    ip.update({'flag_MF':(ipLoc.off >> 13) & 0x1})
    ip.update({'fragment_offset':(ipLoc.off & dpkt.ip.IP_OFFMASK) << 3})
    ip.update({'destination_address':ip_to_str(ipLoc.dst)})
    ip.update({'checksum':ipLoc.sum})
    ip.update({'source_address':ip_to_str(ipLoc.src)})
    ip.update({'id':ipLoc.id})

    ip.update({'data':ipLoc.data})

    return ip

def decodePaket(ts, data, mode):

    #set Defaults:
    ether = None
    ip = None
    ip6 = None
    udp = None
    tcp = None
    bacnetPkt = None
    arp = None
    icmp = None
    icmp6 = None
    
    #-----------------------------------------------------
    #EthernetHeader
    #-----------------------------------------------------

    ether = bacpypes.analysis.decode_ethernet(data)

    eth = dpkt.ethernet.Ethernet(data)

    #-----------------------------------------------------
    # Layer 3 and 4 parsing
    #-----------------------------------------------------

    #IPv4
    if ether['type'] == dpkt.ethernet.ETH_TYPE_IP:
        ip = parseIP(eth.data)

        if ip['protocol'] == dpkt.ip.IP_PROTO_UDP:
            udp = parseUDP(ip['data'])

        elif ip['protocol'] == dpkt.ip.IP_PROTO_TCP:
            tcp = parseTCP(ip['data'])

        elif ip['protocol'] == dpkt.ip.IP_PROTO_ICMP:
            icmp = parseICMP(ip['data'])
            
        else: 
            #default, in case other protocols are needed, this has to be extended
            pass

    #IPv6
    elif ether['type'] == dpkt.ethernet.ETH_TYPE_IP6:
        ip6 = parseIP6(eth.data)

        if ip6['next'] == 17:
            udp = parseUDP(ip6['data'])

        elif ip6['next'] == 6:
            tcp = parseTCP(ip6['data'])

        elif ip6['next'] == 58:
            icmp6 = parseICMP6(ip6['data'])
            
        else: 
            #default, in case other protocols are needed, this has to be extended
            pass
    
    #ARP
    elif ether['type'] == dpkt.ethernet.ETH_TYPE_ARP:
        arp = parseARP(eth.data)

    else:
        #default, in case other protocols are needed, this has to be extended
        pass

        
    #-----------------------------------------------------
    #ApplicationLayer Parsing
    #-----------------------------------------------------

    #BacnetPakets
    if (udp) and (udp['source_port'] == 47808 or udp['destination_port'] == 47808):

        paket = bacpypes.analysis.decode_packet(data)
        bacnetPkt = todict(paket)
        bacnetPkt = decoder(bacnetPkt)

    
    #-----------------------------------------------------
    #Pack everything togehther
    #-----------------------------------------------------

    bacnetPktcomplete = {}


    if mode:
        bacnetPktcomplete.update({'Timestamp':ts})
    else:
        bacnetPktcomplete.update({'Timestamp':ts.getts()[0]})

    if ether != None:
        del ether['data']
        bacnetPktcomplete.update({'EthernetHeader':ether})

    if arp != None:
        bacnetPktcomplete.update({'ArpHeader':arp})

    if ip != None:
        del ip['data']
        bacnetPktcomplete.update({'IPHeader':ip})

    if icmp != None:
        bacnetPktcomplete.update({'IcmpHeader':icmp})

    if ip6 != None:
        del ip6['data']
        bacnetPktcomplete.update({'IP6Header':ip6})

    if icmp6 != None:
        bacnetPktcomplete.update({'Icmp6Header':icmp6})

    if udp != None:
        del udp['data']
        bacnetPktcomplete.update({'UdpHeader':udp})
    
    if tcp != None:
        del tcp['data']
        bacnetPktcomplete.update({'TcpHeader':tcp})
    
    if bacnetPkt != None:
        bacnetPktcomplete.update({'Bacnet':bacnetPkt})	

    return bacnetPktcomplete

def setTimer(timer):

    if not timer:
        timerLocal = 100
    else:
        timerLocal = timer

    print "Local Timer used:"
    print timerLocal

    return timerLocal

def setCounter(pktCount):

    if not pktCount:
        pktCountLocal = 100
    else:
        pktCountLocal = pktCount

    print "Local Counter used:"
    print pktCountLocal

    return pktCountLocal

def storeFileIntoDataBase(fileName, collectionName):

    pcapReader = dpkt.pcap.Reader(open(fileName, "rb"))

    COLLECTION_NAME = collectionName

    connection = pymongo.MongoClient(MONGODB_HOST, MONGODB_PORT)
    database = connection[DB_NAME]
    collection = connection[DB_NAME][COLLECTION_NAME]

    i = 0

    t1 = time.clock()

    for ts, data in pcapReader:

        bacnetPktcomplete = decodePaket(ts, data, True)

        result = collection.insert_one(bacnetPktcomplete)
        
        i = i + 1
        
    t2 = time.clock()
    t = t2 - t1

    print 'Pakete eingelesen: ', i, 'Laufzeit: ', t
    return {"pak": i, "run": t}    


def liveMonitoring(interface, pktCount, timer, collectionName):
  
    COLLECTION_NAME = collectionName

    connection = pymongo.MongoClient(MONGODB_HOST, MONGODB_PORT)
    database = connection[DB_NAME]
    collection = connection[DB_NAME][COLLECTION_NAME]

    capture = pcapy.open_live(interface, 1600, True, 100)
    print 'opened interface'
    i = 0
    t1 = time.clock()
    
    timerLocal = setTimer(timer)
    pktCountLocal = setCounter(pktCount)

    print 'start Loop'
    while 1:        

        try:
            (header,payload) = capture.next()

        except pcapy.PcapError:
            continue

        else:

            if not payload:
                val = 0 
            else:
                val = 1

                bacnetPktcomplete = decodePaket(header, payload, False)

                result = collection.insert_one(bacnetPktcomplete)
                

            i = i + val
            t2 = time.clock()

            if i > pktCountLocal:
                print "Counter Exceeded"
                print i
                break

            if (t2 - t1) > timerLocal:
                print "Timer Exceeded"
                print timerLocal
                break

        
    
def liveMonitoringRemote(interface, pktCount, timer, collectionName, address, port, user, iface):
  
    COLLECTION_NAME = collectionName

    connection = pymongo.MongoClient(MONGODB_HOST, MONGODB_PORT)
    database = connection[DB_NAME]
    collection = connection[DB_NAME][COLLECTION_NAME]

    print 'try to establish connection'

    cmd = "./connect.sh"

    subprocess.Popen([cmd, user, address, iface, interface])

    f = open(interface)

    pcapReader = dpkt.pcap.Reader(f)

    print 'opened interface'
    i = 0
    t1 = time.clock()
    
    timerLocal = setTimer(timer)
    pktCountLocal = setCounter(pktCount)

    print 'start Loop'
    for ts, data in pcapReader:       

        if not data:
            val = 0 
        else:
            val = 1

            bacnetPktcomplete = decodePaket(ts, data, True)

            result = collection.insert_one(bacnetPktcomplete)

        i = i + val
        t2 = time.clock()

        if i > pktCountLocal:
            print "Counter Exceeded"
            print i
            break

        if (t2 - t1) > timerLocal:
            print "Timer Exceeded"
            print timerLocal
            break

        
    
