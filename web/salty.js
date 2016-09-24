var url_home='/';
var last_match={red:null,blue:null};

function xhr(data,callback)
{
	var xmlhttp=new XMLHttpRequest();
	xmlhttp.onreadystatechange=function()
	{
		if(xmlhttp.readyState==4&&xmlhttp.status==200&&callback)
			callback(xmlhttp.responseText);
	};
	xmlhttp.open('POST','',true);
	xmlhttp.send(data);
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

function search(fighters)
{
	for(var key in fighters)
		fighters[key]=fighters[key].trim();
	clear_table();
	print_row(results_table,['Searching...']);
	var request=
	{
		fighters:fighters
	};
	xhr(JSON.stringify(request),function(data)
	{
		try
		{
			print_results(JSON.parse(data));
		}
		catch(error)
		{
			clear_table();
			print_row(results_table,['Error - '+error]);
		}
	});
}

function get_match()
{
	var request={match:true};
	xhr(JSON.stringify(request),function(data)
	{
		try
		{
			data=JSON.parse(data);
			if(data.match&&data.match.red&&data.match.blue)
			{
				if(data.match.red!=last_match.red&&data.match.blue!=last_match.blue)
				{
					clear_table();
					last_match=data.match;
					search(['\''+data.match.red+'\'','\''+data.match.blue+'\'']);
				}
			}
			else
			{
				clear_table();
				print_row(results_table,['Waiting for match...']);
			}
		}
		catch(error)
		{
			clear_table();
			print_row(results_table,['Error - '+error]);
		}
	});
}

function print_results(json)
{
	clear_table();
	var found_result=false;

	for(var key in json.fighters)
	{
		if(!json.fighters[key].existed)
			continue;

		print_row(results_table,['Fighter',fighter_link('\''+json.fighters[key].fighter+'\'')]);
		print_row(results_table,['Wins',json.fighters[key].wins]);
		print_row(results_table,['Losses',json.fighters[key].losses]);
		print_row(results_table,['Win Ratio',json.fighters[key].win_ratio+'%']);
		found_result=true;

		print_row(results_table,['Fights',print_fight_table(json.fighters[key].fighter,
			json.fighters[key].matches)]);
	}

	if(!found_result)
		print_row(results_table,['No results found.']);
}

function print_row(table,entries)
{
	var row=document.createElement('tr');
	table.appendChild(row);

	for(var key in entries)
	{
		var cell=document.createElement('td');
		row.appendChild(cell);
		var node=entries[key];
		if(!node.tagName&&!node.nodeName)
			node=document.createTextNode(entries[key]);
		cell.appendChild(node);
	}
}

function create_table_single_cell(value)
{
	var table=document.createElement('table');
	table.border='1px';
	var row=document.createElement('tr');
	table.appendChild(row);
	var cell=document.createElement('td');
	row.appendChild(cell);
	cell.appendChild(value);
	return table;
}

function clear_table()
{
	while(results_table.firstChild)
		results_table.removeChild(results_table.firstChild);
}

function print_fight_table(fighter,fights)
{
	var table=document.createElement('table');
	table.border='1px';
	print_row(table,['Challenger',fighter+' Was','Count']);
	for(var key in fights)
	{
		var challenger=fighter_link('\''+fights[key].winner+'\'');
		var result='Loser';
		if(fights[key].winner==fighter)
		{
			challenger=fighter_link('\''+fights[key].loser+'\'');
			result='Winner';
		}
		print_row(table,[challenger,result,fights[key].count]);
	}
	table.style.width='100%';
	return table;
}

function fighter_link(fighter)
{
	var a=document.createElement('a');
	a.href=url_home+'?fighter='+encodeURIComponent(fighter);
	if(fighter.length>1&&fighter[0]==fighter[fighter.length-1]&&
		(fighter[0]=='\''||fighter[0]=='"'))
		fighter=fighter.substr(1,fighter.length-2);
	a.innerHTML=fighter;
	return a;
}