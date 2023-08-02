from pyrogram import enums
from telegram.ext import CommandHandler
#from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from bot import bot, LOGGER, dispatcher
from bot.helper.telegram_helper.message_utils import *
from bot.helper.telegram_helper.filters import CustomFilters
from bot.helper.telegram_helper.bot_commands import BotCommands
#from bot.helper.telegram_helper.button_build import ButtonMaker
#from bot.helper.ext_utils.db_handler import DbManger
from bot.modules.datas import db

def short_set(update, context):
    user_id_ = update.message.from_user.id 
    u_men = update.message.from_user.first_name

    if (BotCommands.ShortCommand in update.message.text) and (len(update.message.text.split(' ')) == 1):
        help_msg = "<b>Send This Format👇\n/short kpslink.in 82e88df80123f4812e90568e781566e836ffde3e</b>"
        sendMessage(help_msg, context.bot, update.message)
    else:
        lm = sendMessage(f"<b>Please Wait....Processing🤖</b>", context.bot, update.message)
        pre_send = update.message.text.split(" ", maxsplit=1)
        reply_to = update.message.reply_to_message
        if len(pre_send) > 1:
            txt = pre_send[1]
        elif reply_to is not None:
            txt = reply_to.text
        else:
            txt = ""
        data = txt
        print(data)
        db.update_shortner(user_id_,data)
        saved_user = db.shortner(user_id_)
        LOGGER.info(f"User : {user_id_} Shortener is Saved in DB")
        editMessage(f"<u><b><a href='tg://user?id={user_id_}'>{u_men}</a>'s is Shortener Set Successfully 🚀</b></u>\n\n<b>• info: {saved_user}</b>", lm)
      

short_set_handler = CommandHandler(BotCommands.ShortCommand, short_set,
                                       filters=(CustomFilters.authorized_chat | CustomFilters.authorized_user), run_async=True)

dispatcher.add_handler(short_set_handler)
