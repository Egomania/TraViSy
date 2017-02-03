# Make Links for different libraries
# ToDo adapt libraries to cope with all available inputs

def makeLink(library, project, ident, nodeIndentMapper, directed=True, showedName=None, color=None, context=None, count=True):
    link = {}
    if library == 'sigma':
        link = makeSigmaLink(project, ident, nodeIndentMapper, directed, showedName, color, context, count)
        return link
    elif library == 'vis':
        link = makeVISLink(project, ident, nodeIndentMapper, directed, showedName, color, context, count)
        return link
    elif library == 'alchemy':
        link = makeAlchemyLink(project, ident, nodeIndentMapper, directed, showedName, color, context, count)    
        return link
    elif library == 'forced':
        link = makeForcedLink(project, ident, nodeIndentMapper, directed, showedName, color, context, count)
        return link
    elif library == 'cytoscape':
        link = makeCytoLink(project, ident, nodeIndentMapper, directed, showedName, color, context, count)
        return link
    else:
        return link

def makeCytoLink(project, ident, nodeIndentMapper, directed, showedName, color, context, count):
    link = {}
    dataLink = {}

    dataLink['id'] = str(ident)
    dataLink['source'] = project.get('_id').get('source')
    dataLink['target'] = project.get('_id').get('destination')

    if (directed):
        dataLink["directed"] = '1'
    else:
        dataLink["directed"] = '0'

    if color != None:
        dataLink['faveColor'] = color

    link['data'] = dataLink
    return link

def makeSigmaLink(project, ident, nodeIndentMapper, directed, showedName, color, context, count):
    link = {}
    link['id'] = str(ident)
    link['source'] = str(nodeIndentMapper[project.get('_id').get('source')])
    link['target'] = str(nodeIndentMapper[project.get('_id').get('destination')])
    if count:
        link['size'] = project['count']

    if showedName != None:
        link['label'] = showedName
    else:
        link['label'] = project['count']

    return link

def makeVISLink(project, ident, nodeIndentMapper, directed, showedName, color, context, count):
    link = {}
    link['id'] = ident
    link['from'] = nodeIndentMapper[project.get('_id').get('source')]
    link['to'] = nodeIndentMapper[project.get('_id').get('destination')]

    if count:
        link['value'] = project['count']

    if showedName != None:
        link['label'] = showedName
    else:
        link['label'] = project['count']

    if directed:
        link['arrows'] = 'to'

    if color != None:
        link['color'] = color  

    if context != None:
        link['edge_context'] = context  

    return link

def makeAlchemyLink(project, ident, nodeIndentMapper, directed, showedName, color, context, count):
    link = {}
    link['source'] = nodeIndentMapper[project.get('_id').get('source')]
    link['target'] = nodeIndentMapper[project.get('_id').get('destination')]

    if showedName != None:
        link['caption'] = showedName
    else :
        link['caption'] = project['count']
    return link

def makeForcedLink(project, ident, nodeIndentMapper, directed, showedName, color, context, count):
    link = {}
    link['source'] = project.get('_id').get('source')
    link['target'] = project.get('_id').get('destination')

    if count:
        link['count'] = project['count']

    return link

