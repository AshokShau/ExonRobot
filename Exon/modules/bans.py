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

import html
from typing import Optional

from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ParseMode,
    TelegramError,
    Update,
)
from telegram.error import BadRequest
from telegram.ext import CallbackContext, CallbackQueryHandler, CommandHandler, Filters
from telegram.utils.helpers import mention_html

from Exon import (
    DEMONS,
    DEV_USERS,
    DRAGONS,
    LOGGER,
    OWNER_ID,
    TIGERS,
    WOLVES,
    dispatcher,
)
from Exon.modules.disable import DisableAbleCommandHandler
from Exon.modules.helper_funcs.chat_status import (
    bot_admin,
    can_delete,
    can_restrict,
    connection_status,
    dev_plus,
    is_user_admin,
    is_user_ban_protected,
    is_user_in_chat,
    user_admin,
    user_admin_no_reply,
    user_can_ban,
)
from Exon.modules.helper_funcs.extraction import extract_user_and_text
from Exon.modules.helper_funcs.filters import CustomFilters
from Exon.modules.helper_funcs.string_handling import extract_time
from Exon.modules.log_channel import gloggable, loggable


@connection_status
@bot_admin
@can_restrict
@user_admin
@user_can_ban
@loggable
def ban(update: Update, context: CallbackContext) -> str:
    chat = update.effective_chat
    user = update.effective_user
    message = update.effective_message
    log_message = ""
    bot = context.bot
    args = context.args
    reason = ""
    if message.reply_to_message and message.reply_to_message.sender_chat:
        if r := bot.ban_chat_sender_chat(
            chat_id=chat.id,
            sender_chat_id=message.reply_to_message.sender_chat.id,
        ):
            message.reply_text(
                f"ᴄʜᴀɴɴᴇʟ {html.escape(message.reply_to_message.sender_chat.title)} ᴡᴀs ʙᴀɴɴᴇᴅ sᴜᴄᴄᴇssғᴜʟʟʏ ғʀᴏᴍ {html.escape(chat.title)}",
                parse_mode="html",
            )

        else:
            message.reply_text("ғᴀɪʟᴇᴅ ᴛᴏ ʙᴀɴ ᴄʜᴀɴɴᴇʟ")
        return
    user_id, reason = extract_user_and_text(message, args)
    if not user_id:
        message.reply_text("⚠️ ᴜsᴇʀ ɴᴏᴛ ғᴏᴜɴᴅ.")
        return log_message
    try:
        member = chat.get_member(user_id)
    except BadRequest as excp:
        if excp.message != "ᴜsᴇʀ ɴᴏᴛ ғᴏᴜɴᴅ":
            raise
        message.reply_text("ᴄᴀɴ'ᴛ sᴇᴇᴍ ᴛᴏ ғɪɴᴅ ᴛʜɪs ᴘᴇʀsᴏɴ.")
        return log_message
    if user_id == bot.id:
        message.reply_text("ᴏʜ ʏᴇᴀʜ, ʙᴀɴ ᴍʏsᴇʟғ, ɴᴏᴏʙ sᴀʟᴀ!")
        return log_message
    if is_user_ban_protected(chat, user_id, member) and user not in DEV_USERS:
        if user_id == OWNER_ID:
            message.reply_text("ᴛʀʏɪɴɢ ᴛᴏ ᴘᴜᴛ ᴍᴇ ᴀɢᴀɪɴsᴛ ᴍʏ ᴏɴɪᴄʜᴀɴ ʜᴜʜ?")
        elif user_id in DEV_USERS:
            message.reply_text("I ᴄᴀɴ'ᴛ ᴀᴄᴛ ᴀɢᴀɪɴsᴛ ᴏᴜʀ ғᴀᴍɪʟʏ.")
        elif user_id in DRAGONS:
            message.reply_text(
                "ғɪɢʜᴛɪɴɢ ᴏᴜʀ ʙᴇsᴛ ғʀɪᴇɴᴅs ʜᴇʀᴇ ᴡɪʟʟ ᴘᴜᴛ ᴜsᴇʀ ʟɪᴠᴇs ᴀᴛ risk."
            )
        elif user_id in DEMONS:
            message.reply_text("ʙʀɪɴɢ ᴀɴ ᴏʀᴅᴇʀ ғʀᴏᴍ ᴏɴɪᴄʜᴀɴ ᴛᴏ ғɪɢʜᴛ ᴏᴜʀ ғʀɪᴇɴᴅs.")
        elif user_id in TIGERS:
            message.reply_text("ʙʀɪɴɢ ᴀɴ ᴏʀᴅᴇʀ ғʀᴏᴍ ᴏɴɪᴄʜᴀɴ ᴛᴏ ғɪɢʜᴛ ᴏᴜʀ ᴄʟᴀssᴍᴀᴛᴇs")
        elif user_id in WOLVES:
            message.reply_text("ɪɢɴɪᴛᴇ ᴀᴄᴄᴇss ᴍᴀᴋᴇ ᴛʜᴇᴍ ʙᴀɴ ɪᴍᴍᴜɴᴇ!")
        else:
            message.reply_text("⚠️ ᴄᴀɴɴᴏᴛ ʙᴀɴɴᴇᴅ ᴀᴅᴍɪɴ.")
        return log_message
    if message.text.startswith("/s"):
        silent = True
        if not can_delete(chat, context.bot.id):
            return ""
    else:
        silent = False
    log = (
        f"<b>{html.escape(chat.title)}:</b>\n"
        f"#{'S' if silent else ''}ʙᴀɴɴᴇᴅ\n"
        f"<b>ᴀᴅᴍɪɴ:</b> {mention_html(user.id, html.escape(user.first_name))}\n"
        f"<b>ᴜsᴇʀ:</b> {mention_html(member.user.id, html.escape(member.user.first_name))}"
    )
    if reason:
        log += f"<b>ʀᴇᴀsᴏɴ:</b> {reason}"
    try:
        chat.ban_member(user_id)
        if silent:
            if message.reply_to_message:
                message.reply_to_message.delete()
            message.delete()
            return log
        # bot.send_sticker(chat.id, BAN_STICKER)  # banhammer marie sticker
        reply = (
            f"<code>❕</code><b>Ban Event</b>\n\n"
            f"<b>• ᴜsᴇʀ:</b> {mention_html(member.user.id, html.escape(member.user.first_name))}\n"
            f"<b>• ᴜsᴇʀ 𝙸𝙳:</b> <code>{member.user.id}</code>\n"
            f"<b>• ʙᴀɴɴᴇᴅ ʙʏ:</b> {mention_html(user.id, html.escape(user.first_name))}"
        )
        if reason:
            reply += f"\n<b>• ʀᴇᴀsᴏɴ:</b> {html.escape(reason)}"
        bot.sendMessage(
            chat.id,
            reply,
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text="ᴜɴʙᴀɴ ❗", callback_data=f"unbanb_unban={user_id}"
                        ),
                        InlineKeyboardButton(
                            text="ᴅᴇʟᴇᴛᴇ ❗", callback_data="unbanb_del"
                        ),
                    ]
                ]
            ),
            parse_mode=ParseMode.HTML,
        )
        return log
    except BadRequest as excp:
        if excp.message == "ʀᴇᴘʟʏ ᴍᴇssᴀɢᴇ ɴᴏᴛ ғᴏᴜɴᴅ":
            # Do not reply
            if silent:
                return log
            message.reply_text("ʙᴀɴɴᴇᴅ ❗!", quote=False)
            return log
        else:
            LOGGER.warning(update)
            LOGGER.exception(
                "ERROR ʙᴀɴɴɪɴɢ ᴜsᴇʀ %s ɪɴ ᴄʜᴀᴛ %s (%s) ᴅᴜᴇ ᴛᴏ %s",
                user_id,
                chat.title,
                chat.id,
                excp.message,
            )
            message.reply_text("ᴜʜᴍ...ᴛʜᴀᴛ ᴅɪᴅɴ'ᴛ ᴡᴏʀᴋ...")
    return log_message


