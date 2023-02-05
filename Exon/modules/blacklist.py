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

from telegram import (
    ChatPermissions,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ParseMode,
    Update,
)
from telegram.error import BadRequest
from telegram.ext import CallbackContext, CommandHandler, Filters, MessageHandler
from telegram.utils.helpers import mention_html

import Exon.modules.sql.blacklist_sql as sql
from Exon import LOGGER, dispatcher
from Exon.modules.connection import connected
from Exon.modules.disable import DisableAbleCommandHandler
from Exon.modules.helper_funcs.alternate import send_message, typing_action
from Exon.modules.helper_funcs.chat_status import user_admin, user_not_admin
from Exon.modules.helper_funcs.decorators import Exoncallback as akboss
from Exon.modules.helper_funcs.extraction import extract_text
from Exon.modules.helper_funcs.misc import split_message
from Exon.modules.helper_funcs.string_handling import extract_time
from Exon.modules.log_channel import loggable
from Exon.modules.sql.approve_sql import is_approved
from Exon.modules.warns import warn

BLACKLIST_GROUP = 11


@user_admin
@typing_action
def blacklist(update, context):
    chat = update.effective_chat
    user = update.effective_user
    args = context.args

    conn = connected(context.bot, update, chat, user.id, need_admin=False)
    if conn:
        chat_id = conn
        chat_name = dispatcher.bot.getChat(conn).title
    else:
        if chat.type == "private":
            return
        chat_id = update.effective_chat.id
        chat_name = chat.title

    filter_list = "ᴄᴜʀʀᴇɴᴛ ʙʟᴀᴄᴋʟɪsᴛᴇᴅ ᴡᴏʀᴅs ɪɴ <b>{}</b>:\n".format(chat_name)

    all_blacklisted = sql.get_chat_blacklist(chat_id)

    if len(args) > 0 and args[0].lower() == "copy":
        for trigger in all_blacklisted:
            filter_list += "<code>{}</code>\n".format(html.escape(trigger))
    else:
        for trigger in all_blacklisted:
            filter_list += " - <code>{}</code>\n".format(html.escape(trigger))

    # for trigger in all_blacklisted:
    #     filter_list += " - <code>{}</code>\n".format(html.escape(trigger))

    split_text = split_message(filter_list)
    for text in split_text:
        if filter_list == "ᴄᴜʀʀᴇɴᴛ ʙʟᴀᴄᴋʟɪsᴛᴇᴅ ᴡᴏʀᴅs ɪɴ <b>{}</b>:\n".format(
            html.escape(chat_name)
        ):
            send_message(
                update.effective_message,
                "ɴᴏ ʙʟᴀᴄᴋʟɪsᴛᴇᴅ ᴡᴏʀᴅs ɪɴ <b>{}</b>!".format(html.escape(chat_name)),
                parse_mode=ParseMode.HTML,
            )
            return
        send_message(update.effective_message, text, parse_mode=ParseMode.HTML)


@user_admin
@typing_action
def add_blacklist(update, context):
    msg = update.effective_message
    chat = update.effective_chat
    user = update.effective_user
    words = msg.text.split(None, 1)

    conn = connected(context.bot, update, chat, user.id)
    if conn:
        chat_id = conn
        chat_name = dispatcher.bot.getChat(conn).title
    else:
        chat_id = update.effective_chat.id
        if chat.type == "private":
            return
        chat_name = chat.title

    if len(words) > 1:
        text = words[1]
        to_blacklist = list(
            {trigger.strip() for trigger in text.split("\n") if trigger.strip()}
        )
        for trigger in to_blacklist:
            sql.add_to_blacklist(chat_id, trigger.lower())

        if len(to_blacklist) == 1:
            send_message(
                update.effective_message,
                "ᴀᴅᴅᴇᴅ ʙʟᴀᴄᴋʟɪsᴛ <code>{}</code> ɪɴ ᴄʜᴀᴛ: <b>{}</b>!".format(
                    html.escape(to_blacklist[0]), html.escape(chat_name)
                ),
                parse_mode=ParseMode.HTML,
            )

        else:
            send_message(
                update.effective_message,
                "ᴀᴅᴅᴇᴅ ʙʟᴀᴄᴋʟɪsᴛ ᴛʀɪɢɢᴇʀ: <code>{}</code> in <b>{}</b>!".format(
                    len(to_blacklist), html.escape(chat_name)
                ),
                parse_mode=ParseMode.HTML,
            )

    else:
        send_message(
            update.effective_message,
            "ᴛᴇʟʟ ᴍᴇ ᴡʜɪᴄʜ ᴡᴏʀᴅs ʏᴏᴜ ᴡᴏᴜʟᴅ ʟɪᴋᴇ ᴛᴏ ᴀᴅᴅ ɪɴ ʙʟᴀᴄᴋʟɪsᴛ.",
        )


