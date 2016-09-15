import base64
import select
import socket
import sqlite3

class client:
	def __init__(self,ip='irc.chat.twitch.tv',port=6667,database_file='saltybet.db'):
		self.sock=None
		self.line=''
		self.connect(ip,port)
		self.db=sqlite3_db(database_file)
		self.parser=parser()

	def connect(self,ip=None,port=None):
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

	def run(self):
		try:
			#Got bytes
			if self.available(self.sock):
				buf=self.sock.recv(1024)

				#There were bytes and re couldn't read any...error
				if not buf:
					raise Exception("Disconnect")

				#Go through bytes
				for ii in range(len(buf)):
					self.line+=buf[ii]

					#Got a line
					if self.line[-2:]=='\r\n':
						self.line=self.line.rstrip()

						#Parse ping (keepalive)
						ping_match='PING :tmi.twitch.tv'
						if self.line.find('PING :tmi.twitch.tv')==0:
							self.sock.send('PONG :tmi.twitch.tv\r\n')

						#Parse waifu
						waifu_match=':waifu4u!waifu4u@waifu4u.tmi.twitch.tv PRIVMSG #saltybet :'
						if self.line.find(waifu_match)==0:
							self.line=self.line[len(waifu_match):]

							#Match
							if self.parser.parse_match(self.line):
								print('Match: '+self.parser.red+' vs '+self.parser.blue)

							#Payout
							elif self.parser.parse_payout(self.line) and len(self.parser.red)>0 and len(self.parser.blue)>0:
								if self.parser.red[:4]!='Team' and self.parser.blue[:4]!='Team':
									if self.parser.last_win is 'red':
										self.db.insert(self.parser.red,self.parser.blue)
									if self.parser.last_win is 'blue':
										self.db.insert(self.parser.blue,self.parser.red)
								else:
									print('Ignore team match')

						#Clear line...
						self.line=''

		#Error, die and rethrow
		except:
			self.close()
			raise

class sqlite3_db:
	def __init__(self,filename):
		self.connect(filename)

	def connect(self,filename):
		self.close()
		self.db=sqlite3.connect(filename)
		self.cursor=self.db.cursor()
		self.cursor.execute('create table if not exists saltybet(id integer primary key autoincrement,winner text,loser text,count integer)')
		self.db.commit()

	def close(self):
		try:
			self.db.close()
			self.cursor=None
		except:
			pass

	def insert(self,winner,loser):
		try:
			#Store winner/loser as base64 encoded string to prevent injection...
			#  I know prepared statements supposedly prevent this...but yea...
			winner='"'+base64.b64encode(winner)+'"'
			loser='"'+base64.b64encode(loser)+'"'

			#Get ID
			self.cursor.execute('select id from saltybet where winner=? and loser=?',(winner,loser))
			row_id=self.cursor.fetchone()
			if row_id and len(row_id)>0:
				row_id=row_id[0]

			#Calculate count
			self.cursor.execute('select count from saltybet where winner=? and loser=?',(winner,loser))
			count=self.cursor.fetchone()
			if not count or len(count)<=0:
				count=1
			else:
				count=count[0]+1

			#Insert/replace entry
			self.cursor.execute('insert or replace into saltybet(id,winner,loser,count) values(?,?,?,?)',(row_id,winner,loser,count))
			self.db.commit()

		#Error, close
		except:
			self.close()
			raise
class parser:
	def __init__(self):
		self.reset()

	def reset(self):
		#Reset all our members...
		self.red=''
		self.blue=''
		self.last_win=''

	def parse_match(self,line):
		#Remove trailing/ending whitespace
		line=line.strip()

		#Check for match set, if not stop here
		match='Bets are locked. '
		if line.find(match)!=0:
			return False
		line=line[len(match):]
		self.last_win=''

		#Get red side
		red=''
		for ii in line:
			if ii=='(':
				break
			red+=ii
		red=red.strip()

		#Teams aren't used
		if red[:4]=='Team':
			self.red=''
			self.blue=''
			return False

		#Good red side
		self.red=red

		#Strip odds and bet size
		line=line[len(self.red):]
		comma_index=line.find(',')
		if comma_index>=0 and comma_index!=len(line):
			line=line[comma_index+1:]

		#Get blue side
		self.blue=''
		for ii in line:
			if ii=='(':
				break
			self.blue+=ii
		self.blue=self.blue.strip()

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