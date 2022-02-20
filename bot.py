import os
import requests
import dotenv
import telebot
import time
import threading
from telebot import types

dotenv.load_dotenv()

messages = {
    "hello": "Hey, How's it going?",
    "docs": """
You can read the projects docs <a href=\"https://docs.anetabtc.io/docs/about-anetabtc/Introduction">here</a> ❓
""",
    "report": """
Please be aware that we will never ask for private keys over DM.
Report any suspicious activity to an admin. If you need assistance, we are able to help by checking your public wallet address.
Keep your private keys private and never share them with anyone 🚨
""",
    "socials": """
<b>anetaBTC socials:</b>
→ <a href=\"http://anetabtc.io/">Website</a>
→ <a href=\"https://medium.com/@anetaBTC/anetabtc-litepaper-v1-0-171f29b3276a">Litepaper</a>
→ <a href=\"https://twitter.com/anetaBTC">Twitter</a>
→ <a href=\"hhttps://github.com/anetabtc">Github</a>
→ <a href=\"https://discord.com/invite/anetabtc">Discord</a>
""",
    "welcome": """
Hello and welcome to the anetaBTC community! 🥳  anetaBTC is a decentralized, On Chain BTC protocol to unlock the value of Bitcoin on Ergo and Cardano.
<b>anetaBTC socials:</b>
→ <a href="http://anetabtc.io/">Website</a>
→ <a href="https://medium.com/@anetaBTC/anetabtc-litepaper-v1-0-171f29b3276a">Litepaper</a>
→ <a href="https://twitter.com/anetaBTC">Twitter</a>
→ <a href="https://github.com/anetabtc">Github</a>
→ <a href="https://discord.com/invite/anetabtc">Discord</a>    
""",
    "bot_love": """
Welcome fellow bot 🥰 😍, I am not sure you belong here though... 👀 👀.
"""
}

# constants
API = "https://ergopad.io/api"
TELEGRAM_API_KEY = os.getenv('TELEGRAM_API_KEY')

bot = telebot.TeleBot(TELEGRAM_API_KEY)


# class SyncMap:
#     def __init__(self):
#         self.mapp = {}
#         self.lock = threading.Lock()

#     def get(self, key):
#         self.lock.acquire()
#         if key in self.mapp:
#             self.lock.release()
#             return self.mapp[key]
#         self.lock.release()
#         return None

#     def set(self, key, value):
#         self.lock.acquire()
#         self.mapp[key] = value
#         self.lock.release()

#     def remove(self, key):
#         self.lock.acquire()
#         if key in self.mapp:
#             del self.mapp[key]
#         self.lock.release()


# unverified = SyncMap()


# @bot.message_handler(func=lambda m: True, content_types=['new_chat_members'])
# def on_user_joins(message):
#     global unverified
#     try:
#         markup = types.InlineKeyboardMarkup()
#         verify = types.InlineKeyboardButton(
#             text='Verify Human', callback_data=message.json["new_chat_member"]["id"])
#         markup.add(verify)
#         msg = bot.reply_to(message, messages['welcome'],
#                            parse_mode="html", disable_web_page_preview=True, reply_markup=markup)
#         unverified.set(message.json["new_chat_member"]["id"], {
#             "time": time.time(),
#             "message": msg,
#             "user": message.json["new_chat_member"],
#         })
#     except Exception as e:
#         print(e)


# @bot.callback_query_handler(func=None)
# def welcome_callback(call: types.CallbackQuery):
#     try:
#         key = call.from_user.id
#         msg = unverified.get(key)["message"]
#         verified = bot.delete_message(msg.chat.id, msg.id)
#         if verified:
#             unverified.remove(key)
#     except Exception as e:
#         print(e)
#     bot.answer_callback_query(callback_query_id=call.id, show_alert=False)


# cron for minute wise checkup
# def remove_unverified():
#     while True:
#         now = time.time()

#         unverified.lock.acquire()
#         keys = list(unverified.mapp.keys())
#         unverified.lock.release()
#         for key in keys:
#             data = unverified.get(key)
#             # 1 min older
#             if data["time"] + 60 < now:
#                 # unverfied user
#                 # 1. delete message
#                 msg = data["message"]
#                 usr = data["user"]
#                 try:
#                     bot.delete_message(msg.chat.id, msg.id)
#                 except Exception as e:
#                     print(e)
#                 # 2. send user is being removed
#                 try:
#                     name = usr["first_name"]
#                     bot.send_message(
#                         msg.chat.id, f"Banning {name}: verification failed")
#                 except Exception as e:
#                     print(e)
#                 # 3. ban user
#                 try:
#                     bot.ban_chat_member(msg.chat.id, usr["id"])
#                 except Exception as e:
#                     bot.send_message(
#                         msg.chat.id, "Could not ban member: insufficient priviledges")
#                     print(e)

#                 # remove key regardless
#                 unverified.remove(key)

#         time.sleep(60)


@bot.message_handler(commands=["start", "hello"])
def greet(message):
    bot.reply_to(message, messages["hello"])


price_last_timestamps = {}


@bot.message_handler(commands=["price"])
def price(message):
    try:
        bot.delete_message(message.chat.id, message.id)
        # 30 min cooldown
        if message.chat.id in price_last_timestamps and price_last_timestamps[message.chat.id] + 1800 > time.time():
            return
        res = requests.get(f"{API}/asset/price/neta", verify=False)
        price = round(res.json()["price"], 4)
        bot.send_message(
            message.chat.id, f"$NETA trading at ${price} USD")
        price_last_timestamps[message.chat.id] = time.time()
    except Exception as e:
        bot.reply_to(message, "Sorry cannot get price data from ergopad api.")
        print(e)


@bot.message_handler(commands=["docs"])
def faq(message):
    bot.send_message(
        message.chat.id, messages["docs"], parse_mode="html")


@bot.message_handler(commands=["report"])
def report(message):
    bot.send_message(
        message.chat.id, messages["report"], parse_mode="html")


@bot.message_handler(commands=["socials"])
def socials(message):
    bot.send_message(
        message.chat.id, messages["socials"], parse_mode="html", disable_web_page_preview=True)


def listener(messages):
    for m in messages:
        print(str(m))


# t = threading.Thread(target=remove_unverified)
# t.start()

bot.set_update_listener(listener)
bot.polling()

# t.join()
