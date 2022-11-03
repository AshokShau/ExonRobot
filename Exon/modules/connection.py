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

import re
import time

from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup, ParseMode, Update
from telegram.error import BadRequest, Unauthorized
from telegram.ext import CallbackQueryHandler, CommandHandler

import Exon.modules.sql.connection_sql as sql
from Exon import DEV_USERS, DRAGONS, dispatcher
from Exon.modules.helper_funcs import chat_status
from Exon.modules.helper_funcs.alternate import send_message, typing_action

user_admin = chat_status.user_admin


@user_admin
@typing_action
def allow_connections(update, context) -> str:

    chat = update.effective_chat
    args = context.args

    if chat.type == chat.PRIVATE:
        send_message(
            update.effective_message,
            "ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ ɪs ғᴏʀ ɢʀᴏᴜᴘ ᴏɴʟʏ. ɴᴏᴛ ɪɴ ᴘᴍ!",
        )

    elif len(args) >= 1:
        var = args[0]
        if var == "no":
            sql.set_allow_connect_to_chat(chat.id, False)
            send_message(
                update.effective_message,
                "ᴄᴏɴɴᴇᴄᴛɪᴏɴ ʜᴀs ʙᴇᴇɴ ᴅɪsᴀʙʟᴇᴅ ғᴏʀ ᴛʜɪs ᴄʜᴀᴛ",
            )
        elif var == "yes":
            sql.set_allow_connect_to_chat(chat.id, True)
            send_message(
                update.effective_message,
                "ᴄᴏɴɴᴇᴄᴛɪᴏɴ ʜᴀs ʙᴇᴇɴ ᴇɴᴀʙʟᴇᴅ ғᴏʀ ᴛʜɪs ᴄʜᴀᴛ",
            )
        else:
            send_message(
                update.effective_message,
                "ᴘʟᴇᴀsᴇ ᴇɴᴛᴇʀ `yes` ᴏʀ `no`!",
                parse_mode=ParseMode.MARKDOWN,
            )
    elif get_settings := sql.allow_connect_to_chat(chat.id):
        send_message(
            update.effective_message,
            "ᴄᴏɴɴᴇᴄᴛɪᴏɴs ᴛᴏ ᴛʜɪs ɢʀᴏᴜᴘ ᴀʀᴇ *ᴀʟʟᴏᴡᴇᴅ* ғᴏʀ ᴍᴇᴍʙᴇʀs!",
            parse_mode=ParseMode.MARKDOWN,
        )
    else:
        send_message(
            update.effective_message,
            "ᴄᴏɴɴᴇᴄᴛɪᴏɴ ᴛᴏ ᴛʜɪs ɢʀᴏᴜᴘ ᴀʀᴇ *ɴᴏᴛ ᴀʟʟᴏᴡᴇᴅ* ғᴏʀ ᴍᴇᴍʙᴇʀs!",
            parse_mode=ParseMode.MARKDOWN,
        )


@typing_action
def connection_chat(update, context):

    chat = update.effective_chat
    user = update.effective_user

    conn = connected(context.bot, update, chat, user.id, need_admin=True)

    if conn:
        chat = dispatcher.bot.getChat(conn)
        chat_name = dispatcher.bot.getChat(conn).title
    else:
        if update.effective_message.chat.type != "private":
            return
        chat = update.effective_chat
        chat_name = update.effective_message.chat.title

    if conn:
        message = f"ʏᴏᴜ ᴀʀᴇ ᴄᴜʀʀᴇɴᴛʟʏ ᴄᴏɴɴᴇᴄᴛᴇᴅ ᴛᴏ {chat_name}.\n"
    else:
        message = "ʏᴏᴜ ᴀʀᴇ ᴄᴜʀʀᴇɴᴛʟʏ ɴᴏᴛ ᴄᴏɴɴᴇᴄᴛᴇᴅ ɪɴ ᴀɴʏ ɢʀᴏᴜᴘ.\n"
    send_message(update.effective_message, message, parse_mode="markdown")


