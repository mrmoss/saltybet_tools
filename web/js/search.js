function search(div,fighters)
{
	salty_finder.search(fighters,function(data)
	{
		print_search_results(div,data);
	},
	function(error)
	{
		clear_div(div);
		div.appendChild(document.createTextNode('Error - '+error));
	});
}

function print_search_results(div,json)
{
	clear_div(div);
	var found_result=false;

	for(var key in json.fighters)
	{
		if(json.fighters[key].existed)
		{
			print_card(div,json.fighters[key]);
			found_result=true;
		}
	}

	if(!found_result)
		div.appendChild(document.createTextNode('No results found.'));
}

function print_card(div,entry,custom_class)
{
	if(!div)
		return;

	var panel=create_panel(entry.fighter,custom_class);
	div.appendChild(panel.div);

	var table=document.createElement('table');
	panel.body.appendChild(table);
	table.className='table';
	table.style.marginTop='-16px';
	table.style.marginBottom='0px';

	insert_row(table,['Wins',entry.wins]);
	insert_row(table,['Losses',entry.losses]);
	insert_row(table,['Win Ratio',entry.win_ratio+'%']);
	insert_row(table,['Matches',print_fight_table(entry)]);
}

function print_fight_table(entry)
{
	var table=document.createElement('table');
	table.className='table';
	table.style.marginTop='-9px';
	table.style.marginBottom='0px';

	insert_row(table,['Challenger',entry.fighter+' Was','Count']);

	for(var ii=0;ii<entry.matches.length;++ii)
	{
		var challenger=fighter_link('\''+entry.matches[ii].winner+'\'');
		var result='Loser';

		if(entry.matches[ii].winner==entry.fighter)
		{
			challenger=fighter_link('\''+entry.matches[ii].loser+'\'');
			result='Winner';
		}

		insert_row(table,[challenger,result,entry.matches[ii].count]);
	}

	return table;
}

function fighter_link(fighter)
{
	var a=document.createElement('a');
	a.href='../search/?fighter='+encodeURIComponent(fighter);
	if(fighter.length>1&&fighter[0]==fighter[fighter.length-1]&&
		(fighter[0]=='\''||fighter[0]=='"'))
		fighter=fighter.substr(1,fighter.length-2);
	a.innerHTML=fighter;
	return a;
}