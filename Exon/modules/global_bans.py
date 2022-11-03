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
import time
from datetime import datetime
from io import BytesIO

from telegram import ParseMode, Update
from telegram.error import BadRequest, TelegramError, Unauthorized
from telegram.ext import CallbackContext, CommandHandler, Filters, MessageHandler
from telegram.utils.helpers import mention_html

import Exon.modules.sql.global_bans_sql as sql
from Exon import (
    DEMONS,
    DEV_USERS,
    DRAGONS,
    EVENT_LOGS,
    OWNER_ID,
    SPAMWATCH_SUPPORT_CHAT,
    STRICT_GBAN,
    SUPPORT_CHAT,
    TIGERS,
    WOLVES,
    dispatcher,
    sw,
)
from Exon.modules.helper_funcs.chat_status import (
    is_user_admin,
    support_plus,
    user_admin,
)
from Exon.modules.helper_funcs.extraction import extract_user, extract_user_and_text
from Exon.modules.helper_funcs.misc import send_to_list
from Exon.modules.sql.users_sql import get_user_com_chats

GBAN_ENFORCE_GROUP = 6

GBAN_ERRORS = {
    "ᴜsᴇʀ ɪs ᴀɴ ᴀᴅᴍɪɴɪsᴛʀᴀᴛᴏʀ ᴏғ ᴛʜᴇ ᴄʜᴀᴛ",
    "ᴄʜᴀᴛ ɴᴏᴛ ғᴏᴜɴᴅ",
    "ɴᴏᴛ ᴇɴᴏᴜɢʜ ʀɪɢʜᴛs ᴛᴏ ʀᴇsᴛʀɪᴄᴛ/ᴜɴʀᴇsᴛʀɪᴄᴛ ᴄʜᴀᴛ ᴍᴇᴍʙᴇʀ",
    "ᴜsᴇʀ_ɴᴏᴛ_ᴘᴀʀᴛɪᴄɪᴘᴀɴᴛ",
    "Peer_id_invalid",
    "ɢʀᴏᴜᴘ ᴄʜᴀᴛ ᴡᴀs ᴅᴇᴀᴄᴛɪᴠᴀᴛᴇᴅ",
    "ɴᴇᴇᴅ ᴛᴏ ʙᴇ ɪɴᴠɪᴛᴇʀ ᴏғ a ᴜsᴇʀ ᴛᴏ ᴋɪᴄᴋ ɪᴛ ғʀᴏᴍ ᴀ ʙᴀsɪᴄ ɢʀᴏᴜᴘ",
    "Chat_admin_required",
    "ᴏɴʟʏ ᴛʜᴇ ᴄʀᴇᴀᴛᴏʀ ᴏғ ᴀ ʙᴀsɪᴄ ɢʀᴏᴜᴘ ᴄᴀɴ ᴋɪᴄᴋ ɢʀᴏᴜᴘ ᴀᴅᴍɪɴɪsᴛʀᴀᴛᴏʀs",
    "Channel_private",
    "ɴᴏᴛ ɪɴ ᴛʜᴇ ᴄʜᴀᴛ",
    "ᴄᴀɴ'ᴛ ʀᴇᴍᴏᴠᴇ ᴄʜᴀᴛ ᴏᴡɴᴇʀ",
}

UNGBAN_ERRORS = {
    "ᴜsᴇʀ ɪs ᴀɴ ᴀᴅᴍɪɴɪsᴛʀᴀᴛᴏʀ ᴏғ ᴛʜᴇ ᴄʜᴀᴛ",
    "ᴄʜᴀᴛ ɴᴏᴛ ғᴏᴜɴᴅ",
    "ɴᴏᴛ enough rights to restrict/unrestrict chat member",
    "ᴜsᴇʀ_not_participant",
    "ᴍᴇᴛʜᴏᴅ ɪs ᴀᴠᴀɪʟᴀʙʟᴇ ғᴏʀ sᴜᴘᴇʀɢʀᴏᴜᴘ ᴀɴᴅ ᴄʜᴀɴɴᴇʟ ᴄʜᴀᴛs ᴏɴʟʏ",
    "ɴᴏᴛ in ᴛʜᴇ ᴄʜᴀᴛ",
    "ᴄʜᴀɴɴᴇʟ_ᴘʀɪᴠᴀᴛᴇ",
    "Chat_admin_required",
    "ᴘᴇᴇʀ_id_invalid",
    "ᴜsᴇʀ ɴᴏᴛ ғᴏᴜɴᴅ",
}


