from random import randint

import requests
from pyrogram import enums, filters

from Exon import SUPPORT_CHAT, BOT_NAME
from Exon import app as abishnoi


@abishnoi.on_message(filters.command(["wallpaper"]))
async def wall(_, msg):
    if len(msg.command) < 2:
        await msg.reply_text("ʜᴇʏ ʙᴀʙʏ ɢɪᴠᴇ sᴏᴍᴇᴛʜɪɴɢ ᴛᴏ sᴇᴀʀᴄʜ.")
        return
    else:
        pass

    query = (
        msg.text.split(None, 1)[1]
        if len(msg.command) < 3
        else msg.text.split(None, 1)[1].replace(" ", "%20")
    )

    if not query:
        await msg.reply_text("ʜᴇʏ ʙᴀʙʏ ɢɪᴠᴇ sᴏᴍᴇᴛʜɪɴɢ ᴛᴏ sᴇᴀʀᴄʜ.")
    else:
        pass

    url = f"https://api.safone.me/wall?query={query}"
    re = requests.get(url).json()
    walls = re.get("results")
    if not walls:
        await msg.reply_text("ɴᴏ ʀᴇsᴜʟᴛs ғᴏᴜɴᴅ! ")
        return
    wall_index = randint(0, len(walls) - 1)
    wallpaper = walls[wall_index]
    wallpaper.get("imageUrl")
    preview = wallpaper.get("thumbUrl")
    title = wallpaper.get("title")
    try:
        await abishnoi.send_chat_action(msg.chat.id, enums.ChatAction.UPLOAD_PHOTO)
        await msg.reply_photo(
            preview,
            caption=f"🔎 ᴛɪᴛʟᴇ - {title}\nᴊᴏɪɴ [{BOT_NAME}](t.me/{SUPPORT_CHAT})",
        )
    # await msg.reply_document(pic, caption=f"🔎 ᴛɪᴛʟᴇ - {title} \n🥀 **ʀᴇǫᴜᴇsᴛᴇᴅ ʙʏ :** {msg.from_user.mention}")
    except Exception as error:
        await msg.reply_text(f"ᴀɴ ᴇʀʀᴏʀ ᴏᴄᴄᴜʀᴇᴅ.\n{error}")


__help__ = """
 /wallpaper blackpink *:* ɢᴇᴛ ᴀ ᴡᴀʟʟᴘᴀᴘᴇʀ
"""
__mod_name__ = "𝐖ᴀʟʟ"
