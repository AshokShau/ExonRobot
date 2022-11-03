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

import re
import time

from telegram import Update
from telegram.ext import CommandHandler
from telegram.ext.callbackcontext import CallbackContext
from telegram.ext.filters import Filters
from telegram.parsemode import ParseMode

from Exon import OWNER_ID, dispatcher, updater
from Exon.modules.disable import DisableAbleCommandHandler

job_queue = updater.job_queue


def get_time(time: str) -> int:
    if time[-1] == "s":
        return int(time[:-1])
    if time[-1] == "m":
        return int(time[:-1]) * 60
    if time[-1] == "h":
        return int(time[:-1]) * 3600
    if time[-1] == "d":
        return int(time[:-1]) * 86400


reminder_message = """
ʏᴏᴜʀ ʀᴇᴍɪɴᴅᴇʀ:
{reason}
<i>ᴡʜɪᴄʜ ʏᴏᴜ ᴛɪᴍᴇᴅ {time} ʙᴇғᴏʀᴇ ɪɴ {title}</i>
"""


def reminders(update: Update, context: CallbackContext):
    user = update.effective_user
    msg = update.effective_message
    jobs = list(job_queue.jobs())
    user_reminders = [job.name[1:] for job in jobs if job.name.endswith(str(user.id))]

    if not user_reminders:
        msg.reply_text(
            text="ʏᴏᴜ ᴅᴏɴ'ᴛ have ᴀɴʏ ʀᴇᴍɪɴᴅᴇʀs sᴇᴛ ᴏʀ ᴀʟʟ ᴛʜᴇ ʀᴇᴍɪɴᴅᴇʀs ʏᴏᴜ ʜᴀᴠᴇ set have ʙᴇᴇɴ ᴄᴏᴍᴘʟᴇᴛᴇᴅ",
            reply_to_message_id=msg.message_id,
        )
        return
    reply_text = "ʏᴏᴜʀ ʀᴇᴍɪɴᴅᴇʀs (<i>ᴍᴇɴᴛɪᴏɴᴇᴅ ʙᴇʟᴏᴡ ᴀʀᴇ ᴛʜᴇ <b>ᴛɪᴍsᴛᴀᴍᴘs</b> of the ʀᴇᴍɪɴᴅᴇʀs ʏᴏᴜ ʜᴀᴠᴇ sᴇᴛ</i>):\n"
    for i, u in enumerate(user_reminders):
        reply_text += f"\n{i+1}. <code>{u}</code>"
    msg.reply_text(
        text=reply_text, reply_to_message_id=msg.message_id, parse_mode=ParseMode.HTML
    )


def set_reminder(update: Update, context: CallbackContext):
    user = update.effective_user
    msg = update.effective_message
    chat = update.effective_chat
    reason = msg.text.split()
    if len(reason) == 1:
        msg.reply_text(
            "ɴᴏ ᴛɪᴍᴇ ᴀɴᴅ ʀᴇᴍɪɴᴅᴇʀ ᴛᴏ ᴍᴇɴᴛɪᴏɴ!", reply_to_message_id=msg.message_id
        )
        return
    if len(reason) == 2:
        msg.reply_text(
            "ɴᴏᴛʜɪɴɢ ᴛᴏ ʀᴇᴍɪɴᴅᴇʀ! ᴀᴅᴅ ᴀ ʀᴇᴍɪɴᴅᴇʀ", reply_to_message_id=msg.message_id
        )
        return
    t = reason[1].lower()
    if not re.match(r"[0-9]+(d|h|m|s)", t):
        msg.reply_text(
            "ᴜsᴇ ᴀ ᴄᴏʀʀᴇᴄᴛ ғᴏʀᴍᴀᴛ ᴏғ ᴛɪᴍᴇ!", reply_to_message_id=msg.message_id
        )
        return

    def job(context: CallbackContext):
        title = ""
        if chat.type == "private":
            title += "this chat"
        if chat.type != "private":
            title += chat.title
        context.bot.send_message(
            chat_id=user.id,
            text=reminder_message.format(
                reason=" ".join(reason[2:]), time=t, title=title
            ),
            disable_notification=False,
            parse_mode=ParseMode.HTML,
        )

    job_time = time.time()
    job_queue.run_once(
        callback=job, when=get_time(t), name=f"t{job_time}{user.id}".replace(".", "")
    )
    msg.reply_text(
        text="Your ʀᴇᴍɪɴᴅᴇʀ ʜᴀs ʙᴇᴇɴ sᴇᴛ ᴀғᴛᴇʀ {time} ғʀᴏᴍ ɴᴏᴡ!\nᴛɪᴍᴇsᴛᴀᴍᴘ: <code>{time_stamp}</code>".format(
            time=t, time_stamp=str(job_time).replace(".", "") + str(user.id)
        ),
        reply_to_message_id=msg.message_id,
        parse_mode=ParseMode.HTML,
    )


