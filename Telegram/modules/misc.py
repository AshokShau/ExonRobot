from typing import cast

from telegram import Message, Update, MessageOrigin, MessageOriginUser, MessageOriginChat, MessageOriginChannel, \
    MessageOriginHiddenUser
from telegram.constants import ChatType, MessageOriginType
from telegram.ext import ContextTypes

from Telegram import Cmd
from Telegram.database.users_db import Users
from Telegram.utils.extract_user import extract_user



@Cmd(command=["id"])
async def get_id(update: Update, context: ContextTypes.DEFAULT_TYPE) -> Message:
    message = cast(Message, update.message)
    args = context.args
    chat = update.effective_chat
    user = message.from_user or message.sender_chat
    your_id = user.id if message.from_user else message.sender_chat.id
    reply = message.reply_to_message

    text = f"<b> <a href='tg://user?id={your_id}'>ʏᴏᴜʀ ɪᴅ:</a> </b> <code>{your_id}</code>\n"
    if chat.type != ChatType.PRIVATE:
        text += f"<b> <a href='https://t.me/{chat.username}'>ᴄʜᴀᴛ ɪᴅ:</a> </b> <code>{chat.id}</code>\n"

    if reply and not reply.sender_chat and not reply.forward_origin:
        text += f"<b> <a href='{reply.link}'>ʀᴇᴘʟɪᴇᴅ ᴜsᴇʀ ɪᴅ:</a> </b> <code>{reply.from_user.id}</code>\n"
        await Users(reply.from_user.id).update_user(
            reply.from_user.full_name, reply.from_user.username, False
        )
    if isinstance(reply.forward_origin, MessageOriginUser) and reply.forward_origin.type == MessageOriginType.USER:
        text += f"ᴛʜᴇ ғᴏʀᴡᴀʀᴅᴇᴅ ᴜsᴇʀ {reply.forward_origin.sender_user.first_name} ʜᴀs ᴀɴ ɪᴅ ᴏғ <code>{reply.forward_origin.sender_user.id}</code>\n"
    elif isinstance(reply.forward_origin, MessageOriginChat) and reply.forward_origin == MessageOriginType.CHAT:
         pass
    elif isinstance(reply.forward_origin, MessageOriginChannel) and  reply.forward_origin == MessageOriginType.CHANNEL:
        pass
    elif isinstance(reply.forward_origin, MessageOriginHiddenUser) and reply.forward_origin == MessageOriginType.HIDDEN_USER:
        text += "I can't Get that user Id"


    if reply and message.reply_to_message.animation:
        text += f"<b>ɢɪғ ɪᴅ:</b> <code>{reply.animation.file_id}</code>\n"

    if reply and message.reply_to_message.sticker:
        text += f"<b>sᴛɪᴄᴋᴇʀ ɪᴅ:</b> <code>{reply.sticker.file_id}</code>\n"

    if reply and reply.sender_chat:
        text += f"<b>ɪᴅ ᴏғ ᴛʜᴇ ʀᴇᴘʟɪᴇᴅ ᴄʜᴀᴛ/ᴄʜᴀɴɴᴇʟ ɪs:</b> <code>{reply.sender_chat.id}</code>\n"

    if len(args) >= 1:
        user_id, user_first_name, _, _ = await extract_user(message, context)
        if user_id:
            text += f"<b> <a href='tg://user?id={user_id}'>{user_first_name}:</a> </b> <code>{user_id}</code>\n"

    return await message.reply_text(text)