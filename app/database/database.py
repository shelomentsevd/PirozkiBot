# -*- coding: utf-8 -*-
import pg8000
import helpers

class Database:
    """Cakes database class.
       Wrap above pg8000 and PostgreSQL
       Isn't thread safe!"""
    def __init__(self, user, password, database, host):
        """Connect to database"""
        self.__db = pg8000.connect(user=user, password=password, database=database, host=host)
        self.__cursor = self.__db.cursor()

    def insert(self, post):
        """Insert poem in database"""
        post_id   = post['id']
        text      = helpers.makePretty(post['text'])
        likes     = post['likes']['count']
        reposts   = post['reposts']['count']
        date      = helpers.iso8601(post['date'])
        try:
            self.__cursor.execute('INSERT INTO cakes (post_id, likes, reposts, text, date) values(%s, %s, %s, %s, %s)', 
                (post_id, likes, reposts, text, date))
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
                print '%s Added to base' % ( item['id'] )

    def has(self, id):
        """
            Returns true if post with id already exists
        """
        self.__cursor.execute('SELECT post_id FROM cakes WHERE post_id = %s' % (id))
        result = self.__cursor.fetchone()
        if result:
            return result[0] == id
        else:
            return False

    def count(self):
        """Returns amount of poems in database"""
        self.__cursor.execute('SELECT count(post_id) FROM cakes')
        return self.__cursor.fetchone()[0]
    def last(self):
        """Returns last poem from database"""
        self.__cursor.execute('SELECT max(post_id) FROM cakes')
        return self.__cursor.fetchone()[0]

    def random(self):
        """Returns random poem from database"""
        self.__cursor.execute('SELECT text FROM cakes OFFSET floor(random()*(SELECT count(*) FROM cakes)) LIMIT 1')
        result = self.__cursor.fetchone()
        if result:
            return result[0]
        else:
            return ''

    def randomByWord(self, word):
        """Returns random poem from database which contains @word"""
        self.__cursor.execute("SELECT text FROM cakes WHERE text @@ '%s' OFFSET( random()*( SELECT count(*) FROM cakes WHERE text @@ '%s' ) ) LIMIT 1" % (word, word));
        result = self.__cursor.fetchone()
        if result:
            return result[0]
        else:
            return 'ничего не найдено'

    def listByWord(self, word):
        """Returns poems list. Each poem contains @word"""
        self.__cursor.execute("SELECT text FROM cakes WHERE text @@ '%s'" % (word))
        dbresult = self.__cursor.fetchall()
        if dbresult:
            result = ''
            for text in dbresult:
                result += text[0]
                result += '\n'
            return result
        else:
            return 'ничего не найдено'

    def clean(self):
        """Will delete all cake-poems from database.
           DO NOT USE! ONLY FOR TEST PURPOSE!
        """
        self.__cursor.execute('DELETE FROM cakes WHERE True')
        self.__db.commit()
        return self.count()