@typing_action
def connect_chat(update, context):

    chat = update.effective_chat
    user = update.effective_user
    args = context.args

    if update.effective_chat.type == "private":
        if args and len(args) >= 1:
            try:
                connect_chat = int(args[0])
                getstatusadmin = context.bot.get_chat_member(
                    connect_chat,
                    update.effective_message.from_user.id,
                )
            except ValueError:
                try:
                    connect_chat = str(args[0])
                    get_chat = context.bot.getChat(connect_chat)
                    connect_chat = get_chat.id
                    getstatusadmin = context.bot.get_chat_member(
                        connect_chat,
                        update.effective_message.from_user.id,
                    )
                except BadRequest:
                    send_message(update.effective_message, "ɪɴᴠᴀʟɪᴅ ᴄʜᴀᴛ ID!")
                    return
            except BadRequest:
                send_message(update.effective_message, "ɪɴᴠᴀʟɪᴅ ᴄʜᴀᴛ ID!")
                return

            isadmin = getstatusadmin.status in ("administrator", "creator")
            ismember = getstatusadmin.status in ("member")
            isallow = sql.allow_connect_to_chat(connect_chat)

            if (isadmin) or (isallow and ismember) or (user.id in DRAGONS):
                if connection_status := sql.connect(
                    update.effective_message.from_user.id,
                    connect_chat,
                ):
                    conn_chat = dispatcher.bot.getChat(
                        connected(context.bot, update, chat, user.id, need_admin=False),
                    )
                    chat_name = conn_chat.title
                    send_message(
                        update.effective_message,
                        f"sᴜᴄᴄᴇssғᴜʟʟʏ ᴄᴏɴɴᴇᴄᴛᴇᴅ ᴛᴏ *{chat_name}*. \nᴜsᴇ /helpconnect ᴛᴏ ᴄʜᴇᴄᴋ ᴀᴠᴀɪʟᴀʙʟᴇ ᴄᴏᴍᴍᴀɴᴅs.",
                        parse_mode=ParseMode.MARKDOWN,
                    )

                    sql.add_history_conn(user.id, str(conn_chat.id), chat_name)
                else:
                    send_message(update.effective_message, "Connection failed!")
            else:
                send_message(
                    update.effective_message,
                    "ᴄᴏɴɴᴇᴄᴛɪᴏɴ ᴛᴏ ᴛʜɪs ᴄʜᴀᴛ ɪs ɴᴏᴛ ᴀʟʟᴏᴡᴇᴅ!",
                )
        else:
            gethistory = sql.get_history_conn(user.id)
            if gethistory:
                buttons = [
                    InlineKeyboardButton(
                        text="⛔ ᴄʟᴏsᴇ ʙᴜᴛᴛᴏɴ",
                        callback_data="connect_close",
                    ),
                    InlineKeyboardButton(
                        text="🧹 ᴄʟᴇᴀʀ ʜɪsᴛᴏʀʏ",
                        callback_data="connect_clear",
                    ),
                ]
            else:
                buttons = []
            if conn := connected(context.bot, update, chat, user.id, need_admin=False):
                connectedchat = dispatcher.bot.getChat(conn)
                text = (
                    f"ғ ᴀʀᴇ ᴄᴜʀʀᴇɴᴛʟʏ ᴄᴏɴɴᴇᴄᴛᴇᴅ ᴛᴏ *{connectedchat.title}* (`{conn}`)"
                )
                buttons.append(
                    InlineKeyboardButton(
                        text="🔌 ᴅɪsᴄᴏɴɴᴇᴄᴛ",
                        callback_data="connect_disconnect",
                    ),
                )
            else:
                text = "ᴡʀɪᴛᴇ ᴛʜᴇ ᴄʜᴀᴛ ɪᴅ ᴏʀ ᴛᴀɢ ᴛᴏ ᴄᴏɴɴᴇᴄᴛ!"
            if gethistory:
                text += "\n\n*Connection history:*\n"
                text += "╒═══「 *ɪɴғᴏ* 」\n"
                text += "│  sᴏʀᴛᴇᴅ: `ɴᴇᴡᴇsᴛ`\n"
                text += "│\n"
                buttons = [buttons]
                for x in sorted(gethistory.keys(), reverse=True):
                    htime = time.strftime("%ᴅ/%ᴍ/%ʏ", time.localtime(x))
                    text += f'╞═「 *{gethistory[x]["chat_name"]}* 」\n│   `{gethistory[x]["chat_id"]}`\n│   `{htime}`\n'

                    text += "│\n"
                    buttons.append(
                        [
                            InlineKeyboardButton(
                                text=gethistory[x]["chat_name"],
                                callback_data=f'connect({gethistory[x]["chat_id"]})',
                            )
                        ]
                    )

                text += "╘══「 ᴛᴏᴛᴀʟ {} ᴄʜᴀᴛs 」".format(
                    f"{len(gethistory)} (max)"
                    if len(gethistory) == 5
                    else str(len(gethistory))
                )

                conn_hist = InlineKeyboardMarkup(buttons)
            elif buttons:
                conn_hist = InlineKeyboardMarkup([buttons])
            else:
                conn_hist = None
            send_message(
                update.effective_message,
                text,
                parse_mode="markdown",
                reply_markup=conn_hist,
            )

    else:
        getstatusadmin = context.bot.get_chat_member(
            chat.id,
            update.effective_message.from_user.id,
        )
        isadmin = getstatusadmin.status in ("administrator", "creator")
        ismember = getstatusadmin.status in ("member")
        isallow = sql.allow_connect_to_chat(chat.id)
        if (isadmin) or (isallow and ismember) or (user.id in DRAGONS):
            if connection_status := sql.connect(
                update.effective_message.from_user.id,
                chat.id,
            ):
                chat_name = dispatcher.bot.getChat(chat.id).title
                send_message(
                    update.effective_message,
                    f"sᴜᴄᴄᴇssғᴜʟʟʏ ᴄᴏɴɴᴇᴄᴛᴇᴅ ᴛᴏ *{chat_name}*.",
                    parse_mode=ParseMode.MARKDOWN,
                )

                try:
                    sql.add_history_conn(user.id, str(chat.id), chat_name)
                    context.bot.send_message(
                        update.effective_message.from_user.id,
                        f"ʏᴏᴜ ᴀʀᴇ ᴄᴏɴɴᴇᴄᴛᴇᴅ ᴛᴏ *{chat_name}*. \nᴜsᴇ `/helpconnect` ᴛᴏ ᴄʜᴇᴄᴋ ᴀᴠᴀɪʟᴀʙʟᴇ ᴄᴏᴍᴍᴀɴᴅs.",
                        parse_mode="markdown",
                    )

                except (BadRequest, Unauthorized):
                    pass
            else:
                send_message(update.effective_message, "ᴄᴏɴɴᴇᴄᴛɪᴏɴ ғᴀɪʟᴇᴅ!")
        else:
            send_message(
                update.effective_message,
                "ᴄᴏɴɴᴇᴄᴛɪᴏɴ ᴛᴏ ᴛʜɪs ᴄʜᴀᴛ ɪs ɴᴏᴛ ᴀʟʟᴏᴡᴇᴅ!",
            )


