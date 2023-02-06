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
from typing import Optional

from telegram import ChatPermissions, ParseMode
from telegram.error import BadRequest
from telegram.ext import CommandHandler, Filters, MessageHandler
from telegram.utils.helpers import mention_html

from Exon import dispatcher
from Exon.modules.connection import connected
from Exon.modules.helper_funcs.alternate import send_message, typing_action
from Exon.modules.helper_funcs.chat_status import is_user_admin
from Exon.modules.helper_funcs.string_handling import extract_time
from Exon.modules.log_channel import loggable
from Exon.modules.sql import antiflood_sql as sql
from Exon.modules.sql.approve_sql import is_approved

from ..modules.helper_funcs.anonymous import AdminPerms, user_admin

FLOOD_GROUP = 3


@loggable
def check_flood(update, context) -> Optional[str]:
    user = update.effective_user  # type: Optional[User]
    chat = update.effective_chat  # type: Optional[Chat]
    msg = update.effective_message  # type: Optional[Message]

    if is_approved(chat.id, user.id):
        sql.update_flood(chat.id, None)
        return

    if not user:  # ignore channels
        return ""

    # ignore admins
    if is_user_admin(update, user.id):
        sql.update_flood(chat.id, None)
        return ""

    should_ban = sql.update_flood(chat.id, user.id)
    if not should_ban:
        return ""

    try:
        getmode, getvalue = sql.get_flood_setting(chat.id)
        if getmode == 1:
            chat.ban_member(user.id)
            execstrings = "ʙᴀɴɴᴇᴅ"
            tag = "BANNED"
        elif getmode == 2:
            chat.ban_member(user.id)
            chat.unban_member(user.id)
            execstrings = "ᴋɪᴄᴋᴇᴅ"
            tag = "KICKED"
        elif getmode == 3:
            context.bot.restrict_chat_member(
                chat.id, user.id, permissions=ChatPermissions(can_send_messages=False)
            )
            execstrings = "ᴍᴜᴛᴇᴅ"
            tag = "MUTED"
        elif getmode == 4:
            bantime = extract_time(msg, getvalue)
            chat.ban_member(user.id, until_date=bantime)
            execstrings = "ʙᴀɴɴᴇᴅ ғᴏʀ {}".format(getvalue)
            tag = "TBAN"
        elif getmode == 5:
            mutetime = extract_time(msg, getvalue)
            context.bot.restrict_chat_member(
                chat.id,
                user.id,
                until_date=mutetime,
                permissions=ChatPermissions(can_send_messages=False),
            )
            execstrings = "ᴍᴜᴛᴇᴅ ғᴏʀ {}".format(getvalue)
            tag = "TMUTE"
        send_message(
            update.effective_message,
            "ᴡᴀɴɴᴀ sᴘᴀᴍ?! sᴏʀʀʏ ɪᴛ's ɴᴏᴛ ʏᴏᴜʀ ʜᴏᴜsᴇ ᴍᴀɴ!\n{}!".format(execstrings),
        )

        return (
            "<b>{}:</b>"
            "\n#{}"
            "\n<b>ᴜsᴇʀ:</b> {}"
            "\ɴғʟᴏᴏᴅᴇᴅ ᴛʜᴇ ɢʀᴏᴜᴘ.".format(
                html.escape(chat.title), tag, mention_html(user.id, user.first_name)
            )
        )

    except BadRequest:
        msg.reply_text(
            "I ᴄᴀɴ'ᴛ ʀᴇsᴛʀɪᴄᴛ (ʙᴀɴ) ᴘᴇᴏᴘʟᴇ ʜᴇʀᴇ, ɢɪᴠᴇ ᴍᴇ ᴘᴇʀᴍɪssɪᴏɴs ғɪʀsᴛ! ᴜɴᴛɪʟ ᴛʜᴇɴ, I'ʟʟ ᴅɪsᴀʙʟᴇ ᴀɴᴛɪ-ғʟᴏᴏᴅ."
        )
        sql.set_flood(chat.id, 0)
        return (
            "<b>{}:</b>"
            "\n#𝐀𝐋𝐄𝐑𝐓 !"
            "\nᴅᴏɴ'ᴛ ʜᴀᴠᴇ ᴇɴᴏᴜɢʜ ᴘᴇʀᴍɪssɪᴏɴ ᴛᴏ ʀᴇsᴛʀɪᴄᴛ ᴜsᴇʀs sᴏ ᴀᴜᴛᴏᴍᴀᴛɪᴄᴀʟʟʏ ᴅɪsᴀʙʟᴇᴅ ᴀɴᴛɪ-ғʟᴏᴏᴅ ".format(
                chat.title
            )
        )


