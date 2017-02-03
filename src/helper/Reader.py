import csv
import sys
import string

def store(csvfile, connection, key_collection):

    keyCollection = connection[DB_NAME_KEY][key_collection]

    reader = csv.DictReader(csvfile, delimiter=';', quoting=csv.QUOTE_NONE)
    for row in reader:
        key = {}
        key['subsys'] = row['subsys_short_name']
        key['description'] = row['point_descriptor']
        # parse pysical address
        physical_address = {}
        physical_address['bus_number'] = row['bus_number']
        physical_address['bacnet_id'] = row['bacnet_id']
        physical_address['object_type'] = row['object_type']
        physical_address['object_id'] = row['object_id']
        key['physical_address'] = physical_address
        
        #parse key name
        key_name = {}
        
        #Bauwerk und Etage
        building = {}
        building['fst'] = row['fst']
        building['snd'] = row['snd']
        building['floor'] = row['floor']
        key_name['building'] = building
        
        #Funktionseinheit und Nummer
        function_unit = {}
        function_unit['type'] = row['fu_type']
        function_unit['serial'] = row['fu_serial']
        key_name['unit_id'] = function_unit
        
        #Funktionscode
        function_code = {}
        function_code['type'] = row['fc_type']
        function_code['serial'] = row['fc_serial']
        function_code['counter'] = row['fc_counter']
        key_name['function_code'] = function_code
        
        key['key_name'] = key_name
        
        result = keyCollection.insert_one(key)
