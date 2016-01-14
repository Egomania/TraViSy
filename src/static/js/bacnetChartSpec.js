queue()
	.defer(d3.json, "/bacnet/WhoIs")
	.await(makeGraphs);

function makeGraphs(error, whois ) {

	//calculate window size, in order to setup ths graphs sizes
	var width = window.innerWidth;
	var height = window.innerHeight;

	var height1 = splitSize10(height, 1);
	var width1 = splitSize10(width, 1);

	queue()
		.defer(makeVisGraph, error, whois, "visGraph-chart", width1, height1)
};

