queue()
	.defer(d3.json, "/netmon/transport/IPPortsConnectionCyto")
	.await(makeGraphs);

function makeGraphs(error, node)
{
	makeCytoGraph(error, node);
	
};
