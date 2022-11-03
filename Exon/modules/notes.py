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

import ast
import random
import re
from io import BytesIO
from typing import Optional

from telegram import (
    MAX_MESSAGE_LENGTH,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
    ParseMode,
    Update,
)
from telegram.error import BadRequest
from telegram.ext import (
    CallbackContext,
    CallbackQueryHandler,
    CommandHandler,
    Filters,
    MessageHandler,
)
from telegram.utils.helpers import escape_markdown, mention_markdown

import Exon.modules.sql.notes_sql as sql
from Exon import DRAGONS, JOIN_LOGGER, LOGGER, SUPPORT_CHAT, dispatcher
from Exon.modules.disable import DisableAbleCommandHandler
from Exon.modules.helper_funcs.chat_status import connection_status, user_admin
from Exon.modules.helper_funcs.handlers import MessageHandlerChecker
from Exon.modules.helper_funcs.misc import build_keyboard, revert_buttons
from Exon.modules.helper_funcs.msg_types import get_note_type
from Exon.modules.helper_funcs.string_handling import escape_invalid_curly_brackets

FILE_MATCHER = re.compile(r"^###file_id(!photo)?###:(.*?)(?:\s|$)")
STICKER_MATCHER = re.compile(r"^###sticker(!photo)?###:")
BUTTON_MATCHER = re.compile(r"^###button(!photo)?###:(.*?)(?:\s|$)")
MYFILE_MATCHER = re.compile(r"^###file(!photo)?###:")
MYPHOTO_MATCHER = re.compile(r"^###photo(!photo)?###:")
MYAUDIO_MATCHER = re.compile(r"^###audio(!photo)?###:")
MYVOICE_MATCHER = re.compile(r"^###voice(!photo)?###:")
MYVIDEO_MATCHER = re.compile(r"^###video(!photo)?###:")
MYVIDEONOTE_MATCHER = re.compile(r"^###video_note(!photo)?###:")

ENUM_FUNC_MAP = {
    sql.Types.TEXT.value: dispatcher.bot.send_message,
    sql.Types.BUTTON_TEXT.value: dispatcher.bot.send_message,
    sql.Types.STICKER.value: dispatcher.bot.send_sticker,
    sql.Types.DOCUMENT.value: dispatcher.bot.send_document,
    sql.Types.PHOTO.value: dispatcher.bot.send_photo,
    sql.Types.AUDIO.value: dispatcher.bot.send_audio,
    sql.Types.VOICE.value: dispatcher.bot.send_voice,
    sql.Types.VIDEO.value: dispatcher.bot.send_video,
}


