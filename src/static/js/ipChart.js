queue()
	.defer(d3.json, "/ip/Node")
	.defer(d3.json, "/ip/Matrix")
	.defer(d3.json, "/ip/timeline/0/100")
	.defer(d3.json, "/ip/timeline/1/100")
	.defer(d3.json, "/ip/ttl")
	.defer(d3.json, "/ip/flags")
	.await(makeGraphs);

function makeGraphs(error, node, matrix, receiving, sending, ttl, flags)
{

	//calculate window size, in order to setup ths graphs sizes
	var width = window.innerWidth;
	var height = window.innerHeight;

	var chartNotesHeight = document.getElementsByClassName("heightRow")[0].clientHeight;
	var chartTitleHeight = document.getElementsByClassName("chart-title")[0].clientHeight;

	var width3 = splitSize10(width, 3);
	var height2 = splitSize10(height, 2)
	var height1 = splitSize10(height, 1)

	var p = document.getElementsByClassName("chart-wrapper")[0];
	var style = p.currentStyle || window.getComputedStyle(p);
	var padding = parseInt(style.marginBottom);

	console.log(padding);

	var heightsub = height - chartNotesHeight - chartTitleHeight - padding;
	var height2sub = splitSize10(heightsub, 2)

	queue()
		.defer(makeForcedGraph, error, node, "#graph-chart", width3, height1, ["both","sending","receiving"])
		.defer(makeMatrixGraph, error, matrix, "#adja-chart", width3, height2)
		.defer(makeTimelineBin, error, sending, "#senderTimeline-chart", 2*width3, height2sub)
		.defer(makeTimelineBin, error, receiving, "#recTimeline-chart", 2*width3, height2sub)
		.defer(makeBarChart, error, ttl, "#ttl-chart", width3, height2)
		.defer(makeBarChart, error, flags, "#flag-chart", width3, height2);
};

function ReBinningSend()
{

	var binningValue = parseInt(document.getElementById("binningValue").value); 
	queue()
		.defer(d3.json, "/ip/timeline/1/"+binningValue)
		.await(showBinningTimelineSend);
}

function showBinningTimelineSend(error, controller)
{ 
	makeTimelineBin( error, controller, "#senderTimeline-chart");
}

function ReBinningRec()
{

	var binningValue = parseInt(document.getElementById("binningValue").value); 
	queue()
		.defer(d3.json, "/ip/timeline/0/"+binningValue)
		.await(showBinningTimelineRec);
}

function showBinningTimelineRec(error, controller)
{ 
	makeTimelineBin( error, controller, "#recTimeline-chart");
}

