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

from pyrogram import filters

from Exon import pgram
from Exon.core.decorators.permissions import adminsOnly
from Exon.utils.dbfunctions import antiservice_off, antiservice_on, is_antiservice_on


@pgram.on_message(filters.command("antiservice") & ~filters.private & ~filters.edited)
@adminsOnly("can_change_info")
async def anti_service(_, message):
    if len(message.command) != 2:
        return await message.reply_text("ᴜsᴀɢᴇ: /antiservice [on | off]")
    status = message.text.split(None, 1)[1].strip()
    status = status.lower()
    chat_id = message.chat.id
    if status == "on":
        await antiservice_on(chat_id)
        await message.reply_text(
            "ᴇɴᴀʙʟᴇᴅ ᴀɴᴛɪsᴇʀᴠɪᴄᴇ sʏsᴛᴇᴍ. ɪ ᴡɪʟʟ ᴅᴇʟᴇᴛᴇ sᴇʀᴠɪᴄᴇ ᴍᴇssᴀɢᴇs ғʀᴏᴍ ɴᴏᴡ ᴏɴ."
        )
    elif status == "off":
        await antiservice_off(chat_id)
        await message.reply_text(
            "ᴅɪsᴀʙʟᴇᴅ ᴀɴᴛɪsᴇʀᴠɪᴄᴇ sʏsᴛᴇᴍ. I ᴡᴏɴ'ᴛ ʙᴇ ᴅᴇʟᴇᴛɪɴɢ sᴇʀᴠɪᴄᴇ ᴍᴇssᴀɢᴇ ғʀᴏᴍ ɴᴏᴡ ᴏɴ."
        )
    else:
        await message.reply_text("ᴜɴᴋɴᴏᴡɴ sᴜғғɪx, ᴜsᴇ /antiservice [enable|disable]")


@pgram.on_message(filters.service, group=11)
async def delete_service(_, message):
    chat_id = message.chat.id
    try:
        if await is_antiservice_on(chat_id):
            return await message.delete()
    except Exception:
        pass