def disconnect_chat(update, context):

    if update.effective_chat.type == "private":
        if disconnection_status := sql.disconnect(
            update.effective_message.from_user.id
        ):
            sql.disconnected_chat = send_message(
                update.effective_message,
                "ᴅɪsᴄᴏɴɴᴇᴄᴛᴇᴅ ғʀᴏᴍ ᴄʜᴀᴛ!",
            )
        else:
            send_message(update.effective_message, "ʏᴏᴜ'ʀᴇ ɴᴏᴛ ᴄᴏɴɴᴇᴄᴛᴇᴅ!")
    else:
        send_message(update.effective_message, "ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ ɪs ᴏɴʟʏ ᴀᴠᴀɪʟᴀʙʟᴇ ɪɴ PM.")


def connected(bot: Bot, update: Update, chat, user_id, need_admin=True):
    user = update.effective_user

    if chat.type == chat.PRIVATE and sql.get_connected_chat(user_id):

        conn_id = sql.get_connected_chat(user_id).chat_id
        getstatusadmin = bot.get_chat_member(
            conn_id,
            update.effective_message.from_user.id,
        )
        isadmin = getstatusadmin.status in ("administrator", "creator")
        ismember = getstatusadmin.status in ("member")
        isallow = sql.allow_connect_to_chat(conn_id)

        if (
            (isadmin)
            or (isallow and ismember)
            or (user.id in DRAGONS)
            or (user.id in DEV_USERS)
        ):
            if need_admin is True:
                if (
                    getstatusadmin.status in ("administrator", "creator")
                    or user_id in DRAGONS
                    or user.id in DEV_USERS
                ):
                    return conn_id
                send_message(
                    update.effective_message,
                    "ʏᴏᴜ ᴍᴜsᴛ ʙᴇ ᴀɴ ᴀᴅᴍɪɴ ɪɴ ᴛʜᴇ ᴄᴏɴɴᴇᴄᴛᴇᴅ ɢʀᴏᴜᴘ!",
                )
            else:
                return conn_id
        else:
            send_message(
                update.effective_message,
                "ᴛʜᴇ ɢʀᴏᴜᴘ ᴄʜᴀɴɢᴇᴅ ᴛʜᴇ ᴄᴏɴɴᴇᴄᴛɪᴏɴ ʀɪɢʜᴛs ᴏʀ ʏᴏᴜ ᴀʀᴇ ɴᴏ ʟᴏɴɢᴇʀ ᴀɴ ᴀᴅᴍɪɴ.\nI'ᴠᴇ ᴅɪsᴄᴏɴɴᴇᴄᴛᴇᴅ ʏᴏᴜ.",
            )
            disconnect_chat(update, bot)
    else:
        return False