@user_admin(AdminPerms.CAN_CHANGE_INFO)
@loggable
@typing_action
def set_flood(update, context) -> str:
    chat = update.effective_chat  # type: Optional[Chat]
    user = update.effective_user  # type: Optional[User]
    message = update.effective_message  # type: Optional[Message]
    args = context.args

    conn = connected(context.bot, update, chat, user.id, need_admin=True)
    if conn:
        chat_id = conn
        chat_name = dispatcher.bot.getChat(conn).title
    else:
        if update.effective_message.chat.type == "private":
            send_message(
                update.effective_message,
                "ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ ɪs ᴍᴇᴀɴᴛ ᴛᴏ ᴜsᴇ ɪɴ ɢʀᴏᴜᴘ ɴᴏᴛ ɪɴ ᴘᴍ",
            )
            return ""
        chat_id = update.effective_chat.id
        chat_name = update.effective_message.chat.title

    if len(args) >= 1:
        val = args[0].lower()
        if val in ("off", "no", "0"):
            sql.set_flood(chat_id, 0)
            if conn:
                text = message.reply_text(
                    "ᴀɴᴛɪғʟᴏᴏᴅ ʜᴀs ʙᴇᴇɴ ᴅɪsᴀʙʟᴇᴅ ɪɴ {}.".format(chat_name)
                )
            else:
                text = message.reply_text("ᴀɴᴛɪғʟᴏᴏᴅ ʜᴀs ʙᴇᴇɴ ᴅɪsᴀʙʟᴇᴅ.")
            send_message(update.effective_message, text, parse_mode="markdown")

        elif val.isdigit():
            amount = int(val)
            if amount <= 0:
                sql.set_flood(chat_id, 0)
                if conn:
                    text = message.reply_text(
                        "ᴀɴᴛɪғʟᴏᴏᴅ ʜᴀs ʙᴇᴇɴ ᴅɪsᴀʙʟᴇᴅ ɪɴ {}.".format(chat_name)
                    )
                else:
                    text = message.reply_text("ᴀɴᴛɪғʟᴏᴏᴅ ʜᴀs ʙᴇᴇɴ ᴅɪsᴀʙʟᴇᴅ.")
                return (
                    "<b>{}:</b>"
                    "\n#𝐒𝐄𝐓𝐅𝐋𝐎𝐎𝐃"
                    "\n<b>ᴀᴅᴍɪɴ:</b> {}"
                    "\nᴅɪsᴀʙʟᴇ ᴀɴᴛɪғʟᴏᴏᴅ.".format(
                        html.escape(chat_name), mention_html(user.id, user.first_name)
                    )
                )

            if amount < 3:
                send_message(
                    update.effective_message,
                    "ᴀɴᴛɪғʟᴏᴏᴅ ᴍᴜsᴛ ʙᴇ ᴇɪᴛʜᴇʀ 0 (disabled) ᴏʀ ɴᴜᴍʙᴇʀ ɢʀᴇᴀᴛᴇʀ ᴛʜᴀɴ 3!",
                )
                return ""
            sql.set_flood(chat_id, amount)
            if conn:
                text = message.reply_text(
                    "ᴀɴᴛɪ-ғʟᴏᴏᴅ ʜᴀs ʙᴇᴇɴ sᴇᴛ ᴛᴏ {} ɪɴ ᴄʜᴀᴛ: {}".format(
                        amount, chat_name
                    )
                )
            else:
                text = message.reply_text(
                    "sᴜᴄᴄᴇssғᴜʟʟʏ ᴜᴘᴅᴀᴛᴇᴅ ᴀɴᴛɪ-ғʟᴏᴏᴅ ʟɪᴍɪᴛ ᴛᴏ {}!".format(amount)
                )
            send_message(update.effective_message, text, parse_mode="markdown")
            return (
                "<b>{}:</b>"
                "\n#𝐒𝐄𝐓𝐅𝐋𝐎𝐎𝐃"
                "\n<b>ᴀᴅᴍɪɴ:</b> {}"
                "\nsᴇᴛ ᴀɴᴛɪғʟᴏᴏᴅ ᴛᴏ <code>{}</code>.".format(
                    html.escape(chat_name),
                    mention_html(user.id, user.first_name),
                    amount,
                )
            )

        else:
            message.reply_text("ɪɴᴠᴀʟɪᴅ ᴀʀɢᴜᴍᴇɴᴛ ᴘʟᴇᴀsᴇ ᴜsᴇ ᴀ ɴᴜᴍʙᴇʀ, 'off' ᴏʀ 'no'")
    else:
        message.reply_text(
            (
                "ᴜsᴇ `/setflood ɴᴜᴍʙᴇʀ` ᴛᴏ ᴇɴᴀʙʟᴇ ᴀɴᴛɪ-ғʟᴏᴏᴅ.\nᴏʀ ᴜsᴇ `/setflood off` ᴛᴏ ᴅɪsᴀʙʟᴇ ᴀɴᴛɪ-ғʟᴏᴏᴅ!."
            ),
            parse_mode="markdown",
        )
    return ""


