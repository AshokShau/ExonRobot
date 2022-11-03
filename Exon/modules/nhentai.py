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
from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from Exon import BOT_USERNAME, pgram, telegraph
from Exon.utils.errors import capture_err


@pgram.on_message(~filters.me & filters.command("nhentai", prefixes="/"), group=8)
@capture_err
async def nhentai(client, message):
    query = message.text.split(" ")[1]
    title, tags, artist, total_pages, post_url, cover_image = nhentai_data(query)
    await message.reply_text(
        f"<code>{title}</code>\n\n<b>Tags:</b>\n{tags}\n<b>Artists:</b>\n{artist}\n<b>Pages:</b>\n{total_pages}",
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("ʀᴇᴀᴅ ʜᴇʀᴇ", url=post_url)]]
        ),
    )


def nhentai_data(noombers):
    url = f"https://nhentai.net/api/gallery/{noombers}"
    res = requests.get(url).json()
    pages = res["images"]["pages"]
    info = res["tags"]
    title = res["title"]["english"]
    links = []
    tags = ""
    artist = ""
    total_pages = res["num_pages"]
    extensions = {"j": "jpg", "p": "png", "g": "gif"}
    for i, x in enumerate(pages):
        media_id = res["media_id"]
        temp = x["t"]
        file = f"{i+1}.{extensions[temp]}"
        link = f"https://i.nhentai.net/galleries/{media_id}/{file}"
        links.append(link)

    for i in info:
        if i["type"] == "tag":
            tag = i["name"]
            tag = tag.split(" ")
            tag = "_".join(tag)
            tags += f"#{tag} "
        if i["type"] == "artist":
            artist = f"{i['name']} "

    post_content = "".join(f"<img src={link}><br>" for link in links)

    post = telegraph.create_page(
        f"{title}",
        html_content=post_content,
        author_name="ɪᴛs ᴍᴇ",
        author_url=f"https://t.me/{BOT_USERNAME}",
    )
    return title, tags, artist, total_pages, post["url"], links[0]
