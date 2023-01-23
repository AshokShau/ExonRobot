import ast
import random
import re
from io import BytesIO

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Message, Update
from telegram.constants import MessageLimit, ParseMode
from telegram.error import BadRequest
from telegram.ext import (
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)
from telegram.helpers import escape_markdown, mention_markdown

import Exon.modules.sql.notes_sql as sql
from Exon import DRAGONS, EVENT_LOGS, LOGGER, SUPPORT_CHAT, exon
from Exon.modules.disable import DisableAbleCommandHandler
from Exon.modules.helper_funcs.chat_status import check_admin, connection_status
from Exon.modules.helper_funcs.handlers import MessageHandlerChecker
from Exon.modules.helper_funcs.misc import build_keyboard, revert_buttons
from Exon.modules.helper_funcs.msg_types import get_note_type
from Exon.modules.helper_funcs.string_handling import (
    escape_invalid_curly_brackets,
    markdown_to_html,
)

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
    sql.Types.TEXT.value: exon.bot.send_message,
    sql.Types.BUTTON_TEXT.value: exon.bot.send_message,
    sql.Types.STICKER.value: exon.bot.send_sticker,
    sql.Types.DOCUMENT.value: exon.bot.send_document,
    sql.Types.PHOTO.value: exon.bot.send_photo,
    sql.Types.AUDIO.value: exon.bot.send_audio,
    sql.Types.VOICE.value: exon.bot.send_voice,
    sql.Types.VIDEO.value: exon.bot.send_video,
}


