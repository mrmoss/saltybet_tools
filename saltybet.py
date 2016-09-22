import select
import socket
import sqlite3

class network:
	def __init__(self):
		self.sock=None

	def connect(self,ip,port):
		#Close old session
		self.close()

		try:
			#Connect
			self.sock=socket.socket()
			self.sock.connect((ip,port))

			#Login
			self.sock.send('NICK justinfan92933402244722\r\n')
			self.sock.send('JOIN #saltybet\r\n')

		#Error, die and rethrow
		except:
			self.close()
			raise

	def close(self):
		try:
			self.parser.reset()
			self.sock.close()
		except:
			pass

	def available(self,conn):
		try:
			readable,writeable,errored=select.select([conn],[],[],0)
			if conn in readable:
				return True
		except:
			pass
		return False

	def pong(self):
		self.sock.send('PONG :tmi.twitch.tv\r\n')

	def read(self):
		try:
			#Got bytes
			buf=''
			if self.available(self.sock):
				buf=self.sock.recv(1024)

				#There were bytes and re couldn't read any...error
				if not buf:
					raise Exception("Disconnect")

			return buf

		#Error, die and rethrow
		except:
			self.close()
			raise

class database:
	def connect(self,filename):
		self.close()
		self.db=sqlite3.connect(filename)
		self.cursor=self.db.cursor()
		self.cursor.execute('create table if not exists fights(id integer primary key autoincrement,winner text,loser text,count integer)')
		self.cursor.execute('create table if not exists rankings(id integer primary key autoincrement,fighter text,wins integer,losses integer,fights integer,win_ratio integer,lose_ratio integer)')
		self.db.commit()

	def close(self):
		try:
			self.db.close()
			self.cursor=None
		except:
			pass

	def insert_ranking(self,winner,loser):
		insert_str='insert or replace into rankings(id,fighter,wins,losses,fights,win_ratio,lose_ratio) values(?,?,?,?,?,?,?)'

		#Winner Entry
		winner=self.get_ranking(winner)
		winner['wins']+=1
		winner['fights']+=1
		winner['win_ratio']=int(winner['wins']/float(winner['fights'])*100)
		winner['lose_ratio']=100-winner['win_ratio']
		self.cursor.execute(insert_str,self.ranking_to_query(winner))
		self.db.commit()

		#Loser Entry
		loser=self.get_ranking(loser)
		loser['losses']+=1
		loser['fights']+=1
		loser['win_ratio']=int(loser['wins']/float(loser['fights'])*100)
		loser['lose_ratio']=100-loser['win_ratio']
		self.cursor.execute(insert_str,self.ranking_to_query(loser))
		self.db.commit()

	def ranking_from_query(self,query):
		return {'id':query[0],
			'fighter':query[1],
			'wins':query[2],
			'losses':query[3],
			'fights':query[4],
			'win_ratio':query[5],
			'lose_ratio':query[6]}

	def ranking_to_query(self,obj):
		return (obj['id'],
			obj['fighter'],
			obj['wins'],
			obj['losses'],
			obj['fights'],
			obj['win_ratio'],
			obj['lose_ratio'])

	def get_ranking(self,fighter,case_sensitive=True):
		query_str='select * from rankings where '
		if case_sensitive:
			query_str+='fighter=?'
		else:
			query_str+='lower(fighter) like lower(?)'
		self.cursor.execute(query_str,(fighter,))
		query=self.cursor.fetchone()
		existed=True
		if not query or len(query)!=7:
			query=(None,fighter,0,0,0,0,0)
			existed=False
		ranking=self.ranking_from_query(query)
		ranking["existed"]=existed
		return ranking

	def insert_fight(self,winner,loser):
		#Get Fight
		fight=self.get_fight(winner,loser)
		fight['count']+=1

		#Insert/replace entry
		insert_str='insert or replace into fights(id,winner,loser,count) values(?,?,?,?)'
		self.cursor.execute(insert_str,self.fight_to_query(fight))
		self.db.commit()

	def fight_from_query(self,query):
		return {'id':query[0],
			'winner':query[1],
			'loser':query[2],
			'count':query[3]}

	def fight_to_query(self,obj):
		return (obj['id'],obj['winner'],obj['loser'],obj['count'])

	def get_fight(self,winner,loser):
		query_str='select * from fights where '
		args=[]

		if winner and len(winner)>0:
			query_str+='winner=? '
			args.append(winner)

		if loser and len(loser)>0:
			if winner and len(winner)>0:
				query_str+='and '
			query_str+='loser=?'
			args.append(loser)

		if len(args)<1 or len(args)>2:
			return None
		if len(args)==1:
			args=(args[0],)
		if len(args)==2:
			args=(args[0],args[1])

		self.cursor.execute(query_str,args)
		query=self.cursor.fetchone()
		existed=True
		if not query or len(query)!=4:
			query=(None,winner,loser,0)
			existed=False
		fight=self.fight_from_query(query)
		fight["existed"]=existed
		return fight

	def get_fights(self,winner,loser,case_sensitive=True):
		query_str='select * from fights where'
		args=[]

		if winner and len(winner)>0:
			if case_sensitive:
				query_str+=' winner=?'
			else:
				query_str+=' lower(winner) like lower(?)'
			args.append(winner)

		if loser and len(loser)>0:
			if winner and len(winner)>0:
				query_str+=' and'
			if case_sensitive:
				query_str+=' loser=?'
			else:
				query_str+=' lower(loser) like lower(?)'
			args.append(loser)

		if len(args)<1 or len(args)>2:
			return None
		if len(args)==1:
			args=(args[0],)
		if len(args)==2:
			args=(args[0],args[1])

		self.cursor.execute(query_str,args)
		fights=[]
		queries=self.cursor.fetchall()
		for query in queries:
			existed=True
			if not query or len(query)!=4:
				query=(None,winner,loser,0)
				existed=False
			fight=self.fight_from_query(query)
			fight["existed"]=existed
			fights.append(fight)

		return fights

