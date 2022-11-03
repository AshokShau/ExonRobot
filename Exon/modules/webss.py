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
from pyrogram.types import Message

from Exon import pgram
from Exon.utils.errors import capture_err


@pgram.on_message(filters.command("webss"))
@capture_err
async def take_ss(_, message: Message):
    try:
        if len(message.command) != 2:
            return await message.reply_text(
                "ɢɪᴠᴇ ᴀ ᴜʀʟ ᴛᴏ ғᴇᴛᴄʜ sᴄʀᴇᴇɴsʜᴏᴛ \nʟɪᴋᴇ ||xɴxx.ᴄᴏᴍ||."
            )
        url = message.text.split(None, 1)[1]
        m = await message.reply_text("**ᴛᴀᴋɪɴɢ sᴄʀᴇᴇɴsʜᴏᴛ**")
        await m.edit("**ᴜᴘʟᴏᴀᴅɪɴɢ...**")
        try:
            await message.reply_photo(
                photo=f"https://webshot.amanoteam.com/print?q={url}",
                quote=False,
            )
        except TypeError:
            return await m.edit("ɴᴏ sᴜᴄʜ ᴡᴇʙsɪᴛᴇ ᴍᴀʏ ʙᴇ ʏᴏᴜ ɴᴏᴛ ᴜsᴇ  𝚇.ᴄᴏᴍ.")
        await m.delete()
    except Exception as e:
        await message.reply_text(str(e))


__mod_name__ = "𝚆ᴇʙss"