@user_admin
@typing_action
def unblacklist(update, context):
    msg = update.effective_message
    chat = update.effective_chat
    user = update.effective_user
    words = msg.text.split(None, 1)

    conn = connected(context.bot, update, chat, user.id)
    if conn:
        chat_id = conn
        chat_name = dispatcher.bot.getChat(conn).title
    else:
        chat_id = update.effective_chat.id
        if chat.type == "private":
            return
        chat_name = chat.title

    if len(words) > 1:
        text = words[1]
        to_unblacklist = list(
            {trigger.strip() for trigger in text.split("\n") if trigger.strip()}
        )
        successful = 0
        for trigger in to_unblacklist:
            success = sql.rm_from_blacklist(chat_id, trigger.lower())
            if success:
                successful += 1

        if len(to_unblacklist) == 1:
            if successful:
                send_message(
                    update.effective_message,
                    "ʀᴇᴍᴏᴠᴇᴅ <code>{}</code> ғʀᴏᴍ ʙʟᴀᴄᴋʟɪsᴛ ɪɴ <b>{}</b>!".format(
                        html.escape(to_unblacklist[0]), html.escape(chat_name)
                    ),
                    parse_mode=ParseMode.HTML,
                )
            else:
                send_message(
                    update.effective_message, "ᴛʜɪs ɪs ɴᴏᴛ ᴀ ʙʟᴀᴄᴋʟɪsᴛ ᴛʀɪɢɢᴇʀ!"
                )

        elif successful == len(to_unblacklist):
            send_message(
                update.effective_message,
                "Removed <code>{}</code> ғʀᴏᴍ ʙʟᴀᴄᴋʟɪsᴛ ɪɴ <b>{}</b>!".format(
                    successful, html.escape(chat_name)
                ),
                parse_mode=ParseMode.HTML,
            )

        elif not successful:
            send_message(
                update.effective_message,
                "ɴᴏɴᴇ ᴏғ ᴛʜᴇsᴇ ᴛʀɪɢɢᴇʀs ᴇxɪsᴛ sᴏ ɪᴛ ᴄᴀɴ'ᴛ ʙᴇ ʀᴇᴍᴏᴠᴇᴅ.".format(
                    successful, len(to_unblacklist) - successful
                ),
                parse_mode=ParseMode.HTML,
            )

        else:
            send_message(
                update.effective_message,
                "ʀᴇᴍᴏᴠᴇᴅ <code>{}</code> ғʀᴏᴍ ʙʟᴀᴄᴋʟɪsᴛ. {} ᴅɪᴅ ɴᴏᴛ ᴇxɪsᴛ, "
                "so were not removed.".format(
                    successful, len(to_unblacklist) - successful
                ),
                parse_mode=ParseMode.HTML,
            )
    else:
        send_message(
            update.effective_message,
            "ᴛᴇʟʟ ᴍᴇ ᴡʜɪᴄʜ ᴡᴏʀᴅs ʏᴏᴜ ᴡᴏᴜʟᴅ ʟɪᴋᴇ ᴛᴏ ʀᴇᴍᴏᴠᴇ ғʀᴏᴍ ʙʟᴀᴄᴋʟɪsᴛ!",
        )


