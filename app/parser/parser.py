from requests import post
from app.database import Database
from signal import signal, SIGINT, SIGTERM, SIGABRT
from threading import Thread, Lock, current_thread, Event
from time import sleep
import logging
import json
import helpers

# Enable logging
logger = logging.getLogger(__name__)

class Parser:
    """Parser"""
    def __init__(self, wall, timeout, database):
        self.__wall = wall
        self.__database = database
        self.__timeout = timeout
        self.__stop_event = Event()
        self.__lock = Lock()
        self.running = False

    def start(self):
        with self.__lock:
            if self.running:
                logger.info('Already running')
                return
            self.__thread = Thread(target=self.__parse, name='parser')
            self.__thread.start()
            self.running = True

    def stop(self):
        with self.__lock:
            if self.running:
                self.__stop_event.set()
                while self.running:
                    sleep(0.1)
                self.__thread.join()
                self.__stop_event.clear()

    def signal_handler(self, signum, frame):
        self.is_idle = False
        self.stop()

    def idle(self, stop_signals=(SIGINT, SIGTERM, SIGABRT)):
        for sig in stop_signals:
            signal(sig, self.signal_handler)

        self.is_idle = True

        while self.is_idle:
            sleep(1)

    def __getwall(self, owner, count, offset):
        data = {
            'owner_id':owner,
            'count': count,
            'offset': offset
        }
        try:
            r = post('http://api.vk.com/method/wall.get', data=data)
        except:
            logger.info('Connection reset by peer')
            return []
        return r.json()['response']

    def preprocess(self, data):
        result = []
        for item in data:
            poems = helpers.getPoems(item['text'])
            for poem in poems:
                ritem = dict()
                ritem['raw_text']   = item['text']
                ritem['raw_author'] = poem['author_raw']
                ritem['author']     = helpers.author(poem['author_raw'])
                ritem['text']       = poem['text']
                ritem['date']       = helpers.iso8601(item['date'])
                ritem['id']         = item['id']
                result.append(ritem)

        return result


    def __parse(self):
        logger.info('Parser thread started')
        while True:
            if self.__stop_event.is_set():
                logger.info('Parser stopped')
                break

            try:
                full = self.__database.count()
                logger.info('Count %s' % full)
                if not full:
                    step = 100
                    offset = 0
                    count  = 0
                    while True:
                        raw_result = self.__getwall(self.__wall, step, offset)
                        count = raw_result[0]
                        result = self.preprocess(raw_result[1:])
                        if result:
                            self.__database.insertAll(result)
                            offset += step
                            logger.info('%s/%s processed' % (count, offset))
                        else:
                            continue

                        if offset > count:
                            logger.info('Done')
                            break
                else:
                    step = 10
                    offset = 0
                    while True:
                        logger.debug('Offset %s step %s ' % (offset, step))
                        raw_result = self.__getwall(self.__wall, step, offset)
                        result = self.preprocess(raw_result[1:])
                        if result:
                            if not self.__database.has(result[0]['id']):
                                self.__database.insertAll(result)
                                offset += step
                            else:
                                logger.debug('Break already in database')
                                break
                        else:
                            logger.debug('Break result is None')
                            break
                            
            except Exception as e:
                logger.exception(e)
            sleep(self.__timeout)

        self.running = False
        logger.info('Parser thread stopped')