"""
MIT License

Copyright (c) 2022 ABISHNOI69

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
# TG :- @Abishnoi1m
#     UPDATE   :- Abishnoi_bots
#     GITHUB :- ABISHNOI69 ""

import html
import re

from telegram import ParseMode
from telegram.ext import ChatJoinRequestHandler
from telegram.ext.callbackcontext import CallbackContext
from telegram.inline.inlinekeyboardbutton import InlineKeyboardButton
from telegram.inline.inlinekeyboardmarkup import InlineKeyboardMarkup
from telegram.update import Update
from telegram.utils.helpers import mention_html

from Exon import dispatcher
from Exon.modules.helper_funcs.chat_status import bot_admin, user_can_restrict_no_reply
from Exon.modules.helper_funcs.decorators import Exoncallback
from Exon.modules.log_channel import loggable


def chat_join_req(upd: Update, ctx: CallbackContext):
    bot = ctx.bot
    user = upd.chat_join_request.from_user
    chat = upd.chat_join_request.chat
    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "ᴀᴘᴘʀᴏᴠᴇ", callback_data="cb_approve={}".format(user.id)
                ),
                InlineKeyboardButton(
                    "ᴅᴇᴄʟɪɴᴇ", callback_data="cb_decline={}".format(user.id)
                ),
            ]
        ]
    )
    bot.send_message(
        chat.id,
        "{} ᴡᴀɴᴛs ᴛᴏ ᴊᴏɪɴ {}".format(
            mention_html(user.id, user.first_name), chat.title or "this chat"
        ),
        reply_markup=keyboard,
        parse_mode=ParseMode.HTML,
    )


@Exoncallback(pattern=r"cb_approve=")
@user_can_restrict_no_reply
@bot_admin
@loggable
def approve_joinreq(update: Update, context: CallbackContext) -> str:
    bot = context.bot
    query = update.callback_query
    user = update.effective_user
    chat = update.effective_chat
    match = re.match(r"cb_approve=(.+)", query.data)

    user_id = match.group(1)
    try:
        bot.approve_chat_join_request(chat.id, user_id)
        update.effective_message.edit_text(
            f"ᴊᴏɪɴ ʀᴇǫᴜᴇsᴛ ᴀᴘᴘʀᴏᴠᴇᴅ ʙʏ {mention_html(user.id, user.first_name)}.",
            parse_mode="HTML",
        )
        logmsg = (
            f"<b>{html.escape(chat.title)}:</b>\n"
            f"#𝐉𝐎𝐈𝐍_𝐑𝐄𝐐𝐔𝐄𝐒𝐓\n"
            f"ᴀᴘᴘʀᴏᴠᴇᴅ\n"
            f"<b>ᴀᴅᴍɪɴ:</b> {mention_html(user.id, html.escape(user.first_name))}\n"
            f"<b>ᴜsᴇʀ:</b> {mention_html(user_id, html.escape(user.first_name))}\n"
        )
        return logmsg
    except Exception as e:
        update.effective_message.edit_text(str(e))


@Exoncallback(pattern=r"cb_decline=")
@user_can_restrict_no_reply
@bot_admin
@loggable
def decline_joinreq(update: Update, context: CallbackContext) -> str:
    bot = context.bot
    query = update.callback_query
    user = update.effective_user
    chat = update.effective_chat
    match = re.match(r"cb_decline=(.+)", query.data)

    user_id = match.group(1)
    try:
        bot.decline_chat_join_request(chat.id, user_id)
        update.effective_message.edit_text(
            f"ᴊᴏɪɴ ʀᴇǫᴜᴇsᴛ ᴅᴇᴄʟɪɴᴇᴅ ʙʏ {mention_html(user.id, user.first_name)}.",
            parse_mode="HTML",
        )
        logmsg = (
            f"<b>{html.escape(chat.title)}:</b>\n"
            f"#𝐉𝐎𝐈𝐍_𝐑𝐄𝐐𝐔𝐄𝐒𝐓\n"
            f"ᴅᴇᴄʟɪɴᴇᴅ\n"
            f"<b>ᴀᴅᴍɪɴ:</b> {mention_html(user.id, html.escape(user.first_name))}\n"
            f"<b>ᴜsᴇʀ:</b> {mention_html(user_id, html.escape(user.first_name))}\n"
        )
        return logmsg
    except Exception as e:
        update.effective_message.edit_text(str(e))


dispatcher.add_handler(ChatJoinRequestHandler(callback=chat_join_req, run_async=True))