def clear_reminder(update: Update, context: CallbackContext):
    user = update.effective_user
    msg = update.effective_message
    text = msg.text.split()
    if len(text) == 1 or not re.match(r"[0-9]+", text[1]):
        msg.reply_text(
            text="ɴᴏ/ᴡʀᴏɴɢ ᴛɪᴍᴇsᴛᴀᴍᴘ ᴍᴇɴᴛɪᴏɴᴇᴅ", reply_to_message_id=msg.message_id
        )
        return
    if not text[1].endswith(str(user.id)):
        msg.reply_text(
            text="ᴛʜᴇ ᴛɪᴍᴇsᴛᴀᴍᴘ ᴍᴇɴᴛɪᴏɴᴇᴅ ɪs ɴᴏᴛ ʏᴏᴜʀ ʀᴇᴍɪɴᴅᴇʀ!",
            reply_to_message_id=msg.message_id,
        )
        return
    jobs = list(job_queue.get_jobs_by_name(f"t{text[1]}"))
    if not jobs:
        msg.reply_text(
            text="ᴛʜɪs ʀᴇᴍɪɴᴅᴇʀ ɪs ᴀʟʀᴇᴀᴅʏ ᴄᴏᴍᴘʟᴇᴛᴇᴅ ᴏʀ ᴇɪᴛʜᴇʀ ɴᴏᴛ sᴇᴛ",
            reply_to_message_id=msg.message_id,
        )
        return
    jobs[0].schedule_removal()
    msg.reply_text(
        text="ᴅᴏɴᴇ ᴄʟᴇᴀʀᴇᴅ ᴛʜᴇ ʀᴇᴍɪɴᴅᴇʀ!", reply_to_message_id=msg.message_id
    )


def clear_all_reminders(update: Update, context: CallbackContext):
    user = update.effective_user
    msg = update.effective_message
    if user.id != OWNER_ID:
        msg.reply_text(
            text="ᴡʜᴏ ᴛʜɪs ɢᴜʏ ɴᴏᴛ ʙᴇɪɴɢ ᴛʜᴇ ᴏᴡɴᴇʀ ᴡᴀɴᴛs ᴍᴇ ᴄʟᴇᴀʀ ᴀʟʟ ᴛʜᴇ ʀᴇᴍɪɴᴅᴇʀs!!?",
            reply_to_message_id=msg.message_id,
        )
        return
    jobs = list(job_queue.jobs())
    unremoved_reminders = []
    for job in jobs:
        try:
            job.schedule_removal()
        except Exception:
            unremoved_reminders.append(job.name[1:])
    reply_text = "ᴅᴏɴᴇ ᴄʟᴇᴀʀᴇᴅ ᴀʟʟ ᴛʜᴇ ʀᴇᴍɪɴᴅᴇʀs!\n\n"
    if unremoved_reminders:
        reply_text += "ᴇxᴄᴇᴘᴛ (<i>ᴛɪᴍᴇ sᴛᴀᴍᴘs ʜᴀᴠᴇ ʙᴇᴇɴ ᴍᴇɴᴛɪᴏɴᴇᴅ</i>):"
        for i, u in enumerate(unremoved_reminders):
            reply_text += f"\n{i+1}. <code>{u}</code>"
    msg.reply_text(
        text=reply_text, reply_to_message_id=msg.message_id, parse_mode=ParseMode.HTML
    )


