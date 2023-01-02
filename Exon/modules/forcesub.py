from telethon import Button, events, types
from telethon.errors import ChatAdminRequiredError
from telethon.errors.rpcerrorlist import UserNotParticipantError
from telethon.tl.functions.channels import GetParticipantRequest
# ʙʏ @Abishnoi1M
from Exon import BOT_ID, BOT_NAME, BOT_USERNAME
from Exon import DRAGONS as DEVS
from Exon import OWNER_ID
from Exon import telethn as abishnoi
from Exon import Asuinline
from Exon import register as Asubot
from Exon.modules.sql.mongo import fsub_db as db

async def is_admin(chat_id, user_id):
    try:
        p = await abishnoi(GetParticipantRequest(chat_id, user_id))
    except UserNotParticipantError:
        return False
    if isinstance(p.participant, types.ChannelParticipantAdmin) or isinstance(
        p.participant, types.ChannelParticipantCreator
    ):
        return True
    else:
        return False


async def participant_check(channel, user_id):
    try:
        await abishnoi(GetParticipantRequest(channel, int(user_id)))
        return True
    except UserNotParticipantError:
        return False
    except:
        return False


@Asubot(pattern="^/(fsub|Fsub|forcesubscribe|Forcesub|forcesub|Forcesubscribe) ?(.*)")
async def fsub(event):
    if event.is_private:
        return
    if event.is_group:
        perm = await event.client.get_permissions(event.chat_id, event.sender_id)
        if not perm.is_admin:
            return await event.reply("ʏᴏᴜ ɴᴇᴇᴅ ᴛᴏ ʙᴇ ᴀɴ ᴀᴅᴍɪɴ ᴛᴏ ᴅᴏ ᴛʜɪs.")
        if not perm.is_creator:
            return await event.reply(
                "❗ <b>ɢʀᴏᴜᴘ ᴄʀᴇᴀᴛᴏʀ ʀᴇǫᴜɪʀᴇᴅ</b> \n<i>ʏᴏᴜ ʜᴀᴠᴇ ᴛᴏ ʙᴇ ᴛʜᴇ ɢʀᴏᴜᴘ ᴄʀᴇᴀᴛᴏʀ ᴛᴏ ᴅᴏ ᴛʜᴀᴛ.</i>",
                parse_mode="html",
            )
    try:
        channel = event.text.split(None, 1)[1]
    except IndexError:
        channel = None
    if not channel:
        chat_db = db.fs_settings(event.chat_id)
        if not chat_db:
            await event.reply(
                "<b>❌ ғᴏʀᴄᴇ sᴜʙsᴄʀɪʙᴇ ɪs ᴅɪsᴀʙʟᴇᴅ ɪɴ ᴛʜɪs ᴄʜᴀᴛ.</b>", parse_mode="HTML"
            )
        else:
            await event.reply(
                f"ғᴏʀᴄᴇsᴜʙsᴄʀɪʙᴇ ɪs ᴄᴜʀʀᴇɴᴛʟʏ <b>ᴇɴᴀʙʟᴇᴅ</b>. ᴜsᴇʀs ᴀʀᴇ ғᴏʀᴄᴇᴅ ᴛᴏ ᴊᴏɪɴ <b>@{chat_db.channel}</b> ᴛᴏ sᴘᴇᴀᴋ ʜᴇʀᴇ.",
                parse_mode="html",
            )
    elif channel in ["on", "yes", "y"]:
        await event.reply("❗ᴘʟᴇᴀsᴇ sᴘᴇᴄɪғʏ ᴛʜᴇ ᴄʜᴀɴɴᴇʟ ᴜsᴇʀɴᴀᴍᴇ.")
    elif channel in ["off", "no", "n"]:
        await event.reply("**❌ ғᴏʀᴄᴇ sᴜʙsᴄʀɪʙᴇ ɪs ᴅɪsᴀʙʟᴇᴅ sᴜᴄᴄᴇssғᴜʟʟʏ.**")
        db.disapprove(event.chat_id)
    else:
        try:
            channel_entity = await event.client.get_entity(channel)
        except:
            return await event.reply(
                "❗<b>ɪɴᴠᴀʟɪᴅ ᴄʜᴀɴɴᴇʟ ᴜsᴇʀɴᴀᴍᴇ ᴘʀᴏᴠɪᴅᴇᴅ.</b>", parse_mode="html"
            )
        channel = channel_entity.username
        try:
            if not channel_entity.broadcast:
                return await event.reply("ᴛʜᴀᴛ's ɴᴏᴛ ᴀ ᴠᴀʟɪᴅ ᴄʜᴀɴɴᴇʟ.")
        except:
            return await event.reply("ᴛʜᴀᴛ's ɴᴏᴛ ᴀ ᴠᴀʟɪᴅ ᴄʜᴀɴɴᴇʟ.")
        if not await participant_check(channel, BOT_ID):
            return await event.reply(
                f"❗**ɴᴏᴛ ᴀɴ ᴀᴅᴍɪɴ ɪɴ ᴛʜᴇ ᴄʜᴀɴɴᴇʟ**\nI ᴀᴍ ɴᴏᴛ ᴀɴ ᴀᴅᴍɪɴ ɪɴ ᴛʜᴇ [ᴄʜᴀɴɴᴇʟ](https://t.me/{channel}). ᴀᴅᴅ ᴍᴇ ᴀs ᴀ ᴀᴅᴍɪɴ ɪɴ ᴏʀᴅᴇʀ ᴛᴏ ᴇɴᴀʙʟᴇ ғᴏʀᴄᴇsᴜʙsᴄʀɪʙᴇ.",
                link_preview=False,
            )
        db.add_channel(event.chat_id, str(channel))
        await event.reply(f"✅ **ғᴏʀᴄᴇ sᴜʙsᴄʀɪʙᴇ ɪs ᴇɴᴀʙʟᴇᴅ** to @{channel}.")


