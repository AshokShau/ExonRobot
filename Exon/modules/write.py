from pyrogram import filters
from pyrogram.types import Message

from Exon import pgram


@pgram.on_message(filters.command("write"))
async def handwrite(_, message: Message):
    if not message.reply_to_message:
        name = (
            message.text.split(None, 1)[1]
            if len(message.command) < 3
            else message.text.split(None, 1)[1].replace(" ", "%20")
        )
        m = await pgram.send_message(message.chat.id, "waito...")
        photo = "https://apis.xditya.me/write?text=" + name
        await pgram.send_photo(message.chat.id, photo=photo)
        await m.delete()
    else:
        lol = message.reply_to_message.text
        name = lol.split(None, 0)[0].replace(" ", "%20")
        m = await pgram.send_message(message.chat.id, "waito..")
        photo = "https://apis.xditya.me/write?text=" + name
        await pgram.send_photo(message.chat.id, photo=photo)
        await m.delete()


__mod_name__ = "𝚆ʀɪᴛᴇ"

__help__ = """

ᴡʀɪᴛᴇs ᴛʜᴇ ɢɪᴠᴇɴ ᴛᴇxᴛ ᴏɴ ᴡʜɪᴛᴇ ᴘᴀɢᴇ ᴡɪᴛʜ ᴀ ᴘᴇɴ 🖊

/write <text> *:*` ᴡʀɪᴛᴇs ᴛʜᴇ ɢɪᴠᴇɴ ᴛᴇxᴛ `.
 """
