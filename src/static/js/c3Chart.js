function makeTimelineBin(error, timebin, stringName, widthSet, heightSet)
{
	if (error) throw error;
	
	
	
	var chart = c3.generate({
	    bindto: stringName,
	    size: {
        	height: heightSet,
        	width: widthSet
    		},
	    data: {
		x: 'x',
	    	columns: timebin.lines,
	    },
	    axis: {
	        x: {
	            
	            tick: {            
	                format: function(x) 
	                	{var date = new Date(x*1000); 
	                	var h = date.getHours(); 
	                	var m = "0" + date.getMinutes(); 
	                	var s = "0" + date.getSeconds(); 
	                	var ret =  h + ":" + m.substr(-2) + ":" + s.substr(-2);
	                	return ret;},
	               culling:
	            	   {max: 10}
	            }
	        }
		}
	});

	
};

function makeTimeline(error, time, mac, stringName, widthSet, heightSet)
{
	if (error) throw error;
	
	
	
	var chart = c3.generate({
	    bindto: stringName,
	    size: {
        	height: heightSet,
        	width: widthSet
    		},
	    data: {
	    	json: time, type:'scatter',
	    	keys: {x: 'timestamp', 
	    		value: mac 
	    	}
	    },
	    axis: {
	        x: {
	            
	            tick: {            
	                format: function(x) 
	                	{var date = new Date(x*1000); 
	                	var h = date.getHours(); 
	                	var m = "0" + date.getMinutes(); 
	                	var s = "0" + date.getSeconds(); 
	                	var ret =  h + ":" + m.substr(-2) + ":" + s.substr(-2);
	                	return ret;},
	               culling:
	            	   {max: 10}
	            }
	        },
		    y: {
	            
	            tick: {            
	                format: function(x) {return x.toString(16);}
	            }
	        }
	    }
	});

	
};

