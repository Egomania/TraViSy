def createDataSet(library, nodes, links):
    json_projects = {}
    naming = ("","")
    if library == 'sigma':
        naming = ("nodes", "edges")
    elif library == 'vis':
        naming = ("nodes", "links")
    elif library == 'alchemy':
        naming = ("nodes", "edges")
    elif library == 'forced':
        naming = ("nodes", "links")
    elif library == 'cytoscape':
        naming = ("nodes", "edges")
    else:
        pass

    json_projects[naming[0]] = nodes
    json_projects[naming[1]] = links

    return json_projects

# ToDo: ggf specify library options    
def changeValue (library, elem, key2Change, newValue):
    elem[key2Change] = newValue
    return elem