@typing_action
def flood(update, context):
    chat = update.effective_chat  # type: Optional[Chat]
    user = update.effective_user  # type: Optional[User]
    msg = update.effective_message

    conn = connected(context.bot, update, chat, user.id, need_admin=False)
    if conn:
        chat_id = conn
        chat_name = dispatcher.bot.getChat(conn).title
    else:
        if update.effective_message.chat.type == "private":
            send_message(
                update.effective_message,
                "ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ ɪs ᴍᴇᴀɴᴛ ᴛᴏ ᴜsᴇ ɪɴ ɢʀᴏᴜᴘ ɴᴏᴛ ɪɴ  ᴘᴍ",
            )
            return
        chat_id = update.effective_chat.id
        chat_name = update.effective_message.chat.title

    limit = sql.get_flood_limit(chat_id)
    if limit == 0:
        if conn:
            text = msg.reply_text(
                "I'ᴍ ɴᴏᴛ ᴇɴғᴏʀᴄɪɴɢ ᴀɴʏ ғʟᴏᴏᴅ ᴄᴏɴᴛʀᴏʟ ɪɴ {}!".format(chat_name)
            )
        else:
            text = msg.reply_text("I'ᴍ ɴᴏᴛ ᴇɴғᴏʀᴄɪɴɢ ᴀɴʏ ғʟᴏᴏᴅ ᴄᴏɴᴛʀᴏʟ ʜᴇʀᴇ!")
    elif conn:
        text = msg.reply_text(
            "I'ᴍ ᴄᴜʀʀᴇɴᴛʟʏ ʀᴇsᴛʀɪᴄᴛɪɴɢ ᴍᴇᴍʙᴇʀs ᴀғᴛᴇʀ {} ᴄᴏɴsᴇᴄᴜᴛɪᴠᴇ ᴍᴇssᴀɢᴇs ɪɴ {}.".format(
                limit, chat_name
            )
        )
    else:
        text = msg.reply_text(
            "I'm currently restricting members after {} consecutive messages.".format(
                limit
            )
        )
    send_message(update.effective_message, text, parse_mode="markdown")


