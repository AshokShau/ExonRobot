"""
MIT License

Copyright (c) 2022  Aʙɪsʜɴᴏɪ

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

import os
from time import sleep

from telegram import Update
from telegram.error import BadRequest, RetryAfter, Unauthorized
from telegram.ext import CallbackContext, CommandHandler, Filters

from Exon import OWNER_ID, dispatcher
from Exon.modules.helper_funcs.extraction import extract_user
from Exon.modules.sql.users_sql import get_user_com_chats


def get_user_common_chats(update: Update, context: CallbackContext):
    bot, args = context.bot, context.args
    msg = update.effective_message
    user = extract_user(msg, args)
    if not user:
        msg.reply_text("I sʜᴀʀᴇ ɴᴏ ᴄᴏᴍᴍᴏɴ ᴄʜᴀᴛs ᴡɪᴛʜ ᴛʜᴇ ᴠᴏɪᴅ.")
        return
    common_list = get_user_com_chats(user)
    if not common_list:
        msg.reply_text("ɴᴏ ᴄᴏᴍᴍᴏɴ ᴄʜᴀᴛs ᴡɪᴛʜ ᴛʜɪs ᴜsᴇʀ!")
        return
    name = bot.get_chat(user).first_name
    text = f"<b>ᴄᴏᴍᴍᴏɴ ᴄʜᴀᴛs ᴡɪᴛʜ {name}</b>\n\n"
    for chat in common_list:
        try:
            chat_name = bot.get_chat(chat).title
            sleep(0.3)
            text += f"• <code>{chat_name}</code>\n"
        except (BadRequest, Unauthorized):
            pass
        except RetryAfter as e:
            sleep(e.retry_after)

    if len(text) < 4096:
        msg.reply_text(text, parse_mode="HTML")
    else:
        with open("common_chats.txt", "w") as f:
            f.write(text)
        with open("common_chats.txt", "rb") as f:
            msg.reply_document(f)
        os.remove("common_chats.txt")


COMMON_CHATS_HANDLER = CommandHandler(
    "getchats",
    get_user_common_chats,
    filters=Filters.user(OWNER_ID),
    run_async=True,
)

dispatcher.add_handler(COMMON_CHATS_HANDLER)
