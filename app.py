import sys
import ConfigParser as cp
import logging
from app.database import Database
from app.parser import Parser 

# Enable logging
logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO)

logger = logging.getLogger(__name__)

def main():
    try:
        config = cp.ConfigParser()
        config.read('./app/conf/main.ini')
        #database section
        user     = config.get('database', 'user')
        password = config.get('database', 'password')
        database = config.get('database', 'database')
        host     = config.get('database', 'host')
        #other section
        wall   = config.get('other', 'wall')
        update = config.getfloat('other', 'update')
    except:
        logger.error('Config file error')
        sys.exit()

    logger.info('Cakes thief: trying to connect to PostgreSQL database')
    logger.info('User: %s' % user)
    logger.info('Password: %s' % password)
    logger.info('Database: %s' % database)
    logger.info('Host: %s' % host)
    logger.info('Wall: %s' % wall)
    logger.info('Update in seconds: %s' % update)

    db = Database(user=user, password=password, database=database, host=host)
    parser = Parser(wall, update, db)
    parser.start()
    parser.idle()

main()