@connection_status
@bot_admin
@can_restrict
@user_admin
@user_can_ban
@loggable
def temp_ban(update: Update, context: CallbackContext) -> str:
    chat = update.effective_chat
    user = update.effective_user
    message = update.effective_message
    log_message = ""
    bot, args = context.bot, context.args
    user_id, reason = extract_user_and_text(message, args)
    if not user_id:
        message.reply_text("⚠️ ᴜsᴇʀ ɴᴏᴛ ғᴏᴜɴᴅ.")
        return log_message
    try:
        member = chat.get_member(user_id)
    except BadRequest as excp:
        if excp.message != "ᴜsᴇʀ ɴᴏᴛ ғᴏᴜɴᴅ":
            raise
        message.reply_text("I ᴄᴀɴ'ᴛ sᴇᴇᴍ ᴛᴏ ғɪɴᴅ ᴛʜɪs ᴜsᴇʀ.")
        return log_message
    if user_id == bot.id:
        message.reply_text("I'ᴍ ɴᴏᴛ ɢᴏɴɴᴀ BAN ᴍʏsᴇʟғ, ᴀʀᴇ ʏᴏᴜ ɴᴏᴏʙ ?")
        return log_message
    if is_user_ban_protected(chat, user_id, member):
        message.reply_text("I ᴅᴏɴ'ᴛ ғᴇᴇʟ ʟɪᴋᴇ ɪᴛ.")
        return log_message
    if not reason:
        message.reply_text("ʏᴏᴜ ʜᴀᴠᴇɴ'ᴛ sᴘᴇᴄɪғɪᴇᴅ ᴀ ᴛɪᴍᴇ ᴛᴏ ʙᴀɴ ᴛʜɪs ᴜsᴇʀ ғᴏʀ!")
        return log_message
    split_reason = reason.split(None, 1)
    time_val = split_reason[0].lower()
    reason = split_reason[1] if len(split_reason) > 1 else ""
    bantime = extract_time(message, time_val)
    if not bantime:
        return log_message
    log = (
        f"<b>{html.escape(chat.title)}:</b>\n"
        "#ᴛᴇᴍᴘ ʙᴀɴɴᴇᴅ\n"
        f"<b>ᴀᴅᴍɪɴ:</b> {mention_html(user.id, html.escape(user.first_name))}\n"
        f"<b>ᴜsᴇʀ:</b> {mention_html(member.user.id, html.escape(member.user.first_name))}\n"
        f"<b>ᴛɪᴍᴇ:</b> {time_val}"
    )
    if reason:
        log += f"\nʀᴇᴀsᴏɴ: {reason}"
    try:
        chat.ban_member(user_id, until_date=bantime)
        # bot.send_sticker(chat.id, BAN_STICKER)  # banhammer marie sticker
        reply_msg = (
            f"<code>❕</code><b>Temporarily Banned</b>\n\n"
            f"<b>• ᴜsᴇʀ:</b> {mention_html(member.user.id, html.escape(member.user.first_name))}\n"
            f"<b>• ᴜsᴇʀ ɪᴅ:</b> <code>{member.user.id}</code>\n"
            f"<b>• ʙᴀɴɴᴇᴅ ғᴏʀ:</b> {time_val}\n"
            f"<b>• ʙᴀɴɴᴇᴅ ʙʏ:</b> {mention_html(user.id, html.escape(user.first_name))}"
        )
        if reason:
            reply_msg += f"\n<b>• ʀᴇᴀsᴏɴ:</b> {html.escape(reason)}"
        bot.sendMessage(
            chat.id,
            reply_msg,
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text="ᴜɴʙᴀɴ ❗", callback_data=f"unbanb_unban={user_id}"
                        ),
                        InlineKeyboardButton(
                            text="ᴅᴇʟᴇᴛᴇ ❗", callback_data="unbanb_del"
                        ),
                    ]
                ]
            ),
            parse_mode=ParseMode.HTML,
        )
        return log
    except BadRequest as excp:
        if excp.message == "ʀᴇᴘʟʏ ᴍᴇssᴀɢᴇ ɴᴏᴛ ғᴏᴜɴᴅ":
            # Do not reply
            message.reply_text(
                f"{mention_html(member.user.id, html.escape(member.user.first_name))} [<code>{member.user.id}</code>] ʙᴀɴɴᴇᴅ ғᴏʀ {time_val}.",
                quote=False,
            )
            return log
        else:
            LOGGER.warning(update)
            LOGGER.exception(
                "ᴇʀʀᴏʀ ʙᴀɴɴɪɴɢ ᴜsᴇʀ %s ɪɴ ᴄʜᴀᴛ %s (%s) ᴅᴜᴇ ᴛᴏ %s",
                user_id,
                chat.title,
                chat.id,
                excp.message,
            )
            message.reply_text("ᴡᴇʟʟ ᴅᴀᴍɴ, ɪ ᴄᴀɴ'ᴛ ʙᴀɴ ᴛʜᴀᴛ ᴜsᴇʀ.")
    return log_message


