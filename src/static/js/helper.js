function splitSize10(value, num) {
	return Math.floor((value - (num + 1) * 10) / num);
};

function export_svg(id, docFormat) {

	var f = document.createElement("form");
		f.setAttribute('method',"post");
		f.setAttribute('action',"export");
		f.setAttribute('id', "export_form");

	var data = document.createElement("input"); 
		data.setAttribute('type',"hidden");
		data.setAttribute('name',"data");
		data.setAttribute('id',"data");

	var file = document.createElement("input"); 
		file.setAttribute('type',"hidden");
		file.setAttribute('name',"filename");
		file.setAttribute('id',"filename");

	var format = document.createElement("input"); 
		format.setAttribute('type',"hidden");
		format.setAttribute('name',"format");
		format.setAttribute('id',"format");

	var submit = document.createElement("input"); 
		submit.setAttribute('type',"submit");

	f.appendChild(data);
	f.appendChild(file);
	f.appendChild(format);
	f.appendChild(submit);

	document.getElementsByTagName('body')[0].appendChild(f);

	var svg;

	var elem = document.getElementById(id).getElementsByTagName("svg")[0];

	if (typeof elem !== 'undefined' && elem !== null) 
	{
		svg = document.getElementById(id).getElementsByTagName("svg")[0];
	}
	
	var FirstElem = svg.children[0];

	var styles = document.getElementsByTagName("style");
	var styleCounter = styles.length;

	var defs = document.createElementNS("http://www.w3.org/2000/svg","defs");
	

	for (i = 0; i < styleCounter; i++)
	{
		var style = document.createElementNS("http://www.w3.org/2000/svg","style");
			style.setAttribute("type", "text/css");
		textNode = document.createTextNode(styles[i].textContent)
		style.appendChild(textNode)
		defs.appendChild(style)
	}

	svg.insertBefore(defs, FirstElem);

	var svg_xml = (new XMLSerializer).serializeToString(svg);

	var filename = id+"."+docFormat;

	var form = document.getElementById("export_form");
		 form['data'].value = svg_xml;
		 form['filename'].value = filename;
		 form['format'].value = docFormat;
		 form.submit();
};

							
							
