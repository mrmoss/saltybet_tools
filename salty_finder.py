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
			file=open('web/index.html','r')
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
			if 'fighters' in data:
				ret['fighters']=[]
				for ii in range(len(data['fighters'])):
					data['fighters'][ii]=data['fighters'][ii].strip('%')
					data['fighters'][ii]=data['fighters'][ii].strip('*')
					if len(data['fighters'][ii])==0:
						continue
					if len(data['fighters'][ii])>=3:
						data['fighters'][ii]='%'+data['fighters'][ii]+'%'
					for fighter in db.get_rankings(data['fighters'][ii],False):
						fighter['matches']=[]
						for fight in db.get_fights(fighter['fighter'],None,False):
							fighter['matches'].append(fight)
						for fight in db.get_fights(None,fighter['fighter'],False):
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