def clear_all_my_reminders(update: Update, context: CallbackContext):
    user = update.effective_user
    msg = update.effective_message
    jobs = list(job_queue.jobs())
    if not jobs:
        msg.reply_text(
            text="ʏᴏᴜ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ ᴀɴʏ ʀᴇᴍɪɴᴅᴇʀs!", reply_to_message_id=msg.message_id
        )
        return
    unremoved_reminders = []
    for job in jobs:
        if job.name.endswith(str(user.id)):
            try:
                job.schedule_removal()
            except Exception:
                unremoved_reminders.append(job.name[1:])
    reply_text = "ᴅᴏɴᴇ ᴄʟᴇᴀʀᴇᴅ ᴀʟʟ ʏᴏᴜʀ ʀᴇᴍɪɴᴅᴇʀs!\n\n"
    if unremoved_reminders:
        reply_text += "ᴇxᴄᴇᴘᴛ (<i>ᴛɪᴍᴇ sᴛᴀᴍᴘs ʜᴀᴠᴇ ʙᴇᴇɴ ᴍᴇɴᴛɪᴏɴᴇᴅ</i>):"
        for i, u in enumerate(unremoved_reminders):
            reply_text += f"\n{i+1}. <code>{u}</code>"
    msg.reply_text(
        text=reply_text, reply_to_message_id=msg.message_id, parse_mode=ParseMode.HTML
    )


__mod_name__ = "𝚁ᴇᴍɪɴᴅᴇʀ"
__help__ = """
⍟ /reminders*:* `ɢᴇᴛ ᴀ ʟɪsᴛ ᴏғ *ᴛɪᴍᴇsᴛᴀᴍᴘs* ᴏғ ʏᴏᴜʀ ʀᴇᴍɪɴᴅᴇʀs `

⍟ /setreminder <time> <remind message>*:* `sᴇᴛ ᴀ ʀᴇᴍɪɴᴅᴇʀ ᴀғᴛᴇʀ ᴛʜᴇ ᴍᴇɴᴛɪᴏɴᴇᴅ ᴛɪᴍᴇ `

⍟ /clearreminder <timestamp>*:* `ᴄʟᴇᴀʀs ᴛʜᴇ ʀᴇᴍɪɴᴅᴇʀ ᴡɪᴛʜ ᴛʜᴀᴛ ᴛɪᴍᴇsᴛᴀᴍᴘ ɪғ ᴛʜᴇ ᴛɪᴍᴇ ᴛᴏ ʀᴇᴍɪɴᴅ ɪs ɴᴏᴛ ʏᴇᴛ ᴄᴏᴍᴘʟᴇᴛᴇᴅ `

⍟ /clearmyreminders*:* `ᴄʟᴇᴀʀs ᴀʟʟ ᴛʜᴇ ʀᴇᴍɪɴᴅᴇʀs ᴏғ ᴛʜᴇ ᴜsᴇʀ `.
  
*sɪᴍɪʟᴀʀ ᴄᴏᴍᴍᴀɴᴅs:*

⍟ /reminders | /myreminders

⍟ /clearmyreminders | /clearallmyreminders
  
*ᴜsᴀɢᴇ:*
⍟ /setreminder 30s reminder*:* `ʜᴇʀᴇ ᴛʜᴇ ᴛɪᴍᴇ ғᴏʀᴍᴀᴛ ɪs sᴀᴍᴇ ᴀs ᴛʜᴇ ᴛɪᴍᴇ ғᴏʀᴍᴀᴛ ɪɴ ᴍᴜᴛɪɴɢ ʙᴜᴛ ᴡɪᴛʜ ᴇxᴛʀᴀ sᴇᴄᴏɴᴅs(s)`


✦ `/clearreminder 1234567890123456789`
"""

# ʙsᴅᴋ ᴄᴏᴘʏ ᴋᴀʀ ʀᴀ ʜ ᴄʀᴇᴅɪᴛ ᴅᴇ ᴅᴇɴᴀ @AbishnoiMF|@Abishnoi

RemindersHandler = CommandHandler(
    ["reminders", "myreminders"],
    reminders,
    filters=Filters.chat_type.private,
    run_async=True,
)
SetReminderHandler = DisableAbleCommandHandler(
    "setreminder", set_reminder, run_async=True
)
ClearReminderHandler = DisableAbleCommandHandler(
    "clearreminder", clear_reminder, run_async=True
)
ClearAllRemindersHandler = CommandHandler(
    "clearallreminders",
    clear_all_reminders,
    filters=Filters.chat(OWNER_ID),
    run_async=True,
)
ClearALLMyRemindersHandler = CommandHandler(
    ["clearmyreminders", "clearallmyreminders"],
    clear_all_my_reminders,
    filters=Filters.chat_type.private,
    run_async=True,
)

dispatcher.add_handler(RemindersHandler)
dispatcher.add_handler(SetReminderHandler)
dispatcher.add_handler(ClearReminderHandler)
dispatcher.add_handler(ClearAllRemindersHandler)
dispatcher.add_handler(ClearALLMyRemindersHandler)