@support_plus
def gban(update: Update, context: CallbackContext):
    bot, args = context.bot, context.args
    message = update.effective_message
    user = update.effective_user
    chat = update.effective_chat
    log_message = ""

    user_id, reason = extract_user_and_text(message, args)

    if not user_id:
        message.reply_text(
            "ʏᴏᴜ ᴅᴏɴ'ᴛ sᴇᴇᴍ ᴛᴏ ʙᴇ ʀᴇғᴇʀʀɪɴɢ ᴛᴏ ᴀ ᴜsᴇʀ ᴏʀ ᴛʜᴇ ID sᴘᴇᴄɪғɪᴇᴅ ɪs ɪɴᴄᴏʀʀᴇᴄᴛ..",
        )
        return

    if int(user_id) in DEV_USERS:
        message.reply_text(
            "ᴛʜᴀᴛ ᴜsᴇʀ ɪs ᴍᴇᴍʙᴇʀ ᴏғ ᴏᴜʀ ғᴀᴍɪʟʏ I ᴄᴀɴ'ᴛ ᴀᴄᴛ ᴀɢᴀɪɴsᴛ ᴏᴜʀ ᴏᴡɴ.",
        )
        return

    if int(user_id) in DRAGONS:
        message.reply_text(
            "I sᴘʏ, ᴡɪᴛʜ ᴍʏ ʟɪᴛᴛʟᴇ ᴇʏᴇ... ʙᴇsᴛғʀɪᴇɴᴅs! ᴡʜʏ ᴀʀᴇ ʏᴏᴜ ɢᴜʏs ᴛᴜʀɴɪɴɢ ᴏɴ ᴇᴀᴄʜ ᴏᴛʜᴇʀ?",
        )
        return

    if int(user_id) in DEMONS:
        message.reply_text(
            "OOOH sᴏᴍᴇᴏɴᴇ ᴛʀʏɪɴɢ ᴛᴏ ɢʙᴀɴ ᴏᴜʀ ғʀɪᴇɴᴅᴏ! *ɢʀᴀʙs ᴘᴏᴘᴄᴏʀɴ*",
        )
        return

    if int(user_id) in TIGERS:
        message.reply_text("ᴛʜᴀᴛ's ᴏᴜʀ ᴄʟᴀssᴍᴀᴛᴇ! ᴛʜᴇʏ ᴄᴀɴɴᴏᴛ ʙᴇ ʙᴀɴɴᴇᴅ!")
        return

    if int(user_id) in WOLVES:
        message.reply_text("ᴛʜᴀᴛ's ᴀɴ EXON! ᴛʜᴇʏ ᴄᴀɴɴᴏᴛ ʙᴇ ʙᴀɴɴᴇᴅ!")
        return

    if user_id == bot.id:
        message.reply_text("ʏᴏᴜ ᴜʜʜ...ᴡᴀɴᴛ ᴍᴇ ᴛᴏ ᴘᴜɴᴄʜ ᴍʏsᴇʟғ?")
        return

    try:
        user_chat = bot.get_chat(user_id)
    except BadRequest as excp:
        if excp.message == "User not found":
            message.reply_text("I ᴄᴀɴ'ᴛ sᴇᴇᴍ ᴛᴏ ғɪɴᴅ ᴛʜɪs ᴜsᴇʀ.")
            return ""
        return

    if user_chat.type != "private":
        message.reply_text("ᴛʜᴀᴛ's ɴᴏᴛ ᴀ ᴜsᴇʀ!")
        return

    if sql.is_user_gbanned(user_id):

        if not reason:
            message.reply_text(
                "ᴛʜɪs  user is ᴀʟʀᴇᴀᴅʏ ɢʙᴀɴɴᴇᴅ; I'ᴅ ᴄʜᴀɴɢᴇ ᴛʜᴇ ʀᴇᴀsᴏɴ, ʙᴜᴛ ʏᴏᴜ ʜᴀᴠᴇɴ'ᴛ  ɢɪᴠᴇɴ ᴍᴇ ᴏɴᴇ...",
            )
            return

        old_reason = sql.update_gban_reason(
            user_id,
            user_chat.username or user_chat.first_name,
            reason,
        )
        if old_reason:
            message.reply_text(
                "ᴛʜɪs ᴜsᴇʀ ɪs ᴀʟʀᴇᴀᴅʏ ɢʙᴀɴɴᴇᴅ, ғᴏʀ ᴛʜᴇ ғᴏʟʟᴏᴡɪɴɢ ʀᴇᴀsᴏɴ:\n"
                "<code>{}</code>\n"
                "I've ɢᴏɴᴇ ᴀɴᴅ ᴜᴘᴅᴀᴛᴇᴅ it ᴡɪᴛʜ ʏᴏᴜʀ ɴᴇᴡ ʀᴇᴀsᴏɴ!".format(
                    html.escape(old_reason),
                ),
                parse_mode=ParseMode.HTML,
            )

        else:
            message.reply_text(
                "This ᴜsᴇʀ is ᴀʟʀᴇᴀᴅʏ ɢʙᴀɴɴᴇᴅ, ʙᴜᴛ ʜᴀᴅ ɴᴏ ʀᴇᴀsᴏɴ sᴇᴛ; I'ᴠᴇ ɢᴏɴᴇ ᴀɴᴅ ᴜᴘᴅᴀᴛᴇᴅ ɪᴛ!",
            )

        return

    message.reply_text("ᴏɴ ɪᴛ \nɢʙᴀɴ ᴅᴏɴᴇ !")

    start_time = time.time()
    datetime_fmt = "%Y-%m-%dT%H:%M"
    current_time = datetime.utcnow().strftime(datetime_fmt)

    if chat.type != "private":
        chat_origin = "<b>{} ({})</b>\n".format(html.escape(chat.title), chat.id)
    else:
        chat_origin = "<b>{}</b>\n".format(chat.id)

    log_message = (
        f"#ɢʙᴀɴɴᴇᴅ\n"
        f"<b>ᴏʀɪɢɪɴᴀᴛᴇᴅ ғʀᴏᴍ:</b> <code>{chat_origin}</code>\n"
        f"<b>ᴀᴅᴍɪɴ:</b> {mention_html(user.id, user.first_name)}\n"
        f"<b>ʙᴀɴɴᴇᴅ ᴜsᴇʀ:</b> {mention_html(user_chat.id, user_chat.first_name)}\n"
        f"<b>ʙᴀɴɴᴇᴅ ᴜsᴇʀ ɪᴅ:</b> <code>{user_chat.id}</code>\n"
        f"<b>ᴇᴠᴇɴᴛ sᴛᴀᴍᴘ:</b> <code>{current_time}</code>"
    )

    if reason:
        if chat.type == chat.SUPERGROUP and chat.username:
            log_message += f'\n<b>ʀᴇᴀsᴏɴ:</b> <a href="https://telegram.me/{chat.username}/{message.message_id}">{reason}</a>'
        else:
            log_message += f"\n<b>ʀᴇᴀsᴏɴ:</b> <code>{reason}</code>"

    if EVENT_LOGS:
        try:
            log = bot.send_message(
                EVENT_LOGS,
                log_message,
                parse_mode=ParseMode.HTML,
                disable_web_page_preview=True,
            )
        except BadRequest:
            log = bot.send_message(
                EVENT_LOGS,
                log_message
                + "\n\nғᴏʀᴍᴀᴛᴛɪɴɢ ʜᴀs ʙᴇᴇɴ ᴅɪsᴀʙʟᴇᴅ ᴅᴜᴇ ᴛᴏ ᴀɴ ᴜɴᴇxᴘᴇᴄᴛᴇᴅ ᴇʀʀᴏʀ.",
            )

    else:
        send_to_list(bot, DRAGONS + DEMONS, log_message, html=True)

    sql.gban_user(user_id, user_chat.username or user_chat.first_name, reason)

    chats = get_user_com_chats(user_id)
    gbanned_chats = 0

    for chat in chats:
        chat_id = int(chat)

        # Check if this group has disabled gbans
        if not sql.does_chat_gban(chat_id):
            continue

        try:
            bot.ban_chat_member(chat_id, user_id)
            gbanned_chats += 1

        except BadRequest as excp:
            if excp.message not in GBAN_ERRORS:
                message.reply_text(f"ᴄᴏᴜʟᴅ ɴᴏᴛ ɢʙᴀɴ ᴅᴜᴇ ᴛᴏ: {excp.message}")
                if EVENT_LOGS:
                    bot.send_message(
                        EVENT_LOGS,
                        f"ᴄᴏᴜʟᴅ ɴᴏᴛ ɢʙᴀɴ ᴅᴜᴇ ᴛᴏ {excp.message}",
                        parse_mode=ParseMode.HTML,
                    )
                else:
                    send_to_list(
                        bot,
                        DRAGONS + DEMONS,
                        f"ᴄᴏᴜʟᴅ ɴᴏᴛ ɢʙᴀɴ ᴅᴜᴇ ᴛᴏ: {excp.message}",
                    )
                sql.ungban_user(user_id)
                return
        except TelegramError:
            pass

    if EVENT_LOGS:
        log.edit_text(
            log_message + f"\n<b>ᴄʜᴀᴛs ᴀғғᴇᴄᴛᴇᴅ:</b> <code>{gbanned_chats}</code>",
            parse_mode=ParseMode.HTML,
        )
    else:
        send_to_list(
            bot,
            DRAGONS + DEMONS,
            f"ɢʙᴀɴ ᴄᴏᴍᴘʟᴇᴛᴇ! (ᴜsᴇʀ ʙᴀɴɴᴇᴅ ɪɴ <code>{gbanned_chats}</code> chats)",
            html=True,
        )

    end_time = time.time()
    gban_time = round((end_time - start_time), 2)

    if gban_time > 60:
        gban_time = round((gban_time / 60), 2)
    message.reply_text(
        "ᴅᴏɴᴇ ! ɢʙᴀɴɴᴇᴅ. \nᴅᴏɴ'ᴛ ʟᴏᴠᴇ ᴀɴᴅ ᴄʀʏ ᴊᴜsᴛ ғᴜ*ᴋ & ғʟʏ",
        parse_mode=ParseMode.HTML,
    )
    try:
        bot.send_message(
            user_id,
            "#ᴇᴠᴇɴᴛ"
            "ʏᴏᴜ ʜᴀᴠᴇ ʙᴇᴇɴ ᴍᴀʀᴋᴇᴅ as ᴍᴀʟɪᴄɪᴏᴜs ᴀɴᴅ ᴀs sᴜᴄʜ ʜᴀᴠᴇ ʙᴇᴇɴ ʙᴀɴɴᴇᴅ ғʀᴏᴍ ᴀɴʏ ғᴜᴛᴜʀᴇ ɢʀᴏᴜᴘs ᴡᴇ ᴍᴀɴᴀɢᴇ."
            f"\n<b>ʀᴇᴀsᴏɴ:</b> <code>{html.escape(user.reason)}</code>"
            f"</b>ᴀᴘᴘᴇᴀʟ ᴄʜᴀᴛ:</b> @{SUPPORT_CHAT}",
            parse_mode=ParseMode.HTML,
        )
    except:
        pass  # bot probably blocked by user


