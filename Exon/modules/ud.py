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

import requests
from telethon import Button

from Exon.events import register as asau


@asau(pattern="[/!]ud")
async def ud_(e):
    try:
        text = e.text.split(" ", maxsplit=1)[1]
    except IndexError:
        return await e.reply("ɪɴᴠᴀʟɪᴅ ᴀʀɢs")
    results = requests.get(
        f"https://api.urbandictionary.com/v0/define?term={text}"
    ).json()
    try:
        reply_txt = f'<bold>{text}</bold>\n\n{results["list"][0]["definition"]}\n\n<i>{results["list"][0]["ᴇxᴀᴍᴘʟᴇ"]}</i>'
    except:
        reply_txt = "ɴᴏ ʀᴇsᴜʟᴛs ғᴏᴜɴᴅ."
    await e.reply(
        reply_txt,
        buttons=Button.url("🔎 ɢᴏᴏɢʟᴇ ɪᴛ!", f"https://www.google.com/search?q={text}"),
        parse_mode="html",
    )
