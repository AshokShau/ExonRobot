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

import html
import json
import re
from time import sleep

import requests
from telegram import (
    CallbackQuery,
    Chat,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ParseMode,
    Update,
    User,
)
from telegram.error import BadRequest, RetryAfter, Unauthorized
from telegram.ext import (
    CallbackContext,
    CallbackQueryHandler,
    CommandHandler,
    Filters,
    MessageHandler,
)
from telegram.utils.helpers import mention_html

import Exon.modules.sql.kuki_sql as sql
from Exon import dispatcher
from Exon.modules.helper_funcs.chat_status import user_admin, user_admin_no_reply
from Exon.modules.helper_funcs.filters import CustomFilters
from Exon.modules.log_channel import gloggable


@user_admin_no_reply
@gloggable
def kukirm(update: Update, context: CallbackContext) -> str:
    query: Optional[CallbackQuery] = update.callback_query
    user: Optional[User] = update.effective_user
    if match := re.match(r"rm_chat\((.+?)\)", query.data):
        user_id = match[1]
        chat: Optional[Chat] = update.effective_chat
        if is_kuki := sql.rem_kuki(chat.id):
            sql.rem_kuki(user_id)
            return (
                f"<b>{html.escape(chat.title)}:</b>\n"
                f"AI_ᴅɪsᴀʙʟᴇᴅ\n"
                f"<b>ᴀᴅᴍɪɴ:</b> {mention_html(user.id, html.escape(user.first_name))}\n"
            )
        else:
            query.answer("ᴄʜᴀᴛʙᴏᴛ ᴜɴᴀᴄᴛɪᴠᴇ")
            query.message.delete()

    return ""


@user_admin_no_reply
@gloggable
def kukiadd(update: Update, context: CallbackContext) -> str:
    query: Optional[CallbackQuery] = update.callback_query
    user: Optional[User] = update.effective_user
    if match := re.match(r"add_chat\((.+?)\)", query.data):
        user_id = match[1]
        chat: Optional[Chat] = update.effective_chat
        if is_kuki := sql.set_kuki(chat.id):
            sql.set_kuki(user_id)
            return (
                f"<b>{html.escape(chat.title)}:</b>\n"
                f"ᴀɪ_ᴇɴᴀʙʟᴇ\n"
                f"<b>ᴀᴅᴍɪɴ:</b> {mention_html(user.id, html.escape(user.first_name))}\n"
            )
        else:
            query.answer("ᴄʜᴀᴛʙᴏᴛ ᴀᴄᴛɪᴠᴇ")
            query.message.delete()

    return ""


@user_admin
@gloggable
def kuki(update: Update, context: CallbackContext):
    update.effective_user
    message = update.effective_message
    msg = "ᴄʜᴏᴏsᴇ ᴀɴ ᴏᴘᴛɪᴏɴ ʙᴀʙʏ "
    keyboard = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton(text="ᴇɴᴀʙʟᴇ", callback_data="add_chat({})")],
            [InlineKeyboardButton(text="ᴅɪsᴀʙʟᴇ", callback_data="rm_chat({})")],
        ]
    )
    message.reply_text(
        msg,
        reply_markup=keyboard,
        parse_mode=ParseMode.HTML,
    )


def kuki_message(context: CallbackContext, message):
    reply_message = message.reply_to_message
    if message.text.lower() == "Exon":
        return True
    if reply_message:
        if reply_message.from_user.id == context.bot.get_me().id:
            return True
    else:
        return False


def chatbot(update: Update, context: CallbackContext):
    message = update.effective_message
    chat_id = update.effective_chat.id
    bot = context.bot
    is_kuki = sql.is_kuki(chat_id)
    if not is_kuki:
        return

    if message.text and not message.document:
        if not kuki_message(context, message):
            return
        Message = message.text
        bot.send_chat_action(chat_id, action="typing")
        kukiurl = requests.get(
            f"https://kukiapi.xyz/api/apikey=5281955434-KUKIyq4NCB2Ca8/Himawari/@nekoarsh/message={Message}"
        )

        Kuki = json.loads(kukiurl.text)
        kuki = Kuki["reply"]
        sleep(0.3)
        message.reply_text(kuki, timeout=60)


def list_all_chats(update: Update, context: CallbackContext):
    chats = sql.get_all_kuki_chats()
    text = "<b>ᴋᴜᴋɪ-ᴇɴᴀʙʟᴇᴅ ᴄʜᴀᴛs</b>\n"
    for chat in chats:
        try:
            x = context.bot.get_chat(int(*chat))
            name = x.title or x.first_name
            text += f"• <code>{name}</code>\n"
        except (BadRequest, Unauthorized):
            sql.rem_kuki(*chat)
        except RetryAfter as e:
            sleep(e.retry_after)
    update.effective_message.reply_text(text, parse_mode="HTML")


__help__ = """
ᴄʜᴀᴛʙᴏᴛ ᴜᴛɪʟɪᴢᴇs ᴛʜᴇ ᴋᴜᴋɪ's API ᴡʜɪᴄʜ ᴀʟʟᴏᴡs ᴇxᴏɴ ᴛᴏ ᴛᴀʟᴋ ᴀɴᴅ ᴘʀᴏᴠɪᴅᴇ ᴀ ᴍᴏʀᴇ ɪɴᴛᴇʀᴀᴄᴛɪᴠᴇ ɢʀᴏᴜᴘ ᴄʜᴀᴛ ᴇxᴘᴇʀɪᴇɴᴄᴇ.
*ᴀᴅᴍɪɴs ᴏɴʟʏ ᴄᴏᴍᴍᴀɴᴅs*:

✪ /Chatbot*:* sʜᴏᴡs ᴄʜᴀᴛʙᴏᴛ ᴄᴏɴᴛʀᴏʟ ᴘᴀɴᴇʟ

"""

__mod_name__ = "𝙲ʜᴀᴛʙᴏᴛ"


CHATBOTK_HANDLER = CommandHandler("chatbot", kuki, run_async=True)
ADD_CHAT_HANDLER = CallbackQueryHandler(kukiadd, pattern=r"add_chat", run_async=True)
RM_CHAT_HANDLER = CallbackQueryHandler(kukirm, pattern=r"rm_chat", run_async=True)
CHATBOT_HANDLER = MessageHandler(
    Filters.text
    & (~Filters.regex(r"^#[^\s]+") & ~Filters.regex(r"^!") & ~Filters.regex(r"^\/")),
    chatbot,
    run_async=True,
)
LIST_ALL_CHATS_HANDLER = CommandHandler(
    "allchats", list_all_chats, filters=CustomFilters.dev_filter, run_async=True
)

dispatcher.add_handler(ADD_CHAT_HANDLER)
dispatcher.add_handler(CHATBOTK_HANDLER)
dispatcher.add_handler(RM_CHAT_HANDLER)
dispatcher.add_handler(LIST_ALL_CHATS_HANDLER)
dispatcher.add_handler(CHATBOT_HANDLER)

__handlers__ = [
    ADD_CHAT_HANDLER,
    CHATBOTK_HANDLER,
    RM_CHAT_HANDLER,
    LIST_ALL_CHATS_HANDLER,
    CHATBOT_HANDLER,
]
