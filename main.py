import telebot
import schedule
import time
import datetime
import sys
import logging
import copy
from dotenv import load_dotenv
import os
import configs.config as config

week = None

load_dotenv()
TOKEN = os.getenv('TOKEN', "")
CHAT_ID = os.getenv('CHAT_ID', "")
ADMIN_ID = os.getenv('ADMIN_ID', "")

# setting up logger
logger = logging.getLogger("link_bot")
logger.setLevel(level=logging.DEBUG)

handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(message)s')
handler.setFormatter(formatter)

logger.addHandler(handler)

def send_message(bot: telebot.TeleBot, chat_id: str, text: str) -> None:
    """
        Sends message to chat with id chat_id

        @param bot: telebot.TeleBot - bot instance
        @param chat_id: str - chat id
        @param text: str - text to send
    """
    success = False
    while not success:
        try:
            bot.send_message(chat_id, text)
            success = True
        except Exception as e:
            logger.error(f"[{datetime.datetime.now()}] [ERROR] Error sending message: {e}")
            time.sleep(10)

def ask_week(bot: telebot.TeleBot, chat_id: str) -> int:
    """
        Asks admin to select week

        @param bot: telebot.TeleBot - bot instance
        @param chat_id: str - chat id

        @return week_container: int - selected week
    """
    week_container = 0
    start_time = time.time()
    
    @bot.message_handler(func=lambda message: True)
    def recieve_message(message):
        nonlocal week_container
        if message.chat.id == int(chat_id) and  message.date > start_time:
            if message.text == "1" or message.text == "2":
                week_container = int(message.text)
                bot.stop_polling()
    
    send_message(bot, chat_id, "Select week (1 or 2)")
    bot.polling()
    send_message(bot, chat_id, f"Week selected")
    return week_container
    
            
def send(bot: telebot.TeleBot, day: int, pair: int) -> None:
    """
        Sends message to chat by week, day and pair

        @param bot: telebot.TeleBot - bot instance
        @param week: int - week number
        @param day: int - day number
        @param pair: int - pair number
    """
    global week
    pair_text = config.pairs[week-1][day-1][pair-1]
    if pair_text != "":
        send_message(bot, CHAT_ID, f"Тиждень: {week}, День: {day}, Пара: {pair}\n\n{pair_text}")
        logger.info(f"[{datetime.datetime.now()}] [INFO] Sent week: {week}, day: {day}, pair: {pair}")
    else:
        logger.info(f"[{datetime.datetime.now()}] [INFO] Empty pair week: {week}, day: {day}, pair: {pair}")

def check_config() -> bool:
    """
        Checks config.py for errors

        @return ret: bool - True if config is correct, False otherwise
    """
    ret = True
    if TOKEN == "" or TOKEN == None:
        logging.error(f"[{datetime.datetime.now()}] [ERROR] Token is empty")
        ret = False
    if CHAT_ID == "" or CHAT_ID == None:
        logger.error(f"[{datetime.datetime.now()}] [ERROR] Chat id is empty")
        ret = False
    if ADMIN_ID == "" or ADMIN_ID == None:
        logger.error(f"[{datetime.datetime.now()}] [ERROR] Admin id is empty")
        ret = False
    if config.time == []:
        logger.error(f"[{datetime.datetime.now()}] [ERROR] Time is empty")
        ret = False
    if config.pairs == []:
        logger.error(f"[{datetime.datetime.now()}] [ERROR] Pairs is empty")
        ret = False
    if len(config.pairs) != 2:
        logger.error(f"[{datetime.datetime.now()}] [ERROR] Inserted {len(config.pairs)} weeks, expected 2")
        ret = False
    if len(config.pairs[0]) != 6 or len(config.pairs[1]) != 6:
        logger.error(f"[{datetime.datetime.now()}] [ERROR] Inserted {len(config.pairs[0])} days, expected 6")
        ret = False
    for i in range(2):
        for j in range(6):
            if len(config.pairs[i][j]) != 5:
                logger.error(f"[{datetime.datetime.now()}] [ERROR] Inserted {len(config.pairs[i][j])} pairs, expected 5 (at week {i+1}, day {j+1})")
                ret = False
    return ret

def change_week() -> None:
    """
        Changes week
    """
    global week
    week = week % 2 + 1
    logger.info(f"[{datetime.datetime.now()}] [INFO] Week changed to {week}")    

# There starts main logic

# checking config
if not check_config():
    logger.info(f"[{datetime.datetime.now()}] [INFO] Shuting down...")
    sys.exit()
else:
    logger.info(f"[{datetime.datetime.now()}] [INFO] Config accepted")

# creating bot instance    
try:
    link_bot = telebot.TeleBot(TOKEN)
    logger.info(f"[{datetime.datetime.now()}] [INFO] Token accepted")
except:
    logger.error(f"[{datetime.datetime.now()}] [ERROR] Invalid token")
    logger.info(f"[{datetime.datetime.now()}] [INFO] Shuting down...")
    sys.exit()

# asking admin to select week
logger.info(f"[{datetime.datetime.now()}] [INFO] Waiting for admin to specify week...")
week = copy.deepcopy(ask_week(link_bot, ADMIN_ID))
logger.info(f"[{datetime.datetime.now()}] [INFO] Selected week: {week}")

# creating schedules    
try:
    for i, t in enumerate(config.time):
        schedule.every().monday.at(t).do(send, bot=link_bot, day=1, pair=i+1)
        schedule.every().tuesday.at(t).do(send, bot=link_bot, day=2, pair=i+1)
        schedule.every().wednesday.at(t).do(send, bot=link_bot, day=3, pair=i+1)
        schedule.every().thursday.at(t).do(send, bot=link_bot, day=4, pair=i+1)
        schedule.every().friday.at(t).do(send, bot=link_bot, day=5, pair=i+1)
        schedule.every().saturday.at(t).do(send, bot=link_bot, day=6, pair=i+1)
except Exception as e:
    logger.error(f"[{datetime.datetime.now()}] [ERROR] Creating schedules failed: {e}")
    logger.info(f"[{datetime.datetime.now()}] [INFO] Shuting down...")
    sys.exit()

# creating schedule for week changing    
schedule.every().monday.at("00:00").do(change_week)
    
logger.info(f"[{datetime.datetime.now()}] [INFO] Schedules created")
logger.info(f"[{datetime.datetime.now()}] [INFO] Bot started")

# main loop
while True:
    try:
        schedule.run_pending()
        time.sleep(1)
    except KeyboardInterrupt:
        logger.info(f"[{datetime.datetime.now()}] [INFO] Shuting down manually...")
        sys.exit()
    except Exception as e:
        logger.error(f"[{datetime.datetime.now()}] [ERROR] {e}")
        logger.info(f"[{datetime.datetime.now()}] [INFO] Shuting down with error...")
        sys.exit()