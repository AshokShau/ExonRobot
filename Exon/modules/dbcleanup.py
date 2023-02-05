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
from time import sleep

from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.error import BadRequest, Unauthorized
from telegram.ext import CallbackQueryHandler, CommandHandler

from Exon import DEV_USERS, dispatcher
from Exon.modules.helper_funcs.filters import CustomFilters
from Exon.modules.no_sql import global_bans_db as gban_db
from Exon.modules.no_sql import users_db as user_db


def get_invalid_chats(bot: Bot, update: Update, remove: bool = False):
    chat_id = update.effective_chat.id
    chats = user_db.get_all_chats()
    kicked_chats, progress = 0, 0
    chat_list = []
    progress_message = None

    for chat in chats:
        if ((100 * chats.index(chat)) / len(chats)) > progress:
            progress_bar = f"{progress}% completed in getting invalid chats."
            if progress_message:
                try:
                    bot.editMessageText(
                        progress_bar, chat_id, progress_message.message_id
                    )
                except BaseException:
                    pass
            else:
                progress_message = bot.sendMessage(chat_id, progress_bar)
            progress += 5

        cid = chat["chat_id"]
        sleep(0.5)
        try:
            bot.get_chat(cid, timeout=120)
        except (BadRequest, Unauthorized):
            kicked_chats += 1
            chat_list.append(cid)
        except BaseException:
            pass

    try:
        progress_message.delete()
    except BaseException:
        pass

    if not remove:
        return kicked_chats
    for muted_chat in chat_list:
        sleep(0.5)
        user_db.rem_chat(muted_chat)
    return kicked_chats


def get_invalid_gban(bot: Bot, update: Update, remove: bool = False):
    banned = gban_db.get_gban_list()
    ungbanned_users = 0
    ungban_list = []

    for user in banned:
        user_id = user["_id"]
        sleep(0.5)
        try:
            bot.get_chat(user_id)
        except BadRequest:
            ungbanned_users += 1
            ungban_list.append(user_id)
        except BaseException:
            pass

    if not remove:
        return ungbanned_users
    for user_id in ungban_list:
        sleep(0.5)
        gban_db.ungban_user(user_id)
    return ungbanned_users


def dbcleanup(update, context):
    msg = update.effective_message

    msg.reply_text("Getting invalid chat count ...")
    invalid_chat_count = get_invalid_chats(context.bot, update)

    msg.reply_text("Getting invalid gbanned count ...")
    invalid_gban_count = get_invalid_gban(context.bot, update)

    reply = f"Total invalid chats - {invalid_chat_count}\n"
    reply += f"Total invalid gbanned users - {invalid_gban_count}"

    buttons = [[InlineKeyboardButton("Cleanup DB", callback_data="db_cleanup")]]

    update.effective_message.reply_text(
        reply, reply_markup=InlineKeyboardMarkup(buttons)
    )


def get_muted_chats(bot: Bot, update: Update, leave: bool = False):
    chat_id = update.effective_chat.id
    chats = user_db.get_all_chats()
    muted_chats, progress = 0, 0
    chat_list = []
    progress_message = None

    for chat in chats:
        if ((100 * chats.index(chat)) / len(chats)) > progress:
            progress_bar = f"{progress}% completed in getting muted chats."
            if progress_message:
                try:
                    bot.editMessageText(
                        progress_bar, chat_id, progress_message.message_id
                    )
                except BaseException:
                    pass
            else:
                progress_message = bot.sendMessage(chat_id, progress_bar)
            progress += 5

        cid = chat["chat_id"]
        sleep(0.5)

        try:
            bot.send_chat_action(cid, "TYPING", timeout=120)
        except (BadRequest, Unauthorized):
            muted_chats += +1
            chat_list.append(cid)
        except BaseException:
            pass

    try:
        progress_message.delete()
    except BaseException:
        pass

    if not leave:
        return muted_chats
    for muted_chat in chat_list:
        sleep(0.5)
        try:
            bot.leaveChat(muted_chat, timeout=120)
        except BaseException:
            pass
        users_db.rem_chat(muted_chat)
    return muted_chats


def leave_muted_chats(update, context):
    message = update.effective_message
    progress_message = message.reply_text("Getting chat count ...")
    muted_chats = get_muted_chats(context.bot, update)

    buttons = [[InlineKeyboardButton("Leave chats", callback_data="db_leave_chat")]]

    update.effective_message.reply_text(
        f"I am muted in {muted_chats} chats.",
        reply_markup=InlineKeyboardMarkup(buttons),
    )
    progress_message.delete()


def callback_button(update, context):
    bot = context.bot
    query = update.callback_query
    message = query.message
    chat_id = update.effective_chat.id
    query_type = query.data

    bot.answer_callback_query(query.id)

    if query_type == "db_leave_chat":
        if query.from_user.id in DEV_USERS:
            bot.editMessageText("Leaving chats ...", chat_id, message.message_id)
            chat_count = get_muted_chats(bot, update, True)
            bot.sendMessage(chat_id, f"Left {chat_count} chats.")
        else:
            query.answer("You are not allowed to use this.")
    elif query_type == "db_cleanup":
        if query.from_user.id in DEV_USERS:
            bot.editMessageText("Cleaning up DB ...", chat_id, message.message_id)
            invalid_chat_count = get_invalid_chats(bot, update, True)
            invalid_gban_count = get_invalid_gban(bot, update, True)
            reply = "Cleaned up {} chats and {} gbanned users from db.".format(
                invalid_chat_count, invalid_gban_count
            )
            bot.sendMessage(chat_id, reply)
        else:
            query.answer("You are not allowed to use this.")


DB_CLEANUP_HANDLER = CommandHandler(
    "dbcleanup", dbcleanup, filters=CustomFilters.dev_filter, run_async=True
)
LEAVE_MUTED_CHATS_HANDLER = CommandHandler(
    "leavemutedchats",
    leave_muted_chats,
    filters=CustomFilters.dev_filter,
    run_async=True,
)
BUTTON_HANDLER = CallbackQueryHandler(callback_button, pattern="db_.*", run_async=True)

dispatcher.add_handler(DB_CLEANUP_HANDLER)
dispatcher.add_handler(LEAVE_MUTED_CHATS_HANDLER)
dispatcher.add_handler(BUTTON_HANDLER)

__mod_name__ = "𝐃ʙ-ᴄʟᴇᴀɴ"
__handlers__ = [DB_CLEANUP_HANDLER, LEAVE_MUTED_CHATS_HANDLER, BUTTON_HANDLER]

# ғᴏʀ ʜᴇʟᴘ ᴍᴇɴᴜ


# """
from Exon.modules.language import gs


def get_help(chat):
    return gs(chat, "dbclean_help")


# """