# Do not async
async def get(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    notename,
    show_none=True,
    no_format=False,
):
    bot = context.bot
    chat_id = update.effective_message.chat.id
    chat = update.effective_chat
    note_chat_id = update.effective_chat.id
    note = sql.get_note(note_chat_id, notename)
    message = update.effective_message  # type: Optional[Message]

    if note:
        if MessageHandlerChecker.check_user(update.effective_user.id):
            return
        # If we're replying to a message, reply to that message (unless it's an error)
        if (
            message.reply_to_message
            and not message.reply_to_message.forum_topic_created
        ):
            reply_id = message.reply_to_message.message_id
        else:
            reply_id = message.message_id
        if note.is_reply:
            if EVENT_LOGS:
                try:
                    await bot.forward_message(
                        chat_id=chat_id,
                        from_chat_id=EVENT_LOGS,
                        message_id=note.value,
                    )
                except BadRequest as excp:
                    if excp.message == "ᴍᴇssᴀɢᴇ ᴛᴏ ғᴏʀᴡᴀʀᴅ ɴᴏᴛ ғᴏᴜɴᴅ":
                        await message.reply_text(
                            "ᴛʜɪs ᴍᴇssᴀɢᴇ sᴇᴇᴍs ᴛᴏ ʜᴀᴠᴇ ʙᴇᴇɴ ʟᴏsᴛ - I'ʟʟ ʀᴇᴍᴏᴠᴇ ɪᴛ "
                            "ғʀᴏᴍ ʏᴏᴜʀ ɴᴏᴛᴇs ʟɪsᴛ.",
                        )
                        sql.rm_note(note_chat_id, notename)
                    else:
                        raise
            else:
                try:
                    await bot.forward_message(
                        chat_id=chat_id,
                        from_chat_id=chat_id,
                        message_id=markdown_to_html(note.value),
                    )
                except BadRequest as excp:
                    if excp.message == "ᴍᴇssᴀɢᴇ ᴛᴏ ғᴏʀᴡᴀʀᴅ ɴᴏᴛ ғᴏᴜɴᴅ":
                        await message.reply_text(
                            "ʟᴏᴏᴋs ʟɪᴋᴇ ᴛʜᴇ ᴏʀɪɢɪɴᴀʟ sᴇɴᴅᴇʀ ᴏғ ᴛʜɪs ɴᴏᴛᴇ ʜᴀs ᴅᴇʟᴇᴛᴇᴅ "
                            "ᴛʜᴇɪʀ ᴍᴇssᴀɢᴇ - sᴏʀʀʏ! ɢᴇᴛ ʏᴏᴜʀ ʙᴏᴛ ᴀᴅᴍɪɴ ᴛᴏ sᴛᴀʀᴛ ᴜsɪɴɢ ᴀ "
                            "ᴍᴇssᴀɢᴇ ᴅᴜᴍᴘ ᴛᴏ ᴀᴠᴏɪᴅ ᴛʜɪs. I'ʟʟ ʀᴇᴍᴏᴠᴇ ᴛʜɪs ɴᴏᴛᴇ ғʀᴏᴍ "
                            "ʏᴏᴜʀ sᴀᴠᴇᴅ ɴᴏᴛᴇs.",
                        )
                        sql.rm_note(note_chat_id, notename)
                    else:
                        raise
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
            valid_format = escape_invalid_curly_brackets(
                note.value,
                VALID_NOTE_FORMATTERS,
            )
            if valid_format:
                if not no_format:
                    if "%%%" in valid_format:
                        split = valid_format.split("%%%")
                        if all(split):
                            text = random.choice(split)
                        else:
                            text = valid_format
                    else:
                        text = valid_format
                else:
                    text = valid_format
                text = text.format(
                    first=escape_markdown(message.from_user.first_name),
                    last=escape_markdown(
                        message.from_user.last_name or message.from_user.first_name,
                    ),
                    fullname=escape_markdown(
                        " ".join(
                            [message.from_user.first_name, message.from_user.last_name]
                            if message.from_user.last_name
                            else [message.from_user.first_name],
                        ),
                    ),
                    username="@" + message.from_user.username
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
            parseMode = ParseMode.HTML
            buttons = sql.get_buttons(note_chat_id, notename)
            if no_format:
                parseMode = None
                text += revert_buttons(buttons)
            else:
                keyb = build_keyboard(buttons)

            keyboard = InlineKeyboardMarkup(keyb)

            try:
                if note.msgtype in (sql.Types.BUTTON_TEXT, sql.Types.TEXT):
                    await bot.send_message(
                        chat_id,
                        markdown_to_html(text),
                        reply_to_message_id=reply_id,
                        parse_mode=parseMode,
                        disable_web_page_preview=True,
                        reply_markup=keyboard,
                        message_thread_id=message.message_thread_id
                        if chat.is_forum
                        else None,
                    )
                else:
                    await ENUM_FUNC_MAP[note.msgtype](
                        chat_id,
                        note.file,
                        caption=markdown_to_html(text),
                        reply_to_message_id=reply_id,
                        parse_mode=parseMode,
                        disable_web_page_preview=True,
                        reply_markup=keyboard,
                        message_thread_id=message.message_thread_id
                        if chat.is_forum
                        else None,
                    )

            except BadRequest as excp:
                if excp.message == "Entity_mention_user_invalid":
                    await message.reply_text(
                        "ʟᴏᴏᴋs ʟɪᴋᴇ ʏᴏᴜ ᴛʀɪᴇᴅ ᴛᴏ mention sᴏᴍᴇᴏɴᴇ I'ᴠᴇ ɴᴇᴠᴇʀ sᴇᴇɴ ʙᴇғᴏʀᴇ. ɪғ ʏᴏᴜ ʀᴇᴀʟʟʏ "
                        "ᴡᴀɴᴛ ᴛᴏ ᴍᴇɴᴛɪᴏɴ ᴛʜᴇᴍ, ғᴏʀᴡᴀʀᴅ ᴏɴᴇ ᴏғ ᴛʜᴇɪʀ ᴍᴇssᴀɢᴇs ᴛᴏ ᴍᴇ, ᴀɴᴅ I'ʟʟ ʙᴇ ᴀʙʟᴇ "
                        "ᴛᴏ ᴛᴀɢ ᴛʜᴇᴍ!",
                    )
                elif FILE_MATCHER.match(note.value):
                    await message.reply_text(
                        "ᴛʜɪs note ᴡᴀs ᴀɴ ɪɴᴄᴏʀʀᴇᴄᴛʟʏ ɪᴍᴘᴏʀᴛᴇᴅ ғɪʟᴇ ғʀᴏᴍ ᴀɴᴏᴛʜᴇʀ ʙᴏᴛ - I ᴄᴀɴ'ᴛ ᴜsᴇ "
                        "ɪᴛ. ɪғ ʏᴏᴜ ʀᴇᴀʟʟʏ ɴᴇᴇᴅ ɪᴛ, ʏᴏᴜ'ʟʟ ʜᴀᴠᴇ ᴛᴏ sᴀᴠᴇ ɪᴛ ᴀɢᴀɪɴ. ɪɴ "
                        "ᴛʜᴇ ᴍᴇᴀɴᴛɪᴍᴇ, I'ʟʟ ʀᴇᴍᴏᴠᴇ ɪᴛ ғʀᴏᴍ ʏᴏᴜʀ ɴᴏᴛᴇs ʟɪsᴛ.",
                    )
                    sql.rm_note(note_chat_id, notename)
                else:
                    await message.reply_text(
                        "ᴛʜɪs ɴᴏᴛᴇ ᴄᴏᴜʟᴅ ɴᴏᴛ ʙᴇ sᴇɴᴛ, ᴀs ɪᴛ ɪs ɪɴᴄᴏʀʀᴇᴄᴛʟʏ ғᴏʀᴍᴀᴛᴛᴇᴅ. ᴀsᴋ ɪɴ "
                        f"@{SUPPORT_CHAT} ɪғ ʏᴏᴜ ᴄᴀɴ'ᴛ ғɪɢᴜʀᴇ ᴏᴜᴛ ᴡʜʏ!",
                    )
                    LOGGER.exception(
                        "ᴄᴏᴜʟᴅ ɴᴏᴛ ᴘᴀʀsᴇ ᴍᴇssᴀɢᴇ #%s ɪɴ ᴄʜᴀᴛ %s",
                        notename,
                        str(note_chat_id),
                    )
                    LOGGER.warning("ᴍᴇssᴀɢᴇ ᴡᴀs: %s", str(note.value))
        return
    elif show_none:
        await message.reply_text("ᴛʜɪs ɴᴏᴛᴇ ᴅᴏᴇsɴ'ᴛ ᴇxɪsᴛ")


@connection_status
async def cmd_get(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bot, args = context.bot, context.args
    if len(args) >= 2 and args[1].lower() == "noformat":
        await get(update, context, args[0].lower(), show_none=True, no_format=True)
    elif len(args) >= 1:
        await get(update, context, args[0].lower(), show_none=True)
    else:
        await update.effective_message.reply_text("ɢᴇᴛ ʀᴇᴋᴛ")


@connection_status
async def hash_get(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.effective_message.text
    fst_word = message.split()[0]
    no_hash = fst_word[1:].lower()
    await get(update, context, no_hash, show_none=False)


@connection_status
async def slash_get(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message, chat_id = update.effective_message.text, update.effective_chat.id
    no_slash = message[1:]
    note_list = sql.get_all_chat_notes(chat_id)

    try:
        noteid = note_list[int(no_slash) - 1]
        note_name = str(noteid).strip(">").split()[1]
        await get(update, context, note_name, show_none=False)
    except IndexError:
        await update.effective_message.reply_text("ᴡʀᴏɴɢ ɴᴏᴛᴇ ɪᴅ 👀")


@connection_status
@check_admin(is_user=True)
async def save(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    msg = update.effective_message  # type: Optional[Message]
    if len(context.args) < 1:
        await msg.reply_text("ʏᴏᴜ sʜᴏᴜʟᴅ ɢɪᴠᴇ ᴛʜᴇ ɴᴏᴛᴇ ᴀ ɴᴀᴍᴇ.")
        return

    note_name, text, data_type, content, buttons = get_note_type(msg)
    note_name = note_name.lower()
    if data_type is None:
        await msg.reply_text("ᴅᴜᴅᴇ, ᴛʜᴇʀᴇ's ɴᴏ ɴᴏᴛᴇ ᴄᴏɴᴛᴇɴᴛ")
        return

    sql.add_note_to_db(
        chat_id,
        note_name,
        text,
        data_type,
        buttons=buttons,
        file=content,
    )

    await msg.reply_text(
        f"ʏᴀs! ᴀᴅᴅᴇᴅ `{note_name}` .\n\nɢᴇᴛ ɪᴛ ᴡɪᴛʜ /get `{note_name}`, ᴏʀ `#{note_name}`",
        parse_mode=ParseMode.MARKDOWN,
    )

    if (
        msg.reply_to_message
        and msg.reply_to_message.from_user.is_bot
        and not msg.reply_to_message.forum_topic_created
    ):
        if text:
            await msg.reply_text(
                "sᴇᴇᴍs ʟɪᴋᴇ ʏᴏᴜ'ʀᴇ ᴛʀʏɪɴɢ ᴛᴏ sᴀᴠᴇ ᴀ ᴍᴇssᴀɢᴇ ғʀᴏᴍ ᴀ ʙᴏᴛ. ᴜɴғᴏʀᴛᴜɴᴀᴛᴇʟʏ, "
                "ʙᴏᴛs ᴄᴀɴ'ᴛ ғᴏʀᴡᴀʀᴅ ʙᴏᴛ ᴍᴇssᴀɢᴇs, sᴏ I ᴄᴀɴ'ᴛ sᴀᴠᴇ ᴛʜᴇ ᴇxᴀᴄᴛ ᴍᴇssᴀɢᴇ. "
                "\nɪ'ʟʟ sᴀᴠᴇ ᴀʟʟ ᴛʜᴇ ᴛᴇxᴛ ɪ ᴄᴀɴ, ʙᴜᴛ ɪғ ʏᴏᴜ ᴡᴀɴᴛ ᴍᴏʀᴇ, ʏᴏᴜ'ʟ ʜᴀᴠᴇ ᴛᴏ "
                "ғᴏʀᴡᴀʀᴅ ᴛʜᴇ ᴍᴇssᴀɢᴇ ʏᴏᴜʀsᴇʟғ, ᴀɴᴅ ᴛʜᴇɴ sᴀᴠᴇ ɪᴛ.",
            )
        else:
            await msg.reply_text(
                "ʙᴏᴛs ᴀʀᴇ ᴋɪɴᴅᴀ ʜᴀɴᴅɪᴄᴀᴘᴘᴇᴅ ʙʏ ᴛᴇʟᴇɢʀᴀᴍ, ᴍᴀᴋɪɴɢ ɪᴛ ʜᴀʀᴅ ғᴏʀ ʙᴏᴛs ᴛᴏ "
                "ɪɴᴛᴇʀᴀᴄᴛ ᴡɪᴛʜ ᴏᴛʜᴇʀ ʙᴏᴛs, sᴏ ɪ ᴄᴀɴ'ᴛ sᴀᴠᴇ ᴛʜɪs ᴍᴇssᴀɢᴇ "
                "ʟɪᴋᴇ ɪ ᴜsᴜᴀʟʟʏ ᴡᴏᴜʟᴅ - ᴅᴏ ʏᴏᴜ ᴍɪɴᴅ ғᴏʀᴡᴀʀᴅɪɴɢ ɪᴛ ᴀɴᴅ "
                "ᴛʜᴇɴ sᴀᴠɪɴɢ ᴛʜᴀᴛ ɴᴇᴡ ᴍᴇssᴀɢᴇ? ᴛʜᴀɴᴋs!",
            )
        return


@connection_status
@check_admin(is_user=True)
async def clear(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    chat_id = update.effective_chat.id
    if len(args) >= 1:
        notename = args[0].lower()

        if sql.rm_note(chat_id, notename):
            await update.effective_message.reply_text("sᴜᴄᴄᴇssғᴜʟʟʏ ʀᴇᴍᴏᴠᴇᴅ ɴᴏᴛᴇ.")
        else:
            await update.effective_message.reply_text(
                "ᴛʜᴀᴛ's ɴᴏᴛ ᴀ ɴᴏᴛᴇ ɪɴ ᴍʏ ᴅᴀᴛᴀʙᴀsᴇ!"
            )


async def clearall(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    user = update.effective_user
    member = await chat.get_member(user.id)
    if member.status != "creator" and user.id not in DRAGONS:
        await update.effective_message.reply_text(
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
        await update.effective_message.reply_text(
            f"ᴀʀᴇ ʏᴏᴜ sᴜʀᴇ ʏᴏᴜ ᴡᴏᴜʟᴅ ʟɪᴋᴇ ᴛᴏ ᴄʟᴇᴀʀ ALL ɴᴏᴛᴇs ɪɴ {chat.title}? ᴛʜɪs ᴀᴄᴛɪᴏɴ ᴄᴀɴɴᴏᴛ ʙᴇ ᴜɴᴅᴏɴᴇ.",
            reply_markup=buttons,
            parse_mode=ParseMode.MARKDOWN,
        )


async def clearall_btn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    chat = update.effective_chat
    message = update.effective_message
    member = await chat.get_member(query.from_user.id)
    if query.data == "notes_rmall":
        if member.status == "creator" or query.from_user.id in DRAGONS:
            note_list = sql.get_all_chat_notes(chat.id)
            try:
                for notename in note_list:
                    note = notename.name.lower()
                    sql.rm_note(chat.id, note)
                await message.edit_text("ᴅᴇʟᴇᴛᴇᴅ ᴀʟʟ ɴᴏᴛᴇs.")
            except BadRequest:
                return

        if member.status == "administrator":
            await query.answer("ᴏɴʟʏ ᴏᴡɴᴇʀ ᴏғ ᴛʜᴇ ᴄʜᴀᴛ ᴄᴀɴ ᴅᴏ ᴛʜɪs.")

        if member.status == "member":
            await query.answer("ʏᴏᴜ ɴᴇᴇᴅ ᴛᴏ ʙᴇ ᴀᴅᴍɪɴ ᴛᴏ ᴅᴏ ᴛʜɪs.")
    elif query.data == "notes_cancel":
        if member.status == "creator" or query.from_user.id in DRAGONS:
            await message.edit_text("ᴄʟᴇᴀʀɪɴɢ ᴏғ ᴀʟʟ ɴᴏᴛᴇs ʜᴀs ʙᴇᴇɴ ᴄᴀɴᴄᴇʟʟᴇᴅ.")
            return
        if member.status == "administrator":
            await query.answer("ᴏɴʟʏ ᴏᴡɴᴇʀ ᴏғ ᴛʜᴇ ᴄʜᴀᴛ ᴄᴀɴ ᴅᴏ ᴛʜɪs.")
        if member.status == "member":
            await query.answer("ʏᴏᴜ ɴᴇᴇᴅ ᴛᴏ ʙᴇ ᴀᴅᴍɪɴ ᴛᴏ ᴅᴏ ᴛʜɪs.")


@connection_status
async def list_notes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    note_list = sql.get_all_chat_notes(chat_id)
    notes = len(note_list) + 1
    msg = "ɢᴇᴛ ɴᴏᴛᴇ ʙʏ `/notenumber` ᴏʀ `#notename` \n\n  *ɪᴅ*    *ɴᴏᴛᴇ* \n"
    for note_id, note in zip(range(1, notes), note_list):
        if note_id < 10:
            note_name = f"`{note_id:2}.`  `#{(note.name.lower())}`\n"
        else:
            note_name = f"`{note_id}.`  `#{(note.name.lower())}`\n"
        if len(msg) + len(note_name) > MessageLimit.MAX_TEXT_LENGTH:
            await update.effective_message.reply_text(
                msg, parse_mode=ParseMode.MARKDOWN
            )
            msg = ""
        msg += note_name

    if not note_list:
        try:
            await update.effective_message.reply_text("ɴᴏ ɴᴏᴛᴇs ɪɴ ᴛʜɪs ᴄʜᴀᴛ!")
        except BadRequest:
            await update.effective_message.reply_text(
                "ɴᴏ ɴᴏᴛᴇs ɪɴ ᴛʜɪs ᴄʜᴀᴛ!", quote=False
            )

    elif len(msg) != 0:
        await update.effective_message.reply_text(msg, parse_mode=ParseMode.MARKDOWN)


async def __import_data__(chat_id, data, message: Message):
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
            notedata = notedata[match.end() :].strip()
            if notedata:
                sql.add_note_to_db(chat_id, notename[1:], notedata, sql.Types.TEXT)
        elif matchsticker:
            content = notedata[matchsticker.end() :].strip()
            if content:
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
            buttons = ast.literal_eval(buttons)
            if buttons:
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
            content = file[0]
            if content:
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
            content = photo[0]
            if content:
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
            content = audio[0]
            if content:
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
            content = voice[0]
            if content:
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
            content = video[0]
            if content:
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
            content = video_note[0]
            if content:
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
            await exon.bot.send_document(
                chat_id,
                document=output,
                filename="failed_imports.txt",
                caption="ᴛʜᴇsᴇ ғɪʟᴇs/ᴘʜᴏᴛᴏs ғᴀɪʟᴇᴅ ᴛᴏ ɪᴍᴘᴏʀᴛ ᴅᴜᴇ ᴛᴏ ᴏʀɪɢɪɴᴀᴛɪɴɢ "
                "ғʀᴏᴍ ᴀɴᴏᴛʜᴇʀ ʙᴏᴛ. ᴛʜɪs ɪs ᴀ ᴛᴇʟᴇɢʀᴀᴍ API ʀᴇsᴛʀɪᴄᴛɪᴏɴ, and ᴄᴀɴ'ᴛ "
                "ʙᴇ ᴀᴠᴏɪᴅᴇᴅ. sᴏʀʀʏ ғᴏʀ ᴛʜᴇ ɪɴᴄᴏɴᴠᴇɴɪᴇɴᴄᴇ!",
                message_thread_id=message.message_thread_id
                if message.chat.is_forum
                else None,
            )


def __stats__():
    return f"• {sql.num_notes()} ɴᴏᴛᴇs, ᴀᴄʀᴏss {sql.num_chats()} ᴄʜᴀᴛs."


def __migrate__(old_chat_id, new_chat_id):
    sql.migrate_chat(old_chat_id, new_chat_id)


def __chat_settings__(chat_id, user_id):
    notes = sql.get_all_chat_notes(chat_id)
    return f"ᴛʜᴇʀᴇ ᴀʀᴇ `{len(notes)}` ɴᴏᴛᴇs ɪɴ ᴛʜɪs ᴄʜᴀᴛ."


__help__ = """
• /get <notename>*:* ɢᴇᴛ ᴛʜᴇ ɴᴏᴛᴇ ᴡɪᴛʜ ᴛʜɪs ɴᴏᴛᴇɴᴀᴍᴇ
• #<ɴᴏᴛᴇɴᴀᴍᴇ>*:* sᴀᴍᴇ ᴀs /get
• /notes` or `/saved*:* ʟɪsᴛ ᴀʟʟ sᴀᴠᴇᴅ ɴᴏᴛᴇs ɪɴ ᴛʜɪs ᴄʜᴀᴛ
• /number *:* ᴡɪʟʟ ᴘᴜʟʟ ᴛʜᴇ ɴᴏᴛᴇ ᴏғ ᴛʜᴀᴛ ɴᴜᴍʙᴇʀ ɪɴ ᴛʜᴇ ʟɪsᴛ

ɪғ ʏᴏᴜ ᴡᴏᴜʟᴅ ʟɪᴋᴇ ᴛᴏ ʀᴇᴛʀɪᴇᴠᴇ ᴛʜᴇ ᴄᴏɴᴛᴇɴᴛs ᴏғ ᴀ ɴᴏᴛᴇ ᴡɪᴛʜᴏᴜᴛ ᴀɴʏ ғᴏʀᴍᴀᴛᴛɪɴɢ, ᴜsᴇ `/get <ɴᴏᴛᴇɴᴀᴍᴇ> noformat`. ᴛʜɪs can \
ʙᴇ ᴜsᴇғᴜʟ ᴡʜᴇɴ ᴜᴘᴅᴀᴛɪɴɢ ᴀ ᴄᴜʀʀᴇɴᴛ ɴᴏᴛᴇ

*ᴀᴅᴍɪɴs ᴏɴʟʏ:*
• `/save <ɴᴏᴛᴇɴᴀᴍᴇ> <ɴᴏᴛᴇᴅᴀᴛᴀ>`*:* sᴀᴠᴇs ɴᴏᴛᴇᴅᴀᴛᴀ ᴀs ᴀ ɴᴏᴛᴇ ᴡɪᴛʜ ɴᴀᴍᴇ ɴᴏᴛᴇɴᴀᴍᴇ
ᴀ ʙᴜᴛᴛᴏɴ ᴄᴀɴ ʙᴇ ᴀᴅᴅᴇᴅ ᴛᴏ ᴀ ɴᴏᴛᴇ ʙʏ ᴜsɪɴɢ sᴛᴀɴᴅᴀʀᴅ ᴍᴀʀᴋᴅᴏᴡɴ ʟɪɴᴋ sʏɴᴛᴀx - ᴛʜᴇ ʟɪɴᴋ sʜᴏᴜʟᴅ ᴊᴜsᴛ ʙᴇ ᴘʀᴇᴘᴇɴᴅᴇᴅ ᴡɪᴛʜ ᴀ \
`buttonurl:` sᴇᴄᴛɪᴏɴ, ᴀs sᴜᴄʜ: `[somelink](buttonurl:example.com)`. 
ᴄʜᴇᴄᴋ `/markdownhelp` ғᴏʀ ᴍᴏʀᴇ ɪɴғᴏ

• /save <notename>*:* sᴀᴠᴇ ᴛʜᴇ ʀᴇᴘʟɪᴇᴅ ᴍᴇssᴀɢᴇ ᴀs ᴀ ɴᴏᴛᴇ ᴡɪᴛʜ ɴᴀᴍᴇ ɴᴏᴛᴇɴᴀᴍᴇ
 
 sᴇᴘᴀʀᴀᴛᴇ ᴅɪғғ ʀᴇᴘʟɪᴇs ʙʏ `%%%` ᴛᴏ ɢᴇᴛ ʀᴀɴᴅᴏᴍ ɴᴏᴛᴇs
 *ᴇxᴀᴍᴘʟᴇ:*
 `/save ɴᴏᴛᴇɴᴀᴍᴇ
 ʀᴇᴘʟʏ 1
 %%%
 ʀᴇᴘʟʏ 2
 %%%
 ʀᴇᴘʟʏ 3`
 
• /clear <ɴᴏᴛᴇɴᴀᴍᴇ>*:* ᴄʟᴇᴀʀ ɴᴏᴛᴇ ᴡɪᴛʜ ᴛʜɪs ɴᴀᴍᴇ
• /removeallnotes*:* ʀᴇᴍᴏᴠᴇs ᴀʟʟ ɴᴏᴛᴇs ғʀᴏᴍ ᴛʜᴇ ɢʀᴏᴜᴘ

 *ɴᴏᴛᴇ:* ɴᴏᴛᴇ ɴᴀᴍᴇs ᴀʀᴇ ᴄᴀsᴇ-ɪᴇɴsɪᴛɪᴠᴇ, ᴀɴᴅ ᴛʜᴇʏ ᴀʀᴇ ᴀᴜᴛᴏᴍᴀᴛɪᴄᴀʟʟʏ ᴄᴏɴᴠᴇʀᴛᴇᴅ ᴛᴏ ʟᴏᴡᴇʀᴄᴀsᴇ ʙᴇғᴏʀᴇ ɢᴇᴛᴛɪɴɢ saved.
"""

__mod_name__ = "𝐍ᴏᴛᴇs"

GET_HANDLER = CommandHandler("get", cmd_get)
HASH_GET_HANDLER = MessageHandler(filters.Regex(r"^#[^\s]+"), hash_get)
SLASH_GET_HANDLER = MessageHandler(filters.Regex(r"^/\d+$"), slash_get)
SAVE_HANDLER = CommandHandler(["save", "note"], save)
DELETE_HANDLER = CommandHandler("clear", clear)

LIST_HANDLER = DisableAbleCommandHandler(
    ["notes", "saved"], list_notes, admin_ok=True
)


CLEARALL = DisableAbleCommandHandler("removeallnotes", clearall)
CLEARALL_BTN = CallbackQueryHandler(clearall_btn, pattern=r"notes_.*")

exon.add_handler(GET_HANDLER)
exon.add_handler(SAVE_HANDLER)
exon.add_handler(LIST_HANDLER)
exon.add_handler(DELETE_HANDLER)
exon.add_handler(HASH_GET_HANDLER)
exon.add_handler(SLASH_GET_HANDLER)
exon.add_handler(CLEARALL)
exon.add_handler(CLEARALL_BTN)