@support_plus
def ungban(update: Update, context: CallbackContext):
    bot, args = context.bot, context.args
    message = update.effective_message
    user = update.effective_user
    chat = update.effective_chat
    log_message = ""

    user_id = extract_user(message, args)

    if not user_id:
        message.reply_text(
            "You ᴅᴏɴ'ᴛ sᴇᴇᴍ ᴛᴏ ʙᴇ ʀᴇғᴇʀʀɪɴɢ ᴛᴏ ᴀ ᴜsᴇʀ or ᴛʜᴇ ɪᴅ sᴘᴇᴄɪғɪᴇᴅ ɪs ɪɴᴄᴏʀʀᴇᴄᴛ..",
        )
        return

    user_chat = bot.get_chat(user_id)
    if user_chat.type != "private":
        message.reply_text("ᴛʜᴀᴛ's ɴᴏᴛ a ᴜsᴇʀ!")
        return

    if not sql.is_user_gbanned(user_id):
        message.reply_text("ᴛʜɪs ᴜsᴇʀ ɪs ɴᴏᴛ ɢʙᴀɴɴᴇᴅ!")
        return

    message.reply_text(f"I'ʟʟ ɢɪᴠᴇ {user_chat.first_name} a sᴇᴄᴏɴᴅ ᴄʜᴀɴᴄᴇ, ɢʟᴏʙᴀʟʟʏ.")

    start_time = time.time()
    datetime_fmt = "%Y-%m-%dT%H:%M"
    current_time = datetime.utcnow().strftime(datetime_fmt)

    if chat.type != "private":
        chat_origin = f"<b>{html.escape(chat.title)} ({chat.id})</b>\n"
    else:
        chat_origin = f"<b>{chat.id}</b>\n"

    log_message = (
        f"#ᴜɴɢʙᴀɴɴᴇᴅ\n"
        f"<b>ᴏʀɪɢɪɴᴀᴛᴇᴅ ғʀᴏᴍ:</b> <code>{chat_origin}</code>\n"
        f"<b>ᴀᴅᴍɪɴ:</b> {mention_html(user.id, user.first_name)}\n"
        f"<b>ᴜɴʙᴀɴɴᴇᴅ ᴜsᴇʀ:</b> {mention_html(user_chat.id, user_chat.first_name)}\n"
        f"<b>ᴜɴʙᴀɴɴᴇᴅ ᴜsᴇʀ ID:</b> <code>{user_chat.id}</code>\n"
        f"<b>ᴇᴠᴇɴᴛ sᴛᴀᴍᴘ:</b> <code>{current_time}</code>"
    )

    if EVENT_LOGS:
        try:
            log = bot.send_message(
                EVENT_LOGS,
                log_message,
                parse_mode=ParseMode.HTML,
                disable_web_page_preview=True,
            )
        except BadRequest:
            log = bot.send_message(
                EVENT_LOGS,
                log_message
                + "\n\nғᴏʀᴍᴀᴛᴛɪɴɢ ʜᴀs ʙᴇᴇɴ ᴅɪsᴀʙʟᴇᴅ ᴅᴜᴇ ᴛᴏ ᴀɴ ᴜɴᴇxᴘᴇᴄᴛᴇᴅ ᴇʀʀᴏʀ.",
            )
    else:
        send_to_list(bot, DRAGONS + DEMONS, log_message, html=True)

    chats = get_user_com_chats(user_id)
    ungbanned_chats = 0

    for chat in chats:
        chat_id = int(chat)

        # Check if this group has disabled gbans
        if not sql.does_chat_gban(chat_id):
            continue

        try:
            member = bot.get_chat_member(chat_id, user_id)
            if member.status == "ᴋɪᴄᴋᴇᴅ":
                bot.unban_chat_member(chat_id, user_id)
                ungbanned_chats += 1

        except BadRequest as excp:
            if excp.message not in UNGBAN_ERRORS:
                message.reply_text(f"ᴄᴏᴜʟᴅ ɴᴏᴛ ᴜɴ-ɢᴀɴ ᴅᴜᴇ ᴛᴏ: {excp.message}")
                if EVENT_LOGS:
                    bot.send_message(
                        EVENT_LOGS,
                        f"ᴄᴏᴜʟᴅ ɴᴏᴛ ᴜɴ-ʜᴀɴ ᴅᴜᴇ ᴛᴏ: {excp.message}",
                        parse_mode=ParseMode.HTML,
                    )
                else:
                    bot.send_message(
                        OWNER_ID,
                        f"ᴄᴏᴜʟᴅ ɴᴏᴛ ᴜɴ-ɢʙᴀɴ ᴅᴜᴇ ᴛᴏ: {excp.message}",
                    )
                return
        except TelegramError:
            pass

    sql.ungban_user(user_id)

    if EVENT_LOGS:
        log.edit_text(
            log_message + f"\n<b>ᴄʜᴀᴛs ᴀғғᴇᴄᴛᴇᴅ:</b> {ungbanned_chats}",
            parse_mode=ParseMode.HTML,
        )
    else:
        send_to_list(bot, DRAGONS + DEMONS, "ᴜɴ-ɢᴀɴ ᴄᴏᴍᴘʟᴇᴛᴇ! ")

    end_time = time.time()
    ungban_time = round((end_time - start_time), 2)

    if ungban_time > 60:
        ungban_time = round((ungban_time / 60), 2)
        message.reply_text(f"ᴘᴇʀsᴏɴ has ʙᴇᴇɴ ᴜɴ-ɢʙᴀɴɴᴇᴅ. ᴛᴏᴏᴋ {ungban_time} ᴍɪɴ")
    else:
        message.reply_text(f"ᴘᴇʀsᴏɴ ʜᴀs ʙᴇᴇɴ ᴜɴ-ɢʙᴀɴɴᴇᴅ. ᴛᴏᴏᴋ {ungban_time} sᴇᴄ")


