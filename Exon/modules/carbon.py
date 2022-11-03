import asyncio
from io import BytesIO

from pyrogram import filters

from Exon import aiohttpsession as aiosession
from Exon import pgram
from Exon.events import register
from Exon.utils.errors import capture_err


async def make_carbon(code):
    url = "https://carbonara.vercel.app/api/cook"
    async with aiosession.post(url, json={"code": code}) as resp:
        image = BytesIO(await resp.read())
    image.name = "carbon.png"
    return image


@pgram.on_message(filters.command("carbon"))
@capture_err
async def carbon_func(_, message):
    if not message.reply_to_message:
        return await message.reply_text("`ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴛᴇxᴛ ᴛᴏ ɢᴇɴᴇʀᴀᴛᴇ ᴄᴀʀʙᴏɴ`")
    if not message.reply_to_message.text:
        return await message.reply_text("`ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴛᴇxᴛ ᴛᴏ ɢᴇɴᴇʀᴀᴛᴇ ᴄᴀʀʙᴏɴ`")
    m = await message.reply_text("`ɢᴇɴᴇʀᴀᴛɪɴɢ ᴄᴀʀʙᴏɴ...`")
    carbon = await make_carbon(message.reply_to_message.text)
    await m.edit("`waitoo...`")
    await pgram.send_photo(message.chat.id, carbon)
    await m.delete()
    carbon.close()


@register(pattern="^/repo$")
async def _(event):
    loda = "➥ [EXON](https://github.com/TEAM-ABG/ExonRobot)"
    lund = await event.reply(loda)
    await asyncio.sleep(10)
    await event.delete()
    await lund.delete()


__mod_name__ = "𝙲ᴀʀʙᴏɴ"

__help__ = """

/carbon *:* ᴍᴀᴋᴇs ᴄᴀʀʙᴏɴ ғᴏʀ ʀᴇᴘʟɪᴇᴅ ᴛᴇxᴛ
/repo *:*🌟
 """
