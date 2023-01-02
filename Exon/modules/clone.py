import re

from pyrogram import Client, filters, idle

from Exon import API_HASH, API_ID, app


# ᴊᴜsᴛ ᴛᴇsᴛ ᴀɴᴅ .....
@app.on_message((filters.regex(r"\d[0-9]{8,10}:[0-9A-Za-z_-]{35}")) & filters.private)
async def on_clone(self, message):
    message.from_user.id
    bot_token = re.findall(
        r"\d[0-9]{8,10}:[0-9A-Za-z_-]{35}", message.text, re.IGNORECASE
    )
    bot_token = bot_token[0] if bot_token else None
    bot_id = re.findall(r"\d[0-9]{8,10}", message.text)

    if not str(message.forward_from.id) != "93372553":
        msg = await message.reply_text(
            f"🔑 <code>{bot_token}</code>\n\nᴄᴏᴘʏɪɴɢ sʏsᴛᴇᴍ..."
        )
        try:
            ai = Client(
                f"{bot_token}",
                API_ID,
                API_HASH,
                bot_token=bot_token,
                plugins=dict(root="Exon.modules"),
                in_memory=True,
            )
            await ai.start()
            await idle()
            randi = await ai.get_me()
            await msg.edit_text(
                f"✅ @{randi.username} \n\nʜᴀs ʙᴇᴇɴ ᴄʟᴏɴᴇᴅ sᴜᴄᴄᴇssғᴜʟʟʏ! ᴅᴏɴ'ᴛ ɢɪᴠᴇ ᴛʜᴇ ʙᴏᴛ ᴛᴏᴋᴇɴ ᴛᴏ ᴀɴʏᴏɴᴇ, ʙᴇᴄᴀᴜsᴇ ᴛʜᴇʏ ᴄᴀɴ ᴄᴏɴᴛʀᴏʟ ʏᴏᴜʀ ʙᴏᴛ ᴛʜʀᴏᴜɢʜ ᴛʜᴇ ᴛʜɪʀᴅ ᴘᴀʀᴛʏ ᴏғ ᴛᴇʟᴇɢʀᴀᴍ ᴄʟɪᴇɴᴛ."
            )
        except BaseException as err:
            await msg.edit_text(
                f"⚠️ <b>ʙᴏᴛ ᴇʀʀᴏʀ:</b>\n\n<code>{err}</code>\n\n❔ ғᴏʀᴡᴀʀᴅ ᴛʜɪs ᴍᴇssᴀɢᴇ ᴛᴏ @Abishnoi1M ᴛᴏ ʙᴇ ғɪxᴇᴅ."
            )
