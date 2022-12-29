import time
from typing import List

from httpx import AsyncClient
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from Exon import StartTime, application
from Exon.modules.disable import DisableAbleCommandHandler
from Exon.modules.helper_funcs.chat_status import check_admin

sites_list = {
    "ᴛᴇʟᴇɢʀᴀᴍ": "https://api.telegram.org",
    "ᴋᴀɪᴢᴏᴋᴜ": "https://animekaizoku.com",
    "ᴋᴀʏᴏ": "https://animekayo.com",
    "ᴊɪᴋᴀɴ": "https://api.jikan.moe/v3",
}


def get_readable_time(seconds: int) -> str:
    count = 0
    ping_time = ""
    time_list = []
    time_suffix_list = ["s", "ᴍ", "ʜ", "ᴅᴀʏs"]

    while count < 4:
        count += 1
        if count < 3:
            remainder, result = divmod(seconds, 60)
        else:
            remainder, result = divmod(seconds, 24)
        if seconds == 0 and remainder == 0:
            break
        time_list.append(int(result))
        seconds = int(remainder)

    for x in range(len(time_list)):
        time_list[x] = str(time_list[x]) + time_suffix_list[x]
    if len(time_list) == 4:
        ping_time += time_list.pop() + ", "

    time_list.reverse()
    ping_time += ":".join(time_list)

    return ping_time


async def ping_func(to_ping: List[str]) -> List[str]:
    ping_result = []

    for each_ping in to_ping:

        start_time = time.time()
        site_to_ping = sites_list[each_ping]
        async with AsyncClient() as client:
            r = await client.get(site_to_ping)
        end_time = time.time()
        ping_time = str(round((end_time - start_time), 2)) + "s"

        pinged_site = f"<b>{each_ping}</b>"

        if each_ping == "ᴋᴀɪᴢᴏᴋᴜ" or each_ping == "Kayo":
            pinged_site = f'<a href="{sites_list[each_ping]}">{each_ping}</a>'
            ping_time = f"<code>{ping_time} (Status: {r.status_code})</code>"

        ping_text = f"{pinged_site}: <code>{ping_time}</code>"
        ping_result.append(ping_text)

    return ping_result


async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.effective_message

    start_time = time.time()
    message = await msg.reply_text("⚡.")
    end_time = time.time()
    telegram_ping = str(round((end_time - start_time) * 1000, 3)) + " ms"
    uptime = get_readable_time((time.time() - StartTime))

    await message.edit_text(
        "𝗣𝗢𝗡𝗚 🥀!!\n"
        "<b>ᴛɪᴍᴇ ᴛᴀᴋᴇɴ:</b> <code>{}</code>\n"
        "<b>sᴇʀᴠɪᴄᴇ ᴜᴘᴛɪᴍᴇ:</b> <code>{}</code>".format(telegram_ping, uptime),
        parse_mode=ParseMode.HTML,
    )


@check_admin(only_sudo=True)
async def pingall(update: Update, context: ContextTypes.DEFAULT_TYPE):
    to_ping = ["ᴋᴀɪᴢᴏᴋᴜ", "ᴋᴀʏᴏ", "ᴛᴇʟᴇɢʀᴀᴍ", "ᴊɪᴋᴀɴ"]
    pinged_list = await ping_func(to_ping)
    pinged_list.insert(2, "")
    uptime = get_readable_time((time.time() - StartTime))

    reply_msg = "⏱ᴘɪɴɢ ʀᴇsᴜʟᴛs ᴀʀᴇ:\n"
    reply_msg += "\n".join(pinged_list)
    reply_msg += "\n<b>sᴇʀᴠɪᴄᴇ ᴜᴘᴛɪᴍᴇ:</b> <code>{}</code>".format(uptime)

    await update.effective_message.reply_text(
        reply_msg,
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True,
    )


PING_HANDLER = DisableAbleCommandHandler("ping", ping, block=False)
PINGALL_HANDLER = DisableAbleCommandHandler("pingall", pingall, block=False)

application.add_handler(PING_HANDLER)
application.add_handler(PINGALL_HANDLER)

__command_list__ = ["ping", "pingall"]
__handlers__ = [PING_HANDLER, PINGALL_HANDLER]
