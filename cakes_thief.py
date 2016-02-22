import sys
import pg8000
import ConfigParser as cp
import requests
import json
import helpers

class Database:
	"""Cakes database class.
	   Wrap above pg8000 and PostgreSQL
	   Isn't thread safe!"""
	def __init__(self, user, password, database, host):
		"""Connect to database"""
		self.__db = pg8000.connect(user=user, password=password, database=database, host=host)
		self.__cursor = self.__db.cursor()

	def insert(self, post):
		"""Insert poem in database"""
		post_id   = post['id']
		text      = helpers.makePretty(post['text'])
		likes     = post['likes']['count']
		reposts   = post['reposts']['count']
		date      = helpers.iso8601(post['date'])
		self.__cursor.execute('INSERT INTO cakes (post_id, likes, reposts, text, date) values(%s, %s, %s, %s, %s)', 
			post_id, likes, reposts, text, date)

	def insertAll(self, posts):
		"""Insert poems in database
		   Each item in posts should be like this: 
		   {
				'text': '',
				'likes': {
					'count': 7
				},
				'reposts': {
					'count': 8
				},
				'date': 1438687279,
				'id': 1
			}
		"""
		for item in posts:
			self.insert(item)
		self.__db.commit()

	def count(self):
		"""Returns amount of poems in database"""
	def last(self):
		"""Returns last poem from database"""

def getwall(owner, count, offset):
	data = {
		'owner_id':owner,
		'count': count,
		'offset': offset
	}
	r = requests.post('http://api.vk.com/method/wall.get', data=data)
	return r.json()['response']

def main():
	try:
		config = cp.ConfigParser()
		config.read('./conf/main.ini')
		user 	 = config.get('database', 'user')
		password = config.get('database', 'password')
		database = config.get('database', 'database')
		host 	 = config.get('database', 'host')
	except:
		print 'Config file error'
		sys.exit()

	print 'Cakes thief: trying to connect to PostgreSQL database'
	print 'User: ', user
	print 'Password: ', password
	print 'Database: ', database
	print 'Host: ', host

	db = Database(user='cakesbot', password='cakesbot', database='cakesbot', host='localhost')

	step = 10	
	offset = 10
	count = 0
	while True:
		result = getwall('-28122932', step, offset)
		print 'offset: %d count: %d' % (offset, count)
		count = 10
		db.insertAll(result[1:])
		#count = result[0]
		if offset > count:
			break
		offset += step
		
main()
