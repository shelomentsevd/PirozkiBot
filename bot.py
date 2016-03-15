# -*- coding: utf-8 -*-
from telegram import Updater
import logging
import ConfigParser as cp
from app.database import Database
from signal import signal, SIGINT, SIGTERM, SIGABRT

# Enable logging
logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO)

logger = logging.getLogger(__name__)

class CakesBot:
    __help = '''
Доступные команды:
    /last - присылает пять последних пирожков
    /random - присылает вам случайный пирожок, если после /random написать несколько слов, вы получите случайный пирожок содержащий эти слова
    /help  - выводит эту справку
    /about - выводит информацию о боте
    
    вы можете проголосовать за бота по ссылке:
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

    def random(self, bot, update):
        self.__message_info(update.message)
        text = update.message.text
        word = ' '.join(text.split(' ')[1:])
        poem = ''

        if len(word):
            poem = self.__db.randomByWord(word)
        else:
            poem = self.__db.random()

        bot.sendMessage(update.message.chat_id, text=poem)

    def search(self, bot, update):
        self.__message_info(update.message)
        bot.sendMessage(update.message.chat_id, text='Извините, этот метод пока что не работает')

    def last(self, bot, update):
        self.__message_info(update.message)
        poem = self.__db.last(5)
        bot.sendMessage(update.message.chat_id, text=poem)

    def about(self, bot, update):
        self.__message_info(update.message)
        bot.sendMessage(update.message.chat_id, text=self.__about % self.__db.count())
    
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
    dp.addTelegramCommandHandler("search", cakesBot.random)
    dp.addTelegramCommandHandler("last",   cakesBot.last)
    dp.addTelegramCommandHandler("about",  cakesBot.about)

    # unknow telegram command handler
    dp.addUnknownTelegramCommandHandler(cakesBot.unknow_command)

    # Command line interface
    dp.addUnknownStringCommandHandler(cakesBot.cli_unknow_command)

    # on noncommand i.e message - echo the message on Telegram
    dp.addTelegramMessageHandler(cakesBot.help)

    # log all errors
    dp.addErrorHandler(cakesBot.error)

    # start the bot
    cakesBot.idle()

if __name__ == '__main__':
    main()