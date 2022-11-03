"""
MIT License

Copyright (c) 2022 ABISHNOI

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
#     MY ALL BOTS :- Abishnoi_bots
#     GITHUB :- KingAbishnoi ""

import json
import socket
import sys
from random import randint
from time import time

import aiohttp
from googletrans import Translator
from motor import version as mongover
from pykeyboard import InlineKeyboard
from pyrogram import __version__ as pyrover
from pyrogram.raw.functions import Ping
from pyrogram.types import (
    InlineKeyboardButton,
    InlineQueryResultArticle,
    InlineQueryResultPhoto,
    InputTextMessageContent,
)
from search_engine_parser import GoogleSearch

from Exon import BOT_USERNAME, OWNER_ID
from Exon import OWNER_USERNAME as AK_BOSS
from Exon import arq, pgram
from Exon.utils.pluginhelpers import convert_seconds_to_minutes as time_convert
from Exon.utils.pluginhelpers import fetch

SUDOERS = OWNER_ID
app = pgram


async def _netcat(host, port, content):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, int(port)))
    s.sendall(content.encode())
    s.shutdown(socket.SHUT_WR)
    while True:
        data = s.recv(4096).decode("utf-8").strip("\n\x00")
        if not data:
            break
        return data
    s.close()


async def paste(content):
    link = await _netcat("ezup.dev", 9999, content)
    return link


async def inline_help_func(__HELP__):
    buttons = InlineKeyboard(row_width=2)
    buttons.add(
        InlineKeyboardButton("ɢᴇᴛ ᴍᴏʀᴇ ʜᴇʟᴘ.", url=f"t.me/{BOT_USERNAME}?start=start"),
        InlineKeyboardButton("ɢᴏ ɪɴʟɪɴᴇ!", switch_inline_query_current_chat=""),
    )
    answerss = [
        InlineQueryResultArticle(
            title="ɪɴʟɪɴᴇ ᴄᴏᴍᴍᴀɴᴅs",
            description="ʜᴇʟᴘ ʀᴇʟᴀᴛᴇᴅ ᴛᴏ ɪɴʟɪɴᴇ ᴜsᴀɢᴇ.",
            input_message_content=InputTextMessageContent(__HELP__),
            thumb_url="https://telegra.ph/file/03264297589e442200052.jpg",
            reply_markup=buttons,
        )
    ]
    answerss = await alive_function(answerss)
    return answerss


async def alive_function(answers):
    buttons = InlineKeyboard(row_width=2)
    bot_state = "ᴅᴇᴀᴅ" if not await app.get_me() else "ᴀʟɪᴠᴇ"
    # ubot_state = 'Dead' if not await app2.get_me() else 'Alive'
    buttons.add(
        InlineKeyboardButton("ᴍᴀɪɴ ʙᴏᴛ", url="https://t.me/{BOT_USERNAME}"),
        InlineKeyboardButton("ɢᴏ ɪɴʟɪɴᴇ!", switch_inline_query_current_chat=""),
    )

    msg = f"""
**ᴍᴀɪɴʙᴏᴛ:** `{bot_state}`
**ᴜsᴇʀʙᴏᴛ:** `Alive`
**ᴘʏᴛʜᴏɴ:** `3.9`
**ᴘʏʀᴏɢʀᴀᴍ:** `{pyrover}`
**ᴍᴏɴɢᴏᴅʙ:** `{mongover}`
**ᴘʟᴀᴛғᴏʀᴍ:** `{sys.platform}`
**ᴘʀᴏғɪʟᴇs:** [BOT](t.me/{BOT_USERNAME}) | [Owner](t.me/{AK_BOSS})
"""
    answers.append(
        InlineQueryResultArticle(
            title="ᴀʟɪᴠᴇ",
            description="ᴄʜᴇᴄᴋ ʙᴏᴛ sᴛᴀᴛs",
            thumb_url="https://telegra.ph/file/03264297589e442200052.jpg",
            input_message_content=InputTextMessageContent(
                msg, disable_web_page_preview=True
            ),
            reply_markup=buttons,
        )
    )
    return answers


async def webss(url):
    start_time = time()
    if "." not in url:
        return
    screenshot = await fetch(f"https://patheticprogrammers.cf/ss?site={url}")
    end_time = time()
    # m = await app.send_photo(LOG_GROUP_ID, photo=screenshot["url"])
    await m.delete()
    a = []
    pic = InlineQueryResultPhoto(
        photo_url=screenshot["url"],
        caption=(f"`{url}`\n__ᴛᴏᴏᴋ {round(end_time - start_time)} sᴇᴄᴏɴᴅs.__"),
    )
    a.append(pic)
    return a


async def translate_func(answers, lang, tex):
    i = Translator().translate(tex, dest=lang)
    msg = f"""
