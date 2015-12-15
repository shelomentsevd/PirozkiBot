import sys
import pg8000
import requests
import json
import re
from datetime import datetime

def insertToDB(cursor, text, likes, reposts, date):
	cursor.execute('INSERT INTO cakes(likes, reposts, text, date) values(%s, %s, %s, %s)', (likes, reposts, text, date))

def iso8601(utc):
	return datetime.fromtimestamp(utc).isoformat()

def getwall(owner, count, offset):
	data = {
		'owner_id':owner,
		'count': count,
		'offset': offset
	}
	r = requests.post('http://api.vk.com/method/wall.get', data=data)
	return r.json()['response']

def br(text):
	result = re.sub('\s*<br>\s*', '\n', text)
	return result

def author(raw_text):
	result = re.sub('\[id[0-9^\|]+\||[\]]', '', raw_text).replace('&amp;', '&').strip()
	return re.sub(' +', ' ', result)

def insertAll(cursor, posts):
	for item in posts[1:]:
		text = br(item['text'])
		raw_author = ''
		likes   = item['likes']['count']
		reposts = item['reposts']['count']
		text = author(text)
		date = iso8601(item['date'])
		insertToDB(cursor, text, likes, reposts, date)
		#print 'likes %s reposts %s' % (likes, reposts)
		#print '\n'+text

def main():
	db = pg8000.connect(user='cakesbot', password='cakesbot', database='cakesbot', host='localhost')
	step = 100	
	offset = 0
	count = 0
	cursor = db.cursor()
	while True:
		result = getwall('-28122932', step, offset)
		print 'offset: %d count: %d' % (offset, count)
		insertAll(cursor, result)
		db.commit()
		count = result[0]
		if offset > count:
			break
		offset += step
		
main()
