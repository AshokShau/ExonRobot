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

import jikanpy
from bs4 import BeautifulSoup
from markdown import markdown
from telethon.sync import events

from Exon import DEV_USERS, telethn


def md_to_text(md):
    html = markdown(md)
    soup = BeautifulSoup(html, features="html.parser")
    return soup.get_text()


async def reply_id(event):
    reply_to_id = None
    if event.sender_id in DEV_USERS:
        reply_to_id = event.id
    if event.reply_to_msg_id:
        reply_to_id = event.reply_to_msg_id
    return reply_to_id


async def edit_or_reply(
    event,
    text,
    parse_mode=None,
    link_preview=None,
    file_name=None,
    aslink=False,
    deflink=False,
    noformat=False,
    linktext=None,
    caption=None,
):  # sourcery no-metrics
    link_preview = link_preview or False
    reply_to = await event.get_reply_message()
    if len(text) < 4096 and not deflink:
        parse_mode = parse_mode or "md"
        if event.sender_id in DEV_USERS:
            if reply_to:
                return await reply_to.reply(
                    text, parse_mode=parse_mode, link_preview=link_preview
                )
            return await event.reply(
                text, parse_mode=parse_mode, link_preview=link_preview
            )
        await event.edit(text, parse_mode=parse_mode, link_preview=link_preview)
        return event
    if not noformat:
        text = md_to_text(text)
    if aslink or deflink:
        linktext = linktext or "ᴍᴇssᴀɢᴇ ᴡᴀs ᴛᴏ ʙɪɢ sᴏ ᴘᴀsᴛᴇᴅ ᴛᴏ ʙɪɴ"
        response = await paste_message(text, pastetype="s")
        text = f"{linktext} [here]({response})"
        if event.sender_id in DEV_USERS:
            if reply_to:
                return await reply_to.reply(text, link_preview=link_preview)
            return await event.reply(text, link_preview=link_preview)
        await event.edit(text, link_preview=link_preview)
        return event
    file_name = file_name or "output.txt"
    caption = caption or None
    with open(file_name, "w+") as output:
        output.write(text)
    if reply_to:
        await reply_to.reply(caption, file=file_name)
        await event.delete()
        return os.remove(file_name)
    if event.sender_id in DEV_USERS:
        await event.reply(caption, file=file_name)
        await event.delete()
        return os.remove(file_name)
    await event.client.send_file(event.chat_id, file_name, caption=caption)
    await event.delete()
    os.remove(file_name)


async def edit_delete(event, text, time=None, parse_mode=None, link_preview=None):
    parse_mode = parse_mode or "md"
    link_preview = link_preview or False
    time = time or 5
    if event.sender_id in DEV_USERS:
        reply_to = await event.get_reply_message()
        himaevent = (
            await reply_to.reply(text, link_preview=link_preview, parse_mode=parse_mode)
            if reply_to
            else await event.reply(
                text, link_preview=link_preview, parse_mode=parse_mode
            )
        )
    else:
        himaevent = await event.edit(
            text, link_preview=link_preview, parse_mode=parse_mode
        )
    await asyncio.sleep(time)
    return await himaevent.delete()


import random

import requests


@telethn.on(events.NewMessage(pattern="^[!/]gif"))
async def some(event):
    try:
        inpt = event.text.split(" ", maxsplit=1)[1]
    except IndexError:
        return await event.reply("Usage: /gif <query>")
    """Sends random gifs of your query"""
    reply_to_id = await reply_id(event)
    count = 1
    if ";" in inpt:
        inpt, count = inpt.split(";")
    if int(count) < 0 and int(count) > 20:
        await edit_delete(event, "`ɢɪᴠᴇ ᴠᴀʟᴜᴇ ɪɴ ʀᴀɴɢᴇ 1-20`")
    himaevent = await edit_or_reply(event, "`sᴇɴᴅɪɴɢ ɢɪғ....`")
    res = requests.get("https://giphy.com/")
    res = res.text.split("GIPHY_FE_WEB_API_KEY =")[1].split("\n")[0]
    api_key = res[2:-1]
    r = requests.get(
        f"https://api.giphy.com/v1/gifs/search?q={inpt}&api_key={api_key}&limit=50"
    ).json()
    list_id = [r["data"][i]["id"] for i in range(len(r["data"]))]
    rlist = random.sample(list_id, int(count))
    for items in rlist:
        nood = await event.client.send_file(
            event.chat_id,
            f"https://media.giphy.com/media/{items}/giphy.gif",
            reply_to=reply_to_id,
        )
    await himaevent.delete()


# schedule for anime

weekdays = {
    "monday": 0,
    "tuesday": 1,
    "wednesday": 2,
    "thursday": 3,
    "friday": 4,
    "saturday": 5,
    "sunday": 6,
}


def get_weekday(dayid):
    for key, value in weekdays.items():
        if value == dayid:
            return key


async def get_anime_schedule(weekid):
    "ɢᴇᴛ ᴀɴɪᴍᴇ sᴄʜᴇᴅᴜʟᴇ"
    dayname = get_weekday(weekid)
    result = (
        f"✙ **ᴛɪᴍᴇ ᴢᴏɴᴇ: ᴊᴀᴘᴀɴ**\n**sᴄʜᴇᴅᴜʟᴇᴅ ᴀɴɪᴍᴇ ғᴏʀ {dayname.title()} ᴀʀᴇ : **\n\n"
    )
    async with jikanpy.AioJikan() as animesession:
        scheduled_list = (await animesession.schedule(day=dayname)).get(dayname)
        for a_name in scheduled_list:
            result += f"• [{a_name['title']}]({a_name['url']})\n"
    return result, dayname


@telethn.on(events.NewMessage(pattern="^[!/]schedule ?(.*)"))
async def aschedule_fetch(event):
    "To ɢᴇᴛ ʟɪsᴛ ᴏғ ᴀɴɪᴍᴇs sᴄʜᴇᴅᴜʟᴇᴅ ᴏɴ ᴛʜᴀᴛ ᴅᴀʏ"
    input_str = event.pattern_match.group(1) or datetime.now().weekday()
    if input_str in weekdays:
        input_str = weekdays[input_str]
    try:
        input_str = int(input_str)
    except ValueError:
        return await edit_delete(event, "`ʏᴏᴜ ʜᴀᴠᴇ ɢɪᴠᴇɴ ᴀɴ ɪɴᴠᴀʟɪᴅ ᴡᴇᴇᴋᴅᴀʏ`", 7)
    if input_str not in [0, 1, 2, 3, 4, 5, 6]:
        return await edit_delete(event, "`ʏᴏᴜ ʜᴀᴠᴇ ɢɪᴠᴇɴ ᴀɴ ɪɴᴠᴀʟɪᴅ ᴡᴇᴇᴋᴅᴀʏ`", 7)
    result = await get_anime_schedule(input_str)
    await edit_or_reply(event, result[0])
