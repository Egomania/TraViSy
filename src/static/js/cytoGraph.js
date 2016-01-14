function IsNumeric(n) {
  return !isNaN(parseFloat(n)) && isFinite(n);
}


function valueCheck(valueToCheck, defaultValue, lowerBound, upperBound){
	if (valueToCheck.value == null || valueToCheck.value == "")
		{valueToCheck = defaultValue;}
	else
		{
		if (!IsNumeric(valueToCheck.value))
			{valueToCheck = defaultValue;}
					
		else
			{
			if (valueToCheck.value < lowerBound || valueToCheck.value > upperBound)
				{valueToCheck = defaultValue;}
			else
				{valueToCheck = valueToCheck.value;}
			}
		}

	return valueToCheck
}

function makeCytoGraph(error, json)
{
	if (error)
		throw error;

	cy = cytoscape({
		container: document.getElementById('cy'),

	  	style: cytoscape.stylesheet()
		.selector('node')
		  .css({
		    'background-color': 'data(faveColor)',
		    'width': 'mapData(baz, 0, 10, 10, 40)',
		    'height': 'mapData(baz, 0, 10, 10, 40)',
		    'content': 'data(name)'
		  })
		.selector('edge')
		  .css({
		    'line-color': 'data(faveColor)',
		    'target-arrow-color': 'data(faveColor)',
		    'width': 2,
		    'target-arrow-shape': 'triangle',
		    'opacity': 0.8
		  })
		.selector(':selected')
		  .css({
		    'background-color': 'black',
		    'line-color': 'black',
		    'target-arrow-color': 'black',
		    'source-arrow-color': 'black',
		    'opacity': 1
		  })
		.selector('.CUTselected')
		  .css({
		    'background-color': 'black',
		    'line-color': 'black',
		    'target-arrow-color': 'black',
		    'source-arrow-color': 'black',
		    'opacity': 1
		  })
		.selector('.notUsed')
		  .css({
		    'background-color': 'gray',
		    'line-color': 'gray',
		    'target-arrow-color': 'gray',
		    'source-arrow-color': 'gray',
		    'opacity': 1
		  })
		.selector('.rootOfCol')
		  .css({
		    'background-color': 'red',
		    'line-color': 'red',
		    'target-arrow-color': 'red',
		    'source-arrow-color': 'red',
		    'opacity': 1
		  })
		.selector('.inCollection')
		  .css({
		    'background-color': 'green',
		    'line-color': 'green',
		    'target-arrow-color': 'green',
		    'source-arrow-color': 'green',
		    'opacity': 1
		  })
		.selector('.faded')
		  .css({
		    'opacity': 0.25,
		    'text-opacity': 0
		  }),
	  
	  elements: json,
	  
	  layout: {
		name: 'random',
		padding: 10
	  },
	  
	  ready: function(){
		// ready 1
		console.log("ready");
	  }
	});

	var infoString = "";
	infoString = infoString +  "Number of Nodes: " + cy.nodes().size() + "</br>" ;
	infoString = infoString +  "Number of Edges: " + cy.edges().size() + "</br>";
	infoString = infoString +  "Collection Nodes Total Degree: " + cy.nodes().totalDegree(true) + "</br>";
	infoString = infoString +  "Collection Nodes Min Degree: " + cy.nodes().minDegree(true) + "</br>";
	infoString = infoString +  "Collection Nodes Max Degree :" + cy.nodes().maxDegree(true) + "</br>";
	infoString = infoString +  "Collection Nodes Max Indegree :" + cy.nodes().maxIndegree(true) + "</br>";
	infoString = infoString +  "Collection Nodes Max Outdegree :" + cy.nodes().maxOutdegree(true) + "</br>";
	infoString = infoString +  "Collection Nodes Min Indegree :" + cy.nodes().minIndegree(true) + "</br>";
	infoString = infoString +  "Collection Nodes Min Outdegree :" + cy.nodes().minOutdegree(true) + "</br>";

	document.getElementById("collectionInfoBox").innerHTML = infoString ;


		$('#algo-name').on('click', function(){
				var selectedNode = cy.$(':selected').json();
				var nodeId = selectedNode.data.id;
				var nodeName = selectedNode.data.name;
				var elem = cy.getElementById(nodeId);

				var infoString = "";
				infoString = infoString +  "Node Total Degree: " + elem.degree(true) + "</br>";
				infoString = infoString +  "Node In Degree: " + elem.indegree(true) + "</br>";
				infoString = infoString +  "Node Out Degree: " + elem.outdegree(true) + "</br>";
				infoString = infoString +  "Degree Centrality: " + cy.$().dc({ root: elem }).degree + "</br>" ;
				infoString = infoString +  "Indegree Centrality: " + cy.$().dc({ root: elem, directed: true }).indegree + "</br>";
				infoString = infoString +  "Outdegree Centrality: " + cy.$().dc({ root: elem, directed: true }).outdegree + "</br>";
				infoString = infoString +  "Normalized Degree Centrality: " + cy.$().dcn().degree(elem) + "</br>" ;
				infoString = infoString +  "Normalized Indegree Centrality: " + cy.$().dcn({ directed: true }).indegree(elem) + "</br>";
				infoString = infoString +  "Normalized Outdegree Centrality: " + cy.$().dcn({ directed: true }).outdegree(elem) + "</br>";
				infoString = infoString +  "Closeness Centrality: " + cy.$().cc({ root: elem }) + "</br>" ;
				infoString = infoString +  "Normalized Closeness Centrality: " + cy.$().ccn().closeness(elem) + "</br>" ;
				infoString = infoString +  "Between Centrality: " + cy.$().bc().betweenness(elem) + "</br>" ;

				document.getElementById("nodeInfoBox").innerHTML = infoString ;
	  	});

		$('#algo-remove').on('click', function(){
				cy.elements().removeClass("notUsed");
				cy.elements().removeClass("inCollection");
				cy.elements().removeClass("rootOfCol");
				cy.elements().removeClass("CUTselected");
				cy.elements().unselect();
				
	  	});

		$('#algo-searchbfs').on('click', function(){
				var fromNode = document.getElementById('fromNode');
				var toNode = document.getElementById('toNode');
				var fromValue = fromNode.options[fromNode.selectedIndex].value;
				var toValue = toNode.options[toNode.selectedIndex].value;
				var sourceNode = cy.getElementById(fromValue);
				var targetNode = cy.getElementById(toValue);
				var bfs = cy.elements().bfs(sourceNode, function(i, depth){
				  // example of finding desired node
				  if( this.data('id') == toValue ){
				    return true;
				  }

				}, false);

				var path = bfs.path; // path to found node
				var found = bfs.found; // found node
				// select the path
				if (found.length != 0)
				{
					path.select();
				}

				
	  	});

		$('#algo-searchdfs').on('click', function(){
				var fromNode = document.getElementById('fromNode');
				var toNode = document.getElementById('toNode');
				var fromValue = fromNode.options[fromNode.selectedIndex].value;
				var toValue = toNode.options[toNode.selectedIndex].value;
				var sourceNode = cy.getElementById(fromValue);
				var targetNode = cy.getElementById(toValue);
				var dfs = cy.elements().dfs(sourceNode, function(i, depth){
				  // example of finding desired node
				  if( this.data('id') == toValue ){
				    return true;
				  }

				}, false);

				var path = dfs.path; // path to found node
				var found = dfs.found; // found node
				// select the path
				if (found.length != 0)
				{
					path.select();
				}

				
	  	});

		$('#algo-dikstra').on('click', function(){
				var startNode = document.getElementById('startNode');
				var startValue = startNode.options[startNode.selectedIndex].value;
				var rootNode = cy.getElementById(startValue);

				var endNode = document.getElementById('endNode');
				var endValue = endNode.options[endNode.selectedIndex].value;

				var dijkstra = cy.elements().dijkstra(rootNode);

				var otherNodes;

				if (endValue == "any")
					{otherNodes = cy.nodes().filter('[initClass = "IP"]');}
					
				else
					{
					otherNodes = cy.nodes().filter('[id = "' + endValue + '"]');
					document.getElementById("nodeDistanceBox").innerHTML = "<em>Distance: " + dijkstra.distanceTo(cy.getElementById(endValue)) + "</em>";
					}
					
				
				otherNodes.forEach(function (node) { if (dijkstra.distanceTo(node) != Infinity) {var path = dijkstra.pathTo(node); path.select();}} )

	  	});

		$('#algo-astar').on('click', function(){
				var startNode = document.getElementById('startNode');
				var startValue = startNode.options[startNode.selectedIndex].value;
				var rootNode = cy.getElementById(startValue);

				var endNode = document.getElementById('endNode');
				var endValue = endNode.options[endNode.selectedIndex].value;
				var goalNode = cy.getElementById(endValue);

				var astar = cy.elements().aStar({ root: rootNode, goal: goalNode });

				document.getElementById("nodeDistanceBox").innerHTML = "<em>Distance: " + astar.distance + "</em>";

				if (astar.found)
					{astar.path.select();}

	  	});

		$('#algo-floyd').on('click', function(){
				var startNode = document.getElementById('startNode');
				var startValue = startNode.options[startNode.selectedIndex].value;
				var rootNode = cy.getElementById(startValue);

				var endNode = document.getElementById('endNode');
				var endValue = endNode.options[endNode.selectedIndex].value;
				var goalNode = cy.getElementById(endValue);

				var floyd = cy.elements().floydWarshall();

				document.getElementById("nodeDistanceBox").innerHTML = "<em>Distance: " + floyd.distance(rootNode, goalNode) + "</em>";

				if (floyd.distance(rootNode, goalNode) != Infinity && floyd.distance(rootNode, goalNode) != undefined)
					{floyd.path(rootNode, goalNode).select();}

	  	});

		$('#algo-bellman').on('click', function(){
				var startNode = document.getElementById('startNode');
				var startValue = startNode.options[startNode.selectedIndex].value;
				var rootNode = cy.getElementById(startValue);

				var endNode = document.getElementById('endNode');
				var endValue = endNode.options[endNode.selectedIndex].value;

				var bellman = cy.elements().bellmanFord({ root: rootNode });

				var otherNodes;

				if (endValue == "any")
					{otherNodes = cy.nodes().filter('[initClass = "IP"]');}
					
				else
					{
					otherNodes = cy.nodes().filter('[id = "' + endValue + '"]');
					document.getElementById("nodeDistanceBox").innerHTML = "<em>Distance: " + bellman.distanceTo(cy.getElementById(endValue)) + "</em>";
					}
					
				
				otherNodes.forEach(function (node) { if (bellman.distanceTo(node) != Infinity) {var path = bellman.pathTo(node); path.select();}} )

	  	});

		$('#algo-kruskal').on('click', function(){
				cy.elements().kruskal().select();

	  	});		

		$('#algo-karger').on('click', function(){
				var ks = cy.elements().kargerStein();
				cy.elements().addClass('notUsed');
				console.log(ks.cut);
				ks.cut.forEach(function (n) {n.removeClass("notUsed"); n.addClass("CUTselected");})
				ks.partition1.forEach(function (n) {n.addClass("inCollection");})
				ks.partition2.forEach(function (n) {n.addClass("rootOfCol");})
				
	  	});

		$('#algo-pageRank').on('click', function(){
				var iterations = valueCheck(document.getElementById('iterations'), 15, 1, 100);
				var precision = valueCheck(document.getElementById('precision'), 3.5, 1, 10);
				var numberOfNodes = valueCheck(document.getElementById('NumberOfNodes'), 10, 1, 100);
				var dampingFactor = valueCheck(document.getElementById('dampingFactor'), 5, 1, 10);
			
				var checkedIP = false;
					if (document.querySelector('.ipCheckbox:checked') != null) { checkedIP = true; }

				var checkedPort = false;
					if (document.querySelector('.portCheckbox:checked') != null) { checkedPort = true; }

				var filterString = "";

				if (checkedPort && !checkedIP)
					{ filterString = '[initClass = "Port"]'; }

				if (checkedIP && !checkedPort)
					{ filterString = '[initClass = "IP"]'; }


				var pr = cy.elements().pageRank({dampingFactor: dampingFactor, precision: precision, iterations: iterations});

				var rankArray = [];
				var arrayEntry = [];

				cy.nodes().filter(filterString).forEach
					(
					function (node) {arrayEntry= [node._private.data.id, pr.rank(node)]; rankArray.push(arrayEntry);}
					);

				rankArray.sort(function(a,b){
    				return b[1] - a[1];
				});

				rankString = "";

				for (i = 0; i < rankArray.length; i++) {
    				rankElem = rankArray[i][0] + " : " + rankArray[i][1] + "</br>";
					rankString = rankString + rankElem;
					if (i == numberOfNodes - 1) { break; }
				}

				document.getElementById("pageRankBox").innerHTML = "<em>" + rankString + "</em>";

	  	});		

		$('#algo-neighbourSelect').on('click', function(){
				cy.elements().addClass('notUsed');
				var selectedNode = cy.$(':selected').json();
				var nodeId = selectedNode.data.id;
				var nodeName = selectedNode.data.name;
				var elem = cy.getElementById(nodeId);
				elem.addClass("rootOfCol");
				elem.removeClass("notUsed");
				elem.connectedEdges().each( 
					function(i, ele) { ele.select().addClass("inCollection").removeClass("notUsed"); ele.connectedNodes().each(
						function(i, ele) {	if (!(ele.hasClass("rootOfCol")))
											{ 
											ele.select().addClass("inCollection").removeClass("notUsed");
											} 
										ele.connectedEdges().each( 
							function (i, ele) { ele.select().addClass("inCollection").removeClass("notUsed"); ele.connectedNodes().each(
								function (i, ele) {	if (!(ele.hasClass("rootOfCol")))
													{ 
														ele.select().addClass("inCollection").removeClass("notUsed");
													}
													ele.connectedEdges().each( 
									function (i, ele) { ele.select().addClass("inCollection").removeClass("notUsed"); ele.connectedNodes().each(
										function (i, ele) {
											
											if (ele._private.data.initClass == 'IP')
													{ 
														ele.select().addClass("rootOfCol").removeClass("notUsed");
													}
											else
													{
														ele.select().addClass("inCollection").removeClass("notUsed");
													}
										}
									)} 
								)}
							)}
						)}
					)}
				);
				
	  	});


		//NULL LAYOUT
		$('#layout-null').on('click', function(){
				console.log('changed to null layout');
				var options = {
  					name: 'null',

					ready: function(){}, 
					stop: function(){} 
				};

				cy.layout( options );
	  	});

		//PRESET LAYOUT
		$('#layout-preset').on('click', function(){
				console.log('changed to preset layout');
				var options = {
				  name: 'preset',

				  positions: undefined, // map of (node id) => (position obj); or function(node){ return somPos; }
				  zoom: undefined, // the zoom level to set (prob want fit = false if set)
				  pan: undefined, // the pan level to set (prob want fit = false if set)
				  fit: true, // whether to fit to viewport
				  padding: 30, // padding on fit
				  animate: true, // whether to transition the node positions
				  animationDuration: 500, // duration of animation in ms if enabled
				  ready: undefined, // callback on layoutready
				  stop: undefined // callback on layoutstop
				};

				cy.layout( options );
	  	});

		//GRID LAYOUT
		$('#layout-grid').on('click', function(){
				console.log('changed to grid layout');
				var options = {
				  name: 'grid',

				  fit: true, // whether to fit the viewport to the graph
				  padding: 30, // padding used on fit
				  boundingBox: undefined, // constrain layout bounds; { x1, y1, x2, y2 } or { x1, y1, w, h }
				  avoidOverlap: true, // prevents node overlap, may overflow boundingBox if not enough space
				  rows: undefined, // force num of rows in the grid
				  columns: undefined, // force num of cols in the grid
				  position: function( node ){}, // returns { row, col } for element
				  sort: undefined, // a sorting function to order the nodes; e.g. function(a, b){ return a.data('weight') - b.data('weight') }
				  animate: true, // whether to transition the node positions
				  animationDuration: 500, // duration of animation in ms if enabled
				  ready: undefined, // callback on layoutready
				  stop: undefined // callback on layoutstop
				};

				cy.layout( options );
	  	});

		//DAGRE LAYOUT
		$('#layout-dagre').on('click', function(){
				console.log('changed to dagre layout');
				var options = {
				  name: 'dagre',

				  // dagre algo options, uses default value on undefined
				  nodeSep: undefined, // the separation between adjacent nodes in the same rank
				  edgeSep: undefined, // the separation between adjacent edges in the same rank
				  rankSep: undefined, // the separation between adjacent nodes in the same rank
				  rankDir: undefined, // 'TB' for top to bottom flow, 'LR' for left to right
				  minLen: function( edge ){ return 1; }, // number of ranks to keep between the source and target of the edge
				  edgeWeight: function( edge ){ return 1; }, // higher weight edges are generally made shorter and straighter than lower weight edges

				  // general layout options
				  fit: true, // whether to fit to viewport
				  padding: 30, // fit padding
				  animate: true, // whether to transition the node positions
				  animationDuration: 500, // duration of animation in ms if enabled
				  boundingBox: undefined, // constrain layout bounds; { x1, y1, x2, y2 } or { x1, y1, w, h }
				  ready: function(){}, // on layoutready
				  stop: function(){} // on layoutstop
				};

				cy.layout( options );
	  	});

		//CIRCLE LAYOUT
		$('#layout-circle').on('click', function(){
				console.log('changed to circle layout');
				var options = {
				  name: 'circle',

				  fit: true, // whether to fit the viewport to the graph
				  padding: 30, // the padding on fit
				  boundingBox: undefined, // constrain layout bounds; { x1, y1, x2, y2 } or { x1, y1, w, h }
				  avoidOverlap: true, // prevents node overlap, may overflow boundingBox and radius if not enough space
				  radius: undefined, // the radius of the circle
				  startAngle: 3/2 * Math.PI, // the position of the first node
				  counterclockwise: false, // whether the layout should go counterclockwise (true) or clockwise (false)
				  sort: undefined, // a sorting function to order the nodes; e.g. function(a, b){ return a.data('weight') - b.data('weight') }
				  animate: true, // whether to transition the node positions
				  animationDuration: 500, // duration of animation in ms if enabled
				  ready: undefined, // callback on layoutready
				  stop: undefined // callback on layoutstop
				};

				cy.layout( options );
	  	});

		//RANDOM LAYOUT
		$('#layout-random').on('click', function(){
				console.log('changed to random layout');
				var options = {
				  name: 'random',

				  fit: true,
				  padding: 30, 
				  boundingBox: undefined, // constrain layout bounds; { x1, y1, x2, y2 } or { x1, y1, w, h }
				  animate: true, 
				  animationDuration: 500, // duration of animation in ms if enabled
				  ready: undefined, // callback on layoutready
				  stop: undefined // callback on layoutstop
				};

				cy.layout( options );
	  	});

		//BREADTHFIRST LAYOUT
		$('#layout-breadthfirst').on('click', function(){
				console.log('changed to breadthfirst layout');
				var options = {
				  name: 'breadthfirst',

				  fit: true, // whether to fit the viewport to the graph
				  directed: true, // whether the tree is directed downwards (or edges can point in any direction if false)
				  padding: 30, // padding on fit
				  circle: true, // put depths in concentric circles if true, put depths top down if false
				  spacingFactor: 2.75, // positive spacing factor, larger => more space between nodes (N.B. n/a if causes overlap)
				  boundingBox: undefined, // constrain layout bounds; { x1, y1, x2, y2 } or { x1, y1, w, h }
				  avoidOverlap: true, // prevents node overlap, may overflow boundingBox if not enough space
				  roots: undefined, // the roots of the trees
				  maximalAdjustments: 0, // how many times to try to position the nodes in a maximal way (i.e. no backtracking)
				  animate: true, // whether to transition the node positions
				  animationDuration: 500, // duration of animation in ms if enabled
				  ready: undefined, // callback on layoutready
				  stop: undefined // callback on layoutstop
				};

				cy.layout( options );
	  	});

		//CONCENTRIC LAYOUT
		$('#layout-concentric').on('click', function(){
				console.log('changed to concentric layout');
				var options = {
				  name: 'concentric',

				  fit: true, // whether to fit the viewport to the graph
				  padding: 30, // the padding on fit
				  startAngle: 3/2 * Math.PI, // the position of the first node
				  counterclockwise: true, // whether the layout should go counterclockwise/anticlockwise (true) or clockwise (false)
				  minNodeSpacing: 30, // min spacing between outside of nodes (used for radius adjustment)
				  boundingBox: undefined, // constrain layout bounds; { x1, y1, x2, y2 } or { x1, y1, w, h }
				  avoidOverlap: true, // prevents node overlap, may overflow boundingBox if not enough space
				  height: undefined, // height of layout area (overrides container height)
				  width: undefined, // width of layout area (overrides container width)
				  concentric: function(node){ // returns numeric value for each node, placing higher nodes in levels towards the centre
					return node.degree();
				  },
				  levelWidth: function(nodes){ // the variation of concentric values in each level
					return nodes.maxDegree() / 4;
				  },
				  animate: true, // whether to transition the node positions
				  animationDuration: 500, // duration of animation in ms if enabled
				  ready: undefined, // callback on layoutready
				  stop: undefined // callback on layoutstop
				};

				cy.layout( options );
	  	});

		//COSE LAYOUT
		$('#layout-cose').on('click', function(){
				console.log('changed to cose layout');
				var options = {
				  name: 'cose',
				  ready               : function() {},// Called on `layoutready`
				  stop                : function() {},// Called on `layoutstop`
				  animate             : true,// Whether to animate while running the layout 
				  refresh             : 4,// Number of iterations between consecutive screen positions update (0 -> only updated on the end) 
				  fit                 : true, // Whether to fit the network view after when done
				  padding             : 30, // Padding on fit
				  boundingBox         : undefined, // Constrain layout bounds; { x1, y1, x2, y2 } or { x1, y1, w, h }
				  randomize           : true, // Whether to randomize node positions on the beginning
				  debug               : false, // Whether to use the JS console to print debug messages
				  nodeRepulsion       : 400000, // Node repulsion (non overlapping) multiplier
				  nodeOverlap         : 10, // Node repulsion (overlapping) multiplier
				  idealEdgeLength     : 10, // Ideal edge (non nested) length
				  edgeElasticity      : 100, // Divisor to compute edge forces
				  nestingFactor       : 5, // Nesting factor (multiplier) to compute ideal edge length for nested edges
				  gravity             : 250, // Gravity force (constant)
				  numIter             : 100, // Maximum number of iterations to perform
				  initialTemp         : 200, // Initial temperature (maximum node displacement)
				  coolingFactor       : 0.95, // Cooling factor (how the temperature is reduced between consecutive iterations
				  minTemp             : 1.0 // Lower temperature threshold (below this point the layout will end)
				};

				cy.layout( options );
	  	});

		//COLA LAYOUT
		$('#layout-cola').on('click', function(){
				console.log('changed to cola layout');
				var options = {
				  name: 'cola',

				  animate: true, // whether to show the layout as it's running
				  refresh: 10, // number of ticks per frame; higher is faster but more jerky
				  maxSimulationTime: 4000, // max length in ms to run the layout
				  ungrabifyWhileSimulating: false, // so you can't drag nodes during layout
				  fit: true, // on every layout reposition of nodes, fit the viewport
				  padding: 30, // padding around the simulation
				  boundingBox: undefined, // constrain layout bounds; { x1, y1, x2, y2 } or { x1, y1, w, h }

				  // layout event callbacks
				  ready: function(){}, // on layoutready
				  stop: function(){}, // on layoutstop

				  // positioning options
				  randomize: true, // use random node positions at beginning of layout
				  avoidOverlap: true, // if true, prevents overlap of node bounding boxes
				  handleDisconnected: true, // if true, avoids disconnected components from overlapping
				  nodeSpacing: function( node ){ return 30; }, // extra spacing around nodes
				  flow: undefined, // use DAG/tree flow layout if specified, e.g. { axis: 'y', minSeparation: 30 }
				  alignment: undefined, // relative alignment constraints on nodes, e.g. function( node ){ return { x: 0, y: 1 } }

				  // different methods of specifying edge length
				  // each can be a constant numerical value or a function like `function( edge ){ return 2; }`
				  edgeLength: undefined, // sets edge length directly in simulation
				  edgeSymDiffLength: undefined, // symmetric diff edge length in simulation
				  edgeJaccardLength: undefined, // jaccard edge length in simulation

				  // iterations of cola algorithm; uses default values on undefined
				  unconstrIter: undefined, // unconstrained initial layout iterations
				  userConstIter: undefined, // initial layout iterations with user-specified constraints
				  allConstIter: undefined, // initial layout iterations with all constraints including non-overlap

				  // infinite layout options
				  infinite: false // overrides all other options for a forces-all-the-time mode
				};

				cy.layout( options );
	  	});

		//SPREAD LAYOUT
		$('#layout-spread').on('click', function(){
				console.log('changed to spread layout');
				var options = {
				  name: 'spread',

				  animate: true, // whether to show the layout as it's running
				  ready: undefined, // Callback on layoutready
				  stop: undefined, // Callback on layoutstop
				  fit: true, // Reset viewport to fit default simulationBounds
				  minDist: 20, // Minimum distance between nodes
				  padding: 20, // Padding
				  expandingFactor: -1.0, // If the network does not satisfy the minDist
				  // criterium then it expands the network of this amount
				  // If it is set to -1.0 the amount of expansion is automatically
				  // calculated based on the minDist, the aspect ratio and the
				  // number of nodes
				  maxFruchtermanReingoldIterations: 50, // Maximum number of initial force-directed iterations
				  maxExpandIterations: 4, // Maximum number of expanding iterations
				  boundingBox: undefined // Constrain layout bounds; { x1, y1, x2, y2 } or { x1, y1, w, h }
				};

				cy.layout( options );
	  	});

		//ARBOR LAYOUT
		$('#layout-arbor').on('click', function(){
				console.log('changed to arbor layout');
				var options = {
				  name: 'arbor',

				  animate: true, // whether to show the layout as it's running
				  maxSimulationTime: 4000, // max length in ms to run the layout
				  fit: true, // on every layout reposition of nodes, fit the viewport
				  padding: 30, // padding around the simulation
				  boundingBox: undefined, // constrain layout bounds; { x1, y1, x2, y2 } or { x1, y1, w, h }
				  ungrabifyWhileSimulating: false, // so you can't drag nodes during layout

				  // callbacks on layout events
				  ready: undefined, // callback on layoutready
				  stop: undefined, // callback on layoutstop

				  // forces used by arbor (use arbor default on undefined)
				  repulsion: undefined,
				  stiffness: undefined,
				  friction: undefined,
				  gravity: true,
				  fps: undefined,
				  precision: undefined,

				  // static numbers or functions that dynamically return what these
				  // values should be for each element
				  // e.g. nodeMass: function(n){ return n.data('weight') }
				  nodeMass: undefined,
				  edgeLength: undefined,

				  stepSize: 0.1, // smoothing of arbor bounding box

				  // function that returns true if the system is stable to indicate
				  // that the layout can be stopped
				  stableEnergy: function( energy ){
					var e = energy;
					return (e.max <= 0.5) || (e.mean <= 0.3);
				  },

				  // infinite layout options
				  infinite: false // overrides all other options for a forces-all-the-time mode
				};

				cy.layout( options );
	  	});

		//SPRINGY LAYOUT
		$('#layout-springy').on('click', function(){
				console.log('changed to springy layout');
				var options = {
				  name: 'springy',

				  animate: true, // whether to show the layout as it's running
				  maxSimulationTime: 4000, // max length in ms to run the layout
				  ungrabifyWhileSimulating: false, // so you can't drag nodes during layout
				  fit: true, // whether to fit the viewport to the graph
				  padding: 30, // padding on fit
				  boundingBox: undefined, // constrain layout bounds; { x1, y1, x2, y2 } or { x1, y1, w, h }
				  random: false, // whether to use random initial positions
				  infinite: false, // overrides all other options for a forces-all-the-time mode
				  ready: undefined, // callback on layoutready
				  stop: undefined, // callback on layoutstop

				  // springy forces
				  stiffness: 400,
				  repulsion: 400,
				  damping: 0.5
				};

				cy.layout( options );
	  	});

};

