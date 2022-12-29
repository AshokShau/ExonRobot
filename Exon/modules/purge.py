import time

from telethon import events
from telethon.errors.rpcerrorlist import MessageDeleteForbiddenError

from Exon import LOGGER, telethn
from Exon.modules.helper_funcs.telethn.chatstatus import (
    can_delete_messages,
    user_can_purge,
    user_is_admin,
)


async def purge_messages(event):
    start = time.perf_counter()
    if event.from_id is None:
        return

    if not await user_is_admin(
        user_id=event.sender_id, message=event
    ) and event.from_id not in [1087968824]:
        await event.reply("ᴏɴʟʏ ᴀᴅᴍɪɴs ᴀʀᴇ ᴀʟʟᴏᴡᴇᴅ ᴛᴏ ᴜsᴇ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ")
        return

    if not await user_can_purge(user_id=event.sender_id, message=event):
        await event.reply("ʏᴏᴜ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ ᴛʜᴇ ᴘᴇʀᴍɪssɪᴏɴ ᴛᴏ ᴅᴇʟᴇᴛᴇ ᴍᴇssᴀɢᴇs")
        return

    if not can_delete_messages(message=event):
        await event.reply("ᴄᴀɴ'ᴛ sᴇᴇᴍ ᴛᴏ ᴘᴜʀɢᴇ ᴛʜᴇ ᴍᴇssᴀɢᴇ")
        return

    reply_msg = await event.get_reply_message()
    if not reply_msg:
        await event.reply("ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴍᴇssᴀɢᴇ ᴛᴏ sᴇʟᴇᴄᴛ ᴡʜᴇʀᴇ ᴛᴏ sᴛᴀʀᴛ ᴘᴜʀɢɪɴɢ ғʀᴏᴍ.")
        return
    messages = []
    message_id = reply_msg.id
    delete_to = event.message.id

    messages.append(event.reply_to_msg_id)
    for msg_id in range(message_id, delete_to + 1):
        messages.append(msg_id)
        if len(messages) == 100:
            await event.client.delete_messages(event.chat_id, messages)
            messages = []

    try:
        await event.client.delete_messages(event.chat_id, messages)
    except:
        raise
    time_ = time.perf_counter() - start
    text = f"ᴘᴜʀɢᴇᴅ sᴜᴄᴄᴇssғᴜʟʟʏ ɪɴ {time_:0.2f} sᴇᴄᴏɴᴅ(s)"
    await event.respond(text, parse_mode="markdown")


async def delete_messages(event):
    if event.from_id is None:
        return

    if not await user_is_admin(
        user_id=event.sender_id, message=event
    ) and event.from_id not in [1087968824]:
        await event.reply("ᴏɴʟʏ ᴀᴅᴍɪɴs ᴀʀᴇ ᴀʟʟᴏᴡᴇᴅ ᴛᴏ ᴜsᴇ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ")
        return

    if not await user_can_purge(user_id=event.sender_id, message=event):
        await event.reply("ʏᴏᴜ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ ᴛʜᴇ ᴘᴇʀᴍɪssɪᴏɴ ᴛᴏ ᴅᴇʟᴇᴛᴇ messages")
        return

    message = await event.get_reply_message()
    me = await telethn.get_me()
    BOT_ID = me.id

    if (
        not can_delete_messages(message=event)
        and message
        and not int(message.sender.id) == int(BOT_ID)
    ):
        if event.chat.admin_rights is None:
            return await event.reply(
                "I'ᴍ ɴᴏᴛ ᴀɴ ᴀᴅᴍɪɴ, ᴅᴏ ʏᴏᴜ ᴍɪɴᴅ ᴘʀᴏᴍᴏᴛɪɴɢ ᴍᴇ ғɪʀsᴛ?"
            )
        elif not event.chat.admin_rights.delete_messages:
            return await event.reply("I ᴅᴏɴ'ᴛ ʜᴀᴠᴇ ᴛʜᴇ ᴘᴇʀᴍɪssɪᴏɴ ᴛᴏ ᴅᴇʟᴇᴛᴇ ᴍᴇssᴀɢᴇs!")

    if not message:
        await event.reply("ᴡʜᴀᴛ ᴡᴀɴᴛ ᴛᴏ ᴅᴇʟᴇᴛᴇ?")
        return
    chat = await event.get_input_chat()
    # del_message = [message, event.message]
    await event.client.delete_messages(chat, message)
    try:
        await event.client.delete_messages(chat, event.message)
    except MessageDeleteForbiddenError:
        LOGGER.error(
            "ᴇʀʀᴏʀ ɪɴ ᴅᴇʟᴇᴛɪɴɢ ᴍᴇssᴀɢᴇ {} ɪɴ {}".format(event.message.id, event.chat.id)
        )


__help__ = """
*ᴀᴅᴍɪɴ ᴏɴʟʏ:*
• /del: ᴅᴇʟᴇᴛᴇs ᴛʜᴇ ᴍᴇssᴀɢᴇ ʏᴏᴜ ʀᴇᴘʟɪᴇᴅ to
• /purge: ᴅᴇʟᴇᴛᴇs ᴀʟʟ ᴍᴇssᴀɢᴇs ʙᴇᴛᴡᴇᴇɴ ᴛʜɪs ᴀɴᴅ ᴛʜᴇ ʀᴇᴘʟɪᴇᴅ ᴛᴏ ᴍᴇssᴀɢᴇ.
• /purge <ɪɴᴛᴇɢᴇʀ x>: ᴅᴇʟᴇᴛᴇs ᴛʜᴇ ʀᴇᴘʟɪᴇᴅ ᴍᴇssᴀɢᴇ, ᴀɴᴅ X ᴍᴇssᴀɢᴇs ғᴏʟʟᴏᴡɪɴɢ ɪᴛ ɪғ ʀᴇᴘʟɪᴇᴅ ᴛᴏ ᴀ ᴍᴇssᴀɢᴇ.
"""

PURGE_HANDLER = purge_messages, events.NewMessage(pattern="^[!/]purge$")
DEL_HANDLER = delete_messages, events.NewMessage(pattern="^[!/]del$")

telethn.add_event_handler(*PURGE_HANDLER)
telethn.add_event_handler(*DEL_HANDLER)

__mod_name__ = "𝐏ᴜʀɢᴇ"

__command_list__ = ["del", "purge"]
__handlers__ = [PURGE_HANDLER, DEL_HANDLER]