@loggable
@user_admin
@typing_action
def blacklist_mode(update, context):
    chat = update.effective_chat
    user = update.effective_user
    msg = update.effective_message
    args = context.args

    conn = connected(context.bot, update, chat, user.id, need_admin=True)
    if conn:
        chat = dispatcher.bot.getChat(conn)
        chat_id = conn
        chat_name = dispatcher.bot.getChat(conn).title
    else:
        if update.effective_message.chat.type == "private":
            send_message(
                update.effective_message,
                "ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ ᴄᴀɴ ʙᴇ ᴏɴʟʏ ᴜsᴇᴅ ɪɴ ɢʀᴏᴜᴘ ɴᴏᴛ ɪɴ PM",
            )
            return ""
        chat = update.effective_chat
        chat_id = update.effective_chat.id
        chat_name = update.effective_message.chat.title

    if args:
        if args[0].lower() in ("off", "nothing", "no"):
            settypeblacklist = "ᴅᴏ ɴᴏᴛʜɪɴɢ"
            sql.set_blacklist_strength(chat_id, 0, "0")
        elif args[0].lower() in ("del", "delete"):
            settypeblacklist = "ᴡɪʟʟ ᴅᴇʟᴇᴛᴇ ʙʟᴀᴄᴋʟɪsᴛᴇᴅ ᴍᴇssᴀɢᴇ"
            sql.set_blacklist_strength(chat_id, 1, "0")
        elif args[0].lower() == "warn":
            settypeblacklist = "ᴡᴀʀɴ ᴛʜᴇ sᴇɴᴅᴇʀ"
            sql.set_blacklist_strength(chat_id, 2, "0")
        elif args[0].lower() == "mute":
            settypeblacklist = "ᴍᴜᴛᴇ ᴛʜᴇ sᴇɴᴅᴇʀ"
            sql.set_blacklist_strength(chat_id, 3, "0")
        elif args[0].lower() == "kick":
            settypeblacklist = "ᴋɪᴄᴋ ᴛʜᴇ sᴇɴᴅᴇʀ"
            sql.set_blacklist_strength(chat_id, 4, "0")
        elif args[0].lower() == "ban":
            settypeblacklist = "ʙᴀɴ ᴛʜᴇ sᴇɴᴅᴇʀ"
            sql.set_blacklist_strength(chat_id, 5, "0")
        elif args[0].lower() == "tban":
            if len(args) == 1:
                teks = """ɪᴛ ʟᴏᴏᴋs ʟɪᴋᴇ ʏᴏᴜ ᴛʀɪᴇᴅ ᴛᴏ sᴇᴛ ᴛɪᴍᴇ ᴠᴀʟᴜᴇ ғᴏʀ ʙʟᴀᴄᴋʟɪsᴛ ʙᴜᴛ ʏᴏᴜ ᴅɪᴅɴ'ᴛ sᴘᴇᴄɪғɪᴇᴅ ᴛɪᴍᴇ; 𝐓𝐫𝐲, `/blacklistmode tban <ᴛɪᴍᴇᴠᴀʟᴜᴇ>`.
    ᴇxᴀᴍᴘʟᴇs ᴏғ ᴛɪᴍᴇ ᴠᴀʟᴜᴇ: 4ᴍ = 4 ᴍɪɴᴜᴛᴇs, 3ʜ = 3 ʜᴏᴜʀs, 6d = 6 ᴅᴀʏs, 5ᴡ = 5 ᴡᴇᴇᴋs."""
                send_message(update.effective_message, teks, parse_mode="markdown")
                return ""
            restime = extract_time(msg, args[1])
            if not restime:
                teks = """ɪɴᴠᴀʟɪᴅ ᴛɪᴍᴇ ᴠᴀʟᴜᴇ!
    Example of time value: 4m = 4 minutes, 3h = 3 hours, 6d = 6 days, 5w = 5 weeks."""
                send_message(update.effective_message, teks, parse_mode="markdown")
                return ""
            settypeblacklist = "ᴛᴇᴍᴘᴏʀᴀʀɪʟʏ ʙᴀɴ ғᴏʀ {}".format(args[1])
            sql.set_blacklist_strength(chat_id, 6, str(args[1]))
        elif args[0].lower() == "tmute":
            if len(args) == 1:
                teks = """ɪᴛ ʟᴏᴏᴋs ʟɪᴋᴇ ʏᴏᴜ ᴛʀɪᴇᴅ ᴛᴏ sᴇᴛ ᴛɪᴍᴇ ᴠᴀʟᴜᴇ ғᴏʀ ʙʟᴀᴄᴋʟɪsᴛ ʙᴜᴛ ʏᴏᴜ ᴅɪᴅɴ'ᴛ sᴘᴇᴄɪғɪᴇᴅ  ᴛɪᴍᴇ; ᴛʀʏ, `/blacklistmode tmute <ᴛɪᴍᴇᴠᴀʟᴜᴇ>`.
    Examples of time value: 4m = 4 minutes, 3h = 3 hours, 6d = 6 days, 5w = 5 weeks."""
                send_message(update.effective_message, teks, parse_mode="markdown")
                return ""
            restime = extract_time(msg, args[1])
            if not restime:
                teks = """ɪɴᴠᴀʟɪᴅ ᴛɪᴍᴇ ᴠᴀʟᴜᴇ!
    Examples of time value: 4m = 4 minutes, 3h = 3 hours, 6d = 6 days, 5w = 5 weeks."""
                send_message(update.effective_message, teks, parse_mode="markdown")
                return ""
            settypeblacklist = "ᴛᴇᴍᴘᴏʀᴀʀɪʟʏ ᴍᴜᴛᴇ ғᴏʀ {}".format(args[1])
            sql.set_blacklist_strength(chat_id, 7, str(args[1]))
        else:
            send_message(
                update.effective_message,
                "I ᴏɴʟʏ ᴜɴᴅᴇʀsᴛᴀɴᴅ: off/del/warn/ban/kick/mute/tban/tmute!",
            )
            return ""
        if conn:
            text = "ᴄʜᴀɴɢᴇᴅ ʙʟᴀᴄᴋʟɪsᴛ ᴍᴏᴅᴇ: `{}` in *{}*!".format(
                settypeblacklist, chat_name
            )
        else:
            text = "ᴄʜᴀɴɢᴇᴅ ʙʟᴀᴄᴋʟɪsᴛ ᴍᴏᴅᴇ: `{}`!".format(settypeblacklist)
        send_message(update.effective_message, text, parse_mode="markdown")
        return (
            "<b>{}:</b>\n"
            "<b>ᴀᴅᴍɪɴ:</b> {}\n"
            "ᴄʜᴀɴɢᴇᴅ ᴛʜᴇ ʙʟᴀᴄᴋʟɪsᴛ ᴍᴏᴅᴇ. ᴡɪʟʟ {}.".format(
                html.escape(chat.title),
                mention_html(user.id, html.escape(user.first_name)),
                settypeblacklist,
            )
        )
    getmode, getvalue = sql.get_blacklist_setting(chat.id)
    if getmode == 0:
        settypeblacklist = "ᴅᴏ ɴᴏᴛʜɪɴɢ"
    elif getmode == 1:
        settypeblacklist = "ᴅᴇʟᴇᴛᴇ"
    elif getmode == 2:
        settypeblacklist = "warn"
    elif getmode == 3:
        settypeblacklist = "ᴍᴜᴛᴇ"
    elif getmode == 4:
        settypeblacklist = "ᴋɪᴄᴋ"
    elif getmode == 5:
        settypeblacklist = "ʙᴀɴ"
    elif getmode == 6:
        settypeblacklist = "ᴛᴇᴍᴘᴏʀᴀʀɪʟʏ ʙᴀɴ ғᴏʀ {}".format(getvalue)
    elif getmode == 7:
        settypeblacklist = "ᴛᴇᴍᴘᴏʀᴀʀɪʟʏ ᴍᴜᴛᴇ ғᴏʀ {}".format(getvalue)
    if conn:
        text = "ᴄᴜʀʀᴇɴᴛ ʙʟᴀᴄᴋʟɪsᴛᴍᴏᴅᴇ: *{}* ɪɴ *{}*.".format(
            settypeblacklist, chat_name
        )
    else:
        text = "ᴄᴜʀʀᴇɴᴛ ʙʟᴀᴄᴋʟɪsᴛᴍᴏᴅᴇ: *{}*.".format(settypeblacklist)
    send_message(update.effective_message, text, parse_mode=ParseMode.MARKDOWN)
    return ""


