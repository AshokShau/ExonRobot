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

import random
from random import randint

import requests
from pyrogram import enums, filters
from pyrogram.types import Message

from Exon import Abishnoi, arq


@Abishnoi.on_message(filters.command(["wallpaper"]))
async def wall(_, msg):
    if len(msg.command) < 2:
        await msg.reply_text("ʜᴇʏ ʙᴀʙʏ ɢɪᴠᴇ sᴏᴍᴇᴛʜɪɴɢ ᴛᴏ sᴇᴀʀᴄʜ.")
        return
    else:
        pass

    query = (
        msg.text.split(None, 1)[1]
        if len(msg.command) < 3
        else msg.text.split(None, 1)[1].replace(" ", "%20")
    )

    if not query:
        await msg.reply_text("ʜᴇʏ ʙᴀʙʏ ɢɪᴠᴇ sᴏᴍᴇᴛʜɪɴɢ ᴛᴏ sᴇᴀʀᴄʜ.")
    else:
        pass

    url = f"https://api.safone.me/wall?query={query}"
    re = requests.get(url).json()
    walls = re.get("results")
    if not walls:
        await msg.reply_text("ɴᴏ ʀᴇsᴜʟᴛs ғᴏᴜɴᴅ! ")
        return
    wall_index = randint(0, len(walls) - 1)
    wallpaper = walls[wall_index]
    wallpaper.get("imageUrl")
    preview = wallpaper.get("thumbUrl")
    title = wallpaper.get("title")
    try:
        await Abishnoi.send_chat_action(msg.chat.id, enums.ChatAction.UPLOAD_PHOTO)
        await msg.reply_photo(
            preview, caption=f"🔎 ᴛɪᴛʟᴇ - {title}\nᴊᴏɪɴ [@ᴀʙɪsʜɴᴏɪᴍғ](t.me/AbishnoiMF)"
        )
    # await msg.reply_document(pic, caption=f"🔎 ᴛɪᴛʟᴇ - {title} \n🥀 **ʀᴇǫᴜᴇsᴛᴇᴅ ʙʏ :** {msg.from_user.mention}")
    except Exception as error:
        await msg.reply_text(f"ᴀɴ ᴇʀʀᴏʀ ᴏᴄᴄᴜʀᴇᴅ.\n {error}")


@Abishnoi.on_message(filters.command("wall"))
async def wall(_, m: Message):
    if len(m.command) < 2:
        return await m.reply_text("ɢɪᴠᴇ ᴍᴇ ᴀ ᴛᴇxᴛ !")
    search = m.text.split(None, 1)[1]
    x = await arq.wall(search)
    y = x.result
    await m.reply_photo(random.choice(y).url_image)
    # await m.reply_document(random.choice(y).url_image)
