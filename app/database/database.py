# -*- coding: utf-8 -*-
import logging
import pg8000

logger = logging.getLogger(__name__)

class Database:
    """Cakes database class.
       Wrap above pg8000 and PostgreSQL
       Isn't thread safe!"""

    __msg_nothing_found = 'ничего не найдено'
    def __init__(self, user, password, database, host):
        """Connect to database"""
        self.__db = pg8000.connect(user=user, password=password, database=database, host=host)
        self.__cursor = self.__db.cursor()

    def insert(self, post):
        """Insert poem in database"""
        post_id    = post['id']
        text       = post['text']
        raw_text   = post['raw_text']
        raw_author = post['raw_author']
        date       = post['date']
        query      = 'INSERT INTO cakes (post_id, poem, raw_text, raw_author, text, date) values(%s, True, %s, %s, %s, %s)'
        
        try:
            self.__cursor.execute(query, (post_id, raw_text, raw_author, text, date))
            self.__db.commit()
        except:
            self.__db.rollback()
            return False

        return True

    def insertAll(self, posts):
        """Insert poems in database
           Each item in posts should be like this: 
           {
                'text': '',
                'likes': {
                    'count': 7
                },
                'reposts': {
                    'count': 8
                },
                'date': 1438687279,
                'id': 1
            }
        """
        for item in posts:
            if self.insert(item):
                logger.info('%s Added to base' % ( item['id'] ))

    def has(self, id):
        """
            Returns true if post with id already exists
        """
        query = 'SELECT EXISTS ( SELECT post_id FROM cakes WHERE post_id = %s )'
        row = self.__query_wrapper(query, (id,))
        result = False
        if row:
            # TODO: Why self.has query returns tuple, but self.count returns array?
            result = row[0][0]

        return result
    def count(self):
        """Returns amount of poems in database"""
        query = 'SELECT count(post_id) FROM cakes'
        result = self.__query_wrapper(query)
        if result:
            return result[0][0]
        else:
            return 0

    def random(self):
        """Returns random poem from database"""
        query = 'SELECT text FROM cakes OFFSET floor(random()*(SELECT count(*) FROM cakes)) LIMIT 1'
        result = self.__query_wrapper(query)
        if result:
            return result[0]
        else:
            return ''

    def randomByWord(self, word):
        """Returns random poem from database which contains @word"""
        query = "SELECT text FROM cakes WHERE text @@ %s OFFSET( random()*( SELECT count(*) FROM cakes WHERE text @@ %s ) ) LIMIT 1"
        result = self.__query_wrapper(query, (word, word))
        if result:
            return result[0]
        else:
            return self.listByWord(word)

    def listByWord(self, word):
        """Returns poems list. Each poem contains @word"""
        query = "SELECT text FROM cakes WHERE text @@ %s"
        rows = self.__query_wrapper(query, (word))
        if rows:
            result = ''
            for text in rows:
                result += text[0]
                result += '\n'
            return result
        else:
            return self.__msg_nothing_found

    def last(self, number):
        """Returns last @number poem"""
        query = "SELECT text FROM cakes ORDER BY post_id OFFSET (SELECT count(*) FROM cakes) - %s LIMIT %s"
        rows = self.__query_wrapper(query, (number, number))
        # TODO: Ugly. Should refactor it.
        if rows:
            result = ''
            for text in rows:
                result += text[0]
                result += "\n"
            return result
        else:
            return self.__msg_nothing_found

    # TODO: Didn't remember why i wrote it...
    def next(self, offset, limit):
        query = "SELECT text, post_id FROM cakes OFFSET (SELECT count(*) FROM cakes) - %s LIMIT %s"
        rows = self.__query_wrapper(query, (offset, limit))

        result = list()
        if rows:
            for row in rows:
                text, post_id = row
                result.append({'post_id': post_id, 'text': text})
            return result
        else:
            return result

    def __query_wrapper(self, query, args=()):
        """
            try, except wrap.
            args should be a tuple
        """
        logger.debug('Q: %s', (query % args))
        try:
            self.__cursor.execute(query, args)
            result = self.__cursor.fetchall()
            return result
        except:
            self.__db.rollback()
            logger.info('Exception!')
            logger.info('Q: %s', (query % args))
            return None

    def clean(self):
        """Will delete all cake-poems from database.
           DO NOT USE! ONLY FOR TEST PURPOSE!
        """
        try:
            self.__cursor.execute('DELETE FROM cakes WHERE True')
            self.__db.commit()
        except:
            self.__db.commit()
            return False

        return self.count()