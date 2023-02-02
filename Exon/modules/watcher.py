import re
import time

from pyrogram import filters
from pyrogram.enums import MessageEntityType

from Exon import app
from Exon.modules.helper_funcs import get_readable_time
from Exon.modules.sql.mongo.afk_db import is_afk, remove_afk


@app.on_message(
    ~filters.me & ~filters.bot & ~filters.via_bot,
    group=1,
)
async def chat_watcher_func(_, message):
    if message.sender_chat:
        return
    userid = message.from_user.id
    bot_username = (await _.get_me()).username
    user_name = message.from_user.first_name
    possible = ["/afk",f"/afk{bot_username}".lower()]
    
    try:
        if message.text.split()[0].lower() in possible:
            return 
    except:
        pass
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
                    msg += f"**{replied_first_name}** ɪs ᴀғᴋ\n\n"
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


#  ᴀғᴋ ᴍᴏᴅᴜʟᴇs  ʙʏ - https://github.com/AnonymousX1025/FallenRobot
