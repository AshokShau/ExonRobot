"""
MIT License

Copyright (c) 2022 Aʙɪsʜɴᴏɪ

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

# ""DEAR PRO PEOPLE,  DON'T REMOVE & CHANGE THIS LINE
# TG :- @Abishnoi1M
#     MY ALL BOTS :- Abishnoi_bots
#     GITHUB :- KingAbishnoi ""


from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode, Update
from telegram.ext import CallbackContext, CallbackQueryHandler, CommandHandler
from telegram.utils.helpers import mention_html

from Exon import dispatcher
from Exon.modules.helper_funcs.chat_status import user_admin, user_admin_no_reply
from Exon.modules.log_channel import loggable

bot_name = f"{dispatcher.bot.first_name}"

from pymongo import MongoClient

from Exon import MONGO_DB_URL

worddb = MongoClient(MONGO_DB_URL)
k = worddb["ExonKarma"]["karma_status"]


@user_admin_no_reply
def karmaadd(update: Update, context: CallbackContext):
    query = update.callback_query
    context.bot
    user = update.effective_user
    if query.data == "add_karma":
        chat = update.effective_chat
        done = k.insert_one({"chat_id": chat.id})
        update.effective_message.edit_text(
            f"{bot_name} ᴋᴀʀᴍᴀ sʏsᴛᴇᴍ ᴅɪsᴀʙʟᴇᴅ ʙʏ  {mention_html(user.id, user.first_name)}.",
            parse_mode=ParseMode.HTML,
        )


@user_admin_no_reply
def karmarem(update: Update, context: CallbackContext):
    query = update.callback_query
    context.bot
    user = update.effective_user
    if query.data == "rem_karma":
        chat = update.effective_chat
        done = k.delete_one({"chat_id": chat.id})
        update.effective_message.edit_text(
            f"{bot_name} ᴋᴀʀᴍᴀ sʏsᴛᴇᴍ ᴇɴᴀʙʟᴇᴅ ʙʏ {mention_html(user.id, user.first_name)}.",
            parse_mode=ParseMode.HTML,
        )


@user_admin
@loggable
def karma_toggle(update: Update, context: CallbackContext):
    message = update.effective_message
    chat = update.effective_chat
    is_chatbot = k.find_one({"chat_id": chat.id})
    if is_chatbot:
        msg = "ᴋᴀʀᴍᴀ ᴛᴏɢɢʟᴇ\nᴍᴏᴅᴇ : DISABLE"
        keyboard = InlineKeyboardMarkup(
            [[InlineKeyboardButton(text="ᴇɴᴀʙʟᴇ", callback_data=r"rem_karma")]]
        )
        message.reply_text(
            msg,
            reply_markup=keyboard,
            parse_mode=ParseMode.HTML,
        )
    if not is_chatbot:
        msg = "Karma Toggle\n Mode : ENABLE"
        keyboard = InlineKeyboardMarkup(
            [[InlineKeyboardButton(text="ᴅɪsᴀʙʟᴇ", callback_data=r"add_karma")]]
        )
        message.reply_text(
            msg,
            reply_markup=keyboard,
            parse_mode=ParseMode.HTML,
        )


KARMA_STATUS_HANDLER = CommandHandler("karma", karma_toggle, run_async=True)
ADD_KARMA_HANDLER = CallbackQueryHandler(karmaadd, pattern=r"add_karma", run_async=True)
RM_KARMA_HANDLER = CallbackQueryHandler(karmarem, pattern=r"rem_karma", run_async=True)

dispatcher.add_handler(ADD_KARMA_HANDLER)
dispatcher.add_handler(KARMA_STATUS_HANDLER)
dispatcher.add_handler(RM_KARMA_HANDLER)

__handlers__ = [
    ADD_KARMA_HANDLER,
    KARMA_STATUS_HANDLER,
    RM_KARMA_HANDLER,
]