@connection_status
@bot_admin
@can_restrict
@user_admin_no_reply
@user_can_ban
@loggable
def unbanb_btn(update: Update, context: CallbackContext) -> str:
    bot = context.bot
    query = update.callback_query
    chat = update.effective_chat
    user = update.effective_user
    if query.data != "unbanb_del":
        splitter = query.data.split("=")
        query_match = splitter[0]
        if query_match == "unbanb_unban":
            user_id = splitter[1]
            if not is_user_admin(chat, int(user.id)):
                bot.answer_callback_query(
                    query.id,
                    text="⚠️ ʏᴏᴜ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ ᴇɴᴏᴜɢʜ ʀɪɢʜᴛs ᴛᴏ ᴜɴᴍᴜᴛᴇ ᴘᴇᴏᴘʟᴇ",
                    show_alert=True,
                )
                return ""
            try:
                member = chat.get_member(user_id)
            except BadRequest:
                pass
            chat.unban_member(user_id)
            query.message.edit_text(
                f"{mention_html(member.user.id, html.escape(member.user.first_name))} [<code>{member.user.id}</code>] ᴜɴʙᴀɴɴᴇᴅ ʙʏ {mention_html(user.id, html.escape(user.first_name))}",
                parse_mode=ParseMode.HTML,
            )
            bot.answer_callback_query(query.id, text="Unbanned!")
            return (
                f"<b>{html.escape(chat.title)}:</b>\n"
                f"#ᴜɴʙᴀɴɴᴇᴅ\n"
                f"<b>ᴀᴅᴍɪɴ:</b> {mention_html(user.id, user.first_name)}\n"
                f"<b>ᴜsᴇʀ:</b> {mention_html(member.user.id, member.user.first_name)}"
            )
    else:
        if not is_user_admin(chat, int(user.id)):
            bot.answer_callback_query(
                query.id,
                text="⚠️ ʏᴏᴜ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ ᴇɴᴏᴜɢʜ ʀɪɢʜᴛs ᴛᴏ ᴅᴇʟᴇᴛᴇ ᴛʜɪs ᴍᴇssᴀɢᴇ.",
                show_alert=True,
            )
            return ""
        query.message.delete()
        bot.answer_callback_query(query.id, text="ᴅᴇʟᴇᴛᴇᴅ !")
        return ""


