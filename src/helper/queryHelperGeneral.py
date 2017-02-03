from bson import json_util
from bson.json_util import dumps
from bson.son import SON
import json

import random
import math

import pymongo

# Function to create bar charts for a searchObject and its instances
def bar_chart(collection, searchObject):

    searchObjectExt = "$" + searchObject

    x = {"$project": {"type": searchObjectExt}}
    y = {"$match": {searchObject: {"$exists": True}}}
    z = {"$group": {"_id": "$type", "count": {"$sum" : 1}}} 
    pipeline = [x,z]
    projects = collection.aggregate(pipeline)

    json_projects = []
    for project in projects:
        if project.get('_id') != None:
            project['type'] = int(project.get('_id'))
            project['count'] = int(project.get('count'))
            del project['_id']
            json_projects.append(project)
    json_projects = json.dumps(json_projects, default=json_util.default)
    return json_projects

# Function to create bar charts for a list searchObject and its values
# Define the string that has to be printed under each bar
def bar_chart_Value(collection, searchCollection):

    json_projects = []

    for elem in searchCollection:
        field = {elem[0]: True}
        projects = collection.find(field).count()
        tmp = {}
        tmp['type'] = elem[1]
        tmp['count'] = projects
        json_projects.append(tmp)
    
    json_projects = json.dumps(json_projects, default=json_util.default)
    return json_projects


