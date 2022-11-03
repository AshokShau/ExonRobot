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

# thanks to inrajith for meow meow meow
import os

from pyrogram import filters
from pyrogram.types import Message
from telegram import ParseMode

from Exon import pgram
from Exon.core.sections import section


async def get_chat_info(chat, already=False):
    if not already:
        chat = await pgram.get_chat(chat)
    chat_id = chat.id
    username = chat.username
    title = chat.title
    type_ = chat.type
    is_scam = chat.is_scam
    description = chat.description
    members = chat.members_count
    is_restricted = chat.is_restricted
    link = f"[ʟɪɴᴋ](t.me/{username})" if username else "Null"
    total = ""
    for m in await pgram.get_chat_members(chat.id, filter="administrators"):
        total += f"• [{m.user.first_name}](tg://user?id={m.user.id})\n"
    dc_id = chat.dc_id
    photo_id = chat.photo.big_file_id if chat.photo else None
    body = {
        "ɪᴅ:": chat_id,
        "ᴅᴄ:": dc_id,
        "ᴛʏᴘᴇ:": type_,
        "ɴᴀᴍᴇ:": [title],
        "ᴜsᴇʀɴᴀᴍᴇ:": [f"@{username}" if username else "Null"],
        "ᴍᴇɴᴛɪᴏɴ:": [link],
        "ᴍᴇᴍʙᴇʀs:": members,
        "sᴄᴀᴍ:": is_scam,
        "ʀᴇsᴛʀɪᴄᴛᴇᴅ:": is_restricted,
        "\nᴅᴇsᴄʀɪᴘᴛɪᴏɴ:\n\n": [description],
        "\nᴀᴅᴍɪɴs ʟɪsᴛ:\n": [total],
    }

    caption = section("ᴄʜᴀᴛ ɪɴғᴏ:\n", body)
    return [caption, photo_id]


@pgram.on_message(filters.command("ginfo") & ~filters.edited)
async def chat_info_func(_, message: Message):
    try:
        if len(message.command) > 2:
            return await message.reply_text("**ᴜsᴀɢᴇ:**/ginfo [-ID]")

        if len(message.command) == 1:
            chat = message.chat.id
        elif len(message.command) == 2:
            chat = message.text.split(None, 1)[1]

        m = await message.reply_text("ᴘʀᴏᴄᴇssɪɴɢ...")

        info_caption, photo_id = await get_chat_info(chat)
        if not photo_id:
            return await m.edit(
                info_caption,
                disable_web_page_preview=True,
                parse_mode=ParseMode.MARKDOWN,
            )

        photo = await pgram.download_media(photo_id)
        await message.reply_photo(
            photo, caption=info_caption, quote=False, parse_mode=ParseMode.MARKDOWN
        )

        await m.delete()
        os.remove(photo)
    except Exception as e:
        await m.edit(e),
        ParseMode.MARKDOWN