def findall(p, s):
    i = s.find(p)
    while i != -1:
        yield i
        i = s.find(p, i + 1)


@user_not_admin
def del_blacklist(update, context):
    chat = update.effective_chat
    message = update.effective_message
    user = update.effective_user
    bot = context.bot
    to_match = extract_text(message)

    if not to_match:
        return

    if is_approved(chat.id, user.id):
        return

    getmode, value = sql.get_blacklist_setting(chat.id)

    chat_filters = sql.get_chat_blacklist(chat.id)
    for trigger in chat_filters:
        pattern = r"( |^|[^\w])" + re.escape(trigger) + r"( |$|[^\w])"
        if re.search(pattern, to_match, flags=re.IGNORECASE):
            try:
                if getmode == 0:
                    return
                if getmode == 1:
                    message.delete()
                elif getmode == 2:
                    message.delete()
                    warn(
                        update.effective_user,
                        update,
                        ("ᴜsɪɴɢ ʙʟᴀᴄᴋʟɪsᴛᴇᴅ ᴛʀɪɢɢᴇʀ: {}".format(trigger)),
                        message,
                        update.effective_user,
                    )
                    return
                elif getmode == 3:
                    message.delete()
                    bot.restrict_chat_member(
                        chat.id,
                        update.effective_user.id,
                        permissions=ChatPermissions(can_send_messages=False),
                    )
                    bot.sendMessage(
                        chat.id,
                        f"ᴍᴜᴛᴇᴅ {user.first_name} ғᴏʀ ᴜsɪɴɢ ʙʟᴀᴄᴋʟɪsᴛᴇᴅ ᴡᴏʀᴅ: {trigger}!",
                    )
                    return
                elif getmode == 4:
                    message.delete()
                    res = chat.unban_member(update.effective_user.id)
                    if res:
                        bot.sendMessage(
                            chat.id,
                            f"ᴋɪᴄᴋᴇᴅ {user.first_name} ғᴏʀ ᴜsɪɴɢ ʙʟᴀᴄᴋʟɪsᴛᴇᴅ ᴡᴏʀᴅ: {trigger}!",
                        )
                    return
                elif getmode == 5:
                    message.delete()
                    chat.ban_member(user.id)
                    bot.sendMessage(
                        chat.id,
                        f"ʙᴀɴɴᴇᴅ {user.first_name} ғᴏʀ ᴜsɪɴɢ ʙʟᴀᴄᴋʟɪsᴛᴇᴅ ᴡᴏʀᴅ: {trigger}",
                    )
                    return
                elif getmode == 6:
                    message.delete()
                    bantime = extract_time(message, value)
                    chat.ban_member(user.id, until_date=bantime)
                    bot.sendMessage(
                        chat.id,
                        f"ʙᴀɴɴᴇᴅ {user.first_name} ᴜɴᴛɪʟ '{value}' ғᴏʀ ᴜsɪɴɢ ʙʟᴀᴄᴋʟɪsᴛᴇᴅ ᴡᴏʀᴅ: {trigger}!",
                    )
                    return
                elif getmode == 7:
                    message.delete()
                    mutetime = extract_time(message, value)
                    bot.restrict_chat_member(
                        chat.id,
                        user.id,
                        until_date=mutetime,
                        permissions=ChatPermissions(can_send_messages=False),
                    )
                    bot.sendMessage(
                        chat.id,
                        f"ᴍᴜᴛᴇᴅ {user.first_name} ᴜɴᴛɪʟ '{value}' ғᴏʀ ᴜsɪɴɢ ʙʟᴀᴄᴋʟɪsᴛᴇᴅ ᴡᴏʀᴅ: {trigger}!",
                    )
                    return
            except BadRequest as excp:
                if excp.message != "ᴍᴇssᴀɢᴇ ᴛᴏ ᴅᴇʟᴇᴛᴇ ɴᴏᴛ ғᴏᴜɴᴅ":
                    LOGGER.exception("ᴇʀʀᴏʀ ᴡʜɪʟᴇ ᴅᴇʟᴇᴛɪɴɢ ʙʟᴀᴄᴋʟɪsᴛ ᴍᴇssᴀɢᴇ.")
            break


