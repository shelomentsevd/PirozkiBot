# -*- coding: utf-8 -*-
from telegram import Updater
import logging
import ConfigParser as cp
from app.database import Database

# Enable logging
logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO)

logger = logging.getLogger(__name__)

class CakesBot:
    def __init__(self, user, password, database, host):
        self.__db = Database(user=user, password=password, database=database, host=host)

    def start(self, bot, update):
        bot.sendMessage(update.message.chat_id, text='Hi!')

    def help(self, bot, update):
        bot.sendMessage(update.message.chat_id, text='''
Доступные команды:
    \\random - пришлёт вам случайный пирожок
    \\search [слово] - поиск по пирожкам
    \\help - выведет эту справку
            ''')

    def random(self, bot, update):
        poem = self.__db.random()
        bot.sendMessage(update.message.chat_id, text=poem)

    def search(self, bot, update):
        bot.sendMessage(update.message.chat_id, text='Извините, этот метод пока что не работает')        

    def echo(self, bot, update):
        logger.info('User id %s' % (update.message.chat_id))
        bot.sendMessage(update.message.chat_id, text=update.message.text)
    
    def error(self, bot, update, error):
        logger.warn('Update "%s" caused error "%s"' % (update, error))

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

    cakesBot = CakesBot(user=user, password=password, database=database, host=host)

    # on different commands - answer in Telegram
    dp.addTelegramCommandHandler("start",  cakesBot.start)
    dp.addTelegramCommandHandler("help",   cakesBot.help)
    dp.addTelegramCommandHandler("random", cakesBot.random)
    dp.addTelegramCommandHandler("search", cakesBot.search)

    # on noncommand i.e message - echo the message on Telegram
    dp.addTelegramMessageHandler(cakesBot.echo)

    # log all errors
    dp.addErrorHandler(cakesBot.error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until the you presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()

if __name__ == '__main__':
    main()