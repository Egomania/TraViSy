queue()
	.defer(d3.json, "/bacnet/Matrix")
	.await(makeGraphs);

function makeGraphs(error, whois ) {
	queue()
		.defer(makeMatrixGraph, error, whois, "#matrixGraph-chart")
};

