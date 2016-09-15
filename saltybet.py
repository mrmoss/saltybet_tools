import base64
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
			winner=base64.b64encode(winner)
			loser=base64.b64encode(loser)

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
		match='Bets are locked. '
		if line.find(match)!=0:
			return False
		line=line[len(match):]
		self.reset()

		#Get red side
		self.red=''
		for ii in line:
			if ii=='(':
				break
			self.red+=ii
		self.red=self.red.strip()

		#Teams aren't used
		if self.red[:4]=='Team':
			self.reset()
			return False

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