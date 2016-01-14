function makeSunburstChart(error, json, stringName, widthSet, heightSet) {

	if (error)
		throw error;

	var width = widthSet - 50, height = heightSet - 150, radius = Math.min(width, height) / 2, color = d3.scale
			.category20c();

	var div = d3.select(stringName).append("div").attr("class", "tooltip")
			.style("opacity", 0);

	var svg = d3.select(stringName).append("svg").attr("width", width + 50).attr(
			"height", height + 150).append("g").attr("transform",
			"translate(" + width / 2 + "," + height * .52 + ")");

	var partition = d3.layout.partition().sort(null).size(
			[ 2 * Math.PI, radius * radius ]).value(function(d) {
		return 1;
	});

	var arc = d3.svg.arc().startAngle(function(d) {
		return d.x;
	}).endAngle(function(d) {
		return d.x + d.dx;
	}).innerRadius(function(d) {
		return Math.sqrt(d.y);
	}).outerRadius(function(d) {
		return Math.sqrt(d.y + d.dy);
	});

	var path = svg.datum(json).selectAll("path").data(partition.nodes).enter()
			.append("path")
			.attr("display", function(d) {
				return d.depth ? null : "none";
			}) // hide inner ring
			.attr("d", arc)
			.style("stroke", "#fff")
			.style("fill", function(d) {
				return color((d.children ? d : d.parent).name);
			})
			.style("fill-rule", "evenodd").each(stash)
			.on("mouseover", function(d) {
                        div.transition()
                        .duration(200)
                        .style("opacity", .9);
                        div.html("Description: " + d.name + "<br/>Id: " + d.id + "<br/>Size: " + d.sum + "<br/>Count: " + d.count)
                        .style("left", (d3.event.pageX) + "px")
                        .style("top", (d3.event.pageY - 28) + "px");
                        })
            .on("mouseout", function(d) {
                        div.transition()
                        .duration(500)
                        .style("opacity", 0);
                        });

	d3.selectAll("input").on(
			"change",
			function change() {
				if (this.value === "count") 
					{var value = function(d) {return d.count;}}

				if (this.value === "size") 
					{var value = function(d) {return d.sum;}}

				if (this.value === "norm") 
					{var value = function(d) {return 1;}}
				
				path.data(partition.value(value).nodes).transition().duration(
						1500).attrTween("d", arcTween);
			});

	// Stash the old values for transition.
	function stash(d) {
		d.x0 = d.x;
		d.dx0 = d.dx;
	}

	// Interpolate the arcs in data space.
	function arcTween(a) {
		var i = d3.interpolate({
			x : a.x0,
			dx : a.dx0
		}, a);
		return function(t) {
			var b = i(t);
			a.x0 = b.x;
			a.dx0 = b.dx;
			return arc(b);
		};
	}

	//d3.select(self.frameElement).style("height", height + "px");
};

function makeForcedGraph(error, json, stringName, widthSet, heightSet, legendArray)
{
	if (error) throw error;

	  var width = widthSet,
	    height = heightSet;

		var color = d3.scale.category20();
		
		var force = d3.layout.force()
		    .charge(-120)
		    .linkDistance(30)
		    .size([width, height]);
		
		var div = d3.select(stringName).append("div")
			.attr("class", "tooltip")
			.style("opacity", 0);
		
		var svg = d3.select(stringName).append("svg")
		   	.attr("width", width)
		    .attr("height", height);
	  
	  var edges = [];
	  json.links.forEach(function(e) {
	      var sourceNode = json.nodes.filter(function(n) {
	          return n.name === e.source;
	      })[0],
	          targetNode = json.nodes.filter(function(n) {
	              return n.name === e.target;
	          })[0];

	      edges.push({
	          source: sourceNode,
	          target: targetNode,
	          count: e.count
	      });
	  });

	  
	  force
	      .nodes(json.nodes)
	      .links(edges)
	      .start();
	
	  var link = svg.selectAll(".links")
	      .data(edges)
	    .enter().append("line")
	      .attr("class", "link")
	      .style("stroke-width", function(d) { return Math.sqrt(d.count)/100; });
	
	  var node = svg.selectAll(".nodes")
	      .data(json.nodes)
	    .enter().append("circle")
	      .attr("class", "node")
	      .attr("r", 5)
	      .style("fill", function(d) { return color(d.group); })
	      .call(force.drag);
	
	  node.append("title")
	      .text(function(d) { return d.name; });
	
	  force.on("tick", function() {
	    link.attr("x1", function(d) { return d.source.x; })
	        .attr("y1", function(d) { return d.source.y; })
	        .attr("x2", function(d) { return d.target.x; })
	        .attr("y2", function(d) { return d.target.y; });
	
	    node.attr("cx", function(d) { return d.x; })
	        .attr("cy", function(d) { return d.y; });
	  });

	sampleCategoricalData = legendArray;
  	sampleOrdinal = d3.scale.category20().domain(sampleCategoricalData);
	
  	verticalLegend = d3.svg.legend()
		.labelFormat("none")
		.cellPadding(5)
		.orientation("vertical")
		.units("Node Groups")
		.cellWidth(25)
		.cellHeight(18)
		.inputScale(sampleOrdinal)
		.cellStepping(10);
	
  	svg.append("g")
		.attr("transform", "translate(50,140)")
		.attr("class", "legend").call(verticalLegend);

};

