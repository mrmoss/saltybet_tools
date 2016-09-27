function clear_div(div)
{
	while(div&&div.firstChild)
		div.removeChild(div.firstChild);
}

function insert_row(table,data)
{
	var row=table.insertRow();

	for(var ii=0;ii<data.length;++ii)
	{
		var cell=row.insertCell(ii);

		if(!data[ii].tagName&&!data[ii].nodeName)
			cell.appendChild(document.createTextNode(data[ii]));
		else
			cell.appendChild(data[ii]);
	}
}

function parse_uri()
{
	var queries={};
	var query=window.location.search.substring(1);
	var vars=query.split('&');

	for(let ii=0;ii<vars.length;++ii)
	{
		var pair=vars[ii].split('=');

		if(typeof(queries[pair[0]])==='undefined')
		{
			queries[pair[0]]=decodeURIComponent(pair[1]);
		}
		else if(typeof(queries[pair[0]])==='string')
		{
			var arr=[queries[pair[0]],decodeURIComponent(pair[1])];
			queries[pair[0]]=arr;
		}
		else
		{
			queries[pair[0]].push(decodeURIComponent(pair[1]));
		}
	}

	return queries;
}

function create_panel(title,custom_class)
{
	var panel={};

	if(!custom_class)
		custom_class='panel panel-default';

	panel.div=document.createElement('div');
	panel.div.className=custom_class;

	panel.header=document.createElement('div');
	panel.div.appendChild(panel.header);
	panel.header.className='panel-heading';

	panel.text=document.createTextNode(title);
	panel.header.appendChild(panel.text);

	panel.body=document.createElement('div');
	panel.div.appendChild(panel.body);
	panel.body.className='panel-body';
	panel.body.style.paddingBottom='0px';

	return panel;
}