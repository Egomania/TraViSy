queue()
	.defer(d3.json, "/backend/paket")
	.await(makeGraphs);

function makeGraphs(error, pkt) {

	var width = window.innerWidth;
	var height = window.innerHeight;
	var height2 = splitSize10(height, 2);
	var width2 = splitSize10(width, 2);

	queue()
	.defer(makeBarChart, error, pkt, "#bar-chart", width2, height2)
};

