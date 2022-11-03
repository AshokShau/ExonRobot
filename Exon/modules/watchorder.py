"""
MIT License

Copyright (c) 2022 A𝚋𝚒𝚜𝚑𝚗𝚘𝚒

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
from bs4 import BeautifulSoup
from pyrogram import filters

from Exon import pgram


@pgram.on_message(filters.command("watchorder"))
def watchorderx(_, message):
    anime = message.text.replace(message.text.split(" ")[0], "")
    res = requests.get(
        f"https://chiaki.site/?/tools/autocomplete_series&term={anime}"
    ).json()
    data = None
    id_ = res[0]["id"]
    res_ = requests.get(f"https://chiaki.site/?/tools/watch_order/id/{id_}").text
    soup = BeautifulSoup(res_, "html.parser")
    anime_names = soup.find_all("span", class_="wo_title")
    for x in anime_names:
        if data:
            data = f"{data}\n{x.text}"
        else:
            data = x.text
    message.reply_text(f"**ᴡᴀᴛᴄʜɪɴɢ ᴏʀᴅᴇʀ ʟɪsᴛ ᴏғ {anime}:** \n\n```{data}```")


__help__ = """ 
ɢᴇᴛ ᴡᴀᴛᴄʜ ᴏʀᴅᴇʀ (ᴡᴀᴛᴄʜɪɴɢ sᴇǫᴜᴇɴᴄᴇ) ᴏғ ᴀɴʏ ᴀɴɪᴍᴇ sᴇʀɪᴇs
ᴜsᴀɢᴇ:

/watchorder <ᴀɴɪᴍᴇ ɴᴀᴍᴇ>
"""

__mod_name__ = "𝚆ᴀᴛᴄʜ ᴏʀᴅᴇʀ"
