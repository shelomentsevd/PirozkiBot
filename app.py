import sys
import ConfigParser as cp
from app.database import Database
from app.parser import Parser 

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
        wall   = config.get('other', 'wall')
        update = config.getfloat('other', 'update')
    except:
        print 'Config file error'
        sys.exit()

    print 'Cakes thief: trying to connect to PostgreSQL database'
    print 'User: ', user
    print 'Password: ', password
    print 'Database: ', database
    print 'Host: ', host
    print 'Wall: ', wall
    print 'Update in seconds: ', update

    db = Database(user=user, password=password, database=database, host=host)
    parser = Parser(wall, update, db)
    parser.start()
    parser.idle()

main()
