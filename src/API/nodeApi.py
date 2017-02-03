import random
import math

# Make Nodes for different libraries
# ToDo adapt libraries to cope with all available inputs
def makeNode(library, project, ident, group=None, showedName=None, color=None):
    node = {}
    if library == 'sigma':
        node = makeSigmaNode(project, ident, group, showedName, color)
        return node
    elif library == 'vis':
        node = makeVISNode(project, ident, group, showedName, color)
        return node
    elif library == 'alchemy':
        node = makeAlchemyNode(project, ident, group, showedName, color)
        return node
    elif library == 'forced':
        node = makeForcedNode(project, ident, group, showedName, color)
        return node
    elif library == 'cytoscape':
        node = makeCytoNode(project, ident, group, showedName, color)
        return node
    else:
        return node

def makeCytoNode(project, ident, group, showedName, color):
    node = {}
    dataNode = {}

    dataNode['id'] = project
    if showedName != None:
        dataNode['name'] = showedName
    else:
        dataNode['name'] = project

    if color != None:
        dataNode['faveColor'] = color

    if group != None:
        dataNode['initClass'] = group

    node['data'] = dataNode

    return node

def makeSigmaNode(project, ident, group, showedName, color):
    node = {}
    node['id'] = str(ident)
    node['size'] = 1
    node['x'] = random.randrange(0, 100)
    node['y'] = random.randrange(0, 100)
    if showedName != None:
        node['label'] = showedName
    else:
        node['label'] = project
    return node

def makeVISNode(project, ident, group, showedName, color):
    node = {}
    node['id'] = ident

    if showedName != None:
        node['label'] = showedName
    else:
        node['label'] = project

    if color != None:
        node['color'] = color

    if group != None:
        node['group'] = group

    return node

def makeAlchemyNode(project, ident, group, showedName, color):
    node = {}
    node['id'] = ident
    if showedName != None:
        node['caption'] = showedName
    else:
        node['caption'] = project
    return node

def makeForcedNode(project, ident, group, showedName, color):
    node = {}
    node['id'] = project
    if showedName != None:
        node['name'] = showedName
    else:
        node['name'] = project
    if group != None:
        node['group'] = group
    return node