function makeForcedGraph2(error, json, stringName, widthSet, heightSet)
{
	if (error) throw error;

	  var width = widthSet,
	    height = heightSet;

		var color = d3.scale.category20();
		
		var force = d3.layout.force()
		    .charge(-120)
		    .linkDistance(30)
		    .size([width, height]);
		
		var div = d3.select(stringName).append("div")
			.attr("class", "tooltip")
			.style("opacity", 0);
		
		var svg = d3.select(stringName).append("svg")
		   	.attr("width", width)
		    	.attr("height", height);
	  
	  var edges = [];
	  json.links.forEach(function(e) {
	      var sourceNode = json.nodes.filter(function(n) {
	          return n.id === e.source;
	      })[0],
	          targetNode = json.nodes.filter(function(n) {
	              return n.id === e.target;
	          })[0];

	      edges.push({
	          source: sourceNode,
	          target: targetNode,
	          count: e.count
	      });
	  });

	  
	  force
	      .nodes(json.nodes)
	      .links(edges)
	      .start();
	
	  var link = svg.selectAll(".links")
	      .data(edges)
	    .enter().append("line")
	      .attr("class", "link")
	      .style("stroke-width", function(d) { return Math.sqrt(d.count)/100; });
	
	  var node = svg.selectAll(".nodes")
	      .data(json.nodes)
	    .enter().append("circle")
	      .attr("class", "node")
	      .attr("r", 5)
	      .style("fill", function(d) { return color(d.group); })
	      .call(force.drag);
	
	  node.append("title")
	      .text(function(d) { return d.name; });
	
	  force.on("tick", function() {
	    link.attr("x1", function(d) { return d.source.x; })
	        .attr("y1", function(d) { return d.source.y; })
	        .attr("x2", function(d) { return d.target.x; })
	        .attr("y2", function(d) { return d.target.y; });
	
	    node.attr("cx", function(d) { return d.x; })
	        .attr("cy", function(d) { return d.y; });
	  });
};


