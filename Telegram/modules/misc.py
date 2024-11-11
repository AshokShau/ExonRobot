from typing import cast

from telegram import (
    Message,
    Update,
    MessageOriginUser,
    MessageOriginChat,
    MessageOriginChannel,
    MessageOriginHiddenUser,
)
from telegram.constants import ChatType, MessageOriginType
from telegram.ext import ContextTypes

from Telegram import Cmd
from Telegram.database.users_db import Users
from Telegram.utils.extract_user import extract_user


@Cmd(command=["id"])
async def get_id(update: Update, context: ContextTypes.DEFAULT_TYPE) -> Message:
    """Retrieve and display user and chat IDs based on the command context."""
    message = cast(Message, update.message)
    args = context.args
    chat = update.effective_chat
    user = message.from_user or message.sender_chat
    your_id = user.id if message.from_user else message.sender_chat.id
    reply = message.reply_to_message

    # Base message with user and chat ID if available
    text = f"Your ID: {your_id}\n"
    if chat.type != ChatType.PRIVATE:
        text += f"Chat ID: {chat.id}\n"

    # If replying to a message, provide the replied user's or chat's ID
    if reply:
        if not reply.sender_chat and not reply.forward_origin:
            text += f"Replied User ID: {reply.from_user.id}\n"
            await Users(reply.from_user.id).update_user(
                reply.from_user.full_name, reply.from_user.username, False
            )

        # Determine the forward origin type and add appropriate details
        if (
            isinstance(reply.forward_origin, MessageOriginUser)
            and reply.forward_origin.type == MessageOriginType.USER
        ):
            text += f"Forwarded User: {reply.forward_origin.sender_user.first_name} with ID: {reply.forward_origin.sender_user.id}\n"
        elif (
            isinstance(reply.forward_origin, MessageOriginChat)
            and reply.forward_origin.type == MessageOriginType.CHAT
        ):
            text += f"Forwarded Chat: {reply.forward_origin.sender_chat.full_name} with ID: {reply.forward_origin.sender_chat.id}\n"
        elif (
            isinstance(reply.forward_origin, MessageOriginChannel)
            and reply.forward_origin.type == MessageOriginType.CHANNEL
        ):
            text += f"Forwarded Channel: {reply.forward_origin.chat.full_name} with ID: {reply.forward_origin.chat.id}\n"
        elif (
            isinstance(reply.forward_origin, MessageOriginHiddenUser)
            and reply.forward_origin.type == MessageOriginType.HIDDEN_USER
        ):
            text += f"Unable to retrieve the forwarded {reply.forward_origin.sender_user_name} ID.\n"

        # Additional media IDs if present
        if reply.animation:
            text += f"GIF ID: {reply.animation.file_id}\n"
        if reply.sticker:
            text += f"Sticker ID: {reply.sticker.file_id}\n"

        # Sender chat ID if applicable
        if reply.sender_chat:
            text += f"ID of Replied Chat/Channel: {reply.sender_chat.id}\n"

    # If arguments are provided, try to extract user details
    if len(args) >= 1:
        user_id, user_first_name, _, _ = await extract_user(message, context)
        if user_id:
            text += f"{user_first_name}: {user_id}\n"

    # Reply to the message with the accumulated information
    return await message.reply_text(text)
