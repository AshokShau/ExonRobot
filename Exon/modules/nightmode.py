from apscheduler.schedulers.asyncio import AsyncIOScheduler
from telethon import functions
from telethon.tl.types import ChatBannedRights

from Exon import BOT_NAME, OWNER_ID
from Exon import register as Asubot
from Exon import telethn as asux
from Exon.modules.sql.nightmode_sql import (
    add_nightmode,
    get_all_chat_id,
    is_nightmode_indb,
    rmnightmode,
)

__help__ = """
•➥ /nightmode ᴏɴ ᴏʀ ᴏғғ *:* ᴀᴅᴅs ɢʀᴏᴜᴘ ᴛᴏ ɴɪɢʜᴛᴍᴏᴅᴇ ᴄʜᴀᴛs

*ɴᴏᴛᴇ:* Nɪɢʜᴛ Mᴏᴅᴇ ᴄʜᴀᴛs ɢᴇᴛ Aᴜᴛᴏᴍᴀᴛɪᴄᴀʟʟʏ ᴄʟᴏsᴇᴅ ᴀᴛ 11:30 ᴀᴍ ᴀɴᴅ Aᴜᴛᴏᴍᴀᴛɪᴄᴀʟʟʏ ᴏᴘᴇɴɴᴇᴅ ᴀᴛ 6 ᴀᴍ ᴛᴏ Pʀᴇᴠᴇɴᴛ Nɪɢʜᴛ Sᴘᴀᴍs
"""

__mod_name__ = "𝐍-ᴍᴏᴅᴇ"


abishnoi = ChatBannedRights(
    until_date=None,
    send_messages=True,
    send_media=True,
    send_stickers=True,
    send_gifs=True,
    send_games=True,
    send_inline=True,
    send_polls=True,
    invite_users=True,
    pin_messages=True,
    change_info=True,
)

abishnoiX = ChatBannedRights(
    until_date=None,
    send_messages=False,
    send_media=False,
    send_stickers=False,
    send_gifs=False,
    send_games=False,
    send_inline=False,
    send_polls=False,
    invite_users=True,
    pin_messages=True,
    change_info=True,
)


async def is_register_admin(chat, user):
    if isinstance(chat, (types.InputPeerChannel, types.InputChannel)):
        return isinstance(
            (
                await asux(functions.channels.GetParticipantRequest(chat, user))
            ).participant,
            (types.ChannelParticipantAdmin, types.ChannelParticipantCreator),
        )
    if isinstance(chat, types.InputPeerUser):
        return True


async def can_change_info(message):
    result = await asux(
        functions.channels.GetParticipantRequest(
            channel=message.chat_id,
            user_id=message.sender_id,
        )
    )
    p = result.participant
    return isinstance(p, types.ChannelParticipantCreator) or (
        isinstance(p, types.ChannelParticipantAdmin) and p.admin_rights.change_info
    )


@Asubot(pattern="^/(nightmode|Nightmode|NightMode|kontolmode|KONTOLMODE) ?(.*)")
async def profanity(event):
    if event.fwd_from:
        return
    if event.is_private:
        return
    input = event.pattern_match.group(2)
    if not event.sender_id == OWNER_ID:
        if not await is_register_admin(event.input_chat, event.sender_id):
            await event.reply("ᴏɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴇxᴇᴄᴜᴛᴇ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ!")
            return
        else:
            if not await can_change_info(message=event):
                await event.reply(
                    "ʏᴏᴜ ᴀʀᴇ ᴍɪssɪɴɢ ᴛʜᴇ ғᴏʟʟᴏᴡɪɴɢ ʀɪɢʜᴛs ᴛᴏ ᴜsᴇ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ :CanChangeinfo"
                )
                return
    if not input:
        if is_nightmode_indb(str(event.chat_id)):
            await event.reply("✅ **ᴄᴜʀʀᴇɴᴛʟʏ ɴɪɢʜᴛ ᴍᴏᴅᴇ ɪs** ᴇɴᴀʙʟᴇᴅ")
            return
        await event.reply("❌ **ᴄᴜʀʀᴇɴᴛʟʏ ɴɪɢʜᴛ ᴍᴏᴅᴇ ɪs** ᴅɪsᴀʙʟᴇᴅ")
        return
    if "on" in input:
        if event.is_group:
            if is_nightmode_indb(str(event.chat_id)):
                await event.reply("✅ **ɴɪɢʜᴛ ᴍᴏᴅᴇ ɪs ᴀʟʀᴇᴀᴅʏ** ᴇɴᴀʙʟᴇᴅ")
                return
            add_nightmode(str(event.chat_id))
            await event.reply("✅ **sᴜᴄᴄᴇssғᴜʟʟʏ** ᴇɴᴀʙʟᴇᴅ **ɴɪɢʜᴛ ᴍᴏᴅᴇ**")
    if "off" in input:
        if event.is_group:
            if not is_nightmode_indb(str(event.chat_id)):
                await event.reply("❌ **ɴɪɢʜᴛ ᴍᴏᴅᴇ ɪs ᴀʟʀᴇᴀᴅʏ** ᴅɪsᴀʙʟᴇᴅ")
                return
        rmnightmode(str(event.chat_id))
        await event.reply("❌ **sᴜᴄᴄᴇssғᴜʟʟʏ** ᴅɪsᴀʙʟᴇᴅ **ɴɪɢʜᴛ ᴍᴏᴅᴇ**")
    if not "off" in input and not "on" in input:
        await event.reply("ᴘʟᴇᴀsᴇ sᴘᴇᴄɪғʏ On ᴏʀ Off!")
        return