__**Translated from {i.src} to {lang}**__
**ɪɴᴘᴜᴛ:**
{tex}
**ᴏᴜᴛᴘᴜᴛ:**
{i.text}"""
    answers.extend(
        [
            InlineQueryResultArticle(
                title=f"ᴛʀᴀɴsʟᴀᴛᴇᴅ ғʀᴏᴍ {i.src} ᴛᴏ {lang}.",
                description=i.text,
                input_message_content=InputTextMessageContent(msg),
            ),
            InlineQueryResultArticle(
                title=i.text, input_message_content=InputTextMessageContent(i.text)
            ),
        ]
    )
    return answers


async def urban_func(answers, text):
    results = await arq.urbandict(text)
    if not results.ok:
        answers.append(
            InlineQueryResultArticle(
                title="ᴇʀʀᴏʀ",
                description=results.result,
                input_message_content=InputTextMessageContent(results.result),
            )
        )
        return answers
    results = results.result
    limit = 0
    for i in results:
        if limit > 48:
            break
        limit += 1
        msg = f"""
**ǫᴜᴇʀʏ:** {text}
**ᴅᴇғɪɴɪᴛɪᴏɴ:** __{i.definition}__
**ᴇxᴀᴍᴘʟᴇ:** __{i.example}__"""

        answers.append(
            InlineQueryResultArticle(
                title=i.word,
                description=i.definition,
                input_message_content=InputTextMessageContent(msg),
            )
        )
    return answers


async def google_search_func(answers, text):
    gresults = await GoogleSearch().async_search(text)
    limit = 0
    for i in gresults:
        if limit > 48:
            break
        limit += 1

        try:
            msg = f"""
[{i['titles']}]({i['links']})
{i['descriptions']}"""

            answers.append(
                InlineQueryResultArticle(
                    title=i["titles"],
                    description=i["descriptions"],
                    input_message_content=InputTextMessageContent(
                        msg, disable_web_page_preview=True
                    ),
                )
            )
        except KeyError:
            pass
    return answers


async def wall_func(answers, text):
    results = await arq.wall(text)
    if not results.ok:
        answers.append(
            InlineQueryResultArticle(
                title="ᴇʀʀᴏʀ",
                description=results.result,
                input_message_content=InputTextMessageContent(results.result),
            )
        )
        return answers
    limit = 0
    results = results.result
    for i in results:
        if limit > 48:
            break
        limit += 1
        answers.append(
            InlineQueryResultPhoto(
                photo_url=i.url_image,
                thumb_url=i.url_thumb,
                caption=f"[sᴏᴜʀᴄᴇ]({i.url_image})",
            )
        )
    return answers


async def saavn_func(answers, text):
    buttons_list = []
    results = await arq.saavn(text)
    if not results.ok:
        answers.append(
            InlineQueryResultArticle(
                title="ᴇʀʀᴏʀ",
                description=results.result,
                input_message_content=InputTextMessageContent(results.result),
            )
        )
        return answers
    results = results.result
    for count, i in enumerate(results):
        buttons = InlineKeyboard(row_width=1)
        buttons.add(InlineKeyboardButton("ᴅᴏᴡɴʟᴏᴀᴅ | ᴘʟᴀʏ", url=i.media_url))
        buttons_list.append(buttons)
        duration = await time_convert(i.duration)
        caption = f"""
**ᴛɪᴛʟᴇ:** {i.song}
**ᴀʟʙᴜᴍ:** {i.album}
**ᴅᴜʀᴀᴛɪᴏɴ:** {duration}
**ʀᴇʟᴇᴀsᴇ:** {i.year}
**sɪɴɢᴇʀs:** {i.singers}"""
        description = f"{i.album} | {duration} " + f"| {i.singers} ({i.year})"
        answers.append(
            InlineQueryResultArticle(
                title=i.song,
                input_message_content=InputTextMessageContent(
                    caption, disable_web_page_preview=True
                ),
                description=description,
                thumb_url=i.image,
                reply_markup=buttons_list[count],
            )
        )
    return answers


async def paste_func(answers, text):
    start_time = time()
    url = await paste(text)
    msg = f"__**{url}**__"
    end_time = time()
    answers.append(
        InlineQueryResultArticle(
            title=f"ᴘᴀsᴛᴇᴅ ɪɴ {round(end_time - start_time)} sᴇᴄᴏɴᴅs.",
            description=url,
            input_message_content=InputTextMessageContent(msg),
        )
    )
    return answers


async def deezer_func(answers, text):
    buttons_list = []
    results = await arq.deezer(text, 5)
    if not results.ok:
        answers.append(
            InlineQueryResultArticle(
                title="ᴇʀʀᴏʀ",
                description=results.result,
                input_message_content=InputTextMessageContent(results.result),
            )
        )
        return answers
    results = results.result
    for count, i in enumerate(results):
        buttons = InlineKeyboard(row_width=1)
        buttons.add(InlineKeyboardButton("ᴅᴏᴡɴʟᴏᴀᴅ | ᴘʟᴀʏ", url=i.url))
        buttons_list.append(buttons)
        duration = await time_convert(i.duration)
        caption = f"""