@connection_status
@bot_admin
@can_restrict
@user_admin
@user_can_ban
@loggable
def punch(update: Update, context: CallbackContext) -> str:
    chat = update.effective_chat
    user = update.effective_user
    message = update.effective_message
    log_message = ""
    bot, args = context.bot, context.args
    user_id, reason = extract_user_and_text(message, args)
    if not user_id:
        message.reply_text("⚠️ ᴜsᴇʀ ɴᴏᴛ ғᴏᴜɴᴅ")
        return log_message
    try:
        member = chat.get_member(user_id)
    except BadRequest as excp:
        if excp.message != "ᴜsᴇʀ ɴᴏᴛ ғᴏᴜɴᴅ":
            raise
        message.reply_text("⚠️ I ᴄᴀɴ'ᴛ sᴇᴇᴍ ᴛᴏ ғɪɴᴅ ᴛʜɪs ᴜsᴇʀ.")
        return log_message
    if user_id == bot.id:
        message.reply_text("ʏᴇᴀʜʜʜ I'ᴍ ɴᴏᴛ ɢᴏɴɴᴀ ᴅᴏ ᴛʜᴀᴛ.")
        return log_message
    if is_user_ban_protected(chat, user_id):
        message.reply_text("I ʀᴇᴀʟʟʏ ᴡɪsʜ ɪ ᴄᴏᴜʟᴅ ᴘᴜɴᴄʜ ᴛʜɪs ᴜsᴇʀ....")
        return log_message
    if res := chat.unban_member(user_id):
        # bot.send_sticker(chat.id, BAN_STICKER)  # banhammer marie sticker
        bot.sendMessage(
            chat.id,
            f"{mention_html(member.user.id, html.escape(member.user.first_name))} [<code>{member.user.id}</code>] Kicked by {mention_html(user.id, html.escape(user.first_name))}",
            parse_mode=ParseMode.HTML,
        )
        log = (
            f"<b>{html.escape(chat.title)}:</b>\n"
            f"#ᴋɪᴄᴋᴇᴅ\n"
            f"<b>ᴀᴅᴍɪɴ:</b> {mention_html(user.id, html.escape(user.first_name))}\n"
            f"<b>ᴜsᴇʀ:</b> {mention_html(member.user.id, html.escape(member.user.first_name))}"
        )
        if reason:
            log += f"\n<b>ʀᴇᴀsᴏɴ:</b> {reason}"
        return log
    else:
        message.reply_text("⚠️ ᴡᴇʟʟ ᴅᴀᴍɴ, ɪ ᴄᴀɴ'ᴛ ᴘᴜɴᴄʜ ᴛʜᴀᴛ ᴜsᴇʀ.")
    return log_message


