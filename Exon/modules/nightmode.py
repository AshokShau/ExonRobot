from apscheduler.schedulers.asyncio import AsyncIOScheduler
from telethon import functions, types
from telethon.tl.types import ChatBannedRights

from Exon import dispatcher
from Exon import telethn as tbot
from Exon.events import register
from Exon.modules.sql.nightmode_sql import (
    add_nightmode,
    get_all_chat_id,
    is_nightmode_indb,
    rmnightmode,
)


async def is_register_admin(chat, user):
    if isinstance(chat, (types.InputPeerChannel, types.InputChannel)):

        return isinstance(
            (
                await tbot(functions.channels.GetParticipantRequest(chat, user))
            ).participant,
            (types.ChannelParticipantAdmin, types.ChannelParticipantCreator),
        )
    elif isinstance(chat, types.InputPeerChat):

        ui = await tbot.get_peer_id(user)
        ps = (
            await tbot(functions.messages.GetFullChatRequest(chat.chat_id))
        ).full_chat.participants.participants
        return isinstance(
            next((p for p in ps if p.user_id == ui), None),
            (types.ChatParticipantAdmin, types.ChatParticipantCreator),
        )
    else:
        return None


hima = ChatBannedRights(
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
openhima = ChatBannedRights(
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


@register(pattern="^/nightmode")
async def close_ws(event):
    if event.is_group:
        if not (await is_register_admin(event.input_chat, event.message.sender_id)):
            await event.reply("ʏᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴀᴅᴍɪɴ sᴏ ʏᴏᴜ ᴄᴀɴ'ᴛ ᴜsᴇ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ...")
            return

    if not event.is_group:
        await event.reply("ʏᴏᴜ ᴄᴀɴ ᴏɴʟʏ ᴇɴᴀʙʟᴇ ɴɪɢʜᴛ ᴍᴏᴅᴇ ɪɴ ɢʀᴏᴜᴘs.")
        return
    if is_nightmode_indb(str(event.chat_id)):
        await event.reply("ᴛʜɪs ᴄʜᴀᴛ ʜᴀs ᴀʟʀᴇᴀᴅʏ ᴇɴᴀʙʟᴇᴅ ɴɪɢʜᴛ ᴍᴏᴅᴇ.")
        return
    add_nightmode(str(event.chat_id))
    await event.reply(
        f"ᴀᴅᴅᴇᴅ ᴄʜᴀᴛ {event.chat.title} ᴡɪᴛʜ ɪᴅ `{event.chat_id}` ᴛᴏ ᴅᴀᴛᴀʙᴀsᴇ. **ᴛʜɪs ɢʀᴏᴜᴘ ᴡɪʟʟ ʙᴇ ᴄʟᴏsᴇᴅ ᴏɴ 12 ᴀᴍ (ɪsᴛ) ᴀɴᴅ ᴡɪʟʟ ᴏᴘᴇɴ ᴏɴ 06 ᴀᴍ (ɪsᴛ)**"
    )


@register(pattern="^/rmnight")
async def disable_ws(event):
    if event.is_group:
        if not (await is_register_admin(event.input_chat, event.message.sender_id)):
            await event.reply("ʏᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴀᴅᴍɪɴ sᴏ ʏᴏᴜ ᴄᴀɴ'ᴛ ᴜsᴇ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ...")
            return

    if not event.is_group:
        await event.reply("ʏᴏᴜ ᴄᴀɴ ᴏɴʟʏ ᴅɪsᴀʙʟᴇ ɴɪɢʜᴛ ᴍᴏᴅᴇ ɪɴ ɢʀᴏᴜᴘs.")
        return
    if not is_nightmode_indb(str(event.chat_id)):
        await event.reply("ᴛʜɪs ᴄʜᴀᴛ ʜᴀs ɴᴏᴛ ᴇɴᴀʙʟᴇᴅ ɴɪɢʜᴛ ᴍᴏᴅᴇ.")
        return
    rmnightmode(str(event.chat_id))
    await event.reply(
        f"ʀᴇᴍᴏᴠᴇᴅ ᴄʜᴀᴛ {event.chat.title} ᴡɪᴛʜ ɪᴅ `{event.chat_id}` ғʀᴏᴍ ᴅᴀᴛᴀʙᴀsᴇ."
    )


async def job_close():
    ws_chats = get_all_chat_id()
    if len(ws_chats) == 0:
        return
    for warner in ws_chats:
        try:
            await tbot.send_message(
                int(warner.chat_id),
                f"12:00 AM, ɢʀᴏᴜᴘ ɪs Closing ᴛɪʟʟ 6 ᴀᴍ. ɴɪɢʜᴛ ᴍᴏᴅᴇ sᴛᴀʀᴛᴇᴅ ! \n**ᴘᴏᴡᴇʀᴇᴅ ʙʏ {dispatcher.bot.username} **",
            )
            await tbot(
                functions.messages.EditChatDefaultBannedRightsRequest(
                    peer=int(warner.chat_id), banned_rights=hima
                )
            )
        except Exception as e:
            logger.info(f"ᴜɴᴀʙʟᴇ ᴛᴏ ᴄʟᴏsᴇ ɢʀᴏᴜᴘ {warner} - {e}")


# Run everyday at 12am
scheduler = AsyncIOScheduler(timezone="Asia/Kolkata")
scheduler.add_job(job_close, trigger="cron", hour=23, minute=59)
scheduler.start()


async def job_open():
    ws_chats = get_all_chat_id()
    if len(ws_chats) == 0:
        return
    for warner in ws_chats:
        try:
            await tbot.send_message(
                int(warner.chat_id),
                f"06:00 ᴀᴍ, ɢʀᴏᴜᴘ ɪs ᴏᴘᴇɴɪɴɢ.\n**ᴘᴏᴡᴇʀᴇᴅ ʙʏ {dispatcher.bot.username}**",
            )
            await tbot(
                functions.messages.EditChatDefaultBannedRightsRequest(
                    peer=int(warner.chat_id), banned_rights=openhima
                )
            )
        except Exception as e:
            logger.info(f"ᴜɴᴀʙʟᴇ ᴛᴏ ᴏᴘᴇɴ ɢʀᴏᴜᴘ {warner.chat_id} - {e}")


# Run everyday at 06
scheduler = AsyncIOScheduler(timezone="Asia/Kolkata")
scheduler.add_job(job_open, trigger="cron", hour=5, minute=59)
scheduler.start()

__help__ = """
*ᴀᴅᴍɪɴs ᴏɴʟʏ*

⍟ /nightmode*:* `ᴀᴅᴅs ɢʀᴏᴜᴘ ᴛᴏ ɴɪɢʜᴛᴍᴏᴅᴇ ᴄʜᴀᴛs `

⍟ /rmnight*:* `ʀᴇᴍᴏᴠᴇs ɢʀᴏᴜᴘ ғʀᴏᴍ ɴɪɢʜᴛᴍᴏᴅᴇ ᴄʜᴀᴛs `

*ɴᴏᴛᴇ:* ɴɪɢʜᴛ ᴍᴏᴅᴇ ᴄʜᴀᴛs ɢᴇᴛ ᴀᴜᴛᴏᴍᴀᴛɪᴄᴀʟʟʏ ᴄʟᴏsᴇᴅ ᴀᴛ 12 ᴀᴍ (ɪsᴛ) ᴀɴᴅ ᴀᴜᴛᴏᴍᴀᴛɪᴄᴀʟʟʏ ᴏᴘᴇɴs ᴀᴛ 6 ᴀᴍ (ɪsᴛ) ᴛᴏ ᴘʀᴇᴠᴇɴᴛ ɴɪɢʜᴛ sᴘᴀᴍs.
"""

__mod_name__ = "𝙽-ᴍᴏᴅᴇ"
