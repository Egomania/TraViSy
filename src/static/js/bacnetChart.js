queue()
	.defer(d3.json, "/bacnet/APDU")
	.defer(d3.json, "/bacnet/Prio")
	.defer(d3.json, "/bacnet/pduFlags")
	.defer(d3.json, "/bacnet/Controller/1000")
	.await(makeGraphs);

function makeGraphs(error, type, bar, bar2, controller) {

	//calculate window size, in order to setup ths graphs sizes
	var width = window.innerWidth;
	var height = window.innerHeight;

	var width3 = splitSize10(width, 3);
	var height2 = splitSize10(height, 2);
	var width1 = splitSize10(width, 1);	

	queue()
		.defer(makeSunburstChart, error, type, "#sunburst-chart", width3, height2)
		.defer(makeBarChart, error, bar, "#bar-chart", width3, height2)
		.defer(makeBarChart, error, bar2, "#bar2-chart", width3, height2)
		.defer(makeTimelineBin, error, controller, "#timelineBin-chart", width1, height2)
};

function ReBinning()
{

	var binningValue = parseInt(document.getElementById("binningValue").value); 
	queue()
		.defer(d3.json, "/bacnet/Controller/"+binningValue)
		.await(showBinningTimeline);
}

function showBinningTimeline(error, controller)
{ 
	makeTimelineBin( error, controller, "#timelineBin-chart");
}