@support_plus
def gbanlist(update: Update, context: CallbackContext):
    banned_users = sql.get_gban_list()

    if not banned_users:
        update.effective_message.reply_text(
            "ᴛʜᴇʀᴇ ᴀʀᴇɴᴀᴛ ᴀɴʏ ɢʙᴀɴɴᴇᴅ ᴜsᴇʀs! ʏᴏᴜ'ʀᴇ ᴋɪɴᴅᴇʀ ᴛʜᴀɴ I ᴇxᴘᴇᴄᴛᴇᴅ...",
        )
        return

    banfile = "sᴄʀᴇᴡ ᴛʜᴇsᴇ ɢᴜʏs.\n"
    for user in banned_users:
        banfile += f"[x] {user['name']} - {user['user_id']}\n"
        if user["reason"]:
            banfile += f"ʀᴇᴀsᴏɴ: {user['reason']}\n"

    with BytesIO(str.encode(banfile)) as output:
        output.name = "gbanlist.txt"
        update.effective_message.reply_document(
            document=output,
            filename="gbanlist.txt",
            caption="ʜᴇʀᴇ ɪs ᴛʜᴇ ʟɪsᴛ ᴏғ ᴄᴜʀʀᴇɴᴛʟʏ ɢʙᴀɴɴᴇᴅ users.",
        )


