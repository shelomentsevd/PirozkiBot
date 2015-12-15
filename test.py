import pg8000
import requests
import json
import re
from datetime import datetime

def insertToDB(cursor, text, likes, reposts, date):
	cursor.execute('INSERT INTO cakes(likes, reposts, text, date) values(%s, %s, "%s", "%s")' % (likes, reposts, text, date))

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

def main():
	result = getwall('-28122932', 10, 1)
	print json.dumps(result, sort_keys=True, ensure_ascii=False, indent=4, separators=(',', ':'))
	for item in result[1:]:
		text = br(item['text'])
		raw_author = ''
		likes   = item['likes']['count']
		reposts = item['reposts']['count']
		if(u'\u00A9' in text):
			text, raw_author = text.split(u'\u00A9')
			text = '%s--\n%s' % (text, author(raw_author))
		print 'likes %s reposts %s' % (likes, reposts)
		print text
main()
