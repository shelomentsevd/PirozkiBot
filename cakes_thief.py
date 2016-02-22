import sys
import pg8000
import requests
import json
import helpers

def insertToDB(cursor, post_id, text, likes, reposts, date):
	#WARN: SQL injection!
	cursor.execute('INSERT INTO cakes(post_id, likes, reposts, text, date) values(%s, %s, %s, %s, %s)', (post_id ,likes, reposts, text, date))

def getwall(owner, count, offset):
	data = {
		'owner_id':owner,
		'count': count,
		'offset': offset
	}
	r = requests.post('http://api.vk.com/method/wall.get', data=data)
	return r.json()['response']

def insertAll(cursor, posts):
	for item in posts[1:]:
		text = helpers.br(item['text'])
		raw_author = ''
		likes   = item['likes']['count']
		reposts = item['reposts']['count']
		post_id = item['id']
		text = helpers.author(text)
		#date = iso8601(item['date'])
		#insertToDB(cursor, post_id, text, likes, reposts, date)
		print 'post id %s' % post_id
		#print 'likes %s reposts %s' % (likes, reposts)
		#print '\n'+text

def main():
	#TODO: Add configs!
	db = pg8000.connect(user='cakesbot', password='cakesbot', database='cakesbot', host='localhost')
	step = 10	
	offset = 10
	count = 0
	cursor = db.cursor()
	while True:
		result = getwall('-28122932', step, offset)
		print 'offset: %d count: %d' % (offset, count)
		insertAll(cursor, result)
		db.commit()
		count = 10
		#count = result[0]
		if offset > count:
			break
		offset += step
		
main()
