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
from datetime import timedelta
from typing import Optional

from pytimeparse.timeparse import timeparse
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode, Update
from telegram.ext import CallbackContext
from telegram.utils.helpers import mention_html

import Exon.modules.sql.welcome_sql as sql
from Exon import LOGGER as log
from Exon.modules.cron_jobs import j
from Exon.modules.helper_funcs.anonymous import AdminPerms
from Exon.modules.helper_funcs.anonymous import resolve_user as res_user
from Exon.modules.helper_funcs.anonymous import user_admin as u_admin
from Exon.modules.helper_funcs.chat_status import connection_status, user_admin_no_reply
from Exon.modules.helper_funcs.decorators import Exoncallback, Exoncmd
from Exon.modules.log_channel import loggable


def get_time(time: str) -> int:
    try:
        return timeparse(time)
    except:
        return 0


def get_readable_time(time: int) -> str:
    t = f"{timedelta(seconds=time)}".split(":")
    if time == 86400:
        return "1 day"
    return "{} ʜᴏᴜʀ(s)".format(t[0]) if time >= 3600 else "{} ᴍɪɴᴜᴛᴇs".format(t[1])


@Exoncmd(command="raid", pass_args=True)
@connection_status
@loggable
@u_admin(AdminPerms.CAN_CHANGE_INFO)
def setRaid(update: Update, context: CallbackContext) -> Optional[str]:
    args = context.args
    chat = update.effective_chat
    msg = update.effective_message
    u = update.effective_user
    user = res_user(u, msg.message_id, chat)
    if chat.type == "private":
        context.bot.sendMessage(chat.id, "ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ ɪs ɴᴏᴛ ᴀᴠᴀɪʟᴀʙʟᴇ ɪɴ ᴘᴍs.")
        return
    stat, time, acttime = sql.getDefenseStatus(chat.id)
    readable_time = get_readable_time(time)
    if len(args) == 0:
        if stat:
            text = "ʀᴀɪᴅ ᴍᴏᴅᴇ ɪs ᴄᴜʀʀᴇɴᴛʟʏ <code>ᴇɴᴀʙʟᴇᴅ</code>\nᴡᴏᴜʟᴅ ʏᴏᴜ ʟɪᴋᴇ ᴛᴏ <code>ᴅɪsᴀʙʟᴇ</code> ʀᴀɪᴅ?"
            keyboard = [
                [
                    InlineKeyboardButton(
                        "ᴅɪsᴀʙʟᴇ ʀᴀɪᴅ",
                        callback_data="disable_raid={}={}".format(chat.id, time),
                    ),
                    InlineKeyboardButton("ᴄᴀɴᴄᴇʟ", callback_data="cancel_raid=1"),
                ]
            ]
        else:
            text = f"ʀᴀɪᴅ ᴍᴏᴅᴇ ɪs ᴄᴜʀʀᴇɴᴛʟʏ <code>ᴅɪsᴀʙʟᴇᴅ</code>\nᴡᴏᴜʟᴅ ʏᴏᴜ ʟɪᴋᴇ ᴛᴏ <code>ᴇɴᴀʙʟᴇ</code> ʀᴀɪᴅ ғᴏʀ {readable_time}?"
            keyboard = [
                [
                    InlineKeyboardButton(
                        "ᴇɴᴀʙʟᴇ ʀᴀɪᴅ",
                        callback_data="enable_raid={}={}".format(chat.id, time),
                    ),
                    InlineKeyboardButton("ᴄᴀɴᴄᴇʟ", callback_data="cancel_raid=0"),
                ]
            ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        msg.reply_text(text, parse_mode=ParseMode.HTML, reply_markup=reply_markup)

    elif args[0] == "off":
        if stat:
            sql.setDefenseStatus(chat.id, False, time, acttime)
            text = "ʀᴀɪᴅ ᴍᴏᴅᴇ ʜᴀs ʙᴇᴇɴ <code>ᴅɪsᴀʙʟᴇᴅ</code>, ᴍᴇᴍʙᴇʀs ᴛʜᴀᴛ ᴊᴏɪɴ ᴡɪʟʟ ɴᴏ ʟᴏɴɢᴇʀ ʙᴇ ᴋɪᴄᴋᴇᴅ."
            msg.reply_text(text, parse_mode=ParseMode.HTML)
            logmsg = (
                f"<b>{html.escape(chat.title)}:</b>\n"
                f"#𝐑𝐀𝐈𝐃\n"
                f"ᴅɪsᴀʙʟᴇᴅ\n"
                f"<b>ᴀᴅᴍɪɴ:</b> {mention_html(user.id, user.first_name)}\n"
            )
            return logmsg

    else:
        args_time = args[0].lower()
        time = get_time(args_time)
        if time:
            readable_time = get_readable_time(time)
            if time >= 300 and time < 86400:
                text = f"ʀᴀɪᴅ ᴍᴏᴅᴇ ɪs ᴄᴜʀʀᴇɴᴛʟʏ <code>ᴅɪsᴀʙʟᴇᴅ</code>\nᴡᴏᴜʟᴅ ʏᴏᴜ ʟɪᴋᴇ ᴛᴏ <code>ᴇɴᴀʙʟᴇ</code> ʀᴀɪᴅ ғᴏʀ {readable_time}?"
                keyboard = [
                    [
                        InlineKeyboardButton(
                            "ᴇɴᴀʙʟᴇ ʀᴀɪᴅ",
                            callback_data="enable_raid={}={}".format(chat.id, time),
                        ),
                        InlineKeyboardButton("ᴄᴀɴᴄᴇʟ", callback_data="cancel_raid=0"),
                    ]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                msg.reply_text(
                    text, parse_mode=ParseMode.HTML, reply_markup=reply_markup
                )
            else:
                msg.reply_text(
                    "ʏᴏᴜ ᴄᴀɴ ᴏɴʟʏ sᴇᴛ ᴛɪᴍᴇ ʙᴇᴛᴡᴇᴇɴ 5 ᴍɪɴᴜᴛᴇs ᴀɴᴅ 1 ᴅᴀʏ",
                    parse_mode=ParseMode.HTML,
                )

        else:
            msg.reply_text(
                "ᴜɴᴋɴᴏᴡɴ ᴛɪᴍᴇ ɢɪᴠᴇɴ, ɢɪᴠᴇ ᴍᴇ sᴏᴍᴇᴛʜɪɴɢ ʟɪᴋᴇ 5m ᴏʀ 1h",
                parse_mode=ParseMode.HTML,
            )


@Exoncallback(pattern="enable_raid=")
@connection_status
@user_admin_no_reply
@loggable
def enable_raid_cb(update: Update, _: CallbackContext) -> Optional[str]:
    args = update.callback_query.data.replace("enable_raid=", "").split("=")
    chat = update.effective_chat
    user = update.effective_user
    chat_id = args[0]
    time = int(args[1])
    readable_time = get_readable_time(time)
    _, t, acttime = sql.getDefenseStatus(chat_id)
    sql.setDefenseStatus(chat_id, True, time, acttime)
    update.effective_message.edit_text(
        f"ʀᴀɪᴅ ᴍᴏᴅᴇ ʜᴀs ʙᴇᴇɴ <code>ᴇɴᴀʙʟᴇᴅ</code> ғᴏʀ {readable_time}.",
        parse_mode=ParseMode.HTML,
    )
    log.info("ᴇɴᴀʙʟᴇᴅ ʀᴀɪᴅ ᴍᴏᴅᴇ ɪɴ {} ғᴏʀ {}".format(chat_id, readable_time))

    def disable_raid(_):
        sql.setDefenseStatus(chat_id, False, t, acttime)
        log.info("ᴅɪsʙʟᴇᴅ ʀᴀɪᴅ ᴍᴏᴅᴇ ɪɴ {}".format(chat_id))
        logmsg = (
            f"<b>{html.escape(chat.title)}:</b>\n"
            f"#𝐑𝐀𝐈𝐃\n"
            f"ᴀᴜᴛᴏᴍᴀᴛɪᴄᴀʟʟʏ ᴅɪsᴀʙʟᴇᴅ\n"
        )
        return logmsg

    j.run_once(disable_raid, time)
    logmsg = (
        f"<b>{html.escape(chat.title)}:</b>\n"
        f"#𝐑𝐀𝐈𝐃\n"
        f"ᴇɴᴀʙʟʙᴇᴅ ғᴏʀ {readable_time}\n"
        f"<b>ᴀᴅᴍɪɴ:</b> {mention_html(user.id, user.first_name)}\n"
    )
    return logmsg


@Exoncallback(pattern="disable_raid=")
@connection_status
@user_admin_no_reply
@loggable
def disable_raid_cb(update: Update, _: CallbackContext) -> Optional[str]:
    args = update.callback_query.data.replace("disable_raid=", "").split("=")
    chat = update.effective_chat
    user = update.effective_user
    chat_id = args[0]
    time = args[1]
    _, t, acttime = sql.getDefenseStatus(chat_id)
    sql.setDefenseStatus(chat_id, False, time, acttime)
    update.effective_message.edit_text(
        "ʀᴀɪᴅ ᴍᴏᴅᴇ ʜᴀs ʙᴇᴇɴ <code>Disabled</code>, ᴊᴏɪɴɪɢ ᴍᴇᴍʙᴇʀs ᴡɪʟʟ ɴᴏ ʟᴏɴɢᴇʀ ʙᴇ ᴋɪᴄᴋᴇᴅ.",
        parse_mode=ParseMode.HTML,
    )
    logmsg = (
        f"<b>{html.escape(chat.title)}:</b>\n"
        f"#𝐑𝐀𝐈𝐃\n"
        f"ᴅɪsᴀʙʟᴇᴅ\n"
        f"<b>ᴀᴅᴍɪɴ:</b> {mention_html(user.id, user.first_name)}\n"
    )
    return logmsg


@Exoncallback(pattern="cancel_raid=")
@connection_status
@user_admin_no_reply
def disable_raid_cb(update: Update, context: CallbackContext):
    args = update.callback_query.data.split("=")
    what = args[0]
    update.effective_message.edit_text(
        f"ᴀᴄᴛɪᴏɴ ᴄᴀɴᴄᴇʟʟᴇᴅ, ʀᴀɪᴅ ᴍᴏᴅᴇ ᴡɪʟʟ sᴛᴀʏ <code>{'Enabled' if what ==1 else 'Disabled'}</code>.",
        parse_mode=ParseMode.HTML,
    )


@Exoncmd(command="raidtime")
@connection_status
@loggable
@u_admin(AdminPerms.CAN_CHANGE_INFO)
def raidtime(update: Update, context: CallbackContext) -> Optional[str]:
    what, time, acttime = sql.getDefenseStatus(update.effective_chat.id)
    args = context.args
    msg = update.effective_message
    u = update.effective_user
    chat = update.effective_chat
    user = res_user(u, msg.message_id, chat)
    if not args:
        msg.reply_text(
            f"ʀᴀɪᴅ ᴍᴏᴅᴇ ɪs ᴄᴜʀʀᴇɴᴛʟʏ sᴇᴛ ᴛᴏ {get_readable_time(time)}\nᴡʜᴇɴ ᴛᴏɢɢʟᴇᴅ, ᴛʜᴇ ʀᴀɪᴅ ᴍᴏᴅᴇ ᴡɪʟʟ ʟᴀsᴛ ғᴏʀ {get_readable_time(time)} ᴛʜᴇɴ ᴛᴜʀɴ ᴏғғ ᴀᴜᴛᴏᴍᴀᴛɪᴄᴀʟʟʏ",
            parse_mode=ParseMode.HTML,
        )
        return
    args_time = args[0].lower()
    time = get_time(args_time)
    if time:
        readable_time = get_readable_time(time)
        if time >= 300 and time < 86400:
            text = f"ʀᴀɪᴅ ᴍᴏᴅᴇ ɪs ᴄᴜʀʀᴇɴᴛʟʏ sᴇᴛ ᴛᴏ {readable_time}\nᴡʜᴇɴ ᴛᴏɢɢʟᴇᴅ, ᴛʜᴇ ʀᴀɪᴅ ᴍᴏᴅᴇ ᴡɪʟʟ ʟᴀsᴛ ғᴏʀ {readable_time} ᴛʜᴇɴ ᴛᴜʀɴ ᴏғғ ᴀᴜᴛᴏᴍᴀᴛɪᴄᴀʟʟʏ"
            msg.reply_text(text, parse_mode=ParseMode.HTML)
            sql.setDefenseStatus(chat.id, what, time, acttime)
            logmsg = (
                f"<b>{html.escape(chat.title)}:</b>\n"
                f"#𝐑𝐀𝐈𝐃\n"
                f"sᴇᴛ ʀᴀɪᴅ ᴍᴏᴅᴇ ᴛɪᴍᴇ ᴛᴏ {readable_time}\n"
                f"<b>ᴀᴅᴍɪɴ:</b> {mention_html(user.id, user.first_name)}\n"
            )
            return logmsg
        else:
            msg.reply_text(
                "ʏᴏᴜ ᴄᴀɴ ᴏɴʟʏ sᴇᴛ ᴛɪᴍᴇ ʙᴇᴛᴡᴇᴇɴ 5 ᴍɪɴᴜᴛᴇs ᴀɴᴅ 1 ᴅᴀʏ",
                parse_mode=ParseMode.HTML,
            )
    else:
        msg.reply_text(
            "ᴜɴᴋɴᴏᴡɴ ᴛɪᴍᴇ ɢɪᴠᴇɴ, give ᴍᴇ sᴏᴍᴇᴛʜɪɴɢ ʟɪᴋᴇ 5ᴍ ᴏʀ 1ʜ",
            parse_mode=ParseMode.HTML,
        )


@Exoncmd(command="raidactiontime", pass_args=True)
@connection_status
@u_admin(AdminPerms.CAN_CHANGE_INFO)
@loggable
def raidtime(update: Update, context: CallbackContext) -> Optional[str]:
    what, t, time = sql.getDefenseStatus(update.effective_chat.id)
    args = context.args
    msg = update.effective_message
    u = update.effective_user
    chat = update.effective_chat
    user = res_user(u, msg.message_id, chat)
    if not args:
        msg.reply_text(
            f"ʀᴀɪᴅ ᴀᴄᴛᴏɪɴ ᴛɪᴍᴇ ɪs ᴄᴜʀʀᴇɴᴛʟʏ sᴇᴛ ᴛᴏ {get_readable_time(time)}\nᴡʜᴇɴ ᴛᴏɢɢʟᴇᴅ, ᴛʜᴇ ᴍᴇᴍʙᴇʀs ᴛʜᴀᴛ ᴊᴏɪɴ ᴡɪʟʟ ʙᴇ ᴛᴇᴍᴘ ʙᴀɴɴᴇᴅ ғᴏʀ {get_readable_time(time)}",
            parse_mode=ParseMode.HTML,
        )
        return
    args_time = args[0].lower()
    time = get_time(args_time)
    if time:
        readable_time = get_readable_time(time)
        if time >= 300 and time < 86400:
            text = f"ʀᴀɪᴅ ᴀᴄᴛᴏɪɴ ᴛɪᴍᴇ ɪs ᴄᴜʀʀᴇɴᴛʟʏ sᴇᴛ ᴛᴏ {get_readable_time(time)}\nᴡʜᴇɴ ᴛᴏɢɢʟᴇᴅ, ᴛʜᴇ ᴍᴇᴍʙᴇʀs ᴛʜᴀᴛ ᴊᴏɪɴ ᴡɪʟʟ ʙᴇ ᴛᴇᴍᴘ ʙᴀɴɴᴇᴅ ғᴏʀ {readable_time}"
            msg.reply_text(text, parse_mode=ParseMode.HTML)
            sql.setDefenseStatus(chat.id, what, t, time)
            logmsg = (
                f"<b>{html.escape(chat.title)}:</b>\n"
                f"#𝐑𝐀𝐈𝐃\n"
                f"sᴇᴛ ʀᴀɪᴅ ᴍᴏᴅᴇ ᴀᴄᴛɪᴏɴ ᴛɪᴍᴇ ᴛᴏ {readable_time}\n"
                f"<b>ᴀᴅᴍɪɴ:</b> {mention_html(user.id, user.first_name)}\n"
            )
            return logmsg
        else:
            msg.reply_text(
                "ʏᴏᴜ ᴄᴀɴ ᴏɴʟʏ sᴇᴛ ᴛɪᴍᴇ ʙᴇᴛᴡᴇᴇɴ 5 ᴍɪɴᴜᴛᴇs ᴀɴᴅ 1 ᴅᴀʏ",
                parse_mode=ParseMode.HTML,
            )
    else:
        msg.reply_text(
            "ᴜɴᴋɴᴏᴡɴ ᴛɪᴍᴇ ɢɪᴠᴇɴ, ɢɪᴠᴇ ᴍᴇ sᴏᴍᴇᴛʜɪɴɢ ʟɪᴋᴇ 5m ᴏʀ 1h",
            parse_mode=ParseMode.HTML,
        )


# ғᴏʀ ʜᴇʟᴘ ᴍᴇɴᴜ
# """
from Exon.modules.language import gs


def get_help(chat):
    return gs(chat, "raid_help")


# """

__mod_name__ = "𝐀-ʀᴀɪᴅ"
