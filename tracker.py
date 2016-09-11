#!/usr/bin/env python
import select
import socket
import time

def available(conn):
	try:
		readable,writeable,errored=select.select([conn],[],[],0)
		if conn in readable:
			return True
	except:
		pass
	return False

if __name__=='__main__':
	sock=None
	while True:
		try:
			sock=socket.socket()
			sock.connect(("irc.chat.twitch.tv",6667))
			sock.send('NICK justinfan92933402244722\r\n')
			sock.send('JOIN #saltybet\r\n');
			line=''


			while True:
				if available(sock):
					buf=sock.recv(1024)
					if not buf:
						raise Exception("Disconnect")

					for ii in range(len(buf)):
						line+=buf[ii]
						if line[-2:]=='\r\n':
							line=line.rstrip()
							waifu_match=':waifu4u!waifu4u@waifu4u.tmi.twitch.tv PRIVMSG #saltybet :'
							if waifu_match in line and line.index(waifu_match)==0:
								line=line[len(waifu_match):]
								print(line)
								#with open('log','a') as fstr:
								#	fstr.write(line+"\n")
							line=''
				time.sleep(0.1)
		except KeyboardInterrupt:
			exit(1)
		except Exception as error:
			print(error)
		try:
			sock.close()
		except:
			pass