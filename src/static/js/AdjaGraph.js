function makeMatrixGraph(error, json, stringName, widthSet, heightSet) {

	if (error)
		throw error;

	var width = widthSet;
	var height = heightSet;

	var div = d3.select(stringName)
			.append("div")
			.style("opacity", 0);

	var adjacencyMatrix = d3.layout.adjacencyMatrix()
  				.size([width,height])
  				.nodes(json.nodes)
  				.links(json.links)
  				.directed(true)
  				.nodeID(function (d) {return d.name});

  	var matrixData = adjacencyMatrix();

  	var someColors = d3.scale.category20c();

	var svg = d3.select(stringName)
		.append("svg")
		.attr("width", width)
		.attr("height", height);
		
	svg.append("g")	
  		.attr("transform", "translate(50,50)")
  		.attr("id", "adjacencyG")
		.selectAll("rect")
		.data(matrixData)
		.enter()
		.append("rect")
		.attr("width", function (d) {return d.width})
		.attr("height", function (d) {return d.height})
		.attr("x", function (d) {return d.x})
		.attr("y", function (d) {return d.y})
		.style("stroke", "black")
		.style("stroke-width", "1px")
		.style("stroke-opacity", .1)
		.style("fill", function (d) {return someColors(d.source.group)})
		.style("fill-opacity", function (d) {return d.weight * .8});

	  d3.select("#adjacencyG")
	  	.call(adjacencyMatrix.xAxis);

	  d3.select("#adjacencyG")
	  	.call(adjacencyMatrix.yAxis);

};
