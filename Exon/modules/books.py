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

import os
import re

import requests
from bs4 import BeautifulSoup
from telethon import events

from Exon import BOT_USERNAME, SUPPORT_CHAT, telethn


@telethn.on(events.NewMessage(pattern="^/book (.*)"))
async def _(event):
    if event.fwd_from:
        return
    input_str = event.pattern_match.group(1)
    KkK = await event.reply("sᴇᴀʀᴄʜɪɴɢ ғᴏʀ ᴛʜᴇ ʙᴏᴏᴋ...")
    lin = "https://b-ok.cc/s/"
    text = input_str
    link = lin + text

    headers = [
        "User-Agent",
        "Arsh 5.0 (Macintosh; Intel Mac OS X 10.15; rv:74.0) Gecko/20100101 Firefox/74.0",
    ]
    page = requests.get(link)
    soup = BeautifulSoup(page.content, "html.parser")
    f = open("book.txt", "w")
    total = soup.find(class_="totalCounter")
    for nb in total.descendants:
        nbx = nb.replace("(", "").replace(")", "")
    if nbx == "0":
        await event.reply("ɴᴏ ʙᴏᴏᴋs ғᴏᴜɴᴅ ᴡɪᴛʜ ᴛʜᴀᴛ ɴᴀᴍᴇ.")
    else:

        lool = 0
        for tr in soup.find_all("td"):
            for td in tr.find_all("h3"):
                for ts in td.find_all("a"):
                    title = ts.get_text()
                    lool += 1
                for ts in td.find_all("a", attrs={"href": re.compile("^/book/")}):
                    ref = ts.get("href")
                    link = f"https://b-ok.cc{ref}"

                f.write("\n" + title)
                f.write("\nʙᴏᴏᴋ ʟɪɴᴋ:- " + link + "\n\n")

        f.write(f"ʙʏ @{BOT_USERNAME}.")
        f.close()
        caption = f"ᴇxᴏɴ  \nᴊᴏɪɴ sᴜᴘᴘᴏʀᴛ @{SUPPORT_CHAT} "

        await telethn.send_file(
            event.chat_id,
            "book.txt",
            caption=f"**BOOKS GATHERED SUCCESSFULLY!\n\nBY @ABISHNOIMF **",
        )
        os.remove("book.txt")
        await KkK.delete()