# Do not async
def get(update, context, notename, show_none=True, no_format=False):
    bot = context.bot
    chat_id = update.effective_message.chat.id
    note_chat_id = update.effective_chat.id
    note = sql.get_note(note_chat_id, notename)
    message = update.effective_message  # type: Optional[Message]

    if note:
        if MessageHandlerChecker.check_user(update.effective_user.id):
            return
        # If we're replying to a message, reply to that message (unless it's an error)
        if message.reply_to_message:
            reply_id = message.reply_to_message.message_id
        else:
            reply_id = message.message_id
        if note.is_reply:
            if JOIN_LOGGER:
                try:
                    bot.forward_message(
                        chat_id=chat_id,
                        from_chat_id=JOIN_LOGGER,
                        message_id=note.value,
                    )
                except BadRequest as excp:
                    if excp.message != "ᴍᴇssᴀɢᴇ ᴛᴏ ғᴏʀᴡᴀʀᴅ ɴᴏᴛ ғᴏᴜɴᴅ":
                        raise
                    message.reply_text(
                        "ᴛʜɪs ᴍᴇssᴀɢᴇ sᴇᴇᴍs to ʜᴀᴠᴇ ʙᴇᴇɴ ʟᴏsᴛ - I'ʟʟ ʀᴇᴍᴏᴠᴇ ɪᴛ "
                        "ғʀᴏᴍ ʏᴏᴜʀ ɴᴏᴛᴇs ʟɪsᴛ.",
                    )
                    sql.rm_note(note_chat_id, notename)
            else:
                try:
                    bot.forward_message(
                        chat_id=chat_id,
                        from_chat_id=chat_id,
                        message_id=note.value,
                    )
                except BadRequest as excp:
                    if excp.message != "ᴍᴇssᴀɢᴇ ᴛᴏ ғᴏʀᴡᴀʀᴅ ɴᴏᴛ ғᴏᴜɴᴅ":
                        raise
                    message.reply_text(
                        "ʟᴏᴏᴋs ʟɪᴋᴇ ᴛʜᴇ ᴏʀɪɢɪɴᴀʟ sᴇɴᴅᴇʀ ᴏғ ᴛʜɪs ɴᴏᴛᴇ ʜᴀs ᴅᴇʟᴇᴛᴇᴅ "
                        "ᴛʜᴇɪʀ ᴍᴇssᴀɢᴇ - sorry! ɢᴇᴛ ʏᴏᴜʀ ʙᴏᴛ ᴀᴅᴍɪɴ ᴛᴏ sᴛᴀʀᴛ ᴜsɪɴɢ ᴀ "
                        "ᴍᴇssᴀɢᴇ ᴅᴜᴍᴘ ᴛᴏ ᴀᴠᴏɪᴅ ᴛʜɪs. I'ʟʟ ʀᴇᴍᴏᴠᴇ ᴛʜɪs ɴᴏᴛᴇ from "
                        "your saved notes.",
                    )
                    sql.rm_note(note_chat_id, notename)
        else:
            VALID_NOTE_FORMATTERS = [
                "first",
                "last",
                "fullname",
                "username",
                "id",
                "chatname",
                "mention",
            ]
            if valid_format := escape_invalid_curly_brackets(
                note.value,
                VALID_NOTE_FORMATTERS,
            ):
                if not no_format and "%%%" in valid_format:
                    split = valid_format.split("%%%")
                    text = random.choice(split) if all(split) else valid_format
                else:
                    text = valid_format
                text = text.format(
                    first=escape_markdown(message.from_user.first_name),
                    last=escape_markdown(
                        message.from_user.last_name or message.from_user.first_name,
                    ),
                    fullname=escape_markdown(
                        " ".join(
                            [
                                message.from_user.first_name,
                                message.from_user.last_name,
                            ]
                            if message.from_user.last_name
                            else [message.from_user.first_name],
                        ),
                    ),
                    username=f"@{message.from_user.username}"
                    if message.from_user.username
                    else mention_markdown(
                        message.from_user.id,
                        message.from_user.first_name,
                    ),
                    mention=mention_markdown(
                        message.from_user.id,
                        message.from_user.first_name,
                    ),
                    chatname=escape_markdown(
                        message.chat.title
                        if message.chat.type != "private"
                        else message.from_user.first_name,
                    ),
                    id=message.from_user.id,
                )

            else:
                text = ""

            keyb = []
            parseMode = ParseMode.MARKDOWN
            buttons = sql.get_buttons(note_chat_id, notename)
            if no_format:
                parseMode = None
                text += revert_buttons(buttons)
            else:
                keyb = build_keyboard(buttons)

            keyboard = InlineKeyboardMarkup(keyb)

            try:
                if note.msgtype in (sql.Types.BUTTON_TEXT, sql.Types.TEXT):
                    bot.send_message(
                        chat_id,
                        text,
                        reply_to_message_id=reply_id,
                        parse_mode=parseMode,
                        disable_web_page_preview=True,
                        reply_markup=keyboard,
                    )
                elif ENUM_FUNC_MAP[note.msgtype] == dispatcher.bot.send_sticker:
                    ENUM_FUNC_MAP[note.msgtype](
                        chat_id,
                        note.file,
                        reply_to_message_id=reply_id,
                        reply_markup=keyboard,
                    )
                else:
                    ENUM_FUNC_MAP[note.msgtype](
                        chat_id,
                        note.file,
                        caption=text,
                        reply_to_message_id=reply_id,
                        parse_mode=parseMode,
                        reply_markup=keyboard,
                    )

            except BadRequest as excp:
                if excp.message == "Entity_mention_user_invalid":
                    message.reply_text(
                        "ʟᴏᴏᴋs ʟɪᴋᴇ ʏᴏᴜ ᴛʀɪᴇᴅ ᴛᴏ ᴍᴇɴᴛɪᴏɴ sᴏᴍᴇᴏɴᴇ I'ᴠᴇ ɴᴇᴠᴇʀ sᴇᴇɴ ʙᴇғᴏʀᴇ. ɪғ ʏᴏᴜ ʀᴇᴀʟʟʏ "
                        "ᴡᴀɴᴛ ᴛᴏ ᴍᴇɴᴛɪᴏɴ ᴛʜᴇᴍ, ғᴏʀᴡᴀʀᴅ ᴏɴᴇ ᴏғ ᴛʜᴇɪʀ ᴍᴇssᴀɢᴇs ᴛᴏ ᴍᴇ, ᴀɴᴅ I'ʟʟ ʙᴇ ᴀʙʟᴇ "
                        "ᴛᴏ ᴛᴀɢ ᴛʜᴇᴍ!",
                    )
                elif FILE_MATCHER.match(note.value):
                    message.reply_text(
                        "ᴛʜɪs ɴᴏᴛᴇ ᴡᴀs ᴀɴ ɪɴᴄᴏʀʀᴇᴄᴛʟʏ i=mported ғɪʟᴇ ғʀᴏᴍ ᴀɴᴏᴛʜᴇʀ ʙᴏᴛ - I ᴄᴀɴ'ᴛ ᴜsᴇ "
                        "ɪᴛ. ɪғ ʏᴏᴜ ʀᴇᴀʟʟʏ ɴᴇᴇᴅ it, ʏᴏᴜ'ʟʟ ʜᴀᴠᴇ ᴛᴏ sᴀᴠᴇ ɪᴛ ᴀɢᴀɪɴ. ɪɴ "
                        "ᴛʜᴇ ᴍᴇᴀɴᴛɪᴍᴇ, I'ʟʟ ʀᴇᴍᴏᴠᴇ ɪᴛ ғʀᴏᴍ ʏᴏᴜʀ ɴᴏᴛᴇs ʟɪsᴛ.",
                    )
                    sql.rm_note(note_chat_id, notename)
                else:
                    message.reply_text(
                        "This= ɴᴏᴛᴇ ᴄᴏᴜʟᴅ ɴᴏᴛ ʙᴇ sᴇɴᴛ, ᴀs ɪᴛ ɪs ɪɴᴄᴏʀʀᴇᴄᴛʟʏ ғᴏʀᴍᴀᴛᴛᴇᴅ. ᴀsᴋ ɪɴ "
                        f"@{SUPPORT_CHAT} ɪғ ʏᴏᴜ ᴄᴀɴ'ᴛ ғɪɢᴜʀᴇ ᴏᴜᴛ ᴡʜʏ!",
                    )
                    LOGGER.exception(
                        "ᴄᴏᴜʟᴅ ɴᴏᴛ ᴘᴀʀsᴇ ᴍᴇssᴀɢᴇ #%s ɪɴ ᴄʜᴀᴛ %s",
                        notename,
                        str(note_chat_id),
                    )
                    LOGGER.warning("ᴍᴇssᴀɢᴇ ᴡᴀs: %s", str(note.value))
        return
    if show_none:
        message.reply_text("ᴛʜɪs ɴᴏᴛᴇ ᴅᴏᴇsɴ'ᴛ ᴇxɪsᴛ")