def check_and_ban(update, user_id, should_message=True):

    if user_id in TIGERS or user_id in WOLVES:
        sw_ban = None
    else:
        try:
            sw_ban = sw.get_ban(int(user_id))
        except:
            sw_ban = None

    if sw_ban:
        update.effective_chat.ban_member(user_id)
        if should_message:
            update.effective_message.reply_text(
                f"<b>ᴀʟᴇʀᴛ</b>: ᴛʜɪs ᴜsᴇʀ ʜᴀs ʙᴇᴇɴ ɢʟᴏʙᴀʟʟʏ ʙᴀɴɴᴇᴅ ʙʏ @SpamWatch\n"
                f"<code>*ʙᴀɴs ᴛʜᴇᴍ ғʀᴏᴍ ʜᴇʀᴇ*</code>.\n"
                f"<b>ᴀᴘᴘᴇᴀʟ ғᴏʀ ᴜɴʙᴀɴ</b>: {SPAMWATCH_SUPPORT_CHAT}\n"
                f"<b>ᴜsᴇʀ ɪᴅ</b>: <code>{sw_ban.id}</code>\n"
                f"<b>ʙᴀɴ ʀᴇᴀsᴏɴ</b>: <code>{html.escape(sw_ban.reason)}</code>\n @AbishnoiMF",
                parse_mode=ParseMode.HTML,
            )
        return

    if sql.is_user_gbanned(user_id):
        update.effective_chat.ban_member(user_id)
        if should_message:
            text = (
                f"<b>ᴀʟᴇʀᴛ</b>: ᴛʜɪs ᴜsᴇʀ ʜᴀs ʙᴇᴇɴ ɢʟᴏʙᴀʟʟʏ ʙᴀɴɴᴇᴅ ʙʏ ᴛʜᴇ ʙᴏᴛ ᴏᴡɴᴇʀ\n"
                f"<code>*ʙᴀɴs ᴛʜᴇᴍ ғʀᴏᴍ ʜᴇʀᴇ*</code>.\n"
                f"<b>ᴀᴘᴘᴇᴀʟ ғᴏʀ ᴜɴʙᴀɴ</b>: @{SUPPORT_CHAT}\n"
                f"<b>ᴜsᴇʀ ɪᴅ</b>: <code>{user_id}</code>"
            )
            user = sql.get_gbanned_user(user_id)
            if user.reason:
                text += f"\n<b>ʙᴀɴ ʀᴇᴀsᴏɴ:</b> <code>{html.escape(user.reason)}</code>"
            update.effective_message.reply_text(text, parse_mode=ParseMode.HTML)


