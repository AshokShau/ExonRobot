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

import datetime
import os
from asyncio import get_running_loop
from functools import partial
from io import BytesIO

from pyrogram import filters
from pytube import YouTube
from requests import get

from Exon import aiohttpsession as session
from Exon import arq, pgram
from Exon.core.decorators.errors import capture_err
from Exon.utils.pastebin import paste

is_downloading = False


def download_youtube_audio(arq_resp):
    r = arq_resp.result[0]

    title = r.title
    performer = r.channel

    m, s = r.duration.split(":")
    duration = int(datetime.timedelta(minutes=int(m), seconds=int(s)).total_seconds())

    if duration > 1800:
        return

    thumb = get(r.thumbnails[0]).content
    with open("thumbnail.png", "wb") as f:
        f.write(thumb)
    thumbnail_file = "thumbnail.png"

    url = f"https://youtube.com{r.url_suffix}"
    yt = YouTube(url)
    audio = yt.streams.filter(only_audio=True).get_audio_only()

    out_file = audio.download()
    base, _ = os.path.splitext(out_file)
    audio_file = base + ".mp3"
    os.rename(out_file, audio_file)

    return [title, performer, duration, audio_file, thumbnail_file]


@pgram.on_message(filters.command("song") & ~filters.edited)
@capture_err
async def music(_, message):
    global is_downloading
    if len(message.command) < 2:
        return await message.reply_text("/song ɴᴇᴇᴅs a ǫᴜᴇʀʏ ᴀs ᴀʀɢᴜᴍᴇɴᴛ")

    url = message.text.split(None, 1)[1]
    if is_downloading:
        return await message.reply_text(
            "ᴀɴᴏᴛʜᴇʀ ᴅᴏᴡɴʟᴏᴀᴅ ɪs ɪɴ ᴘʀᴏɢʀᴇss, ᴛʀʏ ᴀɢᴀɪɴ ᴀғᴛᴇʀ sᴏᴍᴇᴛɪᴍᴇ."
        )
    is_downloading = True
    m = await message.reply_text(f"ᴅᴏᴡɴʟᴏᴀᴅɪɴɢ.. {url}", disable_web_page_preview=True)
    try:
        loop = get_running_loop()
        arq_resp = await arq.youtube(url)
        music = await loop.run_in_executor(
            None, partial(download_youtube_audio, arq_resp)
        )

        if not music:
            return await message.reply_text("[ᴇʀʀᴏʀ]: ᴍᴜsɪᴄ ᴛᴏᴏ ʟᴏɴɢ")
        (
            title,
            performer,
            duration,
            audio_file,
            thumbnail_file,
        ) = music
    except Exception as e:
        is_downloading = False
        return await m.edit(str(e))
    await message.reply_audio(
        audio_file,
        duration=duration,
        performer=performer,
        title=title,
        thumb=thumbnail_file,
    )
    await m.delete()
    os.remove(audio_file)
    os.remove(thumbnail_file)
    is_downloading = False


# Funtion To Download Song
async def download_song(url):
    async with session.get(url) as resp:
        song = await resp.read()
    song = BytesIO(song)
    song.name = "a.mp3"
    return song


@pgram.on_message(filters.command("lyrics") & ~filters.edited)
async def lyrics_func(_, message):
    if len(message.command) < 2:
        return await message.reply_text("**ᴜsᴀɢᴇ:**\n/lyrics [QUERY]")
    m = await message.reply_text("**sᴇᴀʀᴄʜɪɴɢ**")
    query = message.text.strip().split(None, 1)[1]

    resp = await arq.lyrics(query)

    if not (resp.ok and resp.result):
        return await m.edit("ɴᴏ ʟʏʀɪᴄs ғᴏᴜɴᴅ.")

    song = resp.result[0]
    song_name = song["song"]
    artist = song["artist"]
    lyrics = song["lyrics"]
    msg = f"**{song_name}** | **{artist}**\n\n__{lyrics}__"

    if len(msg) > 4095:
        msg = await paste(msg)
        msg = f"**ʟʏʀɪᴄs_ᴛᴏᴏ_ʟᴏɴɢ:** [ᴜʀʟ]({msg})"
    return await m.edit(msg)
