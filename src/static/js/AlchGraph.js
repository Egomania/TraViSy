function makeAlchGraph(error, json, width2, height2){
	if (error)
		throw error;

	var config = {
		dataSource: json,
		graphHeight: function(){ return height2; },
		graphWidth: function(){ return width2; },  
            };

        alchemy = new Alchemy(config)
}
