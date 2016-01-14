function makeSigmaGraph(error, json, stringName, setWidth, setHeight) {
	if (error)
		throw error;

	document.getElementById(stringName).setAttribute("style","width:" + setWidth + "px");
	document.getElementById(stringName).setAttribute("style","height:" + setHeight + "px");

	sigma.classes.graph.addMethod('neighbors', function(nodeId) {
	    	var k,
		neighbors = {},
		index = this.allNeighborsIndex[nodeId] || {};

		    for (k in index)
		      neighbors[k] = this.nodesIndex[k];

		    return neighbors;
		  });

	

sigma.parsers.json(
	json,
    {
      	container: stringName,
		settings: 
		{
      		defaultNodeColor: '#ec5148'
   		},
		
	
    },
	function(s) {
		s.graph.nodes().forEach(function(n) {
        	n.originalColor = n.color;
      	});
		s.graph.edges().forEach(function(e) {
        	e.originalColor = e.color;
      	});

	var force = false;
	document.getElementById('layout').onclick = function() {
	if (!force)
		s.startForceAtlas2({slowDown: 10});
	else
    	s.stopForceAtlas2();
  		force = !force;
	};

      	s.bind('clickNode', function(e) {
		    var nodeId = e.data.node.id,
		        toKeep = s.graph.neighbors(nodeId);
		    toKeep[nodeId] = e.data.node;

		    s.graph.nodes().forEach(function(n) {
		      if (toKeep[n.id])
		        n.color = n.originalColor;
		      else
		        n.color = '#eee';
		    });  

		    s.graph.edges().forEach(function(e) {
		      if (toKeep[e.source] && toKeep[e.target])
		        e.color = e.originalColor;
		      else
		        e.color = '#eee';
		    });

        	s.refresh();
      	});// END bind

      
	s.bind('clickStage', function(e) {
		s.graph.nodes().forEach(function(n) {
			n.color = n.originalColor;
        	});

        	s.graph.edges().forEach(function(e) {
          		e.color = e.originalColor;
        	});
        	
		s.refresh();
      	});//END bind


    } // END functions
  
);} // sigma.parser.json END
