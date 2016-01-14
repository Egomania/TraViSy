queue()
	.defer(d3.json, "/ip/NodeVIS")
	.defer(d3.json, "/ip/NodeAlchemy")
	.defer(d3.json, "/ip/NodeForcedGraph")
	.await(makeGraphs);

function makeGraphs(error, VISnode, AlchemyNode, ForcedNode)
{

	//calculate window size, in order to setup ths graphs sizes
	var width = window.innerWidth;
	var height = window.innerHeight;

	var width2 = splitSize10(width, 2);
	var height2 = splitSize10(height, 2)

	queue()
		.defer(makeForcedGraph2, error, ForcedNode, "#plain-chart", width2, height2)
		.defer(makeIPVISGraph, error, VISnode, "visGraph-chart", width2, height2)
		.defer(makeSigmaGraph, error, "/ip/NodeSigma", "sigma-chart", width2, height2)
		.defer(makeAlchGraph, error, AlchemyNode, width2, height2);
	
	
};