@user_admin(AdminPerms.CAN_CHANGE_INFO)
@loggable
@typing_action
def set_flood_mode(update, context):
    chat = update.effective_chat  # type: Optional[Chat]
    user = update.effective_user  # type: Optional[User]
    msg = update.effective_message  # type: Optional[Message]
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
                "ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ ɪs ᴍᴇᴀɴᴛ ᴛᴏ ᴜsᴇ ɪɴ ɢʀᴏᴜᴘ ɴᴏᴛ ɪɴ PM",
            )
            return ""
        chat = update.effective_chat
        chat_id = update.effective_chat.id
        chat_name = update.effective_message.chat.title

    if args:
        if args[0].lower() == "ban":
            settypeflood = "ʙᴀɴ"
            sql.set_flood_strength(chat_id, 1, "0")
        elif args[0].lower() == "kick":
            settypeflood = "ᴋɪᴄᴋ"
            sql.set_flood_strength(chat_id, 2, "0")
        elif args[0].lower() == "mute":
            settypeflood = "ᴍᴜᴛᴇ"
            sql.set_flood_strength(chat_id, 3, "0")
        elif args[0].lower() == "tban":
            if len(args) == 1:
                teks = """ɪᴛ ʟᴏᴏᴋs ʟɪᴋᴇ ʏᴏᴜ ᴛʀɪᴇᴅ ᴛᴏ sᴇᴛ ᴛɪᴍᴇ ᴠᴀʟᴜᴇ ғᴏʀ ᴀɴᴛɪғʟᴏᴏᴅ ʙᴜᴛ ʏᴏᴜ ᴅɪᴅɴ'ᴛ sᴘᴇᴄɪғɪᴇᴅ ᴛɪᴍᴇ; ᴛʀʏ, `/setfloodmode tban <ᴛɪᴍᴇᴠᴀʟᴜᴇ>`.
    ᴇxᴀᴍᴘʟᴇs ᴏғ ᴛɪᴍᴇ ᴠᴀʟᴜᴇ: 4ᴍ = 4 ᴍɪɴᴜᴛᴇs, 3ʜ = 3 ʜᴏᴜʀs, 6ᴅ = 6 ᴅᴀʏs, 5ᴡ = 5 ᴡᴇᴇᴋs."""
                send_message(update.effective_message, teks, parse_mode="markdown")
                return
            settypeflood = "ᴛʙᴀɴ ғᴏʀ {}".format(args[1])
            sql.set_flood_strength(chat_id, 4, str(args[1]))
        elif args[0].lower() == "tmute":
            if len(args) == 1:
                teks = """ɪᴛ ʟᴏᴏᴋs ʟɪᴋᴇ ʏᴏᴜ ᴛʀɪᴇᴅ ᴛᴏ sᴇᴛ ᴛɪᴍᴇ ᴠᴀʟᴜᴇ ғᴏʀ ᴀɴᴛɪғʟᴏᴏᴅ ʙᴜᴛ ʏᴏᴜ ᴅɪᴅɴ'ᴛ sᴘᴇᴄɪғɪᴇᴅ ᴛɪᴍᴇ; ᴛʀʏ, `/setfloodmode tmute <ᴛɪᴍᴇᴠᴀʟᴜᴇ>`.
    ᴇxᴀᴍᴘʟᴇs ᴏғ ᴛɪᴍᴇ ᴠᴀʟᴜᴇ: 4ᴍ = 4 ᴍɪɴᴜᴛᴇs, 3ʜ = 3 ʜᴏᴜʀs, 6d = 6 ᴅᴀʏs, 5ᴡ = 5 ᴡᴇᴇᴋs."""
                send_message(update.effective_message, teks, parse_mode="markdown")
                return
            settypeflood = "ᴛᴍᴜᴛᴇ ғᴏʀ {}".format(args[1])
            sql.set_flood_strength(chat_id, 5, str(args[1]))
        else:
            send_message(
                update.effective_message, "I ᴏɴʟʏ ᴜɴᴅᴇʀsᴛᴀɴᴅ ʙᴀɴ/ᴋɪᴄᴋ/ᴍᴜᴛᴇ/ᴛʙᴀɴ/ᴛᴍᴜᴛᴇ!"
            )
            return
        if conn:
            text = msg.reply_text(
                "ᴇxᴄᴇᴇᴅɪɴɢ ᴄᴏɴsᴇᴄᴜᴛɪᴠᴇ ғʟᴏᴏᴅ ʟɪᴍɪᴛ ᴡɪʟʟ ʀᴇsᴜʟᴛ ɪɴ {} ɪɴ {}!".format(
                    settypeflood, chat_name
                )
            )
        else:
            text = msg.reply_text(
                "ᴇxᴄᴇᴇᴅɪɴɢ ᴄᴏɴsᴇᴄᴜᴛɪᴠᴇ ғʟᴏᴏᴅ ʟɪᴍɪᴛ ᴡɪʟʟ ʀᴇsᴜʟᴛ ɪɴ {}!".format(
                    settypeflood
                )
            )
        send_message(update.effective_message, text, parse_mode="markdown")
        return (
            "<b>{}:</b>\n"
            "<b>ᴀᴅᴍɪɴ:</b> {}\n"
            "ʜᴀs ᴄʜᴀɴɢᴇᴅ ᴀɴᴛɪғʟᴏᴏᴅ ᴍᴏᴅᴇ. ᴜsᴇʀ ᴡɪʟʟ {}.".format(
                settypeflood,
                html.escape(chat.title),
                mention_html(user.id, user.first_name),
            )
        )
    getmode, getvalue = sql.get_flood_setting(chat.id)
    if getmode == 1:
        settypeflood = "ʙᴀɴ"
    elif getmode == 2:
        settypeflood = "ᴋɪᴄᴋ"
    elif getmode == 3:
        settypeflood = "ᴍᴜᴛᴇ"
    elif getmode == 4:
        settypeflood = "ᴛʙᴀɴ ғᴏʀ {}".format(getvalue)
    elif getmode == 5:
        settypeflood = "ᴛᴍᴜᴛᴇ ғᴏʀ {}".format(getvalue)
    if conn:
        text = msg.reply_text(
            "sᴇɴᴅɪɴɢ ᴍᴏʀᴇ ᴍᴇssᴀɢᴇs ᴛʜᴀɴ ғʟᴏᴏᴅ ʟɪᴍɪᴛ ᴡɪʟʟ ʀᴇsᴜʟᴛ ɪɴ {} ɪɴ {}.".format(
                settypeflood, chat_name
            )
        )
    else:
        text = msg.reply_text(
            "sᴇɴᴅɪɴɢ ᴍᴏʀᴇ ᴍᴇssᴀɢᴇ ᴛʜᴀɴ ғʟᴏᴏᴅ ʟɪᴍɪᴛ ᴡɪʟʟ ʀᴇsᴜʟᴛ ɪɴ {}.".format(
                settypeflood
            )
        )
    send_message(update.effective_message, text, parse_mode=ParseMode.MARKDOWN)
    return ""