def __import_data__(chat_id, data):
    # set chat blacklist
    blacklist = data.get("blacklist", {})
    for trigger in blacklist:
        sql.add_to_blacklist(chat_id, trigger)


def __migrate__(old_chat_id, new_chat_id):
    sql.migrate_chat(old_chat_id, new_chat_id)


def __chat_settings__(chat_id, user_id):
    blacklisted = sql.num_blacklist_chat_filters(chat_id)
    return "ᴛʜᴇʀᴇ ᴀʀᴇ {} ʙʟᴀᴄᴋʟɪsᴛᴇᴅ ᴡᴏʀᴅs.".format(blacklisted)


def __stats__():
    return "≛≛  {} ʙʟᴀᴄᴋʟɪsᴛ ᴛʀɪɢɢᴇʀs, ᴀᴄʀᴏss {} ᴄʜᴀᴛs.".format(
        sql.num_blacklist_filters(), sql.num_blacklist_filter_chats()
    )


BLACKLIST_HANDLER = DisableAbleCommandHandler(
    ["blacklist", "blocklist"], blacklist, pass_args=True, admin_ok=True, run_async=True
)


ADD_BLACKLIST_HANDLER = CommandHandler(
    ["addblacklist", "addblocklist"], add_blacklist, run_async=True
)
UNBLACKLIST_HANDLER = CommandHandler(
    ["unblacklist", "rmblocklist", "rmblacklist"], unblacklist, run_async=True
)
BLACKLISTMODE_HANDLER = CommandHandler(
    ["blacklistmode", "blocklistmode"], blacklist_mode, pass_args=True, run_async=True
)
BLACKLIST_DEL_HANDLER = MessageHandler(
    (Filters.text | Filters.command | Filters.sticker | Filters.photo)
    & Filters.chat_type.groups,
    del_blacklist,
    allow_edit=True,
    run_async=True,
)