def enforce_gban(update: Update, context: CallbackContext):
    # Not using @restrict handler to avoid spamming - just ignore if cant gban.
    bot = context.bot
    try:
        restrict_permission = update.effective_chat.get_member(
            bot.id,
        ).can_restrict_members
    except Unauthorized:
        return
    if sql.does_chat_gban(update.effective_chat.id) and restrict_permission:
        user = update.effective_user
        chat = update.effective_chat
        msg = update.effective_message

        if user and not is_user_admin(chat, user.id):
            check_and_ban(update, user.id)
            return

        if msg.new_chat_members:
            new_members = update.effective_message.new_chat_members
            for mem in new_members:
                check_and_ban(update, mem.id)

        if msg.reply_to_message:
            user = msg.reply_to_message.from_user
            if user and not is_user_admin(chat, user.id):
                check_and_ban(update, user.id, should_message=False)


@user_admin
def gbanstat(update: Update, context: CallbackContext):
    args = context.args
    if len(args) > 0:
        if args[0].lower() in ["on", "yes"]:
            sql.enable_gbans(update.effective_chat.id)
            update.effective_message.reply_text(
                "ᴀɴᴛɪsᴘᴀᴍ ɪs ɴᴏᴡ ᴇɴᴀʙʟᴇᴅ ✅ "
                "I ᴀᴍ ɴᴏᴡ ᴘʀᴏᴛᴇᴄᴛɪɴɢ ʏᴏᴜʀ ɢʀᴏᴜᴘ ғʀᴏᴍ ᴘᴏᴛᴇɴᴛɪᴀʟ ʀᴇᴍᴏᴛᴇ ᴛʜʀᴇᴀᴛs!",
            )
        elif args[0].lower() in ["off", "no"]:
            sql.disable_gbans(update.effective_chat.id)
            update.effective_message.reply_text(
                "ᴀɴᴛɪsᴘᴀɴ is ɴᴏᴡ ᴅɪsᴀʙʟᴇᴅ ❌ " "sᴘᴀᴍᴡᴀᴛᴄʜ ɪs ɴᴏᴡ ᴅɪsᴀʙʟᴇᴅ ❌",
            )
    else:
        update.effective_message.reply_text(
            "ɢɪᴠᴇ ᴍᴇ sᴏᴍᴇ ᴀʀɢᴜᴍᴇɴᴛs ᴛᴏ ᴄʜᴏᴏsᴇ ᴀ sᴇᴛᴛɪɴɢ! on/off, yes/no!\n\n"
            "ʏᴏᴜʀ ᴄᴜʀʀᴇɴᴛ sᴇᴛᴛɪɴɢ ɪs: {}\n"
            "ᴡʜᴇɴ ᴛʀᴜᴇ, ᴀɴʏ ɢʙᴀɴs ᴛʜᴀᴛ ʜᴀᴘᴘᴇɴ ᴡɪʟʟ ᴀʟsᴏ ʜᴀᴘᴘᴇɴ ɪɴ ʏᴏᴜʀ ɢʀᴏᴜᴘ. "
            "ᴡʜᴇɴ ғᴀʟsᴇ, ᴛʜᴇʏ ᴡᴏɴ'ᴛ, ʟᴇᴀᴠɪɴɢ ʏᴏᴜ ᴀᴛ ᴛʜᴇ ᴘᴏssɪʙʟᴇ ᴍᴇʀᴄʏ ᴏғ "
            "spammers.".format(sql.does_chat_gban(update.effective_chat.id)),
        )


