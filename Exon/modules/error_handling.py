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
import io
import random
import sys
import traceback

import pretty_errors
import requests
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackContext, CommandHandler

from Exon import DEV_USERS, ERROR_LOGS, dispatcher

pretty_errors.mono()


class ErrorsDict(dict):
    "ᴀ ᴄᴜsᴛᴏᴍ ᴅɪᴄᴛ to sᴛᴏʀᴇ ᴇʀʀᴏʀs ᴀɴᴅ ᴛʜᴇɪʀ ᴄᴏᴜɴᴛ"

    def __init__(self, *args, **kwargs):
        self.raw = []
        super().__init__(*args, **kwargs)

    def __contains__(self, error):
        self.raw.append(error)
        error.identifier = "".join(random.choices("ABCDEFGHIJKLMNOPQRSTUVWXYZ", k=5))
        for e in self:
            if type(e) is type(error) and e.args == error.args:
                self[e] += 1
                return True
        self[error] = 0
        return False

    def __len__(self):
        return len(self.raw)


errors = ErrorsDict()


def error_callback(update: Update, context: CallbackContext):
    if not update:
        return
    if context.error in errors:
        return
    try:
        stringio = io.StringIO()
        pretty_errors.output_stderr = stringio
        output = pretty_errors.excepthook(
            type(context.error),
            context.error,
            context.error.__traceback__,
        )
        pretty_errors.output_stderr = sys.stderr
        pretty_error = stringio.getvalue()
        stringio.close()
    except:
        pretty_error = "ғᴀɪʟᴇᴅ ᴛᴏ ᴄʀᴇᴀᴛᴇ ᴘʀᴇᴛᴛʏ ᴇʀʀᴏʀ."
    tb_list = traceback.format_exception(
        None,
        context.error,
        context.error.__traceback__,
    )
    tb = "".join(tb_list)
    pretty_message = f'{pretty_error}\n-------------------------------------------------------------------------------\nAn exception was raised while handling an update\nUser: {update.effective_user.id}\nChat: {update.effective_chat.title if update.effective_chat else ""} {update.effective_chat.id if update.effective_chat else ""}\nCallback data: {update.callback_query.data if update.callback_query else "None"}\nMessage: {update.effective_message.text if update.effective_message else "No message"}\n\nFull Traceback: {tb}'

    key = requests.post(
        "https://hastebin.com/documents",
        data=pretty_message.encode("UTF-8"),
    ).json()
    e = html.escape(f"{context.error}")
    if not key.get("key"):
        with open("error.txt", "w+") as f:
            f.write(pretty_message)
        context.bot.send_document(
            ERROR_LOGS,
            open("error.txt", "rb"),
            caption=f"#{context.error.identifier}\n<b>An unknown error occured:</b>\n<code>{e}</code>",
            parse_mode="html",
        )
        return
    key = key.get("key")
    url = f"https://hastebin.com/{key}"
    context.bot.send_message(
        ERROR_LOGS,
        text=f"#{context.error.identifier}\n<b>An unknown error occured:</b>\n<code>{e}</code>",
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("ʜᴀsᴛᴇʙɪɴ", url=url)]],
        ),
        parse_mode="html",
    )


def list_errors(update: Update, context: CallbackContext):
    if update.effective_user.id not in DEV_USERS:
        return
    e = dict(sorted(errors.items(), key=lambda item: item[1], reverse=True))
    msg = "<b>ᴇʀʀᴏʀs ʟɪsᴛ:</b>\n"
    for x, value in e.items():
        msg += f"• <code>{x}:</code> <b>{value}</b> #{x.identifier}\n"
    msg += f"{len(errors)} ʜᴀᴠᴇ ᴏᴄᴄᴜʀʀᴇᴅ sɪɴᴄᴇ sᴛᴀʀᴛᴜᴘ."
    if len(msg) > 4096:
        with open("errors_msg.txt", "w+") as f:
            f.write(msg)
        context.bot.send_document(
            update.effective_chat.id,
            open("errors_msg.txt", "rb"),
            caption="ᴛᴏᴏ ᴍᴀɴʏ ᴇʀʀᴏʀs ʜᴀᴠᴇ ᴏᴄᴄᴜʀᴇᴅ..",
            parse_mode="html",
        )
        return
    update.effective_message.reply_text(msg, parse_mode="html")


dispatcher.add_error_handler(error_callback)
dispatcher.add_handler(CommandHandler("errors", list_errors))
