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

    while True:
        step = 10
        offset = 0
        while True:
            result = getwall(wall, step, offset)
            # TODO OUT OF RANGE IF FIRST START
            if not db.has(result[1]['id']):
                db.insertAll(result[1:])
                offset += step
            else:
                break
        print 'Cakes: %s' % (db.count())
        time.sleep(5)

main()
