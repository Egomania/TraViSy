function onlyUnique(value, index, self) { 
    return self.indexOf(value) === index;
}

function makeIPVISGraph(error, json, stringName, setWidth, setHeight){

	if (error) throw error;


	var nodes = new vis.DataSet(json.nodes);
	var edges = new vis.DataSet(json.links);
	
	var visWidth = setWidth + 'px';
	var visHeight = setHeight + 'px';

	var data = {
			nodes: nodes,
			edges: edges
			};

	var options = {
			autoResize: true,
			height: visHeight,
			width: visWidth,
			nodes: {
				shape: 'dot',
		        	size: 30,
		        	borderWidth: 2
				},
			edges:
				{
					scaling: {
		    			customScalingFunction: function (min,max,total,value) {
		      			return value/total;}
		   			}
				},
			physics:
				{
					barnesHut: 
					{
						centralGravity: 0,
						springLength: 1000,
						gravitationalConstant: -500

					}
				}
		        };

	var container = document.getElementById(stringName);

	var network = new vis.Network(container, data, options);
}

function makeVisGraph(error, json, stringName){
	
	if (error) throw error;

	var JSON = json;
	
	var nodes = new vis.DataSet(json.nodes);
	var edges = new vis.DataSet(json.edges);
	
	var data = {
			  nodes: nodes,
			  edges: edges
			};
	
	var container = document.getElementById(stringName);
	
	var options = {
			autoResize: true,
			height: '1500px',
			nodes: {
				shape: 'dot',
		        size: 30,
		        borderWidth: 2
		        },
		    edges: {
		        width: 2,
		        color: '#000000'
		    },
		    groups: {
	            Controller: {
	                color: '#AEC2F4'
	            },
	            DataPoint: {
	                color: '#4274F1'
	            }
	        },
		    interaction:
		    {
		    	hover:true
		    }
	};
	
	var x = - container.clientWidth + 20;
	var y = - container.clientHeight + 200;
	var step = 70;
	
	nodes.add({id: 0, x: x, y: y + 0 * step, label: 'Network Function', title: 'Network Function', value: 1, fixed: true, physics: false, group: 'Selection'});
	nodes.add({id: 1, x: x, y: y + 1 * step, label: 'Building', title: 'Building', value: 1, fixed: true, physics: false, group: 'Selection'});
	nodes.add({id: 2, x: x, y: y + 2 * step, label: 'Floor', title: 'Floor', value: 1, fixed: true, physics: false, group: 'Selection'});
	nodes.add({id: 3, x: x, y: y + 3 * step, label: 'Building and Floor', title: 'Building and Floor', value: 1, fixed: true, physics: false, group: 'Selection'});
	nodes.add({id: 4, x: x, y: y + 4 * step, label: 'Functional Unit', title: 'Functional Unit', value: 1, fixed: true, physics: false, group: 'Selection'});
	
	
	var network = new vis.Network(container, data, options);
	
	network.on("click", function (params) {
		
	      if (network.isCluster(params.nodes[0])) {network.openCluster(params.nodes[0]);}
	      else
	    	  {
	      var node = nodes.get({
	  		  filter: function (item) {
  	  		    return item.id == parseInt(params.nodes[0]);
  	  		  }
  	  		});
	      var cid = node[0];
	      
	      if (cid.group == 'Selection')
	      	{
	    	  
	    	  var legendEntries = [];
	    	  
	    	  var items = nodes.get({
	    	  	filter: function (item) {
	    	  	return !(item.group == 'Legend' || item.group == undefined || item.group == 'Selection' || item.group == 'EdgeSelectionTRUE' || item.group == 'EdgeSelectionFALSE');
	    	  	}
	    	  });
	    	  		
	    	  for (i = 0; i < items.length; i++) {
	    		  if (cid.id == 0)
	    			  {
	    			  	nodes.update({id: items[i].id, group: items[i].NetworkFunction});
	    			  	legendEntries.push(items[i].NetworkFunction);
	    			  }
	    		  if (cid.id == 1)
    			  {
    			  	nodes.update({id: items[i].id, group: items[i].Building});
    			  	legendEntries.push(items[i].Building);
    			  }
	    		  if (cid.id == 2)
    			  {
    			  	nodes.update({id: items[i].id, group: items[i].Floor});
    			  	legendEntries.push(items[i].Floor);
    			  }
	    		  if (cid.id == 3)
    			  {
    			  	nodes.update({id: items[i].id, group: items[i].Building + "." + items[i].Floor});
    			  	legendEntries.push(items[i].Building + "." + items[i].Floor);
    			  }
	    		  if (cid.id == 4)
    			  {
    			  	nodes.update({id: items[i].id, group: items[i].FunctionalUnit});
    			  	legendEntries.push(items[i].FunctionalUnit);
    			  }
	    	  };
	    	  
	    	  legendEntries = legendEntries.filter(onlyUnique);
	    	  
	    	  items = nodes.get({
		    	  	filter: function (item) {
		    	  	return item.cid == 'Legend';
		    	  	}
	    	  });
	    	  
			for (i = 0; i < items.length; i++) {
				nodes.remove(items[i].id);
			};
	    	
			for (i = 0; i < legendEntries.length; i++) {
				if (legendEntries[i] != undefined)
					{
					if (legendEntries[i] != 'undefined.undefined'){
					nodes.add({id: 5 + i, x: x, y: y + (i + 6) * step, label: legendEntries[i], value: 1, fixed: true, physics: false, group: legendEntries[i], cid: 'Legend', title: legendEntries[i]});
					}}
				
			};
	    	  
	    	};
		
	    	if (cid.group == 'EdgeSelectionTRUE')
	      	{
	    		var items = edges.get({
		    	  	filter: function (item) {
		    	  	return item.group == cid.selection;
		    	  	}
		    	  });
	    		for (i = 0; i < items.length; i++) {
	    			edges.update({id: items[i].id, hidden: false});
	    		}
	      	}
	    	
	    	if (cid.group == 'EdgeSelectionFALSE')
	      	{
	    		var items = edges.get({
		    	  	filter: function (item) {
		    	  	return item.group == cid.selection;
		    	  	}
		    	  });
	    		for (i = 0; i < items.length; i++) {
	    			edges.update({id: items[i].id, hidden: true});
	    		}
	      	}
	      
	      if (cid.cid != undefined)
	    	  if (cid.cid == 'Legend')
	    		  {
	    		  var clusterOptionsByData = {
		    	          joinCondition:function(childOptions) {
		    	        	  
		    	              return childOptions.group == cid.group;
		    	          },
		    	          processProperties: function (clusterOptions, childNodes, childEdges) {
		                      var totalMass = 0;
		                      for (var i = 0; i < childNodes.length; i++) {
		                          totalMass += childNodes[i].mass;
		                      }
		                      clusterOptions.mass = totalMass;
		                      return clusterOptions;
		                  },
		    	          clusterNodeProperties: {id:'cidCluster'+cid.group, title:'cidCluster'+cid.group, borderWidth:3, size:40, label: cid.group, shape: 'dot', group: cid.group}            
		    	      }
		    	      network.cluster(clusterOptionsByData);
	    		  }
	    	  else
	    	 {
	    	  var clusterOptionsByData = {
	    	          joinCondition:function(childOptions) {
	    	        	  
	    	              return childOptions.cid == cid.cid;
	    	          },
	    	          processProperties: function (clusterOptions, childNodes, childEdges) {
	                      var totalMass = 0;
	                      for (var i = 0; i < childNodes.length; i++) {
	                          totalMass += childNodes[i].mass;
	                      }
	                      clusterOptions.mass = totalMass;
	                      return clusterOptions;
	                  },
	    	          clusterNodeProperties: {id:'cidCluster'+cid.cid, title:'cidCluster'+cid.cid, borderWidth:3, size:40, label: cid.cid, shape: 'dot'}            
	    	      }
	    	      network.cluster(clusterOptionsByData);
	    	    };
	    	 };
	      
	  });
	
};