@connection_status
def cmd_get(update: Update, context: CallbackContext):
    bot, args = context.bot, context.args
    if len(args) >= 2 and args[1].lower() == "noformat":
        get(update, context, args[0].lower(), show_none=True, no_format=True)
    elif len(args) >= 1:
        get(update, context, args[0].lower(), show_none=True)
    else:
        update.effective_message.reply_text("Get rekt")


@connection_status
def hash_get(update: Update, context: CallbackContext):
    message = update.effective_message.text
    fst_word = message.split()[0]
    no_hash = fst_word[1:].lower()
    get(update, context, no_hash, show_none=False)


@connection_status
def slash_get(update: Update, context: CallbackContext):
    message, chat_id = update.effective_message.text, update.effective_chat.id
    no_slash = message[1:]
    note_list = sql.get_all_chat_notes(chat_id)

    try:
        noteid = note_list[int(no_slash) - 1]
        note_name = str(noteid).strip(">").split()[1]
        get(update, context, note_name, show_none=False)
    except IndexError:
        update.effective_message.reply_text("ᴡʀᴏɴɢ ɴᴏᴛᴇ ID 😾")


@user_admin
@connection_status
def save(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    msg = update.effective_message  # type: Optional[Message]

    note_name, text, data_type, content, buttons = get_note_type(msg)
    note_name = note_name.lower()
    if data_type is None:
        msg.reply_text("ᴅᴜᴅᴇ, ᴛʜᴇʀᴇ's ɴᴏ ɴᴏᴛᴇ")
        return

    sql.add_note_to_db(
        chat_id,
        note_name,
        text,
        data_type,
        buttons=buttons,
        file=content,
    )

    msg.reply_text(
        f"ʏᴀs! ᴀᴅᴅᴇᴅ `{note_name}`.\nɢᴇᴛ ɪᴛ ᴡɪᴛʜ /get `{note_name}`, ᴏʀ `#{note_name}`",
        parse_mode=ParseMode.MARKDOWN,
    )

    if msg.reply_to_message and msg.reply_to_message.from_user.is_bot:
        if text:
            msg.reply_text(
                "sᴇᴇᴍs ʟɪᴋᴇ ʏᴏᴜ'ʀᴇ ᴛʀʏɪɴɢ to sᴀᴠᴇ ᴀ ᴍᴇssᴀɢᴇ ғʀᴏᴍ ᴀ ʙᴏᴛ. ᴜɴғᴏʀᴛᴜɴᴀᴛᴇʟʏ, "
                "ʙᴏᴛ's ᴄᴀɴ'ᴛ ғᴏʀᴡᴀʀᴅ ʙᴏᴛ ᴍᴇssᴀɢᴇs, sᴏ I ᴄᴀɴ'ᴛ sᴀᴠᴇ ᴛʜᴇ ᴇxᴀᴄᴛ ᴍᴇssᴀɢᴇ. "
                "\nI'll sᴀᴠᴇ ᴀʟʟ ᴛʜᴇ ᴛᴇxᴛ I ᴄᴀɴ, ʙᴜᴛ ɪғ ʏᴏᴜ ᴡᴀɴᴛ ᴍᴏʀᴇ, ʏᴏᴜ'ʟʟ  ʜᴀᴠᴇ ᴛᴏ "
                "ғᴏʀᴡᴀʀᴅ ᴛʜᴇ ᴍᴇssᴀɢᴇ ʏᴏᴜʀsᴇʟғ, ᴀɴᴅ ᴛʜᴇɴ sᴀᴠᴇ ɪᴛ.",
            )
        else:
            msg.reply_text(
                "ʙᴏᴛs ᴀʀᴇ ᴋɪɴᴅᴀ ʜᴀɴᴅɪᴄᴀᴘᴘᴇᴅ ʙʏ ᴛᴇʟᴇɢʀᴀᴍ, ᴍᴀᴋɪɴɢ ɪᴛ ʜᴀʀᴅ ғᴏʀ ʙᴏᴛs ᴛᴏ "
                "ɪɴᴛᴇʀᴀᴄᴛ ᴡɪᴛʜ ᴏᴛʜᴇʀ ʙᴏᴛs, sᴏ ɪ ᴄᴀɴ'ᴛ sᴀᴠᴇ ᴛʜɪs ᴍᴇssᴀɢᴇ "
                "ʟɪᴋᴇ I ᴜsᴜᴀʟʟʏ ᴡᴏᴜʟᴅ - ᴅᴏ ʏᴏᴜ ᴍɪɴᴅ ғᴏʀᴡᴀʀᴅɪɴɢ ɪᴛ ᴀɴᴅ "
                "ᴛʜᴇɴ sᴀᴠɪɴɢ ᴛʜᴀᴛ ɴᴇᴡ ᴍᴇssᴀɢᴇ? ᴛʜᴀɴᴋs!",
            )
        return


@user_admin
@connection_status
def clear(update: Update, context: CallbackContext):
    args = context.args
    if len(args) >= 1:
        chat_id = update.effective_chat.id
        notename = args[0].lower()

        if sql.rm_note(chat_id, notename):
            update.effective_message.reply_text("sᴜᴄᴄᴇssғᴜʟʟʏ ʀᴇᴍᴏᴠᴇᴅ ɴᴏᴛᴇ.")
        else:
            update.effective_message.reply_text("ᴛʜᴀᴛ's ɴᴏᴛ ᴀ ɴᴏᴛᴇ ɪɴ ᴍʏ ᴅᴀᴛᴀʙᴀsᴇ!")


def clearall(update: Update, context: CallbackContext):
    chat = update.effective_chat
    user = update.effective_user
    member = chat.get_member(user.id)
    if member.status != "creator" and user.id not in DRAGONS:
        update.effective_message.reply_text(
            "ᴏɴʟʏ ᴛʜᴇ ᴄʜᴀᴛ ᴏᴡɴᴇʀ ᴄᴀɴ ᴄʟᴇᴀʀ ᴀʟʟ ɴᴏᴛᴇs ᴀᴛ ᴏɴᴄᴇ.",
        )
    else:
        buttons = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text="ᴅᴇʟᴇᴛᴇ ᴀʟʟ ɴᴏᴛᴇs",
                        callback_data="notes_rmall",
                    ),
                ],
                [InlineKeyboardButton(text="ᴄᴀɴᴄᴇʟ", callback_data="notes_cancel")],
            ],
        )
        update.effective_message.reply_text(
            f"ᴀʀᴇ ʏᴏᴜ sᴜʀᴇ ʏᴏᴜ ᴡᴏᴜʟᴅ ʟɪᴋᴇ ᴛᴏ ᴄʟᴇᴀʀ ALL ɴᴏᴛᴇs ɪɴ {chat.title}? ᴛʜɪs ᴀᴄᴛɪᴏɴ ᴄᴀɴɴᴏᴛ ʙᴇ ᴜɴᴅᴏɴᴇ.",
            reply_markup=buttons,
            parse_mode=ParseMode.MARKDOWN,
        )


