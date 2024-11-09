from typing import List, Optional, Union

from telegram import Message, MessageEntity
from telegram.error import BadRequest
from telegram.ext import ContextTypes

from Telegram.database.users_db import Users


async def extract_user(
    m: Message,
    context: ContextTypes.DEFAULT_TYPE,
    args: List[str],
) -> Union[(Optional[int], Optional[str])]:

    reply_message = m.reply_to_message

    # 𝘎𝘦𝘵 𝘶𝘴𝘦𝘳 𝘪𝘯𝘧𝘰 𝘶𝘴𝘪𝘯𝘨 reply_message (𝘪𝘯𝘧𝘰 𝘧𝘳𝘰𝘮 𝘵𝘨)
    if reply_message and reply_message.from_user:
        if reply_message.forum_topic_created:
            return None, None, None, None

        user_id = m.reply_to_message.from_user.id
        user_first_name = m.reply_to_message.from_user.first_name
        user_name = m.reply_to_message.from_user.username

        if user_id == 136817688:
            user_id = m.reply_to_message.sender_chat.id
            user_first_name = m.reply_to_message.sender_chat.title
            user_name = m.reply_to_message.sender_chat.username

        res = m.text.split(None, 1)
        if len(res) < 2:
            return user_id, user_first_name, user_name, ""
        return user_id, user_first_name, user_name, res[1]

    # 𝘎𝘦𝘵 𝘶𝘴𝘦𝘳 𝘪𝘯𝘧𝘰 𝘶𝘴𝘪𝘯𝘨 𝘵𝘦𝘹𝘵_𝘮𝘦𝘯𝘵𝘪𝘰𝘯 (𝘪𝘯𝘧𝘰 𝘧𝘳𝘰𝘮 𝘵𝘨 )
    entities = list(m.parse_entities([MessageEntity.TEXT_MENTION]))
    ent = entities[0] if entities else None
    if entities and ent and ent.offset == len(m.text) - len(m.text.split(None, 1)[1]):
        ent = entities[0]
        user_id = ent.user.id
        user_first_name = ent.user.first_name
        user_name = ent.user.username
        text = m.text[ent.offset + ent.length :]

    elif len(args) >= 1 and args[0][0] == "@":
        user = await Users.get_user_info(args[0])
        res = m.text.split(None, 2)
        text = res[2] if len(res) >= 3 else None
        try:
            user_id = user["_id"]
            user_first_name = user["name"]
            user_name = user["username"]
        except KeyError:
            return None, None, None, text

    elif len(args) >= 1 and args[0].isdigit():
        user = await Users.get_user_info(int(args[0]))
        user_id = int(args[0])
        res = m.text.split(None, 2)
        text = res[2] if len(res) >= 3 else None
        try:
            # user_id = user["_id"]
            user_first_name = user["name"]
            user_name = user["username"]
        except KeyError:
            try:
                user = await context.bot.get_chat(user_id)
            except BadRequest as exc:
                if exc.message not in ("User_id_invalid", "Chat not found"):
                    raise exc
                return None, None, None, text
            user_id = user.id
            user_first_name = user.first_name
            user_name = user.username

    else:
        # 𝘎𝘦𝘵 𝘶𝘴𝘦𝘳 𝘪𝘯𝘧𝘰 𝘶𝘴𝘪𝘯𝘨 𝘶𝘴𝘦𝘳 𝘐'𝘥 (𝘪𝘯𝘧𝘰 𝘧𝘳𝘰𝘮 𝘵𝘨 ) / 𝘴𝘦𝘭𝘧 𝘪𝘥
        user_id = m.from_user.id
        user_first_name = m.from_user.first_name
        user_name = m.from_user.username

        res = m.text.split(None, 1)
        if len(res) < 2:
            return user_id, user_first_name, user_name, ""
        return user_id, user_first_name, user_name, res[1]

    return user_id, user_first_name, user_name, text