from telegram import Update, MessageOriginUser, MessageOriginChat
from telegram.constants import ChatType
from telegram.ext import filters, ContextTypes

from Telegram import Msg
from Telegram.database.chats_db import ChatsDB
from Telegram.database.users_db import Users


@Msg(~filters.COMMAND, group=-2)
async def _tracker(update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
    """Saves Users In Database"""
    message = update.effective_message
    chat = update.effective_chat
    user = update.effective_user

    # save chats
    chat_db = ChatsDB(chat.id)
    if chat.type in [ChatType.GROUP, ChatType.SUPERGROUP]:
        await chat_db.update_chat(chat.title, chat.username)
    elif chat.type == ChatType.PRIVATE:
        await Users(user.id).update_user(user.full_name, user.username, True)

    if reply := message.reply_to_message:
        if not reply.sender_chat and not reply.forward_origin:
            await Users(reply.from_user.id).update_user(
                reply.from_user.full_name, reply.from_user.username, False
            )

        if isinstance(reply.forward_origin, MessageOriginUser):
            await Users(reply.forward_origin.sender_user.id).update_user(
                reply.forward_origin.sender_user.full_name,
                reply.forward_origin.sender_user.username,
                False,
            )
            await Users(user.id).update_user(user.full_name, user.username, False)

    if message and message.forward_origin:
        if isinstance(message.forward_origin, MessageOriginUser):
            await Users(message.forward_origin.sender_user.id).update_user(
                message.forward_origin.sender_user.full_name,
                reply.forward_origin.sender_user.username,
                False,
            )
            await Users(message.from_user.id).update_user(
                message.from_user.full_name, message.from_user.username, False
            )
        elif isinstance(message.forward_origin, MessageOriginChat):
            await Users(message.from_user.id).update_user(
                message.from_user.full_name, message.from_user.username, False
            )

    await Users(user.id).update_user(user.full_name, user.username, False)
