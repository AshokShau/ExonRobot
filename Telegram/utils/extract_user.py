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
    """
    reply_message = m.reply_to_message
    args = context.args

    # 1. Retrieve user info using reply (if available)
    if reply_message and reply_message.from_user:
        # Ignore forum topics in replies
        if reply_message.forum_topic_created:
            return None, None, None, None

        # Set initial values from the reply message
        user_id = reply_message.from_user.id
        user_first_name = reply_message.from_user.first_name
        user_name = reply_message.from_user.username

        # Handle a specific user ID case
        if user_id == 136817688:
            user_id = reply_message.sender_chat.id
            user_first_name = reply_message.sender_chat.title
            user_name = reply_message.sender_chat.username

        # Check if there’s additional text after the command and return
        res = m.text.split(None, 1)
        return user_id, user_first_name, user_name, res[1] if len(res) > 1 else ""

    # 2. Retrieve user info using text mentions
    entities = list(m.parse_entities([MessageEntity.TEXT_MENTION]))
    ent = entities[0] if entities else None
    if ent and ent.offset == len(m.text) - len(m.text.split(None, 1)[1]):
        user_id = ent.user.id
        user_first_name = ent.user.first_name
        user_name = ent.user.username
        text = m.text[ent.offset + ent.length :]
        return user_id, user_first_name, user_name, text

    # 3. Retrieve user info using @username (remove '@' if present)
    if len(args) >= 1 and args[0].startswith("@"):
        user = await Users.get_user_info(args[0].lstrip("@"))
        res = m.text.split(None, 2)
        text = res[2] if len(res) >= 3 else None
        if user:
            user_id = user["_id"]
            user_first_name = user["name"]
            user_name = user["username"]
            return user_id, user_first_name, user_name, text
        return None, None, None, text

    # 4. Retrieve user info using numeric user ID
    if len(args) >= 1 and args[0].isdigit():
        user_id = int(args[0])
        res = m.text.split(None, 2)
        text = res[2] if len(res) >= 3 else None
        user = await Users.get_user_info(user_id)

        if user:
            user_first_name = user["name"]
            user_name = user["username"]
            return user_id, user_first_name, user_name, text

        # Attempt to retrieve the user from Telegram if not in database
        try:
            user = await context.bot.get_chat(user_id)
            return user.id, user.first_name, user.username, text
        except BadRequest as exc:
            if exc.message in ("User_id_invalid", "Chat not found"):
                return None, None, None, text
            raise exc

    res = m.text.split(None, 1)
    if sender:
        # 5. Default to message sender if no user found in previous methods
        user_id = m.from_user.id
        user_first_name = m.from_user.first_name
        user_name = m.from_user.username
        return user_id, user_first_name, user_name, res[1] if len(res) > 1 else ""

    return None, None, None, res[1] if len(res) > 1 else ""