dispatcher.add_handler(BLACKLIST_HANDLER)
dispatcher.add_handler(ADD_BLACKLIST_HANDLER)
dispatcher.add_handler(UNBLACKLIST_HANDLER)
dispatcher.add_handler(BLACKLISTMODE_HANDLER)
dispatcher.add_handler(BLACKLIST_DEL_HANDLER, group=BLACKLIST_GROUP)

__handlers__ = [
    BLACKLIST_HANDLER,
    ADD_BLACKLIST_HANDLER,
    UNBLACKLIST_HANDLER,
    BLACKLISTMODE_HANDLER,
    (BLACKLIST_DEL_HANDLER, BLACKLIST_GROUP),
]


# """
# ғᴏʀ ʜᴇʟᴘ ᴍᴇɴᴜ

from Exon.modules.language import gs


def blacklist_help(update: Update, context: CallbackContext):
    update.effective_message.reply_text(
        gs(update.effective_chat.id, "blacklist_help"),
        parse_mode=ParseMode.MARKDOWN,
    )


def sticker_blacklist_help(update: Update, context: CallbackContext):
    update.effective_message.reply_text(
        gs(update.effective_chat.id, "sticker_blacklist_help"),
        parse_mode=ParseMode.MARKDOWN,
    )


@akboss(pattern=r"asusau_help_")
def blacklist_help_bse(update: Update, context: CallbackContext):
    query = update.callback_query
    bot = context.bot
    help_info = query.data.split("asusau_help_")[1]
    if help_info == "wblack":
        help_text = gs(update.effective_chat.id, "blacklist_help")
    elif help_info == "sblack":
        help_text = gs(update.effective_chat.id, "sticker_blacklist_help")
    query.message.edit_text(
        text=help_text,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text="ʙᴀᴄᴋ",
                        callback_data=f"help_module({__mod_name__.lower()})",
                    )
                ]
            ]
        ),
    )
    bot.answer_callback_query(query.id)


__mod_name__ = "𝐁-ʟɪsᴛ️"


def get_help(chat):
    return [
        gs(chat, "blacklist_help_bse"),
        [
            InlineKeyboardButton(
                text="ʙʟᴀᴄᴋʟɪsᴛ 👽", callback_data="asusau_help_wblack"
            ),
            InlineKeyboardButton(
                text="ʙ-sᴛɪᴄᴋᴇʀ 🦍", callback_data="asusau_help_sblack"
            ),
        ],
    ]


# """
