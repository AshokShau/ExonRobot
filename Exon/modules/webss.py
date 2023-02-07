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
# TG :- @Abishnoi1M
#      :- Abishnoi_bots
#     GITHUB :- Abishnoi69 ""


from base64 import b64decode
from inspect import getfullargspec
from io import BytesIO

from pyrogram import filters
from pyrogram.types import Message

from Exon import Abishnoi as app
from Exon import aiohttpsession as session


async def post(url: str, *args, **kwargs):
    async with session.post(url, *args, **kwargs) as resp:
        try:
            data = await resp.json()
        except Exception:
            data = await resp.text()
    return data


async def take_screenshot(url: str, full: bool = False):
    url = "https://" + url if not url.startswith("http") else url
    payload = {
        "url": url,
        "width": 1920,
        "height": 1080,
        "scale": 1,
        "format": "jpeg",
    }
    if full:
        payload["full"] = True
    data = await post(
        "https://webscreenshot.vercel.app/api",
        data=payload,
    )
    if "image" not in data:
        return None
    b = data["image"].replace("data:image/jpeg;base64,", "")
    file = BytesIO(b64decode(b))
    file.name = "webss.jpg"
    return file


async def eor(msg: Message, **kwargs):
    func = (
        (msg.edit_text if msg.from_user.is_self else msg.reply)
        if msg.from_user
        else msg.reply
    )
    spec = getfullargspec(func.__wrapped__).args
    return await func(**{k: v for k, v in kwargs.items() if k in spec})


@app.on_message(filters.command(["webss", "ss", "webshot"]))
async def take_ss(_, message: Message):
    if len(message.command) < 2:
        return await eor(message, text="ɢɪᴠᴇ ᴀ ᴜʀʟ ᴛᴏ ғᴇᴛᴄʜ sᴄʀᴇᴇɴsʜᴏᴛ.")

    if len(message.command) == 2:
        url = message.text.split(None, 1)[1]
        full = False
    elif len(message.command) == 3:
        url = message.text.split(None, 2)[1]
        full = message.text.split(None, 2)[2].lower().strip() in [
            "yes",
            "y",
            "1",
            "true",
        ]
    else:
        return await eor(message, text="ɪɴᴠᴀʟɪᴅ ᴄᴏᴍᴍᴀɴᴅ.")

    m = await eor(message, text="ᴄᴀᴘᴛᴜʀɪɴɢ sᴄʀᴇᴇɴsʜᴏᴛ...")

    try:
        photo = await take_screenshot(url, full)
        if not photo:
            return await m.edit("ғᴀɪʟᴇᴅ ᴛᴏ ᴛᴀᴋᴇ sᴄʀᴇᴇɴsʜᴏᴛ.")

        m = await m.edit("ᴜᴘʟᴏᴀᴅɪɴɢ...")

        if not full:
            await message.reply_document(photo)
        else:
            await message.reply_document(photo)
        await m.delete()
    except Exception as e:
        await m.edit(str(e))


__mod_name__ = "𝐖ᴇʙsʜᴏᴛ"

from Exon.modules.language import gs


def get_help(chat):
    return gs(chat, "webss_help")
