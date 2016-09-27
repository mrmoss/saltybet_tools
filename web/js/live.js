function get_match(red_div,blue_div)
{
	var red_class='panel panel-danger';
	var blue_class='panel panel-info';

	salty_finder.get_match(function(data)
	{
		if(JSON.stringify(data.match)==JSON.stringify(last_match))
			return;
		last_match=data.match;

		clear_div(red_div);
		var red=last_match.red;
		var red_data=null;

		clear_div(blue_div);
		var blue=last_match.blue;
		var blue_data=null;

		if(!data.match)
		{
			show_error(red_div,'Error','No match data available.',red_class);
			show_error(blue_div,'Error','No match data available.',blue_class);
			return;
		}

		var fighters=['\''+red+'\'','\''+blue+'\''];

		salty_finder.search(fighters,function(data)
		{
			if(!data||!data.fighters)
			{
				show_error(red_div,'Error','Error - Invalid response from server.',red_class);
				show_error(blue_div,'Error','Error - Invalid response from server.',blue_class);
				return;
			}

			for(var ii=0;ii<data.fighters.length;++ii)
			{
				if(!red_data&&data.fighters[ii].fighter==red)
					red_data=data.fighters[ii];
				if(!blue_data&&data.fighters[ii].fighter==blue)
					blue_data=data.fighters[ii];
				if(red_data&&blue_data)
					break;
			}

			if(red_data)
				print_card(red_div,red_data,red_class);
			else
				show_error(red_div,red,'No fighter data available.',red_class);
			if(blue_data)
				print_card(blue_div,blue_data,blue_class);
			else
				show_error(blue_div,blue,'No fighter data available.',blue_class);
		},
		function(error)
		{
			show_error(red_div,'Error','Error - '+error,red_class);
			show_error(blue_div,'Error','Error - '+error,blue_class);
		});
	},function(error)
	{
		show_error(red_div,'Error','Error - '+error,red_class);
		show_error(blue_div,'Error','Error - '+error,blue_class);
	});
}

function show_error(div,title,error,custom_class)
{
	if(!div)
		return;

	clear_div(div);

	var panel=create_panel(title,custom_class);
	div.appendChild(panel.div);
	panel.body.style.paddingBottom='20px';

	panel.body.appendChild(document.createTextNode(error));
}