#!/usr/bin/env python
import BaseHTTPServer
import json
import SimpleHTTPServer
import saltybet
import urllib
import urlparse

db=saltybet.database()

class MyHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
	def do_GET(self):
		self.send_response(200)
		self.send_header('Content-type','text/html')
		self.end_headers()
		self.wfile.write('<html></html>')
		self.wfile.close()
	def do_POST(self):
		ret=''
		try:
			data=self.rfile.read(int(self.headers.getheader('content-length',0)))
			data=json.loads(data)
			ret={}
			if 'fighters' in data:
				ret['fighters']=[]
				for ii in range(len(data['fighters'])):
					ret['fighters'].append(db.get_ranking(data['fighters'][ii]))
			if 'fights' in data:
				ret['fights']=[]
				for ii in range(len(data['fights'])):
					winner=None
					if 'winner' in data['fights'][ii]:
						winner=data['fights'][ii]['winner']
					loser=None
					if 'loser' in data['fights'][ii]:
						loser=data['fights'][ii]['loser']
					ret['fights'].append(db.get_fight(winner,loser))
			ret=json.dumps(ret)
		except Exception as error:
			print('ERROR - '+str(error))
			pass
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
	except:
		pass