import random

from telethon import Button

from Exon import Asuinline, register
from Exon.modules.sql.mongo.couples_db import (
    add_vote_down,
    add_vote_up,
    get_couple,
    rm_vote_down,
    rm_vote_up,
    save_couple,
    voted_down,
    voted_up,
)


@register(pattern=r"^/couples ?(.*)")
async def couple(event):
    today = str(dt()[0])
    tomorrow = str(dt_tom())
    if event.is_private:
        return await event.reply(
            "ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ ᴏɴʟʏ ᴡᴏʀᴋs ɪɴ ɢʀᴏᴜᴘs.",
        )
    chat_id = event.chat_id
    is_selected = get_couple(chat_id, today)
    if not is_selected:
        users = []
        u_dict = {}
        async for user in event.client.iter_participants(chat_id):
            if not user.bot and user.first_name:
                users.append(user.id)
                u_dict[user.id] = user.first_name
        if len(users) < 2:
            return await event.reply(
                "ɴᴏᴛ ᴇɴᴏᴜɢʜ users",
            )
        u1_id = random.choice(users)
        u2_id = random.choice(users)
        if u1_id == u2_id:
            u2_id = random.choice(users)
        u1_name = u_dict[u1_id]
        u2_name = u_dict[u2_id]
        couple = {
            "u1_id": u1_id,
            "u2_id": u2_id,
            "u1_name": u1_name,
            "u2_name": u2_name,
        }
        save_couple(chat_id, today, couple)
    elif is_selected:
        u1_id = int(is_selected["u1_id"])
        u2_id = int(is_selected["u2_id"])
        u1_name = is_selected["u1_name"]
        u2_name = is_selected["u2_name"]
    mention1 = f"""<a href='tg://user?id={u1_id}'>{u1_name}</a>"""
    mention2 = f"""<a href='tg://user?id={u2_id}'>{u2_name}</a>"""
    text1 = "ᴄᴏᴜᴘʟᴇ ᴏғ ᴛʜᴇ ᴅᴀʏ"
    text2 = "ɴᴇᴡ ᴄᴏᴜᴘʟᴇ ᴏғ ᴛʜᴇ ᴅᴀʏ ᴍᴀʏ ʙᴇ ᴄʜᴏsᴇɴ ɪɴ"
    couple_final = f"{text1}:\n{mention1} + {mention2} = ❤️\n\n{text2} {tomorrow}"
    cb_data = str(event.id) + "|" + "0" + "|" + "0"
    buttons = Button.inline("👍", data="upco_{}".format(cb_data)), Button.inline(
        "👎", data="downco_{}".format(cb_data)
    )
    await event.respond(couple_final, parse_mode="html", buttons=buttons)


@Asuinline(pattern=r"upco(\_(.*))")
async def up(event):
    d = (((event.pattern_match.group(1)).decode()).split("_", 1)[1]).split("|")
    event_id = int(d[0])
    count1 = int(d[1])
    count2 = int(d[2])
    vote_up = voted_up(event_id, event.sender_id)
    vote_down = voted_down(event_id, event.sender_id)
    if vote_up:
        await event.answer(
            "ʏᴏᴜ ᴛᴏᴏᴋ ʏᴏᴜʀ ʀᴇᴀᴄᴛɪᴏɴ ʙᴀᴄᴋ.",
        )
        rm_vote_up(event_id, event.sender_id)
        count1 -= 1
    elif vote_down:
        await event.answer(
            "ʏᴏᴜ 👍 ᴛʜɪs.",
        )
        rm_vote_down(event_id, event.sender_id)
        count2 -= 1
        add_vote_up(event_id, event.sender_id)
        count1 += 1
    else:
        await event.answer(
            "ʏᴏᴜ 👍 ᴛʜɪs.",
        )
        add_vote_up(event_id, event.sender_id)
        count1 += 1
    cb_data = str(event_id) + "|" + str(count1) + "|" + str(count2)
    C1 = count1
    C2 = count2
    if count1 == 0:
        C1 = ""
    if count2 == 0:
        C2 = ""
    edited_buttons = Button.inline(
        f"👍{C1}", data="upco_{}".format(cb_data)
    ), Button.inline(f"👎{C2}", data="downco_{}".format(cb_data))
    await event.edit(buttons=edited_buttons)


@Asuinline(pattern=r"downco(\_(.*))")
async def up(event):
    d = (((event.pattern_match.group(1)).decode()).split("_", 1)[1]).split("|")
    event_id = int(d[0])
    count1 = int(d[1])
    count2 = int(d[2])
    vote_up = voted_up(event_id, event.sender_id)
    vote_down = voted_down(event_id, event.sender_id)
    if vote_down:
        await event.answer(
            "ʏᴏᴜ ᴛᴏᴏᴋ ʏᴏᴜʀ reaction back.",
        )
        rm_vote_down(event_id, event.sender_id)
        count2 -= 1
    elif vote_up:
        await event.answer("ʏᴏᴜ 👎 ᴛʜɪs.")
        rm_vote_up(event_id, event.sender_id)
        count1 -= 1
        add_vote_down(event_id, event.sender_id)
        count2 += 1
    else:
        await event.answer("ʏᴏᴜ 👎 ᴛʜɪs.")
        add_vote_down(event_id, event.sender_id)
        count2 += 1
    cb_data = str(event_id) + "|" + str(count1) + "|" + str(count2)
    C1 = count1
    C2 = count2
    if count1 == 0:
        C1 = ""
    if count2 == 0:
        C2 = ""
    edited_buttons = Button.inline(
        f"👍{C1}", data="upco_{}".format(cb_data)
    ), Button.inline(f"👎{C2}", data="downco_{}".format(cb_data))
    await event.edit(buttons=edited_buttons)


__help__ = """
*ᴄʜᴏᴏsᴇ ᴄᴏᴜᴘʟᴇs ɪɴ ʏᴏᴜʀ ᴄʜᴀᴛ*

 ❍ /couple *:* ᴄʜᴏᴏsᴇ 2 ᴜsᴇʀs ᴀɴᴅ sᴇɴᴅ ᴛʜᴇɪʀ ɴᴀᴍᴇ ᴀs ᴄᴏᴜᴘʟᴇs ɪɴ ʏᴏᴜʀ ᴄʜᴀᴛ.
"""

__mod_name__ = "𝐂ᴏᴜᴘʟᴇ"
