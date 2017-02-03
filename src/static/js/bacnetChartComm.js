queue()
	.defer(d3.json, "/netmon/bacnet/Matrix")
	.await(makeGraphs);

function makeGraphs(error, whois ) {
	queue()
		.defer(makeMatrixGraph, error, whois, "#matrixGraph-chart")
};