**ᴛɪᴛʟᴇ:** {i.title}
**ᴀʀᴛɪsᴛ:** {i.artist}
**ᴅᴜʀᴀᴛɪᴏɴ:** {duration}
**sᴏᴜʀᴄᴇ:** [Deezer]({i.source})"""
        description = f"{i.artist} | {duration}"
        answers.append(
            InlineQueryResultArticle(
                title=i.title,
                thumb_url=i.thumbnail,
                description=description,
                input_message_content=InputTextMessageContent(
                    caption, disable_web_page_preview=True
                ),
                reply_markup=buttons_list[count],
            )
        )
    return answers


# Used my api key here, don't fuck with it
async def shortify(url):
    if "." not in url:
        return
    header = {
        "Authorization": "Bearer ad39983fa42d0b19e4534f33671629a4940298dc",
        "Content-Type": "application/json",
    }
    payload = {"long_url": f"{url}"}
    payload = json.dumps(payload)
    async with aiohttp.ClientSession() as session, session.post(
        "https://api-ssl.bitly.com/v4/shorten", headers=header, data=payload
    ) as resp:
        data = await resp.json()
    msg = data["link"]
    a = []
    b = InlineQueryResultArticle(
        title="ʟɪɴᴋ sʜᴏʀᴛᴇɴᴇᴅ!",
        description=data["link"],
        input_message_content=InputTextMessageContent(
            msg, disable_web_page_preview=True
        ),
    )
    a.append(b)
    return a


async def torrent_func(answers, text):
    results = await arq.torrent(text)
    if not results.ok:
        answers.append(
            InlineQueryResultArticle(
                title="ᴇʀʀᴏʀ",
                description=results.result,
                input_message_content=InputTextMessageContent(results.result),
            )
        )
        return answers
    limit = 0
    results = results.result
    for i in results:
        if limit > 48:
            break
        title = i.name
        size = i.size
        seeds = i.seeds
        leechs = i.leechs
        upload_date = i.uploaded + " Ago"
        magnet = i.magnet
        caption = f"""
**ᴛɪᴛʟᴇ:** __{title}__
**sɪᴢᴇ:** __{size}__
**sᴇᴇᴅs:** __{seeds}__
**ʟᴇᴇᴄʜs:** __{leechs}__
**ᴜᴘʟᴏᴀᴅᴇᴅ:** __{upload_date}__
**ᴍᴀɢɴᴇᴛ:** `{magnet}`"""

        description = f"{size} | {upload_date} | Seeds: {seeds}"
        answers.append(
            InlineQueryResultArticle(
                title=title,
                description=description,
                input_message_content=InputTextMessageContent(
                    caption, disable_web_page_preview=True
                ),
            )
        )
        limit += 1
    return answers


async def wiki_func(answers, text):
    data = await arq.wiki(text)
    if not data.ok:
        answers.append(
            InlineQueryResultArticle(
                title="ᴇʀʀᴏʀ",
                description=data.result,
                input_message_content=InputTextMessageContent(data.result),
            )
        )
        return answers
    data = data.result
    msg = f"""
**ǫᴜᴇʀʏ:**
{data.title}
**ᴀɴsᴡᴇʀ:**
__{data.answer}__"""
    answers.append(
        InlineQueryResultArticle(
            title=data.title,
            description=data.answer,
            input_message_content=InputTextMessageContent(msg),
        )
    )
    return answers


async def ping_func(answers):
    t1 = time()
    ping = Ping(ping_id=randint(696969, 6969696))
    await app.send(ping)
    t2 = time()
    ping = f"{str(round((t2 - t1), 2))} sᴇᴄᴏɴᴅs"
    answers.append(
        InlineQueryResultArticle(
            title=ping, input_message_content=InputTextMessageContent(f"__**{ping}**__")
        )
    )
    return answers


async def pokedexinfo(answers, pokemon):
    Pokemon = f"https://some-random-api.ml/pokedex?pokemon={pokemon}"
    result = await fetch(Pokemon)
    buttons = InlineKeyboard(row_width=1)
    buttons.add(
        InlineKeyboardButton("ᴘᴏᴋᴇᴅᴇx", switch_inline_query_current_chat="pokedex")
    )
    caption = f"""
**ᴘᴏᴋᴇᴍᴏɴ:** `{result['name']}`
**ᴘᴏᴋᴇᴅᴇx:** `{result['id']}`
**ᴛʏᴘᴇ:** `{result['type']}`
**ᴀʙɪʟɪᴛɪᴇs:** `{result['abilities']}`
**ʜᴇɪɢʜᴛ:** `{result['height']}`
**ᴡᴇɪɢʜᴛ:** `{result['weight']}`
**ɢᴇɴᴅᴇʀ:** `{result['gender']}`
**sᴛᴀᴛs:** `{result['stats']}`
**ᴅᴇsᴄʀɪᴘᴛɪᴏɴ:** `{result['description']}`"""
    answers.append(
        InlineQueryResultPhoto(
            photo_url=f"https://img.pokemondb.net/artwork/large/{pokemon}.jpg",
            title=result["name"],
            description=result["description"],
            caption=caption,
            reply_markup=buttons,
        )
    )
    return answers