def __stats__():
    return f"•➥ {sql.num_gbanned_users()} ɢʙᴀɴɴᴇᴅ ᴜsᴇʀs."


def __user_info__(user_id):
    is_gbanned = sql.is_user_gbanned(user_id)
    text = "ɢʙᴀɴɴᴇᴅ: <b>{}</b>"
    if user_id in [777000, 1087968824]:
        return ""
    if user_id == dispatcher.bot.id:
        return ""
    if int(user_id) in DRAGONS + TIGERS + WOLVES:
        return ""
    if is_gbanned:
        text = text.format("Yes")
        user = sql.get_gbanned_user(user_id)
        if user.reason:
            text += f"\n<b>ʀᴇᴀsᴏɴ:</b> <code>{html.escape(user.reason)}</code>"
        text += f"\n<b>ᴀᴘᴘᴇᴀʟ ᴄʜᴀᴛ:</b> @{SUPPORT_CHAT}"
    else:
        text = text.format("No")
    return text


def __migrate__(old_chat_id, new_chat_id):
    sql.migrate_chat(old_chat_id, new_chat_id)


def __chat_settings__(chat_id, user_id):
    return f"ᴛʜɪs ᴄʜᴀᴛ ɪs ᴇɴғᴏʀᴄɪɴɢ *ɢʙᴀɴs*: `{sql.does_chat_gban(chat_id)}`."