@bot_admin
@can_restrict
def punchme(update: Update, context: CallbackContext):
    user_id = update.effective_message.from_user.id
    if is_user_admin(update.effective_chat, user_id):
        update.effective_message.reply_text("I ᴡɪsʜ I ᴄᴏᴜʟᴅ... ʙᴜᴛ ʏᴏᴜ'ʀᴇ ᴀɴ ᴀᴅᴍɪɴ .")
        return
    if res := update.effective_chat.unban_member(user_id):
        update.effective_message.reply_text(
            "ᴘᴜɴᴄʜᴇs ʏᴏᴜ ᴏᴜᴛ ᴏғ ᴛʜᴇ ɢʀᴏᴜᴘ !!",
        )
    else:
        update.effective_message.reply_text("ʜᴜʜ? I ᴄᴀɴ'ᴛ :/")


@connection_status
@bot_admin
@can_restrict
@user_admin
@user_can_ban
@loggable
def unban(update: Update, context: CallbackContext) -> Optional[str]:
    message = update.effective_message
    user = update.effective_user
    chat = update.effective_chat
    log_message = ""
    bot, args = context.bot, context.args
    if message.reply_to_message and message.reply_to_message.sender_chat:
        if r := bot.unban_chat_sender_chat(
            chat_id=chat.id,
            sender_chat_id=message.reply_to_message.sender_chat.id,
        ):
            message.reply_text(
                f"ᴄʜᴀɴɴᴇʟ {html.escape(message.reply_to_message.sender_chat.title)} ᴡᴀs ᴜɴʙᴀɴɴᴇᴅ sᴜᴄᴄᴇssғᴜʟʟʏ ғʀᴏᴍ {html.escape(chat.title)}",
                parse_mode="html",
            )

        else:
            message.reply_text("ғᴀɪʟᴇᴅ ᴛᴏ ᴜɴʙᴀɴ ᴄʜᴀɴɴᴇʟ")
        return
    user_id, reason = extract_user_and_text(message, args)
    if not user_id:
        message.reply_text("⚠️ ᴜsᴇʀ ɴᴏᴛ ғᴏᴜɴᴅ.")
        return log_message
    try:
        member = chat.get_member(user_id)
    except BadRequest as excp:
        if excp.message != "ᴜsᴇʀ ɴᴏᴛ ғᴏᴜɴᴅ":
            raise
        message.reply_text("I ᴄᴀɴ'ᴛ sᴇᴇᴍ ᴛᴏ ғɪɴᴅ ᴛʜɪs ᴜsᴇʀ.")
        return log_message
    if user_id == bot.id:
        message.reply_text("ʜᴏᴡ ᴡᴏᴜʟᴅ ɪ ᴜɴʙᴀɴ ᴍʏsᴇʟғ ɪғ ɪ ᴡᴀsɴ'ᴛ ʜᴇʀᴇ...?")
        return log_message
    if is_user_in_chat(chat, user_id):
        message.reply_text("⚠️ ᴜsᴇʀ ɴᴏᴛ ғᴏᴜɴᴅ.")
        return log_message
    chat.unban_member(user_id)
    message.reply_text(
        f"{mention_html(member.user.id, html.escape(member.user.first_name))} [<code>{member.user.id}</code>] ᴡᴀs ᴜɴʙᴀɴɴᴇᴅ ʙʏ {mention_html(user.id, user.first_name)}",
        parse_mode=ParseMode.HTML,
    )
    log = (
        f"<b>{html.escape(chat.title)}:</b>\n"
        f"#ᴜɴʙᴀɴɴᴇᴅ\n"
        f"<b>ᴀᴅᴍɪɴ:</b> {mention_html(user.id, html.escape(user.first_name))}\n"
        f"<b>ᴜsᴇʀ:</b> {mention_html(member.user.id, html.escape(member.user.first_name))}"
    )
    if reason:
        log += f"\n<b>ʀᴇᴀsᴏɴ:</b> {reason}"
    return log