@abishnoi.on(events.NewMessage())
async def fsub_n(e):
    if not db.fs_settings(e.chat_id):
        return
    if e.is_private:
        return
    if e.chat.admin_rights:
        if not e.chat.admin_rights.ban_users:
            return
    else:
        return
    if not e.from_id:
        return
    if (
        await is_admin(e.chat_id, e.sender_id)
        or e.sender_id in DEVS
        or e.sender_id == OWNER_ID
    ):
        return
    channel = (db.fs_settings(e.chat_id)).get("channel")
    try:
        check = await participant_check(channel, e.sender_id)
    except ChatAdminRequiredError:
        return
    if not check:
        buttons = [Button.url("ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ", f"t.me/{channel}")], [
            Button.inline("ᴜɴᴍᴜᴛᴇ ᴍᴇ", data="fs_{}".format(str(e.sender_id)))
        ]
        txt = f'<b><a href="tg://user?id={e.sender_id}">{e.sender.first_name}</a></b>, ʏᴏᴜ ʜᴀᴠᴇ <b>ɴᴏᴛ sᴜʙsᴄʀɪʙᴇᴅ</b> ᴛᴏ ᴏᴜʀ <b><a href="t.me/{channel}">ᴄʜᴀɴɴᴇʟ</a></b> ʏᴇᴛ❗.ᴘʟᴇᴀsᴇ <b><a href="t.me/{channel}">ᴊᴏɪɴ</a></b> ᴀɴᴅ <b>ᴘʀᴇss ᴛʜᴇ ʙᴜᴛᴛᴏɴ ʙᴇʟᴏᴡ</b> ᴛᴏ ᴜɴᴍᴜᴛᴇ ʏᴏᴜʀsᴇʟғ.'
        await e.reply(txt, buttons=buttons, parse_mode="html", link_preview=False)
        await e.client.edit_permissions(e.chat_id, e.sender_id, send_messages=False)


