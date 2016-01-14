queue()
	.defer(d3.json, "/transport/IPPortsConnection")
	.defer(d3.json, "/transport/sourcePortDistribution")
	.await(makeGraphs);

function makeGraphs(error, node, distribution)
{
	
	//calculate window size, in order to setup ths graphs sizes
	var width = window.innerWidth;
	var height = window.innerHeight;

	var width2 = splitSize10(width, 2);
	var height2 = splitSize10(height, 2);

	queue()
		.defer(makeSunburstChart, error, distribution, "#distribution-chart", width2, height2)	
		.defer(makeIPVISGraph, error, node, "graph-chart", width2, height2);
	
};


