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

import re
import time

from pyrogram import filters
from pyrogram.enums import MessageEntityType

from Exon import BOT_USERNAME
from Exon import Abishnoi as app
from Exon.modules.helper_funcs.readable_time import get_readable_time
from Exon.modules.no_sql.afk_db import is_afk, remove_afk

chat_watcher_group = 1


@app.on_message(
    ~filters.me & ~filters.bot & ~filters.via_bot,
    group=chat_watcher_group,
)
async def chat_watcher_func(_, message):
    if message.sender_chat:
        return
    userid = message.from_user.id
    user_name = message.from_user.first_name
    if message.entities:
        possible = ["/afk", f"/afk@{BOT_USERNAME}"]
        message_text = message.text or message.caption
        for entity in message.entities:
            if entity.type == MessageEntityType.BOT_COMMAND:
                if (message_text[0 : 0 + entity.length]).lower() in possible:
                    return

    msg = ""
    replied_user_id = 0

    # Self AFK
    verifier, reasondb = await is_afk(userid)
    if verifier:
        await remove_afk(userid)
        try:
            afktype = reasondb["type"]
            timeafk = reasondb["time"]
            data = reasondb["data"]
            reasonafk = reasondb["reason"]
            seenago = get_readable_time((int(time.time() - timeafk)))
            if afktype == "text":
                msg += f"**{user_name[:25]}** ɪs ʙᴀᴄᴋ ᴏɴʟɪɴᴇ ᴀɴᴅ ᴡᴀs ᴀᴡᴀʏ ғᴏʀ {seenago}\n\n"
            if afktype == "text_reason":
                msg += f"**{user_name[:25]}** ɪs ʙᴀᴄᴋ ᴏɴʟɪɴᴇ ᴀɴᴅ ᴡᴀs ᴀᴡᴀʏ ғᴏʀ {seenago}\n\nʀᴇᴀsᴏɴ: `{reasonafk}`\n\n"
            if afktype == "animation":
                if str(reasonafk) == "None":
                    send = await message.reply_animation(
                        data,
                        caption=f"**{user_name[:25]}** ɪs ʙᴀᴄᴋ ᴏɴʟɪɴᴇ ᴀɴᴅ ᴡᴀs ᴀᴡᴀʏ ғᴏʀ {seenago}\n\n",
                    )
                else:
                    send = await message.reply_animation(
                        data,
                        caption=f"**{user_name[:25]}** ɪs ʙᴀᴄᴋ ᴏɴʟɪɴᴇ ᴀɴᴅ ᴡᴀs ᴀᴡᴀʏ ғᴏʀ {seenago}\n\nʀᴇᴀsᴏɴ: `{reasonafk}`\n\n",
                    )
            if afktype == "photo":
                if str(reasonafk) == "None":
                    send = await message.reply_photo(
                        photo=f"downloads/{userid}.jpg",
                        caption=f"**{user_name[:25]}** ɪs ʙᴀᴄᴋ ᴏɴʟɪɴᴇ ᴀɴᴅ ᴡᴀs ᴀᴡᴀʏ ғᴏʀ {seenago}\n\n",
                    )
                else:
                    send = await message.reply_photo(
                        photo=f"downloads/{userid}.jpg",
                        caption=f"**{user_name[:25]}** ɪs ʙᴀᴄᴋ ᴏɴʟɪɴᴇ ᴀɴᴅ ᴡᴀs ᴀᴡᴀʏ ғᴏʀ {seenago}\n\nʀᴇᴀsᴏɴ: `{reasonafk}`\n\n",
                    )
        except:
            msg += f"**{user_name[:25]}** ɪs ʙᴀᴄᴋ ᴏɴʟɪɴᴇ\n\n"

    # Replied to a User which is AFK
    if message.reply_to_message:
        try:
            replied_first_name = message.reply_to_message.from_user.first_name
            replied_user_id = message.reply_to_message.from_user.id
            verifier, reasondb = await is_afk(replied_user_id)
            if verifier:
                try:
                    afktype = reasondb["type"]
                    timeafk = reasondb["time"]
                    data = reasondb["data"]
                    reasonafk = reasondb["reason"]
                    seenago = get_readable_time((int(time.time() - timeafk)))
                    if afktype == "text":
                        msg += (
                            f"**{replied_first_name[:25]}** ɪs ᴀғᴋ sɪɴᴄᴇ {seenago}\n\n"
                        )
                    if afktype == "text_reason":
                        msg += f"**{replied_first_name[:25]}** ɪs ᴀғᴋ sɪɴᴄᴇ {seenago}\n\nʀᴇᴀsᴏɴ: `{reasonafk}`\n\n"
                    if afktype == "animation":
                        if str(reasonafk) == "None":
                            send = await message.reply_animation(
                                data,
                                caption=f"**{replied_first_name[:25]}** ɪs ᴀғᴋ sɪɴᴄᴇ {seenago}\n\n",
                            )
                        else:
                            send = await message.reply_animation(
                                data,
                                caption=f"**{replied_first_name[:25]}** ɪs ᴀғᴋ sɪɴᴄᴇ {seenago}\n\nʀᴇᴀsᴏɴ: `{reasonafk}`\n\n",
                            )
                    if afktype == "photo":
                        if str(reasonafk) == "None":
                            send = await message.reply_photo(
                                photo=f"downloads/{replied_user_id}.jpg",
                                caption=f"**{replied_first_name[:25]}** ɪs ᴀғᴋ sɪɴᴄᴇ {seenago}\n\n",
                            )
                        else:
                            send = await message.reply_photo(
                                photo=f"downloads/{replied_user_id}.jpg",
                                caption=f"**{replied_first_name[:25]}** ɪs ᴀғᴋ sɪɴᴄᴇ {seenago}\n\nʀᴇᴀsᴏɴ: `{reasonafk}`\n\n",
                            )
                except Exception:
                    msg += f"**{replied_first_name}** ɪs ᴀғᴋ,\nᴩᴀᴛᴀ ɴɪ ʙᴄ ᴋᴀʙ sᴇ\n\n"
        except:
            pass

    if message.entities:
        entity = message.entities
        j = 0
        for x in range(len(entity)):
            if (entity[j].type) == MessageEntityType.MENTION:
                found = re.findall("@([_0-9a-zA-Z]+)", message.text)
                try:
                    get_user = found[j]
                    user = await app.get_users(get_user)
                    if user.id == replied_user_id:
                        j += 1
                        continue
                except:
                    j += 1
                    continue
                verifier, reasondb = await is_afk(user.id)
                if verifier:
                    try:
                        afktype = reasondb["type"]
                        timeafk = reasondb["time"]
                        data = reasondb["data"]
                        reasonafk = reasondb["reason"]
                        seenago = get_readable_time((int(time.time() - timeafk)))
                        if afktype == "text":
                            msg += (
                                f"**{user.first_name[:25]}** ɪs ᴀғᴋ sɪɴᴄᴇ {seenago}\n\n"
                            )
                        if afktype == "text_reason":
                            msg += f"**{user.first_name[:25]}** ɪs ᴀғᴋ sɪɴᴄᴇ {seenago}\n\nʀᴇᴀsᴏɴ: `{reasonafk}`\n\n"
                        if afktype == "animation":
                            if str(reasonafk) == "None":
                                send = await message.reply_animation(
                                    data,
                                    caption=f"**{user.first_name[:25]}** ɪs ᴀғᴋ sɪɴᴄᴇ {seenago}\n\n",
                                )
                            else:
                                send = await message.reply_animation(
                                    data,
                                    caption=f"**{user.first_name[:25]}** ɪs ᴀғᴋ sɪɴᴄᴇ {seenago}\n\nʀᴇᴀsᴏɴ: `{reasonafk}`\n\n",
                                )
                        if afktype == "photo":
                            if str(reasonafk) == "None":
                                send = await message.reply_photo(
                                    photo=f"downloads/{user.id}.jpg",
                                    caption=f"**{user.first_name[:25]}** ɪs ᴀғᴋ sɪɴᴄᴇ {seenago}\n\n",
                                )
                            else:
                                send = await message.reply_photo(
                                    photo=f"downloads/{user.id}.jpg",
                                    caption=f"**{user.first_name[:25]}** ɪs ᴀғᴋ sɪɴᴄᴇ {seenago}\n\nʀᴇᴀsᴏɴ: `{reasonafk}`\n\n",
                                )
                    except:
                        msg += f"**{user.first_name[:25]}** ɪs ᴀғᴋ\n\n"
            elif (entity[j].type) == MessageEntityType.TEXT_MENTION:
                try:
                    user_id = entity[j].user.id
                    if user_id == replied_user_id:
                        j += 1
                        continue
                    first_name = entity[j].user.first_name
                except:
                    j += 1
                    continue
                verifier, reasondb = await is_afk(user_id)
                if verifier:
                    try:
                        afktype = reasondb["type"]
                        timeafk = reasondb["time"]
                        data = reasondb["data"]
                        reasonafk = reasondb["reason"]
                        seenago = get_readable_time((int(time.time() - timeafk)))
                        if afktype == "text":
                            msg += f"**{first_name[:25]}** is ᴀғᴋ sɪɴᴄᴇ {seenago}\n\n"
                        if afktype == "text_reason":
                            msg += f"**{first_name[:25]}** ɪs ᴀғᴋ sɪɴᴄᴇ {seenago}\n\nʀᴇᴀsᴏɴ: `{reasonafk}`\n\n"
                        if afktype == "animation":
                            if str(reasonafk) == "None":
                                send = await message.reply_animation(
                                    data,
                                    caption=f"**{first_name[:25]}** ɪs ᴀғᴋ sɪɴᴄᴇ {seenago}\n\n",
                                )
                            else:
                                send = await message.reply_animation(
                                    data,
                                    caption=f"**{first_name[:25]}** ɪs AFK sɪɴᴄᴇ {seenago}\n\nʀᴇᴀsᴏɴ: `{reasonafk}`\n\n",
                                )
                        if afktype == "photo":
                            if str(reasonafk) == "None":
                                send = await message.reply_photo(
                                    photo=f"downloads/{user_id}.jpg",
                                    caption=f"**{first_name[:25]}** ɪs ᴀғᴋ sɪɴᴄᴇ {seenago}\n\n",
                                )
                            else:
                                send = await message.reply_photo(
                                    photo=f"downloads/{user_id}.jpg",
                                    caption=f"**{first_name[:25]}** ɪs ᴀғᴋ sɪɴᴄᴇ {seenago}\n\nʀᴇᴀsᴏɴ: `{reasonafk}`\n\n",
                                )
                    except:
                        msg += f"**{first_name[:25]}** ɪs ᴀғᴋ\n\n"
            j += 1
    if msg != "":
        try:
            send = await message.reply_text(msg, disable_web_page_preview=True)
        except:
            return
