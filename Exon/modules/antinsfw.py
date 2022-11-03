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

from os import remove

from pyrogram import filters

from Exon import BOT_USERNAME, DRAGONS, arq, pgram
from Exon.modules.mongo.nsfw_mongo import is_nsfw_on, nsfw_off, nsfw_on
from Exon.utils.errors import capture_err
from Exon.utils.permissions import adminsOnly


async def get_file_id_from_message(message):
    file_id = None
    if message.document:
        if int(message.document.file_size) > 3145728:
            return
        mime_type = message.document.mime_type
        if mime_type not in ("image/png", "image/jpeg"):
            return
        file_id = message.document.file_id

    if message.sticker:
        if message.sticker.is_animated:
            if not message.sticker.thumbs:
                return
            file_id = message.sticker.thumbs[0].file_id
        else:
            file_id = message.sticker.file_id

    if message.photo:
        file_id = message.photo.file_id

    if message.animation:
        if not message.animation.thumbs:
            return
        file_id = message.animation.thumbs[0].file_id

    if message.video:
        if not message.video.thumbs:
            return
        file_id = message.video.thumbs[0].file_id
    return file_id


@pgram.on_message(
    (
        filters.document
        | filters.photo
        | filters.sticker
        | filters.animation
        | filters.video
    )
    & ~filters.private,
    group=8,
)
@capture_err
async def detect_nsfw(_, message):
    if not await is_nsfw_on(message.chat.id):
        return
    if not message.from_user:
        return
    file_id = await get_file_id_from_message(message)
    if not file_id:
        return
    file = await pgram.download_media(file_id)
    try:
        results = await arq.nsfw_scan(file=file)
    except Exception:
        return
    if not results.ok:
        return
    results = results.result
    remove(file)
    nsfw = results.is_nsfw
    if message.from_user.id in DRAGONS:
        return
    if not nsfw:
        return
    try:
        await message.delete()
    except Exception:
        return
    await message.reply_text(
        f"""
**ɴsғᴡ ɪᴍᴀɢᴇ ᴅᴇᴛᴇᴄᴛᴇᴅ & ᴅᴇʟᴇᴛᴇᴅ sᴜᴄᴄᴇssғᴜʟʟʏ!**

**𝗨𝘀𝗲𝗿:** {message.from_user.mention} [`{message.from_user.id}`]
**𝗦𝗮𝗳𝗲:** `{results.neutral} %`
**𝗣𝗼𝗿𝗻:** `{results.porn} %`
**𝗔𝗱𝘂𝗹𝘁:** `{results.sexy} %`
**𝗛𝗲𝗻𝘁𝗮𝗶:** `{results.hentai} %`
**𝗗𝗿𝗮𝘄𝗶𝗻𝗴𝘀:** `{results.drawings} %`

"""
    )


@pgram.on_message(filters.command(["pscan", f"pscan@{BOT_USERNAME}"]))
@capture_err
async def nsfw_scan_command(_, message):
    if not message.reply_to_message:
        await message.reply_text(
            "ʀᴇᴘʟʏ ᴛᴏ ᴀɴ ɪᴍᴀɢᴇ/ᴅᴏᴄᴜᴍᴇɴᴛ/sᴛɪᴄᴋᴇʀ/ᴀɴɪᴍᴀᴛɪᴏɴ ᴛᴏ sᴄᴀɴ ɪᴛ."
        )
        return
    reply = message.reply_to_message
    if (
        not reply.document
        and not reply.photo
        and not reply.sticker
        and not reply.animation
        and not reply.video
    ):
        await message.reply_text(
            "ʀᴇᴘʟʏ ᴛᴏ ᴀɴ ɪᴍᴀɢᴇ/ᴅᴏᴄᴜᴍᴇɴᴛ/sᴛɪᴄᴋᴇʀ/ᴀɴɪᴍᴀᴛɪᴏɴ ᴛᴏ sᴄᴀɴ ɪᴛ."
        )
        return
    m = await message.reply_text("sᴄᴀɴɴɪɴɢ..")
    file_id = await get_file_id_from_message(reply)
    if not file_id:
        return await m.edit("sᴏᴍᴇᴛʜɪɴɢ ᴡʀᴏɴɢ ʜᴀᴘᴘᴇɴᴇᴅ.")
    file = await pgram.download_media(file_id)
    try:
        results = await arq.nsfw_scan(file=file)
    except Exception:
        return
    remove(file)
    if not results.ok:
        return await m.edit(results.result)
    results = results.result
    await m.edit(
        f"""
**𝗡𝗲𝘂𝘁𝗿𝗮𝗹:** `{results.neutral} %`
**𝗣𝗼𝗿𝗻:** `{results.porn} %`
**𝗛𝗲𝗻𝘁𝗮𝗶:** `{results.hentai} %`
**𝗦𝗲𝘅𝘆:** `{results.sexy} %`
**𝗗𝗿𝗮𝘄𝗶𝗻𝗴𝘀:** `{results.drawings} %`
**𝗡𝗦𝗙𝗪:** `{results.is_nsfw}`
"""
    )


