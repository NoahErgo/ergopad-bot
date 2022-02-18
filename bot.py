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
    "faq": """
You can read the FAQ <a href=\"https://ergopad.io/faq\">here</a> ❓
""",
    "report": """
Please be aware that we will never ask for private keys over DM.
Report any suspicious activity to an admin. If you need assistance, we are able to help by checking your public wallet address.
Keep your private keys private and never share them with anyone 🚨
""",
    "refund": """
If your transaction stuck and you have to refund your Transaction, make sure to watch our tutorial on Youtube in which Marty explains how to make a Refund.

https://www.youtube.com/watch?v=OTcCNNCnS4Q
""",
    "socials": """
<b>Ergopad socials:</b>
→ <a href=\"https://ergopad.io\">Website</a>
→ <a href=\"https://github.com/ergo-pad/ergopad/blob/dev/docs/README.md\">Whitepaper</a>
→ <a href=\"https://twitter.com/ErgoPadOfficial\">Twitter</a>
→ <a href=\"https://github.com/ergo-pad\">Github</a>
→ <a href=\"https://discord.com/invite/E8cHp6ThuZ\">Discord</a>
""",
    "welcome": """
Hello and welcome to the Ergopad community! 🥳  ErgoPad is a project incubator offering token IDOs which provide funding for new projects within the Ergo ecosystem.
Ergopad will release its own native token through an IDO and users will be able to trade Ergo or SigUSD for these tokens and stake them through smart contracts.
<b>Ergopad socials:</b>
→ <a href="https://ergopad.io">Website</a>
→ <a href="https://github.com/ergo-pad/ergopad/blob/dev/docs/README.md">Whitepaper</a>
→ <a href="https://twitter.com/ErgoPadOfficial">Twitter</a>
→ <a href="https://github.com/ergo-pad">Github</a>
→ <a href="https://discord.com/invite/E8cHp6ThuZ">Discord</a>    
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
        res = requests.get(f"{API}/asset/price/ergopad", verify=False)
        price = round(res.json()["price"], 4)
        bot.send_message(
            message.chat.id, f"$ERGOPAD trading at ${price} USD")
        price_last_timestamps[message.chat.id] = time.time()
    except Exception as e:
        bot.reply_to(message, "Sorry cannot get price data from ergopad api.")
        print(e)


@bot.message_handler(commands=["faq"])
def faq(message):
    bot.send_message(
        message.chat.id, messages["faq"], parse_mode="html")


@bot.message_handler(commands=["report"])
def report(message):
    bot.send_message(
        message.chat.id, messages["report"], parse_mode="html")


@bot.message_handler(commands=["refund"])
def refund(message):
    bot.send_message(message.chat.id, messages["refund"])


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
