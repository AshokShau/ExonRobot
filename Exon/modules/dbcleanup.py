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

from time import sleep

from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.error import BadRequest, Unauthorized
from telegram.ext import CallbackContext, CallbackQueryHandler, CommandHandler

import Exon.modules.sql.global_bans_sql as gban_sql
import Exon.modules.sql.users_sql as user_sql
from Exon import DEV_USERS, OWNER_ID, dispatcher
from Exon.modules.helper_funcs.chat_status import dev_plus


def get_muted_chats(bot: Bot, update: Update, leave: bool = False):
    chat_id = update.effective_chat.id
    chats = user_sql.get_all_chats()
    muted_chats, progress = 0, 0
    chat_list = []
    progress_message = None

    for chat in chats:

        if ((100 * chats.index(chat)) / len(chats)) > progress:
            progress_bar = f"{progress}% ᴄᴏᴍᴘʟᴇᴛᴇᴅ ɪɴ ɢᴇᴛᴛɪɴɢ ᴍᴜᴛᴇᴅ ᴄʜᴀᴛs."
            if progress_message:
                try:
                    bot.editMessageText(
                        progress_bar, chat_id, progress_message.message_id
                    )
                except:
                    pass
            else:
                progress_message = bot.sendMessage(chat_id, progress_bar)
            progress += 5

        cid = chat.chat_id
        sleep(0.1)

        try:
            bot.send_chat_action(cid, "TYPING", timeout=120)
        except (BadRequest, Unauthorized):
            muted_chats += +1
            chat_list.append(cid)
    try:
        progress_message.delete()
    except:
        pass

    if not leave:
        return muted_chats
    for muted_chat in chat_list:
        sleep(0.1)
        try:
            bot.leaveChat(muted_chat, timeout=120)
        except:
            pass
        user_sql.rem_chat(muted_chat)
    return muted_chats


def get_invalid_chats(update: Update, context: CallbackContext, remove: bool = False):
    bot = context.bot
    chat_id = update.effective_chat.id
    chats = user_sql.get_all_chats()
    kicked_chats, progress = 0, 0
    chat_list = []
    progress_message = None

    for chat in chats:

        if ((100 * chats.index(chat)) / len(chats)) > progress:
            progress_bar = f"{progress}% ᴄᴏᴍᴘʟᴇᴛᴇᴅ ɪɴ ɢᴇᴛᴛɪɴɢ ɪɴᴠᴀʟɪᴅ ᴄʜᴀᴛs."
            if progress_message:
                try:
                    bot.editMessageText(
                        progress_bar,
                        chat_id,
                        progress_message.message_id,
                    )
                except:
                    pass
            else:
                progress_message = bot.sendMessage(chat_id, progress_bar)
            progress += 5

        cid = chat.chat_id
        sleep(0.1)
        try:
            bot.get_chat(cid, timeout=60)
        except (BadRequest, Unauthorized):
            kicked_chats += 1
            chat_list.append(cid)
    try:
        progress_message.delete()
    except:
        pass

    if not remove:
        return kicked_chats
    for muted_chat in chat_list:
        sleep(0.1)
        user_sql.rem_chat(muted_chat)
    return kicked_chats


def get_invalid_gban(update: Update, context: CallbackContext, remove: bool = False):
    bot = context.bot
    banned = gban_sql.get_gban_list()
    ungbanned_users = 0
    ungban_list = []

    for user in banned:
        user_id = user["user_id"]
        sleep(0.1)
        try:
            bot.get_chat(user_id)
        except BadRequest:
            ungbanned_users += 1
            ungban_list.append(user_id)
    if not remove:
        return ungbanned_users
    for user_id in ungban_list:
        sleep(0.1)
        gban_sql.ungban_user(user_id)
    return ungbanned_users


@dev_plus
def dbcleanup(update: Update, context: CallbackContext):
    msg = update.effective_message

    msg.reply_text("ɢᴇᴛᴛɪɴɢ ɪɴᴠᴀʟɪᴅ ᴄʜᴀᴛ ᴄᴏᴜɴᴛ ...")
    invalid_chat_count = get_invalid_chats(update, context)

    msg.reply_text("ɢᴇᴛᴛɪɴɢ ɪɴᴠᴀʟɪᴅ ɢʙᴀɴɴᴇᴅ ᴄᴏᴜɴᴛ ...")
    invalid_gban_count = get_invalid_gban(update, context)

    reply = f"ᴛᴏᴛᴀʟ ɪɴᴠᴀʟɪᴅ ᴄʜᴀᴛs - {invalid_chat_count}\n"
    reply += f"ᴛᴏᴛᴀʟ ɪɴᴠᴀʟɪᴅ ɢʙᴀɴɴᴇᴅ ᴜsᴇʀs - {invalid_gban_count}"

    buttons = [[InlineKeyboardButton("✦ ᴄʟᴇᴀɴᴜᴘ ᴅʙ ✦", callback_data="db_cleanup")]]

    update.effective_message.reply_text(
        reply,
        reply_markup=InlineKeyboardMarkup(buttons),
    )


def callback_button(update: Update, context: CallbackContext):
    bot = context.bot
    query = update.callback_query
    message = query.message
    chat_id = update.effective_chat.id
    query_type = query.data

    admin_list = [OWNER_ID] + DEV_USERS

    bot.answer_callback_query(query.id)

    if query_type == "db_leave_chat" and query.from_user.id in admin_list:
        bot.editMessageText("ʟᴇᴀᴠɪɴɢ ᴄʜᴀᴛs ...", chat_id, message.message_id)
        chat_count = get_muted_chats(update, context, True)
        bot.sendMessage(chat_id, f"ʟᴇғᴛ {chat_count} ᴄʜᴀᴛs.")
    elif (
        query_type == "db_leave_chat"
        or query_type == "db_cleanup"
        and query.from_user.id not in admin_list
    ):
        query.answer("ʏᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴀʟʟᴏᴡᴇᴅ ᴛᴏ ᴜsᴇ ᴛʜɪs.")
    elif query_type == "db_cleanup":
        bot.editMessageText("ᴄʟᴇᴀɴɪɴɢ ᴜᴘ DB ...", chat_id, message.message_id)
        invalid_chat_count = get_invalid_chats(update, context, True)
        invalid_gban_count = get_invalid_gban(update, context, True)
        reply = f"ᴄʟᴇᴀɴᴇᴅ ᴜᴘ {invalid_chat_count} ᴄʜᴀᴛs ᴀɴᴅ {invalid_gban_count} ɢʙᴀɴɴᴇᴅ ᴜsᴇʀs ғʀᴏᴍ ᴅʙ."

        bot.sendMessage(chat_id, reply)


DB_CLEANUP_HANDLER = CommandHandler("dbcleanup", dbcleanup, run_async=True)
BUTTON_HANDLER = CallbackQueryHandler(callback_button, pattern="db_.*", run_async=True)

dispatcher.add_handler(DB_CLEANUP_HANDLER)
dispatcher.add_handler(BUTTON_HANDLER)

__mod_name__ = "DB ᴄʟᴇᴀɴᴜᴘ"
__handlers__ = [DB_CLEANUP_HANDLER, BUTTON_HANDLER]