CONN_HELP = """
ᴀᴄᴛɪᴏɴs ᴡʜɪᴄʜ ᴀʀᴇ ᴀᴠᴀɪʟᴀʙʟᴇ ᴡɪᴛʜ ᴄᴏɴɴᴇᴄᴛᴇᴅ ɢʀᴏᴜᴘs:-
*ᴜsᴇʀ ᴀᴄᴛɪᴏɴs:*
• ᴠɪᴇᴡ ɴᴏᴛᴇs
• ᴠɪᴇᴡ ғɪʟᴛᴇʀs
• ᴠɪᴇᴡ ʙʟᴀᴄᴋʟɪsᴛ
• ᴠɪᴇᴡ ᴀɴᴛɪғʟᴏᴏᴅ sᴇᴛᴛɪɴɢs
• ᴠɪᴇᴡ ᴅɪsᴀʙʟᴇᴅ ᴄᴏᴍᴍᴀɴᴅs
• ᴍᴀɴʏ ᴍᴏʀᴇ ɪɴ ғᴜᴛᴜʀᴇ
!
*ᴀᴅᴍɪɴ ᴀᴄᴛɪᴏɴs:*
 • View ᴀɴᴅ ᴇᴅɪᴛ ɴᴏᴛᴇs
 • ᴠɪᴇᴡ ᴀɴᴅ ᴇᴅɪᴛ ғɪʟᴛᴇʀs.
 • ɢᴇᴛ ɪɴᴠɪᴛᴇ ʟɪɴᴋ ᴏғ ᴄʜᴀᴛ.
 • sᴇᴛ ᴀɴᴅ ᴄᴏɴᴛʀᴏʟ ᴀɴᴛɪғʟᴏᴏᴅ sᴇᴛᴛɪɴɢs. 
 • sᴇᴛ ᴀɴᴅ ᴄᴏɴᴛʀᴏʟ ʙʟᴀᴄᴋʟɪsᴛ sᴇᴛᴛɪɴɢs.
 • Set ʟᴏᴄᴋs ᴀɴᴅ ᴜɴʟᴏᴄᴋs ɪɴ ᴄʜᴀᴛ.
 • ᴇɴᴀʙʟᴇ and ᴅɪsᴀʙʟᴇ ᴄᴏᴍᴍᴀɴᴅs in chat.
 • ᴇxᴘᴏʀᴛ ᴀɴᴅ Imports ᴏғ ᴄʜᴀᴛ ʙᴀᴄᴋᴜᴘ.
 • ᴍᴏʀᴇ ɪɴ ғᴜᴛᴜʀᴇ!
"""


