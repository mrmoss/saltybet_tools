#!/usr/bin/env python
import saltybet
import time

db=saltybet.database()
net=saltybet.network()

def echo(line):
	print(line)

def pong():
	print('Keepalive')
	net.pong()

if __name__=='__main__':
	while True:
		parser=saltybet.parser(onwaifu=echo,onping=pong)
		try:
			db.connect('saltybet.db')
			net.connect('irc.chat.twitch.tv',6667)
			while True:
				parser.parse(net.read())
				time.sleep(0.1)
		except KeyboardInterrupt:
			net.close()
			db.close()
			exit(1)
		except Exception as error:
			print(error)
			parser.reset()
			net.close()
			db.close()