# -*- coding: utf-8 -*-
from telegram import Updater, InlineQueryResultArticle, ParseMode
import re
import logging
import ConfigParser as cp
from app.database import Database
from signal import signal, SIGINT, SIGTERM, SIGABRT
from random import getrandbits

# Enable logging
logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO)

logger = logging.getLogger(__name__)

def escape_markdown(text):
    """Helper function to escape telegram markup symbols"""
    escape_chars = '\*_`\['
    return re.sub(r'([%s])' % escape_chars, r'\\\1', text)

class CakesBot:
    __help = '''
Доступные команды:
    /last - присылает пять последних пирожков
    /random - присылает вам случайный пирожок, если после /random написать несколько слов, вы получите случайный пирожок содержащий эти слова
    /help  - выводит эту справку
    /about - выводит информацию о боте
Поиск по пирожкам доступен из любого чата, нужно написать имя бота @pirozkibot и слова которые должны содержаться в пирожке.
Например "@pirozkibot олег" 
    
    Вы можете проголосовать за бота по ссылке:
    https://telegram.me/storebot?start=pirozkibot
    '''
    __about = '''
Загружено %s пирожка
Написано just for fun.
Контент берётся отсюда: https://vk.com/perawki
Автор: @HissingSound
    '''
    def __init__(self, updater, user, password, database, host):
        self.updater = updater
        self.__db = Database(user=user, password=password, database=database, host=host)

    def start(self, bot, update):
        self.__message_info(update.message)
        bot.sendMessage(update.message.chat_id, text=self.__help)

    def help(self, bot, update):
        self.__message_info(update.message)
        bot.sendMessage(update.message.chat_id, text=self.__help)

    def random(self, bot, update, args):
        self.__message_info(update.message)
        poem = ''

        if args:
            word = ' '.join(args)
            poem = self.__db.randomByWord(word)
        else:
            poem = self.__db.random()

        bot.sendMessage(update.message.chat_id, text=poem)

    def last(self, bot, update):
        self.__message_info(update.message)
        poems = self.__db.last(5)
        text  = ''
        
        if poems:
            for poem in poems:
                text += poem

        bot.sendMessage(update.message.chat_id, text=text)

    def about(self, bot, update, args):
        self.__message_info(update.message)
        bot.sendMessage(update.message.chat_id, text=self.__about % self.__db.count())

    def inline_search(self, bot, update):
        if update.inline_query:
            query = update.inline_query.query
            results = list()
            if query:
                poems = self.__db.listByWord(query)
                if poems:
                    for poem in poems:
                        results.append(InlineQueryResultArticle(id=hex(getrandbits(64))[2:], 
                                                                title=poem['author'], 
                                                                message_text=poem['text'], 
                                                                description=poem['text']))

            bot.answerInlineQuery(update.inline_query.id, results)

    def error(self, bot, update, error):
        self.__message_info(update.message)
        logger.warn('Update "%s" caused error "%s"' % (update, error))

    def unknow_command(self, bot, update, *args):
        self.help(bot, update)

    def __message_info(self, message):
        user = message.from_user
        logger.info(u'%s from %s @%s %s' % (message.text, 
                                            user.first_name,
                                            user.username,
                                            user.last_name))

    def cli_unknow_command(self, bot, update):
        logger.info('Unknow command')

    def signal_handler(self, signum, frame):
        self.is_idle = False
        self.updater.stop()

    def idle(self, stop_signals=(SIGINT, SIGTERM, SIGABRT)):
        self.is_idle = True

        for sig in stop_signals:
            signal(sig, self.signal_handler)

        self.update_queue = self.updater.start_polling(poll_interval=0.1, timeout=10)
        
        while self.is_idle:
            try:
                text = raw_input()
            except NameError:
                text = input()

            if text == 'stop':
                self.updater.stop()
                break

            elif len(text) > 0:
                self.update_queue.put(text)

def main():
    try:
        config = cp.ConfigParser()
        config.read('./app/conf/main.ini')
        #database section
        user      = config.get('database', 'user')
        password  = config.get('database', 'password')
        database  = config.get('database', 'database')
        host      = config.get('database', 'host')
        # telegram bot section
        token     = config.get('bot', 'token')
    except:
        logger.error('Configure file error')
        sys.exit()

    # Create the EventHandler and pass it your bot's token.
    updater = Updater(token)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    cakesBot = CakesBot(updater=updater, user=user, password=password, database=database, host=host)

    # on different commands - answer in Telegram
    dp.addTelegramCommandHandler("start",  cakesBot.start)
    dp.addTelegramCommandHandler("help",   cakesBot.help)
    dp.addTelegramCommandHandler("random", cakesBot.random)
    dp.addTelegramCommandHandler("last",   cakesBot.last)
    dp.addTelegramCommandHandler("about",  cakesBot.about)
    dp.addTelegramInlineHandler(cakesBot.inline_search)
    # unknow telegram command handler
    dp.addUnknownTelegramCommandHandler(cakesBot.unknow_command)

    # Command line interface
    dp.addUnknownStringCommandHandler(cakesBot.cli_unknow_command)

    # log all errors
    dp.addErrorHandler(cakesBot.error)

    # start the bot
    cakesBot.idle()

if __name__ == '__main__':
    main()