@Asuinline(pattern=r"fs(\_(.*))")
async def unmute_fsub(event):
    user_id = int(((event.pattern_match.group(1)).decode()).split("_", 1)[1])
    if not event.sender_id == user_id:
        return await event.answer("ᴛʜɪs ɪs ɴᴏᴛ ᴍᴇᴀɴᴛ ғᴏʀ ʏᴏᴜ.", alert=True)
    channel = (db.fs_settings(event.chat_id)).get("channel")
    try:
        check = await participant_check(channel, user_id)
    except ChatAdminRequiredError:
        check = False
        return
    if not check:
        return await event.answer(
            "ʏᴏᴜ ʜᴀᴠᴇ ᴛᴏ ᴊᴏɪɴ ᴛʜᴇ ᴄʜᴀɴɴᴇʟ ғɪʀsᴛ, ᴛᴏ ɢᴇᴛ ᴜɴᴍᴜᴛᴇᴅ!", alert=True
        )
    try:
        await event.client.edit_permissions(event.chat_id, user_id, send_messages=True)
    except ChatAdminRequiredError:
        pass
    await event.delete()


__help__ = f"""
⍟ * {BOT_NAME} ᴄᴀɴ ᴍᴜᴛᴇ ᴍᴇᴍʙᴇʀꜱ ᴡʜᴏ ᴀʀᴇ ɴᴏᴛ ꜱᴜʙꜱᴄʀɪʙᴇᴅ ʏᴏᴜʀ ᴄʜᴀɴɴᴇʟ ᴜɴᴛɪʟ ᴛʜᴇʏ ꜱᴜʙꜱᴄʀɪʙᴇ*
⍟ ᴡʜᴇɴ ᴇɴᴀʙʟᴇᴅ ɪ ᴡɪʟʟ ᴍᴜᴛᴇ ᴜɴꜱᴜʙꜱᴄʀɪʙᴇᴅ ᴍᴇᴍʙᴇʀꜱ ᴀɴᴅ ꜱʜᴏᴡ ᴛʜᴇᴍ ᴀ ᴜɴᴍᴜᴛᴇ ʙᴜᴛᴛᴏɴ. ᴡʜᴇɴ ᴛʜᴇʏ ᴘʀᴇꜱꜱᴇᴅ ᴛʜᴇ ʙᴜᴛᴛᴏɴ ɪ ᴡɪʟʟ ᴜɴᴍᴜᴛᴇ ᴛʜᴇᴍ

⍟ *ꜱᴇᴛᴜᴘ*
*ᴏɴʟʏ ᴄʀᴇᴀᴛᴏʀ*
⍟ [ᴀᴅᴅ ᴍᴇ ɪɴ ʏᴏᴜʀ ɢʀᴏᴜᴘ ᴀꜱ ᴀᴅᴍɪɴ](http://t.me/{BOT_USERNAME}?startgroup=new)
⍟ [ᴀᴅᴅ ᴍᴇ ɪɴ your ᴄʜᴀɴɴᴇʟ ᴀꜱ ᴀᴅᴍɪɴ](http://t.me/{BOT_USERNAME}?startgroup=new)
 
*ᴄᴏᴍᴍᴍᴀɴᴅꜱ*
⍟ /fsub {ᴄʜᴀɴɴᴇʟ ᴜsᴇʀɴᴀᴍᴇ} - ᴛᴏ ᴛᴜʀɴ ᴏɴ ᴀɴᴅ sᴇᴛᴜᴘ ᴛʜᴇ ᴄʜᴀɴɴᴇʟ.

💡*ᴅᴏ ᴛʜɪꜱ ғɪʀꜱᴛ...*
⍟ /fsub - ᴛᴏ ɢᴇᴛ ᴛʜᴇ ᴄᴜʀʀᴇɴᴛ ꜱᴇᴛᴛɪɴɢꜱ.
⍟ /fsub off - ᴛᴏ ᴛᴜʀɴ ᴏғ ғᴏʀᴄᴇꜱᴜʙꜱᴄʀɪʙᴇ..

💡ɪғ ʏᴏᴜ ᴅɪꜱᴀʙʟᴇ ғꜱᴜʙ, ʏᴏᴜ ɴᴇᴇᴅ ᴛᴏ ꜱᴇᴛ ᴀɢᴀɪɴ ғᴏʀ ᴡᴏʀᴋɪɴɢ /fsub {channel username}
"""
__mod_name__ = "𝐅-sᴜʙ"

