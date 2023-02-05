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

from io import BytesIO
from time import sleep

from telegram import ParseMode, TelegramError, Update
from telegram.error import BadRequest, Unauthorized
from telegram.ext import CallbackContext, Filters

import Exon.modules.no_sql.users_db as user_db
from Exon import DEV_USERS, LOGGER, OWNER_ID, dispatcher
from Exon.modules.helper_funcs.chat_status import dev_plus, sudo_plus
from Exon.modules.helper_funcs.decorators import Exoncmd, Exonmsg
from Exon.modules.no_sql.users_db import get_all_users

USERS_GROUP = 4
CHAT_GROUP = 5
DEV_AND_MORE = DEV_USERS.append(int(OWNER_ID))


def get_user_id(username):
    # ensure valid userid
    if len(username) <= 5:
        return None

    if username.startswith("@"):
        username = username[1:]

    users = user_db.get_userid_by_name(username)

    if not users:
        return None

    if len(users) == 1:
        return users[0]["_id"]

    for user_obj in users:
        try:
            userdat = dispatcher.bot.get_chat(user_obj["_id"])
            if userdat.username == username:
                return userdat.id

        except BadRequest as excp:
            if excp.message != "Chat not found":
                LOGGER.exception("Error extracting user ID")

    return None


@Exoncmd(command=["broadcastall", "broadcastusers", "broadcastgroups"])
@dev_plus
def broadcast(update: Update, context: CallbackContext):
    to_send = update.effective_message.text.split(None, 1)

    if len(to_send) >= 2:
        to_group = False
        to_user = False
        if to_send[0] == "/broadcastgroups":
            to_group = True
        if to_send[0] == "/broadcastusers":
            to_user = True
        else:
            to_group = to_user = True
        chats = user_db.get_all_chats() or []
        users = get_all_users()
        failed = 0
        failed_user = 0
        if to_group:
            for chat in chats:
                try:
                    context.bot.sendMessage(
                        int(chat["chat_id"]),
                        to_send[1],
                        parse_mode="MARKDOWN",
                        disable_web_page_preview=True,
                    )
                    sleep(0.1)
                except TelegramError:
                    failed += 1
        if to_user:
            for user in users:
                try:
                    context.bot.sendMessage(
                        int(user["_id"]),
                        to_send[1],
                        parse_mode="MARKDOWN",
                        disable_web_page_preview=True,
                    )
                    sleep(0.1)
                except TelegramError:
                    failed_user += 1
        update.effective_message.reply_text(
            f"Broadcast complete.\nGroups failed: <code>{failed}</code>.\nUsers failed: <code>{failed_user}</code>.",
            parse_mode=ParseMode.HTML,
        )


@Exonmsg((Filters.all & Filters.chat_type.groups), group=USERS_GROUP)
def log_user(update: Update, context: CallbackContext):
    chat = update.effective_chat
    msg = update.effective_message

    user_db.update_user(msg.from_user.id, msg.from_user.username, chat.id, chat.title)

    if msg.reply_to_message:
        user_db.update_user(
            msg.reply_to_message.from_user.id,
            msg.reply_to_message.from_user.username,
            chat.id,
            chat.title,
        )

    if msg.forward_from:
        user_db.update_user(msg.forward_from.id, msg.forward_from.username)


@Exoncmd(command="groups")
@sudo_plus
def chats(update: Update, context: CallbackContext):
    all_chats = user_db.get_all_chats() or []
    chatfile = "List of chats.\n0. Chat name | Chat ID | Members count\n"
    P = 1
    for chat in all_chats:
        try:
            curr_chat = context.bot.getChat(chat.chat_id)
            curr_chat.get_member(context.bot.id)
            chat_members = curr_chat.get_member_count(context.bot.id)
            chatfile += "{}. {} | {} | {}\n".format(
                P,
                chat.chat_name,
                chat.chat_id,
                chat_members,
            )
            P += 1
        except:
            pass

    with BytesIO(str.encode(chatfile)) as output:
        output.name = "groups_list.txt"
        update.effective_message.reply_document(
            document=output,
            filename="groups_list.txt",
            caption="ʜᴇʀᴇ ʙᴇ ᴛʜᴇ ʟɪꜱᴛ ᴏꜰ ɢʀᴏᴜᴘꜱ ɪɴ ᴍʏ ᴅᴀᴛᴀʙᴀꜱᴇ.",
        )


@Exonmsg((Filters.all & Filters.chat_type.groups), group=CHAT_GROUP)
def chat_checker(update: Update, context: CallbackContext):
    bot = context.bot
    try:
        if update.effective_message.chat.get_member(bot.id).can_send_messages is False:
            bot.leaveChat(update.effective_message.chat.id)
    except Unauthorized:
        pass


def __user_info__(user_id):
    if user_id in [777000, 1087968824]:
        return """╘══「 ɢʀᴏᴜᴘꜱ ᴄᴏᴜɴᴛ: <code>???</code> 」"""
    if user_id == dispatcher.bot.id:
        return """╘══「 ɢʀᴏᴜᴘꜱ ᴄᴏᴜɴᴛ: <code>???</code> 」"""
    num_chats = user_db.get_user_num_chats(user_id)
    return f"""╘══「 ɢʀᴏᴜᴘꜱ ᴄᴏᴜɴᴛ: <code>{num_chats}</code> 」"""


def __stats__():
    return f"× 0{user_db.num_users()} ᴜsᴇʀs, ᴀᴄʀᴏss 0{user_db.num_chats()} ᴄʜᴀᴛs"


def __migrate__(old_chat_id, new_chat_id):
    user_db.migrate_chat(old_chat_id, new_chat_id)


__mod_name__ = "𝐆-ᴄᴀsᴛ"


# ғᴏʀ ʜᴇʟᴘ ᴍᴇɴᴜ


# """
from Exon.modules.language import gs


def get_help(chat):
    return gs(chat, "gcast_help")


# """
