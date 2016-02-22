import pg8000
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
	def has(id):
		"""
			Returns true if post with id already exists
		"""
		self.__cursor.execute('SELECT id FROM cakes WHERE post_id = %s', id)
		self.fetchone()
	def count(self):
		"""Returns amount of poems in database"""
		self.__cursor.execute('SELECT count(post_id) FROM cakes')
		return self.__cursor.fetchone()
	def last(self):
		"""Returns last poem from database"""
		self.__cursor.execute('SELECT max(post_id) FROM cakes')
		return self.__cursor.fetchone()