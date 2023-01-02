from gpytranslate import Translator

from Exon import app as Abishnoi


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

[ʟᴀɴɢᴜᴀɢᴇ ᴄᴏᴅᴇs](https://telegra.ph/ɪᴛs-ᴍᴇ-𒆜-Aʙɪsʜɴᴏɪ-07-30-2)
"""
__mod_name__ = "𝐓ʀᴀɴsʟᴀᴛᴏʀ"
