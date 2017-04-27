#!/usr/bin/env python2
import saltybet

db=saltybet.database()

def echo(line):
	print(line)

def team():
	print('Ignoring team entry.')

def insert(winner,loser):
	db.insert_ranking(winner,loser)
	db.insert_fight(winner,loser)

if __name__=='__main__':
	verbose=False
	try:
		parser=saltybet.parser(onteam=team,onwin=insert)
		if verbose:
			parser.onecho=echo
		db.connect('saltybet.db')
		with open('saltybet.raw') as log:
			for line in log:
				parser.parse(line.rstrip()+'\r\n')
	except KeyboardInterrupt:
		exit(1)
	except Exception as error:
		print(error)
	exit(0)
