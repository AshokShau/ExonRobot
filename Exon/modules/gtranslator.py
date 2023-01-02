import os

from gpytranslate import Translator
from gtts import gTTS
from mutagen.mp3 import MP3
from pyrogram import filters

from Exon import app as Abishnoi
from Exon import register as Asubot


@Asubot(pattern="^/tts ?(.*)")
async def tts(event):
    if not event.reply_to_msg_id and event.pattern_match.group(1):
        text = event.text.split(None, 1)[1]
        _total = text.split(None, 1)
        if len(_total) == 2:
            lang = (_total[0]).lower()
            text = _total[1]
        else:
            lang = "en"
            text = _total[0]
    elif event.reply_to_msg_id:
        text = (await event.get_reply_message()).text
        if event.pattern_match.group(1):
            lang = (event.pattern_match.group(1)).lower()
        else:
            lang = "en"
    else:
        return await event.reply(
            "`/tts <ʟᴀɴɢᴜᴀɢᴇ ᴄᴏᴅᴇ>` ᴀs ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴍᴇssᴀɢᴇ ᴏʀ `/tts <ʟᴀɴɢᴜᴀɢᴇ ᴄᴏᴅᴇ> <text>`",
        )
    try:
        tts = gTTS(text, tld="com", lang=lang)
        tts.save("exon-tts.mp3")
    except BaseException as e:
        return await event.reply(str(e))
    aud_len = int((MP3("exon-tts.mp3")).info.length)
    if aud_len == 0:
        aud_len = 1
    async with Rani.action(event.chat_id, "record-voice"):
        await event.respond(
            file="exon-tts.mp3",
            attributes=[
                DocumentAttributeAudio(
                    duration=aud_len,
                    title=f"stt_{lang}",
                    performer="rani_form",
                    waveform="320",
                )
            ],
        )
        os.remove("exon-tts.mp3")


@Abishnoi.on_message(filters.command(["tr", "tl"]))
async def tr(_, message):
    trl = Translator()
    if message.reply_to_message and (
        message.reply_to_message.text or message.reply_to_message.caption
    ):
        if len(message.text.split()) == 1:
            target_lang = "en"
        else:
            target_lang = message.text.split()[1]
        if message.reply_to_message.text:
            text = message.reply_to_message.text
        else:
            text = message.reply_to_message.caption
    else:
        if len(message.text.split()) <= 2:
            await message.reply_text(
                "ᴘʀᴏᴠɪᴅᴇ ʟᴀɴɢ ᴄᴏᴅᴇ.\n[ᴀᴠᴀɪʟᴀʙʟᴇ ᴏᴘᴛɪᴏɴs](https://telegra.ph/ɪᴛs-ᴍᴇ-𒆜-Aʙɪsʜɴᴏɪ-07-30-2).\n<b>ᴜsᴀɢᴇ:</b> <code>/tr en</code>",
            )
            return
        target_lang = message.text.split(None, 2)[1]
        text = message.text.split(None, 2)[2]
    detectlang = await trl.detect(text)
    try:
        tekstr = await trl(text, targetlang=target_lang)
    except ValueError as err:
        await message.reply_text(f"ᴇʀʀᴏʀ: <code>{str(err)}</code>")
        return
    return await message.reply_text(
        f"<b>ᴛʀᴀɴsʟᴀᴛᴇᴅ:</b> ғʀᴏᴍ {detectlang} ᴛᴏ {target_lang} \n<code>``{tekstr.text}``</code>",
    )


__help__ = """
❍ /tr or /tl (ʟᴀɴɢᴜᴀɢᴇ ᴄᴏᴅᴇ) ᴀs ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴍᴇssᴀɢᴇ

*ᴇxᴀᴍᴘʟᴇ:* 
❍ /tr en*:* ᴛʀᴀɴsʟᴀᴛᴇs sᴏᴍᴇᴛʜɪɴɢ ᴛᴏ ᴇɴɢʟɪsʜ
❍ /tr hi-en*:* ᴛʀᴀɴsʟᴀᴛᴇs ʜɪɴᴅɪ ᴛᴏ ᴇɴɢʟɪsʜ
❍ /tts *:* ᴛᴇxᴛ ᴛᴏ sᴘᴇᴀᴋ

[ʟᴀɴɢᴜᴀɢᴇ ᴄᴏᴅᴇs](https://telegra.ph/ɪᴛs-ᴍᴇ-𒆜-Aʙɪsʜɴᴏɪ-07-30-2)
"""
__mod_name__ = "𝐓ʀᴀɴsʟᴀᴛᴏʀ"