def help_connect_chat(update, context):

    context.args

    if update.effective_message.chat.type != "private":
        send_message(update.effective_message, "PM ᴍᴇ ᴡɪᴛʜ ᴛʜᴀᴛ ᴄᴏᴍᴍᴀɴᴅ ᴛᴏ ɢᴇᴛ ʜᴇʟᴘ.")
        return
    send_message(update.effective_message, CONN_HELP, parse_mode="markdown")


def connect_button(update, context):

    query = update.callback_query
    chat = update.effective_chat
    user = update.effective_user

    connect_match = re.match(r"connect\((.+?)\)", query.data)
    disconnect_match = query.data == "connect_disconnect"
    clear_match = query.data == "connect_clear"
    connect_close = query.data == "connect_close"

    if connect_match:
        target_chat = connect_match[1]
        getstatusadmin = context.bot.get_chat_member(target_chat, query.from_user.id)
        isadmin = getstatusadmin.status in ("administrator", "creator")
        ismember = getstatusadmin.status in ("member")
        isallow = sql.allow_connect_to_chat(target_chat)

        if (isadmin) or (isallow and ismember) or (user.id in DRAGONS):
            if connection_status := sql.connect(query.from_user.id, target_chat):
                conn_chat = dispatcher.bot.getChat(
                    connected(context.bot, update, chat, user.id, need_admin=False),
                )
                chat_name = conn_chat.title
                query.message.edit_text(
                    f"sᴜᴄᴄᴇssғᴜʟʟʏ ᴄᴏɴɴᴇᴄᴛᴇᴅ ᴛᴏ *{chat_name}*. \nᴜsᴇ `/helpconnect` ᴛᴏ ᴄʜᴇᴄᴋ ᴀᴠᴀɪʟᴀʙʟᴇ ᴄᴏᴍᴍᴀɴᴅs.",
                    parse_mode=ParseMode.MARKDOWN,
                )

                sql.add_history_conn(user.id, str(conn_chat.id), chat_name)
            else:
                query.message.edit_text("ᴄᴏɴɴᴇᴄᴛɪᴏɴ ғᴀɪʟᴇᴅ!")
        else:
            context.bot.answer_callback_query(
                query.id,
                "ᴄᴏɴɴᴇᴄᴛɪᴏɴ ᴛᴏ ᴛʜɪs ᴄʜᴀᴛ ɪs ɴᴏᴛ ᴀʟʟᴏᴡᴇᴅ!",
                show_alert=True,
            )
    elif disconnect_match:
        if disconnection_status := sql.disconnect(query.from_user.id):
            sql.disconnected_chat = query.message.edit_text("Disconnected from chat!")
        else:
            context.bot.answer_callback_query(
                query.id,
                "ʏᴏᴜ'ʀᴇ ɴᴏᴛ ᴄᴏɴɴᴇᴄᴛᴇᴅ!",
                show_alert=True,
            )
    elif clear_match:
        sql.clear_history_conn(query.from_user.id)
        query.message.edit_text("ʜɪsᴛᴏʀʏ ᴄᴏɴɴᴇᴄᴛᴇᴅ ʜᴀs ʙᴇᴇɴ ᴄʟᴇᴀʀᴇᴅ!")
    elif connect_close:
        query.message.edit_text("ᴄʟᴏsᴇᴅ.\nᴛᴏ ᴏᴘᴇɴ ᴀɢᴀɪɴ, ᴛʏᴘᴇ /connect")
    else:
        connect_chat(update, context)


__mod_name__ = "𝙲ᴏɴɴᴇᴄᴛs"

