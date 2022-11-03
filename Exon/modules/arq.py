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

from Exon import BOT_USERNAME, arq, pgram


@pgram.on_message(filters.command("arq"))
async def arq_stats(_, message):
    data = await arq.stats()
    if not data.ok:
        return await message.reply_text(data.result)
    data = data.result
    uptime = data.uptime
    requests = data.requests
    cpu = data.cpu
    server_mem = data.memory.server
    api_mem = data.memory.api
    disk = data.disk
    platform = data.platform
    python_version = data.python
    users = data.users
    statistics = f"""
**>-< sʏsᴛᴇᴍ >-<**
**ᴜᴘᴛɪᴍᴇ:** `{uptime}`
**ʀᴇǫᴜᴇsᴛs  ᴜᴘᴛɪᴍᴇ:** `{requests}`
**ᴄᴘᴜ:** `{cpu}`
**ᴍᴇᴍᴏʀʏ:**
**ᴛᴏᴛᴀʟ ᴜsᴇᴅ:** `{server_mem}`
**ᴀᴘɪ:** `{api_mem}`
**ᴅɪsᴋ:** `{disk}`
**ᴘʟᴀᴛғᴏʀᴍ:** `{platform}`
**ᴘʏᴛʜᴏɴ:** `{python_version}`

**ᴀʀǫ sᴛᴀᴛɪsᴛɪᴄs:**
**ᴜsᴇʀs:** `{users}`

**@{BOT_USERNAME} sᴏᴍᴇ ᴍᴏᴅᴜʟᴇs ʀᴜɴɴɪɴɢ ᴏɴ ᴀʀǫ**
"""
    await message.reply_text(statistics, disable_web_page_preview=True)
