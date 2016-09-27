function salty_finder_t()
{}

salty_finder_t.prototype.xhr=function(data,onsuccess,onerror)
{
	var xmlhttp=new XMLHttpRequest();
	xmlhttp.onreadystatechange=function()
	{
		if(xmlhttp.readyState==4)
		{
			if(xmlhttp.status==200)
			{
				if(onsuccess)
					onsuccess(xmlhttp.responseText);
			}
			else
			{
				onerror('Response '+xmlhttp.status);
			}
		}
	};
	xmlhttp.open('POST','',true);
	xmlhttp.send(data);
}
salty_finder_t.prototype.search=function(fighters,onsuccess,onerror)
{
	for(var key in fighters)
		fighters[key]=fighters[key].trim();
	var request={fighters:fighters};
	this.xhr(JSON.stringify(request),function(data)
	{
		try
		{
			var data=JSON.parse(data);
			if(onsuccess)
				onsuccess(data);
		}
		catch(error)
		{
			if(onerror)
				onerror(error);
		}
	},onerror);
}

salty_finder_t.prototype.get_match=function(onsuccess,onerror)
{
	var request={match:true};
	this.xhr(JSON.stringify(request),function(data)
	{
		try
		{
			var data=JSON.parse(data);
			if(onsuccess)
				onsuccess(data);
		}
		catch(error)
		{
			if(onerror)
				onerror(error);
		}
	},onerror);
}

var salty_finder=new salty_finder_t();