__help__ = """
*sᴏᴍᴇᴛɪᴍᴇs, ʏᴏᴜ ᴊᴜsᴛ ᴡᴀɴᴛ ᴛᴏ ᴀᴅᴅ sᴏᴍᴇ ɴᴏᴛᴇs ᴀɴᴅ ғɪʟᴛᴇʀs ᴛᴏ ᴀ ɢʀᴏᴜᴘ ᴄʜᴀᴛ, ʙᴜᴛ ʏᴏᴜ ᴅᴏɴ'ᴛ ᴡᴀɴᴛ ᴇᴠᴇʀʏᴏɴᴇ ᴛᴏ sᴇᴇ; ᴛʜɪs ɪs ᴡʜᴇʀᴇ ᴄᴏɴɴᴇᴄᴛɪᴏɴs ᴄᴏᴍᴇ ɪɴ...
ᴛʜɪs ᴀʟʟᴏᴡs ʏᴏᴜ ᴛᴏ ᴄᴏɴɴᴇᴄᴛ ᴛᴏ ᴀ ᴄʜᴀᴛ's ᴅᴀᴛᴀʙᴀsᴇ, ᴀɴᴅ ᴀᴅᴅ ᴛʜɪɴɢs ᴛᴏ ɪᴛ ᴡɪᴛʜᴏᴜᴛ ᴛʜᴇ ᴄᴏᴍᴍᴀɴᴅs ᴀᴘᴘᴇᴀʀɪɴɢ ɪɴ ᴄʜᴀᴛ! ғᴏʀ ᴏʙᴠɪᴏᴜs ʀᴇᴀsᴏɴs, ʏᴏᴜ ɴᴇᴇᴅ ᴛᴏ ʙᴇ ᴀɴ ᴀᴅᴍɪɴ ᴛᴏ ᴀᴅᴅ ᴛʜɪɴɢs; ʙᴜᴛ ᴀɴʏ ᴍᴇᴍʙᴇʀ ɪɴ ᴛʜᴇ ɢʀᴏᴜᴘ ᴄᴀɴ ᴠɪᴇᴡ ʏᴏᴜʀ ᴅᴀᴛᴀ.*


❂ /connect: `ᴄᴏɴɴᴇᴄᴛꜱ ᴛᴏ ᴄʜᴀᴛ` (ᴄᴀɴ ʙᴇ ᴅᴏɴᴇ ɪɴ ᴀ ɢʀᴏᴜᴘ ʙʏ /connect ᴏʀ /connect <chat id> ɪɴ ᴘᴍ)

❂ /connection: `ʟɪꜱᴛ ᴄᴏɴɴᴇᴄᴛᴇᴅ ᴄʜᴀᴛꜱ`

❂ /disconnect: `ᴅɪꜱᴄᴏɴɴᴇᴄᴛ ғʀᴏᴍ ᴀ ᴄʜᴀᴛ`

❂ /helpconnect: `ʟɪꜱᴛ ᴀᴠᴀɪʟᴀʙʟᴇ ᴄᴏᴍᴍᴀɴᴅꜱ ᴛʜᴀᴛ ᴄᴀɴ ʙᴇ ᴜꜱᴇᴅ ʀᴇᴍᴏᴛᴇʟʏ`

*ᴀᴅᴍɪɴ ᴏɴʟʏ:*

❂ /allowconnect <yes/no>: `ᴀʟʟᴏᴡ ᴀ ᴜꜱᴇʀ ᴛᴏ ᴄᴏɴɴᴇᴄᴛ ᴛᴏ ᴀ ᴄʜᴀᴛ`

"""

CONNECT_CHAT_HANDLER = CommandHandler(
    "connect", connect_chat, pass_args=True, run_async=True
)
CONNECTION_CHAT_HANDLER = CommandHandler("connection", connection_chat, run_async=True)
DISCONNECT_CHAT_HANDLER = CommandHandler("disconnect", disconnect_chat, run_async=True)
ALLOW_CONNECTIONS_HANDLER = CommandHandler(
    "allowconnect", allow_connections, pass_args=True, run_async=True
)
HELP_CONNECT_CHAT_HANDLER = CommandHandler(
    "helpconnect", help_connect_chat, run_async=True
)
CONNECT_BTN_HANDLER = CallbackQueryHandler(
    connect_button, pattern=r"connect", run_async=True
)

dispatcher.add_handler(CONNECT_CHAT_HANDLER)
dispatcher.add_handler(CONNECTION_CHAT_HANDLER)
dispatcher.add_handler(DISCONNECT_CHAT_HANDLER)
dispatcher.add_handler(ALLOW_CONNECTIONS_HANDLER)
dispatcher.add_handler(HELP_CONNECT_CHAT_HANDLER)
dispatcher.add_handler(CONNECT_BTN_HANDLER)
