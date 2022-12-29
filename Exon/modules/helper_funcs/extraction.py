from typing import List, Optional, Union

from telegram import Message, MessageEntity
from telegram.error import BadRequest
from telegram.ext import ContextTypes

from Exon import LOGGER
from Exon.modules.users import get_user_id


async def id_from_reply(message: Message):
    prev_message = message.reply_to_message
    if not prev_message or prev_message.forum_topic_created:
        return None, None
    user_id = prev_message.from_user.id
    # if user id is from channel bot, then fetch channel id from sender_chat
    if user_id == 136817688:
        user_id = message.reply_to_message.sender_chat.id
    res = message.text.split(None, 1)
    if len(res) < 2:
        return user_id, ""
    return user_id, res[1]


async def extract_user(
    message: Message,
    context: ContextTypes.DEFAULT_TYPE,
    args: List[str],
) -> Optional[int]:
    return (await extract_user_and_text(message, context, args))[0]


async def extract_user_and_text(
    message: Message,
    context: ContextTypes.DEFAULT_TYPE,
    args: List[str],
) -> Union[(Optional[int], Optional[str])]:
    prev_message = message.reply_to_message
    split_text = message.text.split(None, 1)

    if len(split_text) < 2:
        return await id_from_reply(message)  # only option possible

    text_to_parse = split_text[1]

    text = ""

    entities = list(message.parse_entities([MessageEntity.TEXT_MENTION]))
    ent = entities[0] if entities else None
    # if entity offset matches (command end/text start) then all good
    if entities and ent and ent.offset == len(message.text) - len(text_to_parse):
        ent = entities[0]
        user_id = ent.user.id
        text = message.text[ent.offset + ent.length :]

    elif len(args) >= 1 and args[0][0] == "@":
        user = args[0]
        user_id = await get_user_id(user)
        if not user_id:
            await message.reply_text(
                "ɴᴏ ɪᴅᴇᴀ ᴡʜᴏ ᴛʜɪs ᴜsᴇʀ ɪs. ʏᴏᴜ'ʟʟ ʙᴇ ᴀʙʟᴇ ᴛᴏ ɪɴᴛᴇʀᴀᴄᴛ ᴡɪᴛʜ ᴛʜᴇᴍ if "
                "ʏᴏᴜ ʀᴇᴘʟʏ ᴛᴏ ᴛʜᴀᴛ ᴘᴇʀsᴏɴ's ᴍᴇssᴀɢᴇ ɪɴsᴛᴇᴀᴅ, ᴏʀ ғᴏʀᴡᴀʀᴅ ᴏɴᴇ ᴏғ ᴛʜᴀᴛ ᴜsᴇʀ's ᴍᴇssᴀɢᴇs.",
            )
            return None, None

        else:
            user_id = user_id
            res = message.text.split(None, 2)
            if len(res) >= 3:
                text = res[2]

    elif len(args) >= 1 and args[0].isdigit():
        user_id = int(args[0])
        res = message.text.split(None, 2)
        if len(res) >= 3:
            text = res[2]

    elif prev_message:
        user_id, text = await id_from_reply(message)

    else:
        return None, None

    try:
        await context.bot.get_chat(user_id)
    except BadRequest as excp:
        if excp.message in ("User_id_invalid", "Chat not found"):
            await message.reply_text(
                "I ᴅᴏɴ'ᴛ sᴇᴇᴍ ᴛᴏ ʜᴀᴠᴇ ɪɴᴛᴇʀᴀᴄᴛᴇᴅ ᴡɪᴛʜ ᴛʜɪs ᴜsᴇʀ ʙᴇғᴏʀᴇ - ᴘʟᴇᴀsᴇ ғᴏʀᴡᴀʀᴅ ᴀ ᴍᴇssᴀɢᴇ ғʀᴏᴍ "
                "ᴛʜᴇᴍ ᴛᴏ ɢɪᴠᴇ ᴍᴇ ᴄᴏɴᴛʀᴏʟ! (ʟɪᴋᴇ ᴀ ᴠᴏᴏᴅᴏᴏ ᴅᴏʟʟ, ɪ ɴᴇᴇᴅ ᴀ ᴘɪᴇᴄᴇ ᴏғ ᴛʜᴇᴍ ᴛᴏ ʙᴇ ᴀʙʟᴇ "
                "ᴛᴏ ᴇxᴇᴄᴜᴛᴇ ᴄᴇʀᴛᴀɪɴ ᴄᴏᴍᴍᴀɴᴅs...)",
            )
        else:
            LOGGER.exception("ᴇxᴄᴇᴘᴛɪᴏɴ %s ᴏɴ ᴜsᴇʀ %s", excp.message, user_id)

        return None, None

    return user_id, text


async def extract_text(message) -> str:
    return (
        message.text
        or message.caption
        or (message.sticker.emoji if message.sticker else None)
    )


async def extract_unt_fedban(
    message: Message, context: ContextTypes.DEFAULT_TYPE, args: List[str]
) -> Union[(Optional[int], Optional[str])]:
    prev_message = message.reply_to_message
    split_text = message.text.split(None, 1)

    if len(split_text) < 2:
        return await id_from_reply(message)  # only option possible

    text_to_parse = split_text[1]

    text = ""

    entities = list(message.parse_entities([MessageEntity.TEXT_MENTION]))
    ent = entities[0] if entities else None
    # if entity offset matches (command end/text start) then all good
    if entities and ent and ent.offset == len(message.text) - len(text_to_parse):
        ent = entities[0]
        user_id = ent.user.id
        text = message.text[ent.offset + ent.length :]

    elif len(args) >= 1 and args[0][0] == "@":
        user = args[0]
        user_id = await get_user_id(user)
        if not user_id and not isinstance(user_id, int):
            await message.reply_text(
                "I ᴅᴏɴ'ᴛ ʜᴀᴠᴇ ᴛʜᴀᴛ ᴜsᴇʀ ɪɴ ᴍʏ ᴅʙ.  "
                "ʏᴏᴜ'ʟʟ ʙᴇ ᴀʙʟᴇ ᴛᴏ ɪɴᴛᴇʀᴀᴄᴛ ᴡɪᴛʜ ᴛʜᴇᴍ ɪғ ʏᴏᴜ ʀᴇᴘʟʏ ᴛᴏ ᴛʜᴀᴛ ᴘᴇʀsᴏɴ's ᴍᴇssᴀɢᴇ ɪɴsᴛᴇᴀᴅ, ᴏʀ ғᴏʀᴡᴀʀᴅ ᴏɴᴇ ᴏғ ᴛʜᴀᴛ ᴜsᴇʀ's ᴍᴇssᴀɢᴇs.",
            )
            return None, None

        else:
            user_id = user_id
            res = message.text.split(None, 2)
            if len(res) >= 3:
                text = res[2]

    elif len(args) >= 1 and args[0].isdigit():
        user_id = int(args[0])
        res = message.text.split(None, 2)
        if len(res) >= 3:
            text = res[2]

    elif prev_message:
        user_id, text = await id_from_reply(message)

    else:
        return None, None

    try:
        await context.bot.get_chat(user_id)
    except BadRequest as excp:
        if excp.message in ("User_id_invalid", "Chat not found") and not isinstance(
            user_id,
            int,
        ):
            await message.reply_text(
                "I ᴅᴏɴ'ᴛ sᴇᴇᴍ ᴛᴏ ʜᴀᴠᴇ ɪɴᴛᴇʀᴀᴄᴛᴇᴅ ᴡɪᴛʜ ᴛʜɪs ᴜsᴇʀ ʙᴇғᴏʀᴇ "
                "ᴘʟᴇᴀsᴇ ғᴏʀᴡᴀʀᴅ a ᴍᴇssᴀɢᴇ ғʀᴏᴍ ᴛʜᴇᴍ ᴛᴏ ɢɪᴠᴇ ᴍᴇ ᴄᴏɴᴛʀᴏʟ! "
                "(ʟɪᴋᴇ ᴀ ᴠᴏᴏᴅᴏᴏ ᴅᴏʟʟ, I ɴᴇᴇᴅ ᴀ ᴘɪᴇᴄᴇ ᴏғ ᴛʜᴇᴍ ᴛᴏ ʙᴇ ᴀʙʟᴇ ᴛᴏ ᴇxᴇᴄᴜᴛᴇ ᴄᴇʀᴛᴀɪɴ ᴄᴏᴍᴍᴀɴᴅs...)",
            )
            return None, None
        elif excp.message != "ᴄʜᴀᴛ ɴᴏᴛ ғᴏᴜɴᴅ":
            LOGGER.exception("ᴇxᴄᴇᴘᴛɪᴏɴ %s ᴏɴ ᴜsᴇʀ %s", excp.message, user_id)
            return None, None
        elif not isinstance(user_id, int):
            return None, None

    return user_id, text


async def extract_user_fban(
    message: Message, context: ContextTypes.DEFAULT_TYPE, args: List[str]
) -> Optional[int]:
    return (await extract_unt_fedban(message, context, args))[0]