@pgram.on_message(
    filters.command(["antiporn", f"antiporn@{BOT_USERNAME}"]) & ~filters.private
)
@adminsOnly("can_change_info")
async def nsfw_enable_disable(_, message):
    if len(message.command) != 2:
        await message.reply_text("ᴜsᴀɢᴇ: /antiporn [on/off]")
        return
    status = message.text.split(None, 1)[1].strip()
    status = status.lower()
    chat_id = message.chat.id
    if status in ("on", "yes"):
        await nsfw_on(chat_id)
        await message.reply_text(
            "ᴇɴᴀʙʟᴇᴅ ᴀɴᴛɪ-ᴘᴏʀɴ  sʏsᴛᴇᴍ. I ᴡɪʟʟ ᴅᴇʟᴇᴛᴇ ᴍᴇssᴀɢᴇs ᴄᴏɴᴛᴀɪɴɪɴɢ ɪɴᴀᴘᴘʀᴏᴘʀɪᴀᴛᴇ ᴄᴏɴᴛᴇɴᴛ."
        )
    elif status in ("off", "no"):
        await nsfw_off(chat_id)
        await message.reply_text("ᴅɪsᴀʙʟᴇᴅ ᴀɴᴛɪ-ᴘᴏʀɴ sʏsᴛᴇᴍ.")
    else:
        await message.reply_text("ᴜɴᴋɴᴏᴡɴ sᴜғғɪx, ᴜsᴇ /antiporn [on/off]")


__mod_name__ = "𝙿ᴏʀɴ"


__help__ = """
*ᴀɴᴛɪ ᴘᴏʀɴ sʏsᴛᴇᴍ*

/antiporn <oɴ> *:* `ᴇɴᴀʙʟᴇᴅ ᴀɴᴛɪɴsғᴡ` *ᴀɴᴛɪᴘᴏʀɴ* `sʏsᴛᴇᴍ. ʙᴏᴛ ᴡɪʟʟ ᴅᴇʟᴇᴛᴇ ᴍᴇssᴀɢᴇs ᴄᴏɴᴛᴀɪɴɪɴɢ ɪɴᴀᴘᴘʀᴏᴘʀɪᴀᴛᴇ ᴄᴏɴᴛᴇɴᴛ` [ᴅᴇғᴇᴀᴛ ᴏɴ]

/antiporn <ᴏғғ> *:* `sᴀʟᴇ ᴏғғ ʜɪ ǫ ᴋᴀᴇ ɴᴀ ʙ ᴏɴ ᴋᴀʀ ᴅᴇ`

/pscan *:* `ʀᴇᴘʟʏ ᴛᴏ ᴀɴ ɪᴍᴀɢᴇ/ᴅᴏᴄᴜᴍᴇɴᴛ/sᴛɪᴄᴋᴇʀ/ᴀɴɪᴍᴀᴛɪᴏɴ ᴛᴏ sᴄᴀɴ ɪᴛ`

"""