class parser:
	def __init__(self,onecho=None,onping=None,onwaifu=None,onmatch=None,onwin=None,onteam=None):
		self.onecho=onecho
		self.onwaifu=onwaifu
		self.onping=onping
		self.onmatch=onmatch
		self.onwin=onwin
		self.onteam=onteam
		self.line=''
		self.reset()

	def reset(self):
		#Reset all our members...
		self.red=''
		self.blue=''
		self.last_win=''

	def parse(self,buf):
		#Go through bytes
		for ii in range(len(buf)):
			self.line+=buf[ii]

			#Got a line
			if self.line[-2:]=='\r\n':
				self.line=self.line.rstrip()
				if self.onecho:
					self.onecho(self.line)

				#Parse ping (keepalive)
				ping_match='PING :tmi.twitch.tv'
				if self.line.find('PING :tmi.twitch.tv')==0 and self.onping:
					self.onping()

				#Parse waifu
				waifu_match=':waifu4u!waifu4u@waifu4u.tmi.twitch.tv PRIVMSG #saltybet :'
				if self.line.find(waifu_match)==0:
					self.line=self.line[len(waifu_match):]
					if self.onwaifu:
						self.onwaifu(self.line)

					#Match
					if self.parse_match(self.line) and self.onmatch:
						self.onmatch(self.red,self.blue)

					#Payout
					elif self.parse_payout(self.line) and len(self.red)>0 and len(self.blue)>0:
						if self.red[:4]!='Team' and self.blue[:4]!='Team':
							if self.last_win is 'red' and self.onwin:
								self.onwin(self.red,self.blue)
							if self.last_win is 'blue' and self.onwin:
								self.onwin(self.blue,self.red)
						elif self.onteam:
							self.onteam()

				#Clear line...
				self.line=''

	def parse_match(self,line):
		#Remove trailing/ending whitespace
		line=line.strip()

		#Check for match set, if not stop here
		match='Bets are OPEN for '
		if line.find(match)!=0:
			return False
		line=line[len(match):]
		self.reset()

		#Get end of versus statement
		end_index=line.find('!')
		if end_index<0:
			return False
		line=line[:end_index]

		#Split up versus statement, more than two means something weird is going on
		sides=line.split(' vs ')
		if len(sides)!=2:
			return False

		#Get red side
		self.red=sides[0].strip()

		#Teams aren't used here
		if self.red[:4]=='Team':
			self.reset()
			return False

		#Get blue side
		self.blue=sides[1].strip()

		#Done
		return True

	def parse_payout(self,line):
		#Remove trailing/ending whitespace
		line=line.strip()

		#No teams...who cares about win/lose...
		if len(self.red)<=0 or len(self.blue)<=0:
			return False

		#Check for red side win
		if line.find(' wins! Payouts to Team Red. ')>0:
			self.last_win='red'
			return True

		#Check for blue side win
		if line.find(' wins! Payouts to Team Blue. ')>0:
			self.last_win='blue'
			return True

		#Not a payout...
		return False