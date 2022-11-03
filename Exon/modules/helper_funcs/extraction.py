"""
MIT License

Copyright (c) 2022 Aʙɪsʜɴᴏɪ

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from typing import List, Optional

from telegram import Message, MessageEntity
from telegram.error import BadRequest

from Exon import LOGGER
from Exon.modules.users import get_user_id


def id_from_reply(message):
    prev_message = message.reply_to_message
    if not prev_message:
        return None, None
    user_id = (
        prev_message.sender_chat.id
        if prev_message.sender_chat
        else prev_message.from_user.id
    )
    res = message.text.split(None, 1)
    if len(res) < 2:
        return user_id, ""
    return user_id, res[1]


def extract_user(message: Message, args: List[str]) -> Optional[int]:
    return extract_user_and_text(message, args)[0]


def extract_user_and_text(
    message: Message,
    args: List[str],
) -> (Optional[int], Optional[str]):
    prev_message = message.reply_to_message
    split_text = message.text.split(None, 1)

    if len(split_text) < 2:
        return id_from_reply(message)  # only option possible

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
        user_id = get_user_id(user)
        if not user_id:
            message.reply_text(
                "ɴᴏ ɪᴅᴇᴀ ᴡʜᴏ ᴛʜɪs ᴜsᴇʀ ɪs. ʏᴏᴜ'ʟʟ ʙᴇ ᴀʙʟᴇ ᴛᴏ ɪɴᴛᴇʀᴀᴄᴛ ᴡɪᴛʜ ᴛʜᴇᴍ ɪғ "
                "ʏᴏᴜ ʀᴇᴘʟʏ ᴛᴏ ᴛʜᴀᴛ ᴘᴇʀsᴏɴ's ᴍᴇssᴀɢᴇ ɪɴsᴛᴇᴀᴅ, ᴏʀ ғᴏʀᴡᴀʀᴅ ᴏɴᴇ ᴏғ ᴛʜᴀᴛ ᴜsᴇʀ ᴍᴇssᴀɢᴇs.",
            )
            return None, None
        res = message.text.split(None, 2)
        if len(res) >= 3:
            text = res[2]

    elif len(args) >= 1 and args[0].isdigit():
        user_id = int(args[0])
        res = message.text.split(None, 2)
        if len(res) >= 3:
            text = res[2]

    elif prev_message:
        user_id, text = id_from_reply(message)

    else:
        return None, None

    try:
        message.bot.get_chat(user_id)
    except BadRequest as excp:
        if excp.message in ("User_id_invalid", "ᴄʜᴀᴛ ɴᴏᴛ ғᴏᴜɴᴅ"):
            message.reply_text(
                "I ᴅᴏɴ'ᴛ sᴇᴇᴍ ᴛᴏ ʜᴀᴠᴇ ɪɴᴛᴇʀᴀᴄᴛᴇᴅ ᴡɪᴛʜ ᴛʜɪs ᴜsᴇʀ ʙᴇғᴏʀᴇ - ᴘʟᴇᴀsᴇ ғᴏʀᴡᴀʀᴅ ᴀ ᴍᴇssᴀɢᴇ ғʀᴏᴍ "
                "ᴛʜᴇᴍ ᴛᴏ ɢɪᴠᴇ ᴍᴇ ᴄᴏɴᴛʀᴏʟ! (ʟɪᴋᴇ ᴀ ᴠᴏᴏᴅᴏᴏ ᴅᴏʟʟ, I ɴᴇᴇᴅ ᴀ ᴘɪᴇᴄᴇ ᴏғ ᴛʜᴇᴍ ᴛᴏ ʙᴇ ᴀʙʟᴇ "
                "ᴛᴏ ᴇxᴇᴄᴜᴛᴇ ᴄᴇʀᴛᴀɪɴ ᴄᴏᴍᴍᴀɴᴅs...)",
            )
        else:
            LOGGER.exception("ᴇxᴄᴇᴘᴛɪᴏɴ %s ᴏɴ ᴜsᴇʀ %s", excp.message, user_id)

        return None, None

    return user_id, text


def extract_text(message) -> str:
    return (
        message.text
        or message.caption
        or (message.sticker.emoji if message.sticker else None)
    )


def extract_unt_fedban(
    message: Message,
    args: List[str],
) -> (Optional[int], Optional[str]):
    prev_message = message.reply_to_message
    split_text = message.text.split(None, 1)

    if len(split_text) < 2:
        return id_from_reply(message)  # only option possible

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
        user_id = get_user_id(user)
        if not user_id and not isinstance(user_id, int):
            message.reply_text(
                "I ᴅᴏɴ'ᴛ ʜᴀᴠᴇ ᴛʜᴀᴛ ᴜsᴇʀ ɪɴ ᴍʏ ᴅʙ.  "
                "ʏᴏᴜ'ʟʟ be ᴀʙʟᴇ ᴛᴏ ɪɴᴛᴇʀᴀᴄᴛ ᴡɪᴛʜ ᴛʜᴇᴍ ɪғ ʏᴏᴜ ʀᴇᴘʟʏ ᴛᴏ ᴛʜᴀᴛ ᴘᴇʀsᴏɴ's ᴍᴇssᴀɢᴇ ɪɴsᴛᴇᴀᴅ, ᴏʀ ғᴏʀᴡᴀʀᴅ ᴏɴᴇ ᴏғ ᴛʜᴀᴛ ᴜsᴇʀ's ᴍᴇssᴀɢᴇs.",
            )
            return None, None
        res = message.text.split(None, 2)
        if len(res) >= 3:
            text = res[2]

    elif len(args) >= 1 and args[0].isdigit():
        user_id = int(args[0])
        res = message.text.split(None, 2)
        if len(res) >= 3:
            text = res[2]

    elif prev_message:
        user_id, text = id_from_reply(message)

    else:
        return None, None

    try:
        message.bot.get_chat(user_id)
    except BadRequest as excp:
        if excp.message in ("User_id_invalid", "Chat not found") and not isinstance(
            user_id,
            int,
        ):
            message.reply_text(
                "I ᴅᴏɴ'ᴛ sᴇᴇᴍ ᴛᴏ ʜᴀᴠᴇ ɪɴᴛᴇʀᴀᴄᴛᴇᴅ ᴡɪᴛʜ ᴛʜɪs ᴜsᴇʀ ʙᴇғᴏʀᴇ "
                "ᴘʟᴇᴀsᴇ ғᴏʀᴡᴀʀᴅ ᴀ ᴍᴇssᴀɢᴇ ғʀᴏᴍ ᴛʜᴇᴍ ᴛᴏ ɢɪᴠᴇ ᴍᴇ ᴄᴏɴᴛʀᴏʟ! "
                "(ʟɪᴋᴇ ᴀ ᴠᴏᴏᴅᴏᴏ ᴅᴏʟʟ, ɪ ɴᴇᴇᴅ ᴀ ᴘɪᴇᴄᴇ of ᴛʜᴇᴍ ᴛᴏ ʙᴇ ᴀʙʟᴇ ᴛᴏ ᴇxᴇᴄᴜᴛᴇ ᴄᴇʀᴛᴀɪɴ ᴄᴏᴍᴍᴀɴᴅs...)",
            )
            return None, None
        if excp.message != "ᴄʜᴀᴛ ɴᴏᴛ ғᴏᴜɴᴅ":
            LOGGER.exception("ᴇxᴄᴇᴘᴛɪᴏɴ %s ᴏɴ ᴜsᴇʀ %s", excp.message, user_id)
            return None, None
        if not isinstance(user_id, int):
            return None, None

    return user_id, text


def extract_user_fban(message: Message, args: List[str]) -> Optional[int]:
    return extract_unt_fedban(message, args)[0]