def clearall_btn(update: Update, context: CallbackContext):
    query = update.callback_query
    chat = update.effective_chat
    message = update.effective_message
    member = chat.get_member(query.from_user.id)
    if query.data == "notes_rmall":
        if member.status == "creator" or query.from_user.id in DRAGONS:
            note_list = sql.get_all_chat_notes(chat.id)
            try:
                for notename in note_list:
                    note = notename.name.lower()
                    sql.rm_note(chat.id, note)
                message.edit_text("ᴅᴇʟᴇᴛᴇᴅ ᴀʟʟ ɴᴏᴛᴇs.")
            except BadRequest:
                return

        if member.status == "administrator":
            query.answer("ᴏɴʟʏ ᴏᴡɴᴇʀ ᴏғ ᴛʜᴇ ᴄʜᴀᴛ ᴄᴀɴ ᴅᴏ ᴛʜɪs.")

        if member.status == "member":
            query.answer("ʏᴏᴜ ɴᴇᴇᴅ ᴛᴏ ʙᴇ ᴀᴅᴍɪɴ ᴛᴏ ᴅᴏ ᴛʜɪs.")
    elif query.data == "notes_cancel":
        if member.status == "creator" or query.from_user.id in DRAGONS:
            message.edit_text("ᴄʟᴇᴀʀɪɴɢ ᴏғ ᴀʟʟ ɴᴏᴛᴇs ʜᴀs ʙᴇᴇɴ ᴄᴀɴᴄᴇʟʟᴇᴅ.")
            return
        if member.status == "administrator":
            query.answer("ᴏɴʟʏ ᴏᴡɴᴇʀ ᴏғ ᴛʜᴇ ᴄʜᴀᴛ ᴄᴀɴ ᴅᴏ ᴛʜɪs.")
        if member.status == "member":
            query.answer("ʏᴏᴜ ɴᴇᴇᴅ ᴛᴏ ʙᴇ ᴀᴅᴍɪɴ ᴛᴏ ᴅᴏ ᴛʜɪs.")


