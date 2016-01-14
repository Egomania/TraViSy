queue()
	.defer(d3.json, "/transport/IPPortsConnectionCyto")
	.await(makeGraphs);

function makeGraphs(error, node)
{
	makeCytoGraph(error, node);
	
};
