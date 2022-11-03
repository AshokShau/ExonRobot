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

import asyncio
import os
import re
import subprocess
import sys
from statistics import mean
from time import monotonic as time
from time import sleep

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, TelegramError, Update
from telegram.ext import CallbackContext, CommandHandler
from telegram.ext.callbackqueryhandler import CallbackQueryHandler
from telethon import events

from Exon import DEV_USERS, OWNER_ID, dispatcher, telethn
from Exon.modules.helper_funcs.chat_status import dev_plus


def leave_cb(update: Update, context: CallbackContext):
    bot = context.bot
    callback = update.callback_query
    if callback.from_user.id not in DEV_USERS:
        callback.answer(text="ᴛʜɪs ɪsɴ'ᴛ ғᴏʀ ʏᴏᴜ", show_alert=True)
        return

    match = re.match(r"leavechat_cb_\((.+?)\)", callback.data)
    chat = int(match[1])
    bot.leave_chat(chat_id=chat)
    callback.answer(text="ʟᴇғᴛ ᴄʜᴀᴛ")


@dev_plus
def allow_groups(update: Update, context: CallbackContext):
    args = context.args
    if not args:
        state = "off" if Exon.ALLOW_CHATS else "ʟᴏᴄᴋᴅᴏᴡɴ ɪs " + "on"
        update.effective_message.reply_text(f"ᴄᴜʀʀᴇɴᴛ sᴛᴀᴛᴇ: {state}")
        ʀᴇᴛᴜʀɴ
    if args[0].lower() in ["off", "no"]:
        Exon.ALLOW_CHATS = True
    elif args[0].lower() in ["yes", "on"]:
        Exon.ALLOW_CHATS = False
    else:
        update.effective_message.reply_text("ғᴏʀᴍᴀᴛ: /lockdown Yes/No ᴏʀ Off/On")
        return
    update.effective_message.reply_text("ᴅᴏɴᴇ! ʟᴏᴄᴋᴅᴏᴡɴ ᴠᴀʟᴜᴇ ᴛᴏɢɢʟᴇᴅ.")


class Store:
    def __init__(self, func):
        self.func = func
        self.calls = []
        self.time = time()
        self.lock = asyncio.Lock()

    def average(self):
        return round(mean(self.calls), 2) if self.calls else 0

    def __repr__(self):
        return f"<Store func={self.func.__name__}, average={self.average()}>"

    async def __call__(self, event):
        async with self.lock:
            if not self.calls:
                self.calls = [0]
            if time() - self.time > 1:
                self.time = time()
                self.calls.append(1)
            else:
                self.calls[-1] += 1
        await self.func(event)


async def nothing(event):
    pass


messages = Store(nothing)
inline_queries = Store(nothing)
callback_queries = Store(nothing)

telethn.add_event_handler(messages, events.NewMessage())
telethn.add_event_handler(inline_queries, events.InlineQuery())
telethn.add_event_handler(callback_queries, events.CallbackQuery())


@telethn.on(events.NewMessage(pattern=r"/getstats", from_users=OWNER_ID))
async def getstats(event):
    await event.reply(
        f"**__ᴇᴠᴇɴᴛ sᴛᴀᴛɪsᴛɪᴄs__**\n**ᴀᴠᴇʀᴀɢᴇ ᴍᴇssᴀɢᴇs:** {messages.average()}/s\n**ᴀᴠᴇʀᴀɢᴇ ᴄᴀʟʟʙᴀᴄᴋ ǫᴜᴇʀɪᴇs:** {callback_queries.average()}/s\n**ᴀᴠᴇʀᴀɢᴇ ɪɴʟɪɴᴇ ǫᴜᴇʀɪᴇs:** {inline_queries.average()}/s",
        parse_mode="md",
    )


@dev_plus
def pip_install(update: Update, context: CallbackContext):
    message = update.effective_message
    args = context.args
    if not args:
        message.reply_text("ᴇɴᴛᴇʀ ᴀ ᴘᴀᴄᴋᴀɢᴇ ɴᴀᴍᴇ.")
        return
    if len(args) >= 1:
        cmd = f"py -m pip install {' '.join(args)}"
        process = subprocess.Popen(
            cmd.split(" "),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=True,
        )
        stdout, stderr = process.communicate()
        reply = ""
        stderr = stderr.decode()
        if stdout := stdout.decode():
            reply += f"*sᴛᴅᴏᴜᴛ*\n`{stdout}`\n"
        if stderr:
            reply += f"*sᴛᴅᴇʀʀ*\n`{stderr}`\n"

        message.reply_text(text=reply, parse_mode=ParseMode.MARKDOWN)


