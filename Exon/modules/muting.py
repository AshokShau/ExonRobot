"""
MIT License

Copyright (c) 2022 ABISHNOI69

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

# ""DEAR PRO PEOPLE,  DON'T REMOVE & CHANGE THIS LINE
# TG :- @Abishnoi1m
#     UPDATE   :- Abishnoi_bots
#     GITHUB :- ABISHNOI69 ""

import html
import re
from typing import Optional

from telegram import (
    Bot,
    CallbackQuery,
    Chat,
    ChatPermissions,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ParseMode,
    Update,
    User,
)
from telegram.error import BadRequest
from telegram.ext import CallbackContext, CallbackQueryHandler, CommandHandler
from telegram.utils.helpers import mention_html

from Exon import LOGGER, TIGERS, dispatcher
from Exon.modules.helper_funcs.chat_status import (
    bot_admin,
    can_restrict,
    connection_status,
    is_user_admin,
    user_admin,
    user_admin_no_reply,
)
from Exon.modules.helper_funcs.extraction import extract_user_and_text
from Exon.modules.helper_funcs.string_handling import extract_time
from Exon.modules.log_channel import loggable


def check_user(user_id: int, bot: Bot, update: Update) -> Optional[str]:
    if not user_id:
        return "You don't seem to be referring to a user or the ID specified is incorrect.."

    try:
        member = update.effective_chat.get_member(user_id)
    except BadRequest as excp:
        if excp.message == "User not found":
            return "I can't seem to find this user"
        raise
    if user_id == bot.id:
        return "I'm not gonna MUTE myself, How high are you?"

    if is_user_admin(update, user_id, member) or user_id in TIGERS:
        return "Can't. Find someone else to mute but not this one."

    return None


@connection_status
@bot_admin
@user_admin
@loggable
def mute(update: Update, context: CallbackContext) -> str:
    bot, args = context.bot, context.args
    chat = update.effective_chat
    user = update.effective_user
    message = update.effective_message

    user_id, reason = extract_user_and_text(message, args)
    reply = check_user(user_id, bot, update)

    if reply:
        message.reply_text(reply)
        return ""

    member = chat.get_member(user_id)

    log = (
        f"<b>{html.escape(chat.title)}:</b>\n"
        f"#MUTE\n"
        f"<b>Admin:</b> {mention_html(user.id, user.first_name)}\n"
        f"<b>User:</b> {mention_html(member.user.id, member.user.first_name)}"
    )

    if reason:
        log += f"\n<b>Reason:</b> {reason}"

    if member.can_send_messages is None or member.can_send_messages:
        chat_permissions = ChatPermissions(can_send_messages=False)
        bot.restrict_chat_member(chat.id, user_id, chat_permissions)
        msg = (
            f"Yep! Muted {mention_html(member.user.id, member.user.first_name)} for talking in {chat.title}\n"
            f"by {mention_html(user.id, html.escape(user.first_name))}"
        )
        if reason:
            msg += f"\nReason: {html.escape(reason)}"

        keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text="⚠️ Unmute",
                        callback_data="unmute_({})".format(member.user.id),
                    ),
                    InlineKeyboardButton(text="❌ Delete", callback_data="close2"),
                ]
            ]
        )
        bot.sendMessage(
            chat.id,
            msg,
            reply_markup=keyboard,
            parse_mode=ParseMode.HTML,
        )
        return log
    message.reply_text("This user is already muted!")

    return ""


close_keyboard = InlineKeyboardMarkup(
    [[InlineKeyboardButton("❌ Delete", callback_data="close2")]]
)


@connection_status
@bot_admin
@user_admin
@loggable
def unmute(update: Update, context: CallbackContext) -> str:
    bot, args = context.bot, context.args
    chat = update.effective_chat
    user = update.effective_user
    message = update.effective_message

    user_id, reason = extract_user_and_text(message, args)
    if not user_id:
        message.reply_text(
            "You'll need to either give me a username to unmute, or reply to someone to be unmuted."
        )
        return ""

    member = chat.get_member(int(user_id))

    if member.status in ("kicked", "left"):
        message.reply_text(
            "This user isn't even in the chat, unmuting them won't make them talk more than they "
            "already do!",
        )

    elif (
        member.can_send_messages
        and member.can_send_media_messages
        and member.can_send_other_messages
        and member.can_add_web_page_previews
    ):
        message.reply_text("This user already has the right to speak.")
    else:
        chat_permissions = ChatPermissions(
            can_send_messages=True,
            can_invite_users=True,
            can_pin_messages=True,
            can_send_polls=True,
            can_change_info=True,
            can_send_media_messages=True,
            can_send_other_messages=True,
            can_add_web_page_previews=True,
        )
        try:
            bot.restrict_chat_member(chat.id, int(user_id), chat_permissions)
        except BadRequest:
            pass
        reply = (
            f"Yep! Unmuted {mention_html(member.user.id, member.user.first_name)} "
            f"by {mention_html(user.id, user.first_name)} in <b>{message.chat.title}</b>"
        )
        if reason:
            reply += f"Reason: {reason}"
        bot.sendMessage(
            chat.id,
            reply,
            parse_mode=ParseMode.HTML,
        )
        return (
            f"<b>{html.escape(chat.title)}:</b>\n"
            f"#UNMUTE\n"
            f"<b>Admin:</b> {mention_html(user.id, user.first_name)}\n"
            f"<b>User:</b> {mention_html(member.user.id, member.user.first_name)}"
        )
    return ""


@connection_status
@bot_admin
@can_restrict
@user_admin
@loggable
def temp_mute(update: Update, context: CallbackContext) -> str:
    bot, args = context.bot, context.args
    chat = update.effective_chat
    user = update.effective_user
    message = update.effective_message

    user_id, reason = extract_user_and_text(message, args)
    reply = check_user(user_id, bot, update)

    if reply:
        message.reply_text(reply)
        return ""

    member = chat.get_member(user_id)

    if not reason:
        message.reply_text("You haven't specified a time to mute this user for!")
        return ""

    split_reason = reason.split(None, 1)

    time_val = split_reason[0].lower()
    reason = split_reason[1] if len(split_reason) > 1 else ""
    mutetime = extract_time(message, time_val)

    if not mutetime:
        return ""

    log = (
        f"<b>{html.escape(chat.title)}:</b>\n"
        f"#TEMP MUTED\n"
        f"<b>Admin:</b> {mention_html(user.id, user.first_name)}\n"
        f"<b>User:</b> {mention_html(member.user.id, member.user.first_name)}\n"
        f"<b>Time:</b> {time_val}"
    )
    if reason:
        log += f"\n<b>Reason:</b> {reason}"

    try:
        if member.can_send_messages is None or member.can_send_messages:
            chat_permissions = ChatPermissions(can_send_messages=False)
            bot.restrict_chat_member(
                chat.id,
                user_id,
                chat_permissions,
                until_date=mutetime,
            )
            msg = (
                f"Yep! Temporary Muted {mention_html(member.user.id, member.user.first_name)} from talking for <code>{time_val}</code> in {chat.title}\n"
                f"by {mention_html(user.id, html.escape(user.first_name))}",
            )

            keyboard = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text="⚠️ Unmute",
                            callback_data="unmute_({})".format(member.user.id),
                        ),
                        InlineKeyboardButton(text="❌ Delete", callback_data="close2"),
                    ]
                ]
            )
            bot.sendMessage(
                chat.id, msg, reply_markup=keyboard, parse_mode=ParseMode.HTML
            )

            return log
        message.reply_text("This user is already muted.")

    except BadRequest as excp:
        if excp.message == "Reply message not found":
            # Do not reply
            message.reply_text(f"Muted for {time_val}!", quote=False)
            return log
        LOGGER.warning(update)
        LOGGER.exception(
            "ERROR muting user %s in chat %s (%s) due to %s",
            user_id,
            chat.title,
            chat.id,
            excp.message,
        )
        message.reply_text("Well damn, I can't mute that user.")

    return ""


close_keyboard = InlineKeyboardMarkup(
    [[InlineKeyboardButton("❌ Delete", callback_data="close2")]]
)


@user_admin_no_reply
@bot_admin
@loggable
def button(update: Update, context: CallbackContext) -> str:
    query: Optional[CallbackQuery] = update.callback_query
    user: Optional[User] = update.effective_user
    bot: Optional[Bot] = context.bot
    match = re.match(r"unmute_\((.+?)\)", query.data)
    if match:
        user_id = match.group(1)
        chat: Optional[Chat] = update.effective_chat
        member = chat.get_member(user_id)
        chat_permissions = ChatPermissions(
            can_send_messages=True,
            can_invite_users=True,
            can_pin_messages=True,
            can_send_polls=True,
            can_change_info=True,
            can_send_media_messages=True,
            can_send_other_messages=True,
            can_add_web_page_previews=True,
        )
        unmuted = bot.restrict_chat_member(chat.id, int(user_id), chat_permissions)
        if unmuted:
            update.effective_message.edit_text(
                f"Yep! User {mention_html(member.user.id, member.user.first_name)} can start talking again in {chat.title}!",
                parse_mode=ParseMode.HTML,
            )
            query.answer("Unmuted!")
            return (
                f"<b>{html.escape(chat.title)}:</b>\n"
                f"#UNMUTE\n"
                f"<b>Admin:</b> {mention_html(user.id, user.first_name)}\n"
                f"<b>User:</b> {mention_html(member.user.id, member.user.first_name)}"
            )
    else:
        update.effective_message.edit_text(
            "This user is not muted or has left the group!"
        )
        return ""


MUTE_HANDLER = CommandHandler("mute", mute, run_async=True)
UNMUTE_HANDLER = CommandHandler("unmute", unmute, run_async=True)
TEMPMUTE_HANDLER = CommandHandler(["tmute", "tempmute"], temp_mute, run_async=True)
UNMUTE_BUTTON_HANDLER = CallbackQueryHandler(button, pattern=r"unmute_", run_async=True)

dispatcher.add_handler(MUTE_HANDLER)
dispatcher.add_handler(UNMUTE_HANDLER)
dispatcher.add_handler(TEMPMUTE_HANDLER)
dispatcher.add_handler(UNMUTE_BUTTON_HANDLER)

__mod_name__ = "𝐌ᴜᴛɪɴɢ"
__handlers__ = [MUTE_HANDLER, UNMUTE_HANDLER, TEMPMUTE_HANDLER]


# ғᴏʀ ʜᴇʟᴘ ᴍᴇɴᴜ


# """
from Exon.modules.language import gs


def get_help(chat):
    return gs(chat, "muting_help")


# """