function makeChord(error, json, stringName, widthSet, heightSet)
{

	var fill = d3.scale.category20c();
	
var width = widthSet,
height = heightSet,
outerRadius = Math.min(width, height) / 2 - 10,
innerRadius = outerRadius - 24;
 
var formatPercent = d3.format(".1%");
 
var arc = d3.svg.arc()
.innerRadius(innerRadius)
.outerRadius(outerRadius);
 
var layout = d3.layout.chord()
.padding(.04)
.sortSubgroups(d3.descending)
.sortChords(d3.ascending);
 
var path = d3.svg.chord()
.radius(innerRadius);
 
var div = d3.select(stringName).append("div")
.attr("class", "tooltip")
.style("opacity", 0);

var svg = d3.select(stringName).append("svg")
.attr("width", width)
.attr("height", height)
.append("g")
.attr("id", "circle")
.attr("transform", "translate(" + width / 2 + "," + height / 2 + ")");
 
svg.append("circle")
.attr("r", outerRadius);
 
var indexByName = d3.map(),
nameByIndex = d3.map(),
matrix = [],
n = 0;

// Compute a unique index for each package name.
json.nodes.forEach(function(d) {
if (!indexByName.has(d = d.name)) {
nameByIndex.set(n, d);
indexByName.set(d, n++);
}
});


// Construct a square matrix counting package imports.
json.links.forEach(function(d) {
var source = indexByName.get(d.source),
  row = matrix[source];
if (!row) {
row = matrix[source] = [];
for (var i = -1; ++i < n;) row[i] = 0;
}
row[indexByName.get(d.target)] = d.count;

});



//chord.matrix(matrix);
 
// Compute the chord layout.
layout.matrix(matrix);
 
// Add a group per neighborhood.
var group = svg.selectAll(".group")
.data(layout.groups)
.enter().append("g")
.attr("class", "group")
.on("mouseover", mouseover);
 
// Add the group arc.
var groupPath = group.append("path")
.attr("id", function(d, i) { return "group" + i; })
.style("fill", function(d, i) {  return fill(d.index); })
.attr("d", arc);

 
// Add a text label.
var groupText = group.append("text")
.attr("x", 6)
.attr("dy", 15);
 
groupText.append("textPath")
.attr("xlink:href", function(d, i) { return "#group" + i; })
.text(function(d, i) { return nameByIndex.get(d.index); });
 
// Remove the labels that don't fit. :(
groupText.filter(function(d, i) { return groupPath[0][i].getTotalLength() / 2 - 16 < this.getComputedTextLength(); })
.remove();
 
// Add the chords.
var chord = svg.selectAll(".chord")
.data(layout.chords)
.enter().append("path")
.attr("class", "chord")
.style("fill", function(d) { return fill(d.source.index); })
.attr("d", path);
 
// Add an elaborate mouseover title for each chord.
 	chord.append("title").text(function(d) {nameByIndex.get(d.index);});

 function mouseover(d, i) {
	 chord.classed("fadechord", function(p) {
		 return p.source.index != i
		 && p.target.index != i;
	 });
 }

};

function makeBarChart(error, json, divIdent, widthSet, heightSet)
{
	if (error) throw error;
	
	var margin = {top: 20, right: 20, bottom: 30, left: 80},
    width = widthSet - margin.left - margin.right,
    height = heightSet - margin.top - margin.bottom;
	
	
	var x = d3.scale.ordinal()
    .rangeRoundBands([0, width], .1);

	var y = d3.scale.linear()
	    .range([height, 0]);
	
	var xAxis = d3.svg.axis()
	    .scale(x)
	    .orient("bottom");
	
	var yAxis = d3.svg.axis()
	    .scale(y)
	    .orient("left");
	
	var tip = d3.tip()
	  .attr('class', 'd3-tip')
	  .offset([-10, 0])
	  .html(function(d) {
	    return "<strong>Amount:</strong> <span style='color:steelblue'>" + d.count + "</span>";
	  })
	
	var div = d3.select(divIdent).append("div")
	.attr("class", "tooltip")
	.style("opacity", 0);

	var svg = d3.select(divIdent).append("svg")
	.attr("width", width + margin.left + margin.right)
    .attr("height", height + margin.top + margin.bottom)
    .append("g")
    .attr("transform", "translate(" + margin.left + "," + margin.top + ")");
	
	svg.call(tip);
	
	x.domain(json.map(function(d) { return d.type; }));
	
	y.domain([0, d3.max(json, function(d) { return d.count; })]);
	
	svg.append("g")
    .attr("class", "x axis")
    .attr("transform", "translate(0," + height + ")")
    .call(xAxis);

	svg.append("g")
	    .attr("class", "y axis")
	    .call(yAxis)
	  .append("text")
	    .attr("transform", "rotate(-90)")
	    .attr("y", 3)
	    .attr("dy", ".71em")
	    .style("text-anchor", "end")
	    .text("Number");
	
	svg.selectAll(".bar")
	    .data(json)
	  .enter().append("rect")
	    .attr("class", "bar")
	    .attr("x", function(d) { return x(d.type); })
	    .attr("width", x.rangeBand()-10)
	    .attr("y", function(d) { return y(d.count); })
	    .attr("height", function(d) { return height - y(d.count); })
		.on('mouseover', tip.show)
		.on('mouseout', tip.hide);
};