@dev_plus
def leave(update: Update, context: CallbackContext):
    bot = context.bot
    if args := context.args:
        chat_id = str(args[0])
        leave_msg = " ".join(args[1:])
        try:
            context.bot.send_message(chat_id, leave_msg)
            bot.leave_chat(int(chat_id))
            update.effective_message.reply_text("ʟᴇғᴛ ᴄʜᴀᴛ.")
        except TelegramError:
            update.effective_message.reply_text("ғᴀɪʟᴇᴅ ᴛᴏ ʟᴇᴀᴠᴇ ᴄʜᴀᴛ ғᴏʀ sᴏᴍᴇ ʀᴇᴀsᴏɴ.")
    else:
        chat = update.effective_chat
        # user = update.effective_user
        Exon_leave_bt = [
            [
                InlineKeyboardButton(
                    text="ɪ ᴀᴍ sᴜʀᴇ ᴏғ ᴛʜɪs ᴀᴄᴛɪᴏɴ.",
                    callback_data=f"leavechat_cb_({chat.id})",
                )
            ]
        ]

        update.effective_message.reply_text(
            f"I'm ɢᴏɪɴɢ ᴛᴏ ʟᴇᴀᴠᴇ {chat.title}, ᴘʀᴇss ᴛʜᴇ ʙᴜᴛᴛᴏɴ ʙᴇʟᴏᴡ ᴛᴏ ᴄᴏɴғɪʀᴍ",
            reply_markup=InlineKeyboardMarkup(Exon_leave_bt),
        )


@dev_plus
def gitpull(update: Update, context: CallbackContext):
    sent_msg = update.effective_message.reply_text(
        "ᴘᴜʟʟɪɴɢ ᴀʟʟ ᴄʜᴀɴɢᴇs ғʀᴏᴍ ʀᴇᴍᴏᴛᴇ ᴀɴᴅ ᴛʜᴇɴ ᴀᴛᴛᴇᴍᴘᴛɪɴɢ ᴛᴏ ʀᴇsᴛᴀʀᴛ."
    )
    subprocess.Popen("git pull", stdout=subprocess.PIPE, shell=True)

    sent_msg_text = sent_msg.text + "\n\nᴄʜᴀɴɢᴇs ᴘᴜʟʟᴇᴅ...I ɢᴜᴇss.. ʀᴇsᴛᴀʀᴛɪɴɢ ɪɴ "

    for i in reversed(range(5)):
        sent_msg.edit_text(sent_msg_text + str(i + 1))
        sleep(1)

    sent_msg.edit_text("ʀᴇsᴛᴀʀᴛᴇᴅ..")

    os.system("restart.bat")
    os.execv("start.bat", sys.argv)


@dev_plus
def restart(update: Update, context: CallbackContext):
    update.effective_message.reply_text("ᴇxɪᴛɪɴɢ ᴀʟʟ ᴀʟʟ ᴀɴᴅ sᴛᴀʀᴛɪɴɢ ᴀ ɴᴇᴡ ɪɴsᴛᴀɴᴄᴇ!")
    process = subprocess.run("pkill python3 && python3 -m Exon", shell=True, check=True)
    process.communicate()


PIP_INSTALL_HANDLER = CommandHandler("install", pip_install, run_async=True)
LEAVE_HANDLER = CommandHandler("leave", leave, run_async=True)
GITPULL_HANDLER = CommandHandler("gitpull", gitpull, run_async=True)
RESTART_HANDLER = CommandHandler("reboot", restart, run_async=True)
ALLOWGROUPS_HANDLER = CommandHandler("lockdown", allow_groups, run_async=True)
LEAVE_CALLBACK_HANDLER = CallbackQueryHandler(
    leave_cb, pattern=r"leavechat_cb_", run_async=True
)

dispatcher.add_handler(PIP_INSTALL_HANDLER)
dispatcher.add_handler(ALLOWGROUPS_HANDLER)
dispatcher.add_handler(LEAVE_HANDLER)
dispatcher.add_handler(GITPULL_HANDLER)
dispatcher.add_handler(RESTART_HANDLER)
dispatcher.add_handler(LEAVE_CALLBACK_HANDLER)

__mod_name__ = "𝙳ᴇᴠ"
__handlers__ = [
    LEAVE_HANDLER,
    GITPULL_HANDLER,
    RESTART_HANDLER,
    ALLOWGROUPS_HANDLER,
    LEAVE_CALLBACK_HANDLER,
    PIP_INSTALL_HANDLER,
]
