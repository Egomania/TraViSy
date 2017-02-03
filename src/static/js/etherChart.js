queue()
	.defer(d3.json, "/netmon/ethernet/ForcedGraph")
	.defer(d3.json, "/netmon/ethernet/Ethertype")
	.defer(d3.json, "/netmon/ethernet/Timeline/0/100")
	.defer(d3.json, "/netmon/ethernet/MacSrc")
	.await(makeGraphs);

var start = 0
var end = 100
var diff = 100

//function, that is called initialy in order to setup all graphs
function makeGraphs(error, forced, ether, time, mac)
{
	
	//calculate window size, in order to setup ths graphs sizes
	var width = window.innerWidth;
	var height = window.innerHeight;

	var width3 = splitSize10(width, 3);
	var height2 = splitSize10(height, 2);
	var width1 = splitSize10(width, 1);
	var height3 = splitSize10(height, 3);

	queue()
		.defer(makeForcedGraph, error, forced, "#forced-chart", width3, height2, ["both","sending","receiving"])
		.defer(makeBarChart, error, ether, "#bar-chart", width3, height2)
		.defer(makeChord, error, forced, "#chord-chart", width3, height2)
		.defer(makeTimeline, error, time, mac,"#time-chart", width1, height3);
	
};

function NextData()
{
	start = start + diff;
	end = end + diff;
	
	queue()
	.defer(d3.json, "/netmon/ethernet/Timeline/"+start+"/"+end)
	.defer(d3.json, "/netmon/ethernet/MacSrc")
	.await(showTimeline);
}


function PrevData()
{
	start = start - diff;
	end = end - diff;
	
	queue()
	.defer(d3.json, "/netmon/ethernet/Timeline/"+start+"/"+end)
	.defer(d3.json, "/netmon/ethernet/MacSrc")
	.await(showTimeline);
}

function ShowData()
{
	
	var startNew = parseInt(document.getElementById("startNew").value);
	var endNew = parseInt(document.getElementById("endNew").value);
	
	console.log(startNew);
	console.log(endNew);
	
	start = startNew;
	end = endNew;
	
	diff = end - start;
	
	queue()
	.defer(d3.json, "/netmon/ethernet/Timeline/"+startNew+"/"+endNew)
	.defer(d3.json, "/netmon/ethernet/MacSrc")
	.await(showTimeline);
}

function showTimeline(error, time, mac)
{
	makeTimeline(error, time, mac,"#time-chart");
}