@connection_status
@bot_admin
@can_restrict
@gloggable
def selfunban(update: Update, context: CallbackContext) -> str:
    message = update.effective_message
    user = update.effective_user
    bot, args = context.bot, context.args
    if user.id not in DRAGONS or user.id not in TIGERS:
        return
    try:
        chat_id = int(args[0])
    except:
        message.reply_text("ɢɪᴠᴇ ᴀ ᴠᴀʟɪᴅ ᴄʜᴀᴛ ɪᴅ.")
        return
    chat = bot.getChat(chat_id)
    try:
        member = chat.get_member(user.id)
    except BadRequest as excp:
        if excp.message == "ᴜsᴇʀ ɴᴏᴛ ғᴏᴜɴᴅ":
            message.reply_text("I ᴄᴀɴ'ᴛ sᴇᴇᴍ ᴛᴏ ғɪɴᴅ ᴛʜɪs ᴜsᴇʀ.")
            return
        else:
            raise
    if is_user_in_chat(chat, user.id):
        message.reply_text("Aren't you already in the chat??")
        return
    chat.unban_member(user.id)
    message.reply_text(f"ʏᴇᴘ, ɪ ʜᴀᴠᴇ ᴜɴʙᴀɴɴᴇᴅ ᴛʜᴇ ᴜsᴇʀ.")
    log = (
        f"<b>{html.escape(chat.title)}:</b>\n"
        f"#ᴜɴʙᴀɴɴᴇᴅ\n"
        f"<b>ᴜsᴇʀ:</b> {mention_html(member.user.id, html.escape(member.user.first_name))}"
    )
    return log


@bot_admin
@can_restrict
@loggable
def banme(update: Update, context: CallbackContext):
    user_id = update.effective_message.from_user.id
    chat = update.effective_chat
    user = update.effective_user
    if is_user_admin(update.effective_chat, user_id):
        update.effective_message.reply_text("⚠️ I ᴄᴀɴɴᴏᴛ ʙᴀɴɴᴇᴅ ᴀᴅᴍɪɴ.")
        return
    if res := update.effective_chat.ban_member(user_id):
        update.effective_message.reply_text("ʏᴇs, ʏᴏᴜ'ʀᴇ ʀɪɢʜᴛ! ɢᴛғᴏ..")
        return f"<b>{html.escape(chat.title)}:</b>\n#ʙᴀɴᴍᴇ\n<b>ᴜsᴇʀ:</b> {mention_html(user.id, user.first_name)}\n<b>ɪᴅ:</b> <code>{user_id}</code>"

    else:
        update.effective_message.reply_text("Huh? I can't :/")


