import sys
import ConfigParser as cp
import requests
import json
import time
from app.database import Database

def getwall(owner, count, offset):
    data = {
        'owner_id':owner,
        'count': count,
        'offset': offset
    }
    try:
        r = requests.post('http://api.vk.com/method/wall.get', data=data)
    except:
        print 'Connection reset by peer'
        return False
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

    step = 100    
    offset = 0
    count = 0
    while True:
        result = getwall(wall, step, offset)
        
        while not result:
            result = getwall(wall, step, offset)

        print 'offset: %d count: %d' % (offset, db.count())
        db.insertAll(result[1:])
        count = result[0]
        if offset > count:
            break
        offset += step

    while True:
        time.sleep(60*5)
        offset = db.count()
        print 'Cakes: %s' % (offset)
        result = getwall(wall, step, offset)
        
main()
