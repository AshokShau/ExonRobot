import asyncio
from io import BytesIO
from typing import Union

from telegram import ChatMemberAdministrator, Update
from telegram.constants import ParseMode
from telegram.error import BadRequest, Forbidden, TelegramError
from telegram.ext import CommandHandler, ContextTypes, MessageHandler, filters
from telegram.helpers import escape_markdown

import Exon.modules.sql.users_sql as sql
from Exon import DEV_USERS, LOGGER, OWNER_ID, exon
from Exon.modules.helper_funcs.chat_status import check_admin
from Exon.modules.sql.users_sql import get_all_users

# from Exon.modules.sql.topics_sql import get_action_topic


USERS_GROUP = 4
CHAT_GROUP = 5
DEV_AND_MORE = DEV_USERS.append(int(OWNER_ID))


async def get_user_id(username: str) -> Union[int, None]:
    # ensure valid userid
    if len(username) <= 5:
        return None

    if username.startswith("@"):
        username = username[1:]

    users = sql.get_userid_by_name(username)

    if not users:
        return None

    elif len(users) == 1:
        return users[0].user_id

    else:
        for user_obj in users:
            try:
                userdat = await exon.bot.get_chat(user_obj.user_id)
                if userdat.username == username:
                    return userdat.id

            except BadRequest as excp:
                if excp.message == "ᴄʜᴀᴛ ɴᴏᴛ ғᴏᴜɴᴅ":
                    pass
                else:
                    LOGGER.exception("ᴇʀʀᴏʀ ᴇxᴛʀᴀᴄᴛɪɴɢ ᴜsᴇʀ ID")

    return None


@check_admin(only_dev=True)
async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
        chats = sql.get_all_chats() or []
        users = get_all_users()
        failed = 0
        failed_user = 0
        if to_group:
            for chat in chats:
                try:
                    # topic_chat = get_action_topic(chat.chat_id)
                    await context.bot.sendMessage(
                        int(chat.chat_id),
                        escape_markdown(to_send[1], 2),
                        parse_mode=ParseMode.MARKDOWN_V2,
                        disable_web_page_preview=True,
                    )
                    await asyncio.sleep(1)
                except TelegramError:
                    failed += 1
        if to_user:
            for user in users:
                try:
                    await context.bot.sendMessage(
                        int(user.user_id),
                        escape_markdown(to_send[1], 2),
                        parse_mode=ParseMode.MARKDOWN_V2,
                        disable_web_page_preview=True,
                    )
                    await asyncio.sleep(1)
                except TelegramError:
                    failed_user += 1
        await update.effective_message.reply_text(
            f"ʙʀᴏᴀᴅᴄᴀsᴛ ᴄᴏᴍᴘʟᴇᴛᴇ.\nɢʀᴏᴜᴘs ғᴀɪʟᴇᴅ: {failed}.\nᴜsᴇʀs ғᴀɪʟᴇᴅ: {failed_user}.",
        )


async def log_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    msg = update.effective_message

    sql.update_user(msg.from_user.id, msg.from_user.username, chat.id, chat.title)

    if msg.reply_to_message:
        sql.update_user(
            msg.reply_to_message.from_user.id,
            msg.reply_to_message.from_user.username,
            chat.id,
            chat.title,
        )

    if msg.forward_from:
        sql.update_user(msg.forward_from.id, msg.forward_from.username)


@check_admin(only_sudo=True)
async def chats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    all_chats = sql.get_all_chats() or []
    chatfile = "ʟɪsᴛ ᴏғ ᴄʜᴀᴛs.\n0. ᴄʜᴀᴛ ɴᴀᴍᴇ | ᴄʜᴀᴛ ɪᴅ | ᴍᴇᴍʙᴇʀs ᴄᴏᴜɴᴛ\n"
    P = 1
    for chat in all_chats:
        try:
            curr_chat = await context.bot.getChat(chat.chat_id)
            await curr_chat.get_member(context.bot.id)
            chat_members = await curr_chat.get_member_count(context.bot.id)
            chatfile += "{}. {} | {} | {}\n".format(
                P,
                chat.chat_name,
                chat.chat_id,
                chat_members,
            )
            P = P + 1
        except:
            pass

    with BytesIO(str.encode(chatfile)) as output:
        output.name = "groups_list.txt"
        await update.effective_message.reply_document(
            document=output,
            filename="groups_list.txt",
            caption="ʜᴇʀᴇ ʙᴇ ᴛʜᴇ ʟɪsᴛ ᴏғ ɢʀᴏᴜᴘs ɪɴ ᴍʏ ᴅᴀᴛᴀʙᴀsᴇ.",
        )


async def chat_checker(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bot = context.bot
    try:
        bot_admin = await update.effective_message.chat.get_member(bot.id)
        if isinstance(bot_admin, ChatMemberAdministrator):
            if bot_admin.can_post_messages is False:
                await bot.leaveChat(update.effective_message.chat.id)
    except Forbidden:
        pass


def __user_info__(user_id):
    if user_id in [777000, 1087968824]:
        return """╘══「 ɢʀᴏᴜᴘs ᴄᴏᴜɴᴛ: <code>???</code> 」"""
    if user_id == exon.bot.id:
        return """╘══「 ɢʀᴏᴜᴘs ᴄᴏᴜɴᴛ: <code>???</code> 」"""
    num_chats = sql.get_user_num_chats(user_id)
    return f"""╘══「 ɢʀᴏᴜᴘs ᴄᴏᴜɴᴛ: <code>{num_chats}</code> 」"""


def __stats__():
    return f"• {sql.num_users()} ᴜsᴇʀs, ᴀᴄʀᴏss {sql.num_chats()} ᴄʜᴀᴛs"


def __migrate__(old_chat_id, new_chat_id):
    sql.migrate_chat(old_chat_id, new_chat_id)


__help__ = ""  # no help string

BROADCAST_HANDLER = CommandHandler(
    ["broadcastall", "broadcastusers", "broadcastgroups"], broadcast
)
USER_HANDLER = MessageHandler(
    filters.ALL & filters.ChatType.GROUPS, log_user, allow_edit=True
)
CHAT_CHECKER_HANDLER = MessageHandler(
    filters.ALL & filters.ChatType.GROUPS, chat_checker, allow_edit=True
)
CHATLIST_HANDLER = CommandHandler("groups", chats)

exon.add_handler(USER_HANDLER, USERS_GROUP)
exon.add_handler(BROADCAST_HANDLER)
exon.add_handler(CHATLIST_HANDLER)
exon.add_handler(CHAT_CHECKER_HANDLER, CHAT_GROUP)

__mod_name__ = "𝐔sᴇʀs"
__handlers__ = [(USER_HANDLER, USERS_GROUP), BROADCAST_HANDLER, CHATLIST_HANDLER]