def __migrate__(old_chat_id, new_chat_id):
    sql.migrate_chat(old_chat_id, new_chat_id)


def __chat_settings__(chat_id, user_id):
    limit = sql.get_flood_limit(chat_id)
    if limit == 0:
        return "ɴᴏᴛ ᴇɴғᴏʀᴄɪɴɢ ᴛᴏ ғʟᴏᴏᴅ ᴄᴏɴᴛʀᴏʟ."
    return "ᴀɴᴛɪғʟᴏᴏᴅ ʜᴀs ʙᴇᴇɴ sᴇᴛ ᴛᴏ`{}`.".format(limit)


__mod_name__ = "𝐀-ғʟᴏᴏᴅ"

# ғᴏʀ ʜᴇʟᴘ ᴍᴇɴᴜ

# """
from Exon.modules.language import gs


def get_help(chat):
    return gs(chat, "antiflood_help")


# """


FLOOD_BAN_HANDLER = MessageHandler(
    Filters.all & ~Filters.status_update & Filters.chat_type.groups,
    check_flood,
    run_async=True,
)
SET_FLOOD_HANDLER = CommandHandler(
    "setflood", set_flood, pass_args=True, run_async=True
)  # , filters=Filters.chat_type.groups)
SET_FLOOD_MODE_HANDLER = CommandHandler(
    "setfloodmode", set_flood_mode, pass_args=True, run_async=True
)  # , filters=Filters.chat_type.groups)
FLOOD_HANDLER = CommandHandler(
    "flood", flood, run_async=True
)  # , filters=Filters.chat_type.groups)

dispatcher.add_handler(FLOOD_BAN_HANDLER, FLOOD_GROUP)
dispatcher.add_handler(SET_FLOOD_HANDLER)
dispatcher.add_handler(SET_FLOOD_MODE_HANDLER)
dispatcher.add_handler(FLOOD_HANDLER)
