from typing import Optional, Tuple

from telegram import Message, MessageEntity
from telegram.error import BadRequest
from telegram.ext import ContextTypes

from Telegram.database.users_db import Users


async def extract_user(
    m: Message,
    context: ContextTypes.DEFAULT_TYPE,
    sender: bool = False,
) -> Tuple[Optional[int], Optional[str], Optional[str], Optional[str]]:
    """
    Extract user information from a message based on various conditions:
    replies, mentions, usernames, or user IDs.

    returns: user_id, full_name, username, args
    """
    reply_message = m.reply_to_message
    args = context.args
    if reply_message and reply_message.from_user:
        user = reply_message.from_user
        if user.id == 136817688:
            user = reply_message.sender_chat
        return user.id, user.full_name, user.username, (m.text.split(None, 1) + [""])[1]

    if entities := list(m.parse_entities([MessageEntity.TEXT_MENTION])):
        ent = entities[0]
        if ent.offset == len(m.text) - len(m.text.split(None, 1)[1]):
            return (
                ent.user.id,
                ent.user.full_name,
                ent.user.username,
                m.text[ent.offset + ent.length :],
            )

    if len(args) >= 1 and args[0].startswith("@"):
        user = await Users.get_user_info(args[0].lstrip("@"))
        if user:
            return (
                user["_id"],
                user["name"],
                user["username"],
                (m.text.split(None, 2) + [""])[2],
            )
        return None, None, None, (m.text.split(None, 2) + [""])[2]

    if len(args) >= 1 and args[0].isdigit():
        user_id = int(args[0])
        user = await Users.get_user_info(user_id)
        if user:
            return (
                user_id,
                user["name"],
                user["username"],
                (m.text.split(None, 2) + [""])[2],
            )
        try:
            user = await context.bot.get_chat(user_id)
            return (
                user.id,
                user.full_name,
                user.username,
                (m.text.split(None, 2) + [""])[2],
            )
        except BadRequest:
            return None, None, None, None

    if sender:
        return (
            m.from_user.id,
            m.from_user.full_name,
            m.from_user.username,
            (m.text.split(None, 1) + [""])[1],
        )

    return None, None, None, (m.text.split(None, 1) + [""])[1]