@dev_plus
def abishnoi(update: Update, context: CallbackContext):
    args = context.args
    bot = context.bot
    try:
        chat_id = str(args[0])
        del args[0]
    except TypeError:
        update.effective_message.reply_text("ᴘʟᴇᴀsᴇ ɢɪᴠᴇ ᴍᴇ ᴀ ᴄʜᴀᴛ ᴛᴏ ᴇᴄʜᴏ ᴛᴏ!")
    to_send = " ".join(args)
    if len(to_send) >= 2:
        try:
            bot.sendMessage(int(chat_id), to_send)
        except TelegramError:
            LOGGER.warning("ᴄᴏᴜʟᴅɴ'ᴛ sᴇɴᴅ ᴛᴏ ɢʀᴏᴜᴘ %s", chat_id)
            update.effective_message.reply_text(
                "ᴄᴏᴜʟᴅɴ'ᴛ sᴇɴᴅ ᴛʜᴇ ᴍᴇssᴀɢᴇ. ᴘᴇʀʜᴀᴘs ɪ'ᴍ ɴᴏᴛ ᴘᴀʀᴛ ᴏғ ᴛʜᴀᴛ ɢʀᴏᴜᴘ?"
            )


__help__ = """
*ᴜsᴇʀ ᴄᴏᴍᴍᴀɴᴅs:*

• /kickme*:* `ᴋɪᴄᴋs ᴛʜᴇ ᴜsᴇʀ ᴡʜᴏ ɪssᴜᴇᴅ ᴛʜᴇ ᴄᴏᴍᴍᴀɴᴅ `

• /banme*:* `ʙᴀɴs ᴛʜᴇ ᴜsᴇʀ ᴡʜᴏ ɪssᴜᴇᴅ ᴛʜᴇ ᴄᴏᴍᴍᴀɴᴅ `

*ᴀᴅᴍɪɴs ᴏɴʟʏ:*

• /ban <userhandle>*:*` ʙᴀɴs ᴀ ᴜsᴇʀ. (ᴠɪᴀ ʜᴀɴᴅʟᴇ, ᴏʀ ʀᴇᴘʟʏ `
)
• /sban <ᴜsᴇʀʜᴀɴᴅʟᴇ>*:* `sɪʟᴇɴᴛʟʏ ʙᴀɴ ᴀ ᴜsᴇʀ. ᴅᴇʟᴇᴛᴇs ᴄᴏᴍᴍᴀɴᴅ, ʀᴇᴘʟɪᴇᴅ ᴍᴇssᴀɢᴇ ᴀɴᴅ ᴅᴏᴇsɴ'ᴛ ʀᴇᴘʟʏ. (ᴠɪᴀ ʜᴀɴᴅʟᴇ, ᴏʀ ʀᴇᴘʟʏ)`

• /tban <ᴜsᴇʀʜᴀɴᴅʟᴇ> x(m/h/d)*:* `ʙᴀɴs ᴀ ᴜsᴇʀ ғᴏʀ x ᴛɪᴍᴇ. (ᴠɪᴀ ʜᴀɴᴅʟᴇ, ᴏʀ ʀᴇᴘʟʏ). ᴍ = ᴍɪɴᴜᴛᴇs, h = ʜᴏᴜʀs, d = ᴅᴀʏs.`

• /unban <userhandle>*:* `ᴜɴʙᴀɴs ᴀ ᴜsᴇʀ. (ᴠɪᴀ ʜᴀɴᴅʟᴇ, ᴏʀ ʀᴇᴘʟʏ )`

• /kick <userhandle>*:* `ᴋɪᴄᴋs ᴀ ᴜsᴇʀ ᴏᴜᴛ ᴏғ ᴛʜᴇ ɢʀᴏᴜᴘ, (via ʜᴀɴᴅʟᴇ, ᴏʀ ʀᴇᴘʟʏ)`

• /mute <userhandle>*:* `sɪʟᴇɴᴄᴇs ᴀ ᴜsᴇʀ. ᴄᴀɴ ᴀʟsᴏ ʙᴇ ᴜsᴇᴅ ᴀs ᴀ ʀᴇᴘʟʏ, ᴍᴜᴛɪɴɢ ᴛʜᴇ ʀᴇᴘʟɪᴇᴅ ᴛᴏ ᴜsᴇʀ.`

• /tmute <userhandle> x(m/h/d)*:* `ᴍᴜᴛᴇs a ᴜsᴇʀᴛ for x ᴛɪᴍᴇ. (ᴠɪᴀ ʜᴀɴᴅʟᴇ, ᴏʀ ʀᴇᴘʟʏ). ᴍ = ᴍɪɴᴜᴛᴇs, h = ʜᴏᴜʀs, d = ᴅᴀʏs `
.
• /unmute <userhandle>*:* `ᴜɴᴍᴜᴛᴇs ᴀ ~ user. ᴄᴀɴ ᴀʟsᴏ ʙᴇ ᴜsᴇᴅ ᴀs a ʀᴇᴘʟʏ, ᴍᴜᴛɪɴɢ ᴛʜᴇ ʀᴇᴘʟɪᴇᴅ ᴛᴏ ᴜsᴇʀ `
.
• /zombies*:* `sᴇᴀʀᴄʜᴇs ᴅᴇʟᴇᴛᴇᴅ ᴀᴄᴄᴏᴜɴᴛ `

• /zombies clean*:* `ʀᴇᴍᴏᴠᴇs ᴅᴇʟᴇᴛᴇᴅ ᴀᴄᴄᴏᴜɴᴛs ғʀᴏᴍ ᴛʜᴇ ɢʀᴏᴜᴘ `
.
• /abishnoi <chatid> <ᴍsɢ>*:* `ᴍᴀᴋᴇ ᴍᴇ sᴇɴᴅ ᴀ ᴍᴇssᴀɢᴇ ᴛᴏ ᴀ sᴘᴇᴄɪғɪᴄ ᴄʜᴀᴛ `.
"""

