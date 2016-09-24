#!/usr/bin/env python
import BaseHTTPServer
import json
import os
import SimpleHTTPServer
import saltybet
import urllib
import urlparse

db=saltybet.database()

class MyHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
	def do_GET(self):
		try:
			self.path=self.path.strip()
			if self.path=='/salty.js':
				self.path='web/salty.js'
			elif self.path=='/live':
				self.path='web/live.html'
			else:
				self.path='web/index.html'
			file=open(self.path,'r')
			self.send_response(200)
			self.send_header('Content-type','text/html')
			self.end_headers()
			self.wfile.write(file.read())
			self.wfile.close()
		except Exception as error:
			print('ERROR - '+str(error))
	def do_POST(self):
		ret=''
		try:
			data=self.rfile.read(int(self.headers.getheader('content-length',0)))
			data=json.loads(data)
			ret={}
			if 'match' in data and data['match']:
				ret['match']=db.get_match()
			if 'fighters' in data:
				ret['fighters']=[]
				for ii in range(len(data['fighters'])):
					query=data['fighters'][ii]
					query=query.strip('%')
					query=query.strip('*')
					exact=False
					if len(query)==0:
						continue
					if len(query)>1 and query[0]==query[-1] and (query[0]=='\'' or query[0]=='"'):
						exact=True
						query=query[1:-1]
					elif len(query)>=3:
						query='%'+query+'%'
					rankings=[]
					if exact:
						print(db.get_ranking(query))
						rankings.append(db.get_ranking(query))
					else:
						rankings=db.get_rankings(query,False)
					for fighter in rankings:
						fighter['matches']=[]
						for fight in db.get_fights(fighter['fighter'],None):
							fighter['matches'].append(fight)
						for fight in db.get_fights(None,fighter['fighter']):
							fighter['matches'].append(fight)
						ret['fighters'].append(fighter)
			ret=json.dumps(ret)
		except Exception as error:
			print('ERROR - '+str(error))
		self.send_response(200)
		self.send_header('Content-type','text/plain')
		self.end_headers()
		self.wfile.write(ret)
		self.wfile.close()

if __name__=='__main__':
	try:
		db.connect('saltybet.db')
		Handler=MyHandler
		server=BaseHTTPServer.HTTPServer(('127.0.0.1',8080),MyHandler)
		server.serve_forever()
	except Exception as error:
		print('ERROR - '+str(error))