__help__ = f"""
*ᴀᴅᴍɪɴs ᴏɴʟʏ:*
• /antispam <on/off/yes/no>*:*` ᴡɪʟʟ ᴛᴏɢɢʟᴇ ᴏᴜʀ ᴀɴᴛɪsᴘᴀᴍ ᴛᴇᴄʜ ᴏʀ ʀᴇᴛᴜʀɴ ʏᴏᴜʀ ᴄᴜʀʀᴇɴᴛ sᴇᴛᴛɪɴɢs `.

`ᴀɴᴛɪ-ᴘᴀᴍ, used ʙʏ ʙᴏᴛ ᴅᴇᴠs ᴛᴏ ʙᴀɴ sᴘᴀᴍᴍᴇʀs ᴀᴄʀᴏss ᴀʟʟ ɢʀᴏᴜᴘs. ᴛʜɪs ʜᴇʟᴘs ᴘʀᴏᴛᴇᴄᴛ \
ʏᴏᴜ ᴀɴᴅ ʏᴏᴜʀ ɢʀᴏᴜᴘs ʙʏ ʀᴇᴍᴏᴠɪɴɢ sᴘᴀᴍ ғʟᴏᴏᴅᴇʀs ᴀs ǫᴜɪᴄᴋʟʏ ᴀs ᴘᴏssɪʙʟᴇ `.

*Note:* ᴜsᴇʀs can ᴀᴘᴘᴇᴀʟ ɢʙᴀɴs ᴏʀ ʀᴇᴘᴏʀᴛ sᴘᴀᴍᴍᴇʀs ᴀᴛ @{SUPPORT_CHAT}

ᴛʜɪs ᴀʟsᴏ ɪɴᴛᴇɢʀᴀᴛᴇs @Spamwatch API ᴛᴏ ʀᴇᴍᴏᴠᴇ sᴘᴀᴍᴍᴇʀs as ᴍᴜᴄʜ ᴀs ᴘᴏssɪʙʟᴇ ғʀᴏᴍ ʏᴏᴜʀ ᴄʜᴀᴛʀᴏᴏᴍ!
*ᴡʜᴀᴛ ɪs sᴘᴀᴍᴡᴀᴛᴄʜ?*

sᴘᴀᴍᴡᴀᴛᴄʜ ᴍᴀɪɴᴛᴀɪɴs a ʟᴀʀɢᴇ ᴄᴏɴsᴛᴀɴᴛʟʏ ᴜᴘᴅᴀᴛᴇᴅ ʙᴀɴᴛ of sᴘᴀᴍʙᴏᴛs, ᴛʀᴏʟʟs, ʙɪᴛᴄᴏɪɴ sᴘᴀᴍᴍᴇʀs ᴀɴᴅ ᴜɴsᴀᴠᴏᴜʀʏ ᴄʜᴀʀᴀᴄᴛᴇʀs[.]

ᴄᴏɴsᴛᴀɴᴛʟʏ help banning spammers off from your group automatically sᴏ, ʏᴏᴜ ᴡᴏɴᴛ ʜᴀᴠᴇ ᴛᴏ ᴡᴏʀʀʏ ᴀʙᴏᴜᴛ sᴘᴀᴍᴍᴇʀs sᴛᴏʀᴍɪɴɢ ʏᴏᴜʀ ɢʀᴏᴜᴘ.

*ɴᴏᴛᴇ:* ||ᴜsᴇʀs ᴄᴀɴ ᴀᴘᴘᴇᴀʟ sᴘᴀᴍᴡᴀᴛᴄʜ ʙᴀɴs ᴀᴛ @SpamwatchSupport||
"""

GBAN_HANDLER = CommandHandler("gban", gban, run_async=True)
UNGBAN_HANDLER = CommandHandler("ungban", ungban, run_async=True)
GBAN_LIST = CommandHandler("gbanlist", gbanlist, run_async=True)

GBAN_STATUS = CommandHandler(
    "antispam", gbanstat, filters=Filters.chat_type.groups, run_async=True
)

GBAN_ENFORCER = MessageHandler(
    Filters.all & Filters.chat_type.groups, enforce_gban, run_async=True
)

dispatcher.add_handler(GBAN_HANDLER)
dispatcher.add_handler(UNGBAN_HANDLER)
dispatcher.add_handler(GBAN_LIST)
dispatcher.add_handler(GBAN_STATUS)

__mod_name__ = "𝙰nti-sᴘᴀᴍ"
__handlers__ = [GBAN_HANDLER, UNGBAN_HANDLER, GBAN_LIST, GBAN_STATUS]

if STRICT_GBAN:  # enforce GBANS if this is set
    dispatcher.add_handler(GBAN_ENFORCER, GBAN_ENFORCE_GROUP)
    __handlers__.append((GBAN_ENFORCER, GBAN_ENFORCE_GROUP))