async def job_close():
    chats = get_all_chat_id()
    if len(chats) == 0:
        return
    for akboss in chats:
        try:
            await asux.send_message(
                int(akboss.chat_id),
                f"━━━━━━  **ᴇxᴇᴄᴜᴛɪᴠᴇ**  ━━━━━━\n     🌗 **ɴɪɢʜᴛ ᴍᴏᴅᴇ ꜱᴛᴀʀᴛᴇᴅ !**\n\n  ɢʀᴏᴜᴘ ɪꜱ ᴄʟᴏꜱɪɴɢ ᴛɪʟʟ 06:00.\n  ᴏɴʟʏ ᴀᴅᴍɪɴꜱ ꜱʜᴏᴜʟᴅ ʙᴇ ᴀʙʟᴇ\n                 ᴛᴏ ᴍᴇꜱꜱᴀɢᴇ\n\n     ≛≛       **ᴘᴏᴡᴇʀᴇᴅ ʙʏ :**      ≛≛\n     ≛≛  {BOT_NAME}  ≛≛\n━━━━━━  **ᴇxᴇᴄᴜᴛɪᴠᴇ**  ━━━━━━",
            )
            await asux(
                functions.messages.EditChatDefaultBannedRightsRequest(
                    peer=int(akboss.chat_id), banned_rights=abishnoi
                )
            )
        except Exception as e:
            logger.info(f"ᴜɴᴀʙʟᴇ ᴛᴏ ᴄʟᴏsᴇ ɢʀᴏᴜᴘ {chat} - {e}")


# Run everyday at 11:30 am
scheduler = AsyncIOScheduler(timezone="Asia/Kolkata")
scheduler.add_job(job_close, trigger="cron", hour=23, minute=30)
scheduler.start()


async def job_open():
    chats = get_all_chat_id()
    if len(chats) == 0:
        return
    for akboss in chats:
        try:
            await asux.send_message(
                int(akboss.chat_id),
                f"━━━━━━  **ᴇxᴇᴄᴜᴛɪᴠᴇ**  ━━━━━━\n       🌗 **ɴɪɢʜᴛ ᴍᴏᴅᴇ ᴇɴᴅᴇᴅ !**\n\n  ɢʀᴏᴜᴘ ɪꜱ ᴏᴘᴇɴɪɴɢ. ᴇᴠᴇʀʏᴏɴᴇ\n   ꜱʜᴏᴜʟᴅ ʙᴇ ᴀʙʟᴇ ᴛᴏ ᴍᴇꜱꜱᴀɢᴇ.\n\n     ≛≛       **ᴘᴏᴡᴇʀᴇᴅ ʙʏ :**      ≛≛\n     ≛≛  {BOT_NAME}  ≛≛\n━━━━━━  **ᴇxᴇᴄᴜᴛɪᴠᴇ**  ━━━━━━",
            )
            await asux(
                functions.messages.EditChatDefaultBannedRightsRequest(
                    peer=int(akboss.chat_id), banned_rights=abishnoiX
                )
            )
        except Exception as e:
            logger.info(f"ᴜɴᴀʙʟᴇ ᴛᴏ ᴏᴘᴇɴ ɢʀᴏᴜᴘ {akboss.chat_id} - {e}")


# Run everyday at 06
scheduler = AsyncIOScheduler(timezone="Asia/Kolkata")
scheduler.add_job(job_open, trigger="cron", hour=5, minute=59)
scheduler.start()
