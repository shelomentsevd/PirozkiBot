import sys
import ConfigParser as cp
import requests
import json
from app.database import Database

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
        config.read('./app/conf/main.ini')
        #database section
        user      = config.get('database', 'user')
        password = config.get('database', 'password')
        database = config.get('database', 'database')
        host      = config.get('database', 'host')
        #other section
        wall = config.get('other', 'wall')
    except:
        print 'Config file error'
        sys.exit()

    print 'Cakes thief: trying to connect to PostgreSQL database'
    print 'User: ', user
    print 'Password: ', password
    print 'Database: ', database
    print 'Host: ', host
    print 'Wall: ', wall

    db = Database(user='cakesbot', password='cakesbot', database='cakesbot', host='localhost')

    step = 10    
    offset = 10
    count = 0
    while True:
        result = getwall(wall, step, offset)
        print 'offset: %d count: %d' % (offset, count)
        count = 10
        db.insertAll(result[1:])
        #count = result[0]
        if offset > count:
            break
        offset += step
        
main()
