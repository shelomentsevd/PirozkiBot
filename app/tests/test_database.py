# -*- coding: utf-8 -*-
import unittest
from ..database import Database

class DatabaseTestCase(unittest.TestCase):
    posts = [
        {
            'text': u'поймали на крючок русалку\
                     и вдруг она снимает хвост\
                     и говорит мужичьим басом\
                     майор гаврилов рыбнадзор\
                     © [id7253775| Евгений Клыков]',
            'likes': {
                'count': 2
            },
            'reposts': {
                'count': 1
            },
            'date': 1438687279,
            'id': 2
        },
        {
            'text': u'хотите нарисую анну\
                     не с пачкой сигарет в руках\
                     не одинокую по лужам\
                     и не промокшую от слёз\
                     © [id22301914|Отто Сандер]',
            'likes': {
                'count': 7
            },
            'reposts': {
                'count': 8
            },
            'date': 1438687279,
            'id': 1
        }
    ]

    def setUp(self):
        self.__db = Database(user='cakesbot', password='cakesbot', database='cakesbot_test', host='localhost')
        self.__db.clean()
    
    def tearDown(self):
        self.__db.clean()

    def test_insertAll_1(self):
        """Database.insertAll base functionality test"""
        self.__db.insertAll(self.posts)
        count = self.__db.count()
        self.assertEqual(count, 2, 'Database.insertAll([post1, post2]) test 1 failed')

    def test_insertAll_2(self):
        """insert posts twice or more"""
        self.__db.insertAll(self.posts)
        self.__db.insertAll(self.posts)
        self.__db.insertAll(self.posts)
        count = self.__db.count()
        self.assertTrue(count == 2, 'Database.insertAll([post1, post2]) test 2 failed')

    def test_insert(self):
        self.assertTrue(self.__db.insert(self.posts[0]), 'Database.insert(post) failed')
        self.assertFalse(self.__db.insert(self.posts[0]),'Database.insert(post) failed')

    def test_hasId(self):
        self.__db.insertAll(self.posts)
        self.assertTrue(self.__db.has(2), 'Database.has(id) test failed')

    def test_last(self):
        self.__db.insertAll(self.posts)
        self.assertEqual(self.__db.last(), 2)