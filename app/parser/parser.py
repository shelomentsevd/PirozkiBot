from requests import post
from app.database import Database
from signal import signal, SIGINT, SIGTERM, SIGABRT
from threading import Thread, Lock, current_thread, Event
from time import sleep
import json
import helpers

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
                print 'Already running'
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
            print 'Connection reset by peer'
            return []
        return r.json()['response']

    def preprocess(self, data):
        result = []
        for item in data:
            poems = helpers.getPoems(item['text'])
            for poem in poems:
                ritem = dict()
                ritem['raw_text'] = item['text']
                ritem['text']     = poem['text']
                ritem['date']     = helpers.iso8601(item['date'])
                ritem['id']       = item['id']
                result.append(ritem)

        return result


    def __parse(self):
        print 'Parser thread started'
        while True:
            if self.__stop_event.is_set():
                print 'Parser stopped'
                break

            #try:
            step = 10
            offset = 0
            while True:
                raw_result = self.__getwall(self.__wall, step, offset)
                result = self.preprocess(raw_result[1:])
                print "offset ", offset
                if result:
                    if not self.__database.has(result[0]['id']):
                        self.__database.insertAll(result)
                        offset += step
                        #print "offset ", offset
                    else:
                        break
                else:
                    break
            #except:
            #    print 'Unhandled exception in Parser thread'

            sleep(self.__timeout)

        self.running = False
        print 'Parser thread stopped'