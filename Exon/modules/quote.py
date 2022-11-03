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

from io import BytesIO
from traceback import format_exc

from pyrogram import filters
from pyrogram.types import Message

from Exon import arq, pgram
from Exon.utils.errors import capture_err


async def quotify(messages: list):
    response = await arq.quotly(messages)
    if not response.ok:
        return [False, response.result]
    sticker = response.result
    sticker = BytesIO(sticker)
    sticker.name = "sticker.webp"
    return [True, sticker]


def getArg(message: Message) -> str:
    return message.text.strip().split(None, 1)[1].strip()


def isArgInt(message: Message) -> list:
    count = getArg(message)
    try:
        count = int(count)
        return [True, count]
    except ValueError:
        return [False, 0]


@pgram.on_message(filters.command("q"))
@capture_err
async def quotly_func(client, message: Message):
    if not message.reply_to_message:
        return await message.reply_text("ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴍᴇssᴀɢᴇ ᴛᴏ ǫᴜᴏᴛᴇ ɪᴛ.")
    if not message.reply_to_message.text:
        return await message.reply_text("ʀᴇᴘʟɪᴇᴅ ᴍᴇssᴀɢᴇ ʜᴀs ɴᴏ ᴛᴇxᴛ, ᴄᴀɴ'ᴛ ǫᴜᴏᴛᴇ ɪᴛ.")
    m = await message.reply_text("ǫᴜᴏᴛɪɴɢ ᴍᴇssᴀɢᴇs")
    if len(message.command) < 2:
        messages = [message.reply_to_message]

    elif len(message.command) == 2:
        arg = isArgInt(message)
        if arg[0]:
            if arg[1] < 2 or arg[1] > 10:
                return await m.edit("ᴀʀɢᴜᴍᴇɴᴛ ᴍᴜsᴛ ʙᴇ ʙᴇᴛᴡᴇᴇɴ 2-10.")

            count = arg[1]

            # Fetching 5 extra messages so tha twe can ignore media
            # messages and still end up with correct offset
            messages = [
                i
                for i in await client.get_messages(
                    message.chat.id,
                    range(
                        message.reply_to_message.id,
                        message.reply_to_message.id + (count + 5),
                    ),
                    replies=0,
                )
                if not i.empty and not i.media
            ]
            messages = messages[:count]
        else:
            if getArg(message) != "r":
                return await m.edit(
                    "ɪɴᴄᴏʀʀᴇᴄᴛ ᴀʀɢᴜᴍᴇɴᴛ, ᴘᴀss **'r'** or **'INT'**, **EX:** __/q 2__"
                )
            reply_message = await client.get_messages(
                message.chat.id,
                message.reply_to_message.id,
                replies=1,
            )
            messages = [reply_message]
    else:
        return await m.edit("ɪɴᴄᴏʀʀᴇᴄᴛ ᴀʀɢᴜᴍᴇɴᴛ, ᴄʜᴇᴄᴋ ǫᴜᴏᴛʟʏ ᴍᴏᴅᴜʟᴇ ɪɴ ʜᴇʟᴘ sᴇᴄᴛɪᴏɴ.")
    try:
        if not message:
            return await m.edit("sᴏᴍᴇᴛʜɪɴɢ ᴡᴇɴᴛ ᴡʀᴏɴɢ.")

        sticker = await quotify(messages)
        if not sticker[0]:
            await message.reply_text(sticker[1])
            return await m.delete()
        sticker = sticker[1]
        await message.reply_sticker(sticker)
        await m.delete()
        sticker.close()
    except Exception as e:
        await m.edit(
            "sᴏᴍᴇᴛʜɪɴɢ ᴡᴇɴᴛ ᴡʀᴏɴɢ ᴡʜɪʟᴇ ǫᴜᴏᴛɪɴɢ ᴍᴇssᴀɢᴇs,"
            + " ᴛʜɪs ᴇʀʀᴏʀ ᴜsᴜᴀʟʟʏ ʜᴀᴘᴘᴇɴs ᴡʜᴇɴ ᴛʜᴇʀᴇ's ᴀ "
            + " ᴍᴇssᴀɢᴇ ᴄᴏɴᴛᴀɪɴɪɴɢ sᴏᴍᴇᴛʜɪɴɢ other than text,"
            + " ᴏʀ ᴏɴᴇ ᴏғ ᴛʜᴇ ᴍᴇssᴀɢᴇs ɪɴ-ᴇᴛᴡᴇᴇɴ ᴀʀᴇ ᴅᴇʟᴇᴛᴇᴅ."
        )
        e = format_exc()
        print(e)


__mod_name__ = "𝚀ᴜᴏᴛᴇ"

__help__ = """   

⍟  /q : `ᴄʀᴇᴀᴛᴇ ǫᴜᴏᴛᴇ `

⍟ /q r :

⍟ /q 2 ᴛᴏ 8 :
"""
