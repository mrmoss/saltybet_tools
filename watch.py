#!/usr/bin/env python2
import saltybet
import time

net=saltybet.network()

def echo(line):
	print(line)

def pong():
	print('Keepalive')
	net.pong()

if __name__=='__main__':
	while True:
		parser=saltybet.parser(onecho=echo,onping=pong)
		try:
			net.connect('irc.chat.twitch.tv',6667)
			while True:
				parser.parse(net.read())
				time.sleep(0.1)
		except KeyboardInterrupt:
			net.close()
			exit(1)
		except Exception as error:
			print(error)
			parser.reset()
			net.close()