@connection_status
def list_notes(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    note_list = sql.get_all_chat_notes(chat_id)
    notes = len(note_list) + 1
    msg = "ɢᴇᴛ ɴᴏᴛᴇ ʙʏ `/notenumber` ᴏʀ `#notename` \n\n  *ɪᴅ*    *ɴᴏᴛᴇ* \n"
    for note_id, note in zip(range(1, notes), note_list):
        if note_id < 10:
            note_name = f"`{note_id:2}.`  `#{(note.name.lower())}`\n"
        else:
            note_name = f"`{note_id}.`  `#{(note.name.lower())}`\n"
        if len(msg) + len(note_name) > MAX_MESSAGE_LENGTH:
            update.effective_message.reply_text(msg, parse_mode=ParseMode.MARKDOWN)
            msg = ""
        msg += note_name

    if not note_list:
        try:
            update.effective_message.reply_text("ɴᴏ ɴᴏᴛᴇs ɪɴ ᴛʜɪs ᴄʜᴀᴛ!")
        except BadRequest:
            update.effective_message.reply_text("ɴᴏ ɴᴏᴛᴇs ɪɴ ᴛʜɪs ᴄʜᴀᴛ!", quote=False)

    elif len(msg) != 0:
        update.effective_message.reply_text(msg, parse_mode=ParseMode.MARKDOWN)


def __import_data__(chat_id, data):
    failures = []
    for notename, notedata in data.get("extra", {}).items():
        match = FILE_MATCHER.match(notedata)
        matchsticker = STICKER_MATCHER.match(notedata)
        matchbtn = BUTTON_MATCHER.match(notedata)
        matchfile = MYFILE_MATCHER.match(notedata)
        matchphoto = MYPHOTO_MATCHER.match(notedata)
        matchaudio = MYAUDIO_MATCHER.match(notedata)
        matchvoice = MYVOICE_MATCHER.match(notedata)
        matchvideo = MYVIDEO_MATCHER.match(notedata)
        matchvn = MYVIDEONOTE_MATCHER.match(notedata)

        if match:
            failures.append(notename)
            if notedata := notedata[match.end() :].strip():
                sql.add_note_to_db(chat_id, notename[1:], notedata, sql.Types.TEXT)
        elif matchsticker:
            if content := notedata[matchsticker.end() :].strip():
                sql.add_note_to_db(
                    chat_id,
                    notename[1:],
                    notedata,
                    sql.Types.STICKER,
                    file=content,
                )
        elif matchbtn:
            parse = notedata[matchbtn.end() :].strip()
            notedata = parse.split("<###button###>")[0]
            buttons = parse.split("<###button###>")[1]
            if buttons := ast.literal_eval(buttons):
                sql.add_note_to_db(
                    chat_id,
                    notename[1:],
                    notedata,
                    sql.Types.BUTTON_TEXT,
                    buttons=buttons,
                )
        elif matchfile:
            file = notedata[matchfile.end() :].strip()
            file = file.split("<###TYPESPLIT###>")
            notedata = file[1]
            if content := file[0]:
                sql.add_note_to_db(
                    chat_id,
                    notename[1:],
                    notedata,
                    sql.Types.DOCUMENT,
                    file=content,
                )
        elif matchphoto:
            photo = notedata[matchphoto.end() :].strip()
            photo = photo.split("<###TYPESPLIT###>")
            notedata = photo[1]
            if content := photo[0]:
                sql.add_note_to_db(
                    chat_id,
                    notename[1:],
                    notedata,
                    sql.Types.PHOTO,
                    file=content,
                )
        elif matchaudio:
            audio = notedata[matchaudio.end() :].strip()
            audio = audio.split("<###TYPESPLIT###>")
            notedata = audio[1]
            if content := audio[0]:
                sql.add_note_to_db(
                    chat_id,
                    notename[1:],
                    notedata,
                    sql.Types.AUDIO,
                    file=content,
                )
        elif matchvoice:
            voice = notedata[matchvoice.end() :].strip()
            voice = voice.split("<###TYPESPLIT###>")
            notedata = voice[1]
            if content := voice[0]:
                sql.add_note_to_db(
                    chat_id,
                    notename[1:],
                    notedata,
                    sql.Types.VOICE,
                    file=content,
                )
        elif matchvideo:
            video = notedata[matchvideo.end() :].strip()
            video = video.split("<###TYPESPLIT###>")
            notedata = video[1]
            if content := video[0]:
                sql.add_note_to_db(
                    chat_id,
                    notename[1:],
                    notedata,
                    sql.Types.VIDEO,
                    file=content,
                )
        elif matchvn:
            video_note = notedata[matchvn.end() :].strip()
            video_note = video_note.split("<###TYPESPLIT###>")
            notedata = video_note[1]
            if content := video_note[0]:
                sql.add_note_to_db(
                    chat_id,
                    notename[1:],
                    notedata,
                    sql.Types.VIDEO_NOTE,
                    file=content,
                )
        else:
            sql.add_note_to_db(chat_id, notename[1:], notedata, sql.Types.TEXT)

    if failures:
        with BytesIO(str.encode("\n".join(failures))) as output:
            output.name = "failed_imports.txt"
            dispatcher.bot.send_document(
                chat_id,
                document=output,
                filename="failed_imports.txt",
                caption="ᴛʜᴇsᴇ ғɪʟᴇs/ᴘʜᴏᴛᴏs ғᴀɪʟᴇᴅ ᴛᴏ ɪᴍᴘᴏʀᴛ ᴅᴜᴇ ᴛᴏ ᴏʀɪɢɪɴᴀᴛɪɴɢ "
                "ғʀᴏᴍ ᴀɴᴏᴛʜᴇʀ ʙᴏᴛ. ᴛʜɪs ɪs ᴀ ᴛᴇʟᴇɢʀᴀᴍ ᴀᴘɪ ʀᴇsᴛʀɪᴄᴛɪᴏɴ, ᴀɴᴅ ᴄᴀɴ'ᴛ "
                "ʙᴇ ᴀᴠᴏɪᴅᴇᴅ. sᴏʀʀʏ ғᴏʀ ᴛʜᴇ ɪɴᴄᴏɴᴠᴇɴɪᴇɴᴄᴇ!",
            )


def __stats__():
    return f"•➥ {sql.num_notes()} ɴᴏᴛᴇs, ᴀᴄʀᴏss {sql.num_chats()} ᴄʜᴀᴛs."


def __migrate__(old_chat_id, new_chat_id):
    sql.migrate_chat(old_chat_id, new_chat_id)


def __chat_settings__(chat_id, user_id):
    notes = sql.get_all_chat_notes(chat_id)
    return f"ᴛʜᴇʀᴇ ᴀʀᴇ `{len(notes)}` ɴᴏᴛᴇs ɪɴ ᴛʜɪs ᴄʜᴀᴛ."


__help__ = """
•➥ /get <notename>*:* `ɢᴇᴛ ᴛʜᴇ ɴᴏᴛᴇ ᴡɪᴛʜ this ɴᴏᴛᴇɴᴀᴍᴇ`

•➥ `#<notename>*:* same as /get`

•➥ /notes or /saved*:* `ʟɪsᴛ ᴀʟʟ sᴀᴠᴇᴅ ɴᴏᴛᴇs ɪɴ ᴛʜɪs ᴄʜᴀᴛ`

•➥ /number *:* `ᴡɪʟʟ ᴘᴜʟʟ ᴛʜᴇ ɴᴏᴛᴇ ᴏғ ᴛʜᴀᴛ ɴᴜᴍʙᴇʀ ɪɴ ᴛʜᴇ ʟɪsᴛ`

`ɪғ ʏᴏᴜ ᴡᴏᴜʟᴅ ʟɪᴋᴇ ᴛᴏ ʀᴇᴛʀɪᴇᴠᴇ ᴛʜᴇ ᴄᴏɴᴛᴇɴᴛs ᴏғ ᴀ ɴᴏᴛᴇ ᴡɪᴛʜᴏᴜᴛ ᴀɴʏ ғᴏʀᴍᴀᴛᴛɪɴɢ, ᴜsᴇ` `/get <notename> ɴᴏғᴏʀᴍᴀᴛ`. `ᴛʜɪs ᴄᴀɴ` \
`ʙᴇ ᴜsᴇғᴜʟ ᴡʜᴇɴ ᴜᴘᴅᴀᴛɪɴɢ ᴀ ᴄᴜʀʀᴇɴᴛ ɴᴏᴛᴇ`

*ᴀᴅᴍɪɴꜱ ᴏɴʟʏ:*
•➥ /save <notename> <notedata>*:* `ꜱᴀᴠᴇꜱ ɴᴏᴛᴇᴅᴀᴛᴀ ᴀꜱ ᴀ ɴᴏᴛᴇ ᴡɪᴛʜ ɴᴀᴍᴇ ɴᴏᴛᴇɴᴀᴍᴇ`

`A ʙᴜᴛᴛᴏɴ ᴄᴀɴ ʙᴇ ᴀᴅᴅᴇᴅ ᴛᴏ ᴀ ɴᴏᴛᴇ ʙʏ ᴜꜱɪɴɢ ꜱᴛᴀɴᴅᴀʀᴅ ᴍᴀʀᴋᴅᴏᴡɴ ʟɪɴᴋ ꜱʏɴᴛᴀx - ᴛʜᴇ ʟɪɴᴋ ꜱʜᴏᴜʟᴅ ᴊᴜꜱᴛ ʙᴇ ᴘʀᴇᴘᴇɴᴅᴇᴅ ᴡɪᴛʜ ᴀ`
 \
`buttonurl:` ꜱᴇᴄᴛɪᴏɴ, ᴀꜱ ꜱᴜᴄʜ: `[somelink](buttonurl:example.com)`. ᴄʜᴇᴄᴋ `/ᴍᴀʀᴋᴅᴏᴡɴʜᴇʟᴘ` ғᴏʀ ᴍᴏʀᴇ ɪɴғᴏ

•➥ /save <notename>*:* `ꜱᴀᴠᴇ ᴛʜᴇ ʀᴇᴘʟɪᴇᴅ ᴍᴇꜱꜱᴀɢᴇ ᴀꜱ ᴀ ɴᴏᴛᴇ ᴡɪᴛʜ ɴᴀᴍᴇ ɴᴏᴛᴇɴᴀᴍᴇ`

 `ꜱᴇᴘᴀʀᴀᴛᴇ ᴅɪғғ ʀᴇᴘʟɪᴇꜱ ʙʏ` `%%%` `ᴛᴏ ɢᴇᴛ ʀᴀɴᴅᴏᴍ ɴᴏᴛᴇꜱ`
 
 *ᴇxᴀᴍᴘʟᴇ:*
 `/save notename
 Reply 1
 %%%
 Reply 2
 %%%
 Reply 3`
 
•➥ /clear <notename>*:* `ᴄʟᴇᴀʀ ɴᴏᴛᴇ ᴡɪᴛʜ ᴛʜɪꜱ ɴᴀᴍᴇ`

•➥ /removeallnotes*:* `ʀᴇᴍᴏᴠᴇꜱ ᴀʟʟ ɴᴏᴛᴇꜱ ғʀᴏᴍ ᴛʜᴇ ɢʀᴏᴜᴘ`

 *ɴᴏᴛᴇ:* `ɴᴏᴛᴇ ɴᴀᴍᴇꜱ ᴀʀᴇ ᴄᴀꜱᴇ--ꜱᴇɴꜱɪᴛɪᴠᴇ, ᴀɴᴅ ᴛʜᴇʏ ᴀʀᴇ ᴀᴜᴛᴏᴍᴀᴛɪᴄᴀʟʟʏ ᴄᴏɴᴠᴇʀᴛᴇᴅ ᴛᴏ ʟᴏᴡᴇʀᴄᴀꜱᴇ ʙᴇғᴏʀᴇ ɢᴇᴛᴛɪɴɢ ꜱᴀᴠᴇᴅ.`
 
"""

__mod_name__ = "𝙽ᴏᴛᴇs"

GET_HANDLER = CommandHandler("get", cmd_get, run_async=True)
HASH_GET_HANDLER = MessageHandler(Filters.regex(r"^#[^\s]+"), hash_get, run_async=True)
SLASH_GET_HANDLER = MessageHandler(Filters.regex(r"^/\d+$"), slash_get, run_async=True)
SAVE_HANDLER = CommandHandler("save", save, run_async=True)
DELETE_HANDLER = CommandHandler("clear", clear, run_async=True)

LIST_HANDLER = DisableAbleCommandHandler(
    ["notes", "saved"], list_notes, admin_ok=True, run_async=True
)

CLEARALL = DisableAbleCommandHandler("removeallnotes", clearall, run_async=True)
CLEARALL_BTN = CallbackQueryHandler(clearall_btn, pattern=r"notes_.*", run_async=True)

dispatcher.add_handler(GET_HANDLER)
dispatcher.add_handler(SAVE_HANDLER)
dispatcher.add_handler(LIST_HANDLER)
dispatcher.add_handler(DELETE_HANDLER)
dispatcher.add_handler(HASH_GET_HANDLER)
dispatcher.add_handler(SLASH_GET_HANDLER)
dispatcher.add_handler(CLEARALL)
dispatcher.add_handler(CLEARALL_BTN)
