# Author: Dmitriy Shelomentsev (shelomentsev@protonmail.ch)
# -*- coding: utf-8 -*-
from telegram import InlineQueryResultArticle, ParseMode
from telegram.ext import Updater
from telegram.utils.botan import Botan
import re
import logging
import ConfigParser as cp
from app.database import Database
from random import getrandbits

# Enable logging
logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO)

logger = logging.getLogger(__name__)


class CakesBot:
    __help = '''Напишите боту слово, что бы получить случайный пирожок с ним.
Доступные команды:
    /last - присылает пять последних пирожков
    /random - присылает вам случайный пирожок
    /help  - выводит эту справку
    /about - выводит информацию о боте
Для поиска напишите в чате имя бота и ключевые слова. Пример:
    @pirozkibot олег
    '''
    __about = '''
Загружено %s пирожка
Написано just for fun.
Контент берётся отсюда: https://vk.com/perawki
Вы можете проголосовать за бота по ссылке:
https://telegram.me/storebot?start=pirozkibot
Автор бота: @HissingSound
    '''

    def __init__(self,  updater, database, botan_token=''):
        self.updater = updater
        self.botan = None
        if botan_token:
            self.botan = Botan(botan_token)
        self.__db = database

    def start(self, bot, update):
        self.__message_info(update.message, 'start')
        bot.sendMessage(update.message.chat_id, text=self.__help)

    def help(self, bot, update):
        self.__message_info(update.message, 'help')
        bot.sendMessage(update.message.chat_id, text=self.__help)

    def random(self, bot, update, args):
        self.__message_info(update.message, 'random')
        poem = ''

        if args:
            word = ' '.join(args)
            poem = self.__db.randomByWord(word)
        else:
            poem = self.__db.random()

        bot.sendMessage(update.message.chat_id, text=poem)

    def last(self, bot, update):
        self.__message_info(update.message, 'last')
        poems = self.__db.last(5)
        bot.sendMessage(update.message.chat_id, text=''.join(poems))

    def about(self, bot, update, args):
        self.__message_info(update.message, 'about')
        bot.sendMessage(update.message.chat_id,
                        text=self.__about % self.__db.count())

    def inline_search(self, bot, update):
        if update.inline_query:
            user = update.inline_query.from_user
            query = update.inline_query.query
            results = list()
            if query:
                logger.info('Inline: %s from %s @%s %s' % (query,
                                                           user.first_name,
                                                           user.username,
                                                           user.last_name))
                poems = self.__db.listByWord(query)
                if poems:
                    for poem in poems:
                        text, author = poem['text'], poem['author']
                        msg = text + author
                        uniqueId = hex(getrandbits(64))[2:]
                        article = InlineQueryResultArticle(id=uniqueId,
                                                           title=author,
                                                           message_text=msg,
                                                           description=text)
                        results.append(article)

            bot.answerInlineQuery(update.inline_query.id, results)

    def error(self, bot, update, error):
        self.__message_info(update.message, 'error')
        logger.warn('Update "%s" caused error "%s"' % (update, error))

    def unknow_command(self, bot, update, *args):
        self.__message_info(update.message)

    def message(self, bot, update):
        self.__message_info(update.message, 'message')
        poem = self.__db.randomByWord(update.message.text)
        bot.sendMessage(update.message.chat_id, text=poem)

    def __message_info(self, message, command='unknow'):
        if self.botan:
            self.botan.track(
                message=message,
                event_name=command
            )
        user = message.from_user
        logger.info(u'%s from %s @%s %s' % (message.text,
                                            user.first_name,
                                            user.username,
                                            user.last_name))

    def idle(self):
        self.updater.start_polling()
        self.updater.idle()


def main():
    try:
        config = cp.ConfigParser()
        config.read('./app/conf/main.ini')
        # database section
        user = config.get('database', 'user')
        password = config.get('database', 'password')
        database = config.get('database', 'database')
        host = config.get('database', 'host')
        # telegram bot section
        token = config.get('bot', 'token')
        # botan.io analytics
        botan_token = config.get('botan', 'token')
    except:
        logger.error('Configure file error')
        sys.exit()

    # Create the EventHandler and pass it your bot's token.
    updater = Updater(token)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher
    # Connect to database
    botDB = Database(user=user,
                     password=password,
                     database=database,
                     host=host)
    # Main class
    cakesBot = CakesBot(updater=updater,
                        database=botDB,
                        botan_token=botan_token)

    # on different commands - answer in Telegram
    dp.addTelegramCommandHandler("start",  cakesBot.start)
    dp.addTelegramCommandHandler("help",   cakesBot.help)
    dp.addTelegramCommandHandler("random", cakesBot.random)
    dp.addTelegramCommandHandler("last",   cakesBot.last)
    dp.addTelegramCommandHandler("about",  cakesBot.about)
    dp.addTelegramInlineHandler(cakesBot.inline_search)
    # unknow telegram command handler
    dp.addUnknownTelegramCommandHandler(cakesBot.unknow_command)
    dp.addTelegramMessageHandler(cakesBot.message)

    # log all errors
    dp.addErrorHandler(cakesBot.error)

    # start the bot
    cakesBot.idle()

if __name__ == '__main__':
    main()