__mod_name__ = "𝙱ᴀɴs"

BAN_HANDLER = CommandHandler(["ban", "sban"], ban, run_async=True)
TEMPBAN_HANDLER = CommandHandler(["tban"], temp_ban, run_async=True)
KICK_HANDLER = CommandHandler(["kick", "punch"], punch, run_async=True)
UNBAN_HANDLER = CommandHandler("unban", unban, run_async=True)
##ROAR_HANDLER = CommandHandler("roar", selfunban, run_async=True)
UNBAN_BUTTON_HANDLER = CallbackQueryHandler(unbanb_btn, pattern=r"unbanb_")
KICKME_HANDLER = DisableAbleCommandHandler(
    ["kickme", "punchme"], punchme, filters=Filters.chat_type.groups, run_async=True
)
ABISHNOI_HANDLER = CommandHandler(
    "abishnoi",
    abishnoi,
    pass_args=True,
    filters=CustomFilters.sudo_filter,
    run_async=True,
)
BANME_HANDLER = CommandHandler("banme", banme, run_async=True)

dispatcher.add_handler(BAN_HANDLER)
dispatcher.add_handler(TEMPBAN_HANDLER)
dispatcher.add_handler(KICK_HANDLER)
dispatcher.add_handler(UNBAN_HANDLER)
# dispatcher.add_handler(ROAR_HANDLER)
dispatcher.add_handler(KICKME_HANDLER)
dispatcher.add_handler(UNBAN_BUTTON_HANDLER)
dispatcher.add_handler(ABISHNOI_HANDLER)
dispatcher.add_handler(BANME_HANDLER)

__handlers__ = [
    BAN_HANDLER,
    TEMPBAN_HANDLER,
    KICK_HANDLER,
    UNBAN_HANDLER,
    # ROAR_HANDLER,
    KICKME_HANDLER,
    UNBAN_BUTTON_HANDLER,
    ABISHNOI_HANDLER,
    BANME_HANDLER,
]
