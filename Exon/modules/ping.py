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

import time
from typing import List

import requests
from telegram import ParseMode, Update
from telegram.ext import CallbackContext

from Exon import StartTime, dispatcher
from Exon.modules.disable import DisableAbleCommandHandler
from Exon.modules.helper_funcs.chat_status import sudo_plus

sites_list = {
    "ᴛᴇʟᴇɢʀᴀᴍ": "https://api.telegram.org",
    "ᴋᴀɪᴢᴏᴋᴜ": "https://animekaizoku.com",
    "ᴊɪᴋᴀɴ": "https://api.jikan.moe/v3",
    "ᴋᴜᴋɪ ᴄʜᴀᴛʙᴏᴛ": "https://kuki-yukicloud.up.railway.app/",
    "ʟɪᴏɴᴇs ᴀᴘɪ": "https://liones-api.herokuapp.com/",
}


def get_readable_time(seconds: int) -> str:
    count = 0
    ping_time = ""
    time_list = []
    time_suffix_list = ["s", "ᴍ", "ʜ", "ᴅᴀʏs"]

    while count < 4:
        count += 1
        remainder, result = divmod(seconds, 60) if count < 3 else divmod(seconds, 24)
        if seconds == 0 and remainder == 0:
            break
        time_list.append(int(result))
        seconds = int(remainder)

    for x in range(len(time_list)):
        time_list[x] = str(time_list[x]) + time_suffix_list[x]
    if len(time_list) == 4:
        ping_time += f"{time_list.pop()}, "

    time_list.reverse()
    ping_time += ":".join(time_list)

    return ping_time


def ping_func(to_ping: List[str]) -> List[str]:
    ping_result = []

    for each_ping in to_ping:

        start_time = time.time()
        site_to_ping = sites_list[each_ping]
        r = requests.get(site_to_ping)
        end_time = time.time()
        ping_time = f"{str(round((end_time - start_time), 2))}s"

        pinged_site = f"<b>{each_ping}</b>"

        if each_ping in ("Kaizoku"):
            pinged_site = f'<a href="{sites_list[each_ping]}">{each_ping}</a>'
            ping_time = f"<code>{ping_time} (Status: {r.status_code})</code>"

        ping_text = f"{pinged_site}: <code>{ping_time}</code>"
        ping_result.append(ping_text)

    return ping_result


@sudo_plus
def ping(update: Update, context: CallbackContext):
    msg = update.effective_message

    start_time = time.time()
    message = msg.reply_text("ᴘɪɴɢɪɴɢ.....")
    end_time = time.time()
    telegram_ping = f"{str(round((end_time - start_time) * 1000, 3))} ms"
    uptime = get_readable_time((time.time() - StartTime))

    message.edit_text(
        f"𝗣𝗢𝗡𝗚 🎉!!\n<b>ᴛɪᴍᴇ ᴛᴀᴋᴇɴ:</b> <code>{telegram_ping}</code>\n<b>sᴇʀᴠɪᴄᴇ ᴜᴘᴛɪᴍᴇ:</b> <code>{uptime}</code>",
        parse_mode=ParseMode.HTML,
    )


@sudo_plus
def pingall(update: Update, context: CallbackContext):
    to_ping = ["ᴋᴀɪᴢᴏᴋᴜ", "ᴛᴇʟᴇɢʀᴀᴍ", "ᴊɪᴋᴀɴ", "ᴋᴜᴋɪ ᴄʜᴀᴛʙᴏᴛ", "ʟɪᴏɴᴇs ᴀᴘɪ"]
    pinged_list = ping_func(to_ping)
    pinged_list.insert(2, "")
    uptime = get_readable_time((time.time() - StartTime))

    reply_msg = "⏱ᴘɪɴɢ ʀᴇsᴜʟᴛs ᴀʀᴇ:\n" + "\n".join(pinged_list)
    reply_msg += f"\n<b>sᴇʀᴠɪᴄᴇ ᴜᴘᴛɪᴍᴇ:</b> <code>{uptime}</code>"

    update.effective_message.reply_text(
        reply_msg,
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True,
    )


PING_HANDLER = DisableAbleCommandHandler("ping", ping, run_async=True)
PINGALL_HANDLER = DisableAbleCommandHandler("pingall", pingall, run_async=True)

dispatcher.add_handler(PING_HANDLER)
dispatcher.add_handler(PINGALL_HANDLER)

__command_list__ = ["ping", "pingall"]
__handlers__ = [PING_HANDLER, PINGALL_HANDLER]
