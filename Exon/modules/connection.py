import re
import time

from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.constants import ChatType, ChatMemberStatus, ParseMode
from telegram.error import BadRequest, Forbidden
from telegram.ext import CallbackQueryHandler, CommandHandler, ContextTypes

import Exon.modules.sql.connection_sql as sql
from Exon import DEV_USERS, DRAGONS, exon
from Exon.modules.helper_funcs.alternate import send_message, typing_action

try:
    from Exon.modules.helper_funcs.chat_status import check_admin
except ImportError as e:
    print(e)

check_admin = chat_status.check_admin


@check_admin(is_user=True)
@typing_action
async def allow_connections(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:

    chat = update.effective_chat
    args = context.args

    if chat.type != ChatType.PRIVATE:
        if len(args) >= 1:
            var = args[0]
            if var == "no":
                sql.set_allow_connect_to_chat(chat.id, False)
                await send_message(
                    update.effective_message,
                    "ᴄᴏɴɴᴇᴄᴛɪᴏɴ ʜᴀs ʙᴇᴇɴ ᴅɪsᴀʙʟᴇᴅ ғᴏʀ ᴛʜɪs ᴄʜᴀᴛ",
                )
            elif var == "yes":
                sql.set_allow_connect_to_chat(chat.id, True)
                await send_message(
                    update.effective_message,
                    "ᴄᴏɴɴᴇᴄᴛɪᴏɴ ʜᴀs ʙᴇᴇɴ ᴇɴᴀʙʟᴇᴅ ғᴏʀ ᴛʜɪs ᴄʜᴀᴛ",
                )
            else:
                await send_message(
                    update.effective_message,
                    "ᴘʟᴇᴀsᴇ ᴇɴᴛᴇʀ `yes` ᴏʀ `no`!",
                    parse_mode=ParseMode.MARKDOWN,
                )
        else:
            get_settings = sql.allow_connect_to_chat(chat.id)
            if get_settings:
                await send_message(
                    update.effective_message,
                    "ᴄᴏɴɴᴇᴄᴛɪᴏɴs ᴛᴏ ᴛʜɪs ɢʀᴏᴜᴘ ᴀʀᴇ *ᴀʟʟᴏᴡᴇᴅ* ғᴏʀ ᴍᴇᴍʙᴇʀs!",
                    parse_mode=ParseMode.MARKDOWN,
                )
            else:
                await send_message(
                    update.effective_message,
                    "ᴄᴏɴɴᴇᴄᴛɪᴏɴ ᴛᴏ ᴛʜɪs ɢʀᴏᴜᴘ ᴀʀᴇ *ɴᴏᴛ ᴀʟʟᴏᴡᴇᴅ* ғᴏʀ ᴍᴇᴍʙᴇʀs!",
                    parse_mode=ParseMode.MARKDOWN,
                )
    else:
        await send_message(
            update.effective_message,
            "ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ ɪs ғᴏʀ ɢʀᴏᴜᴘ ᴏɴʟʏ. ɴᴏᴛ ɪɴ ᴘᴍ!",
        )


@typing_action
async def connection_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):

    chat = update.effective_chat
    user = update.effective_user

    conn = await connected(context.bot, update, chat, user.id, need_admin=True)

    if conn:
        chat = await exon.bot.getChat(conn)
        chat_name = (await exon.bot.getChat(conn)).title
    else:
        if update.effective_message.chat.type != "ChatType.PRIVATE":
            return
        chat = update.effective_chat
        chat_name = update.effective_message.chat.title

    if conn:
        message = "ʏᴏᴜ ᴀʀᴇ ᴄᴜʀʀᴇɴᴛʟʏ ᴄᴏɴɴᴇᴄᴛᴇᴅ ᴛᴏ {}.\n".format(chat_name)
    else:
        message = "ʏᴏᴜ ᴀʀᴇ ᴄᴜʀʀᴇɴᴛʟʏ ɴᴏᴛ ᴄᴏɴɴᴇᴄᴛᴇᴅ ɪɴ ᴀɴʏ ɢʀᴏᴜᴘ.\n"
    await send_message(update.effective_message, message, parse_mode=ParseMode.MARKDOWN))


@typing_action
async def connect_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):

    chat = update.effective_chat
    user = update.effective_user
    args = context.args

    if update.effective_chat.type == "ChatType.PRIVATE":
        if args and len(args) >= 1:
            try:
                connect_chat = int(args[0])
                getstatusadmin = await context.bot.get_chat_member(
                    connect_chat,
                    update.effective_message.from_user.id,
                )
            except ValueError:
                try:
                    connect_chat = str(args[0])
                    get_chat = await context.bot.getChat(connect_chat)
                    connect_chat = get_chat.id
                    getstatusadmin = await context.bot.get_chat_member(
                        connect_chat,
                        update.effective_message.from_user.id,
                    )
                except BadRequest:
                    await send_message(update.effective_message, "Invalid Chat ID!")
                    return
            except BadRequest:
                await send_message(update.effective_message, "Invalid Chat ID!")
                return

            isadmin = getstatusadmin.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]
            ismember = getstatusadmin.status == ChatMemberStatus.MEMBER
            isallow = sql.allow_connect_to_chat(connect_chat)

            if (isadmin) or (isallow and ismember) or (user.id in DRAGONS):
                connection_status = sql.connect(
                    update.effective_message.from_user.id,
                    connect_chat,
                )
                if connection_status:
                    conn = await connected(
                        context.bot, update, chat, user.id, need_admin=False
                    )
                    conn_chat = await exon.bot.getChat(conn)
                    chat_name = conn_chat.title
                    await send_message(
                        update.effective_message,
                        "sᴜᴄᴄᴇssғᴜʟʟʏ ᴄᴏɴɴᴇᴄᴛᴇᴅ ᴛᴏ *{}*. \nᴜsᴇ /helpconnect ᴛᴏ ᴄʜᴇᴄᴋ ᴀᴠᴀɪʟᴀʙʟᴇ commands.".format(
                            chat_name,
                        ),
                        parse_mode=ParseMode.MARKDOWN,
                    )
                    sql.add_history_conn(user.id, str(conn_chat.id), chat_name)
                else:
                    await send_message(update.effective_message, "Connection failed!")
            else:
                await send_message(
                    update.effective_message,
                    "ᴄᴏɴɴᴇᴄᴛɪᴏɴ ᴛᴏ ᴛʜɪs ᴄʜᴀᴛ ɪs ɴᴏᴛ ᴀʟʟᴏᴡᴇᴅ!",
                )
        else:
            gethistory = sql.get_history_conn(user.id)
            if gethistory:
                buttons = [
                    InlineKeyboardButton(
                        text="❎ ᴄʟᴏsᴇ ʙᴜᴛᴛᴏɴ",
                        callback_data="connect_close",
                    ),
                    InlineKeyboardButton(
                        text="🧹 ᴄʟᴇᴀʀ ʜɪsᴛᴏʀʏ",
                        callback_data="connect_clear",
                    ),
                ]
            else:
                buttons = []
            conn = await connected(context.bot, update, chat, user.id, need_admin=False)
            if conn:
                connectedchat = await exon.bot.getChat(conn)
                text = "ʏᴏᴜ ᴀʀᴇ ᴄᴜʀʀᴇɴᴛʟʏ ᴄᴏɴɴᴇᴄᴛᴇᴅ ᴛᴏ *{}* (`{}`)".format(
                    connectedchat.title,
                    conn,
                )
                buttons.append(
                    InlineKeyboardButton(
                        text="🔌 ᴅɪsᴄᴏɴɴᴇᴄᴛ",
                        callback_data="connect_disconnect",
                    ),
                )
            else:
                text = "ᴡʀɪᴛᴇ ᴛʜᴇ ᴄʜᴀᴛ ID ᴏʀ ᴛᴀɢ ᴛᴏ ᴄᴏɴɴᴇᴄᴛ!"
            if gethistory:
                text += "\n\n*ᴄᴏɴɴᴇᴄᴛɪᴏɴ ʜɪsᴛᴏʀʏ:*\n"
                text += "╒═══「 *ɪɴғᴏ* 」\n"
                text += "│  sᴏʀᴛᴇᴅ: `ɴᴇᴡᴇsᴛ`\n"
                text += "│\n"
                buttons = [buttons]
                for x in sorted(gethistory.keys(), reverse=True):
                    htime = time.strftime("%d/%m/%Y", time.localtime(x))
                    text += "╞═「 *{}* 」\n│   `{}`\n│   `{}`\n".format(
                        gethistory[x]["chat_name"],
                        gethistory[x]["chat_id"],
                        htime,
                    )
                    text += "│\n"
                    buttons.append(
                        [
                            InlineKeyboardButton(
                                text=gethistory[x]["chat_name"],
                                callback_data="connect({})".format(
                                    gethistory[x]["chat_id"],
                                ),
                            ),
                        ],
                    )
                text += "╘══「 ᴛᴏᴛᴀʟ {} ᴄʜᴀᴛs 」".format(
                    str(len(gethistory)) + " (max)"
                    if len(gethistory) == 5
                    else str(len(gethistory)),
                )
                conn_hist = InlineKeyboardMarkup(buttons)
            elif buttons:
                conn_hist = InlineKeyboardMarkup([buttons])
            else:
                conn_hist = None
            await send_message(
                update.effective_message,
                text,
                parse_mode=ParseMode.MARKDOWN",
                reply_markup=conn_hist,
            )

    else:
        getstatusadmin = await context.bot.get_chat_member(
            chat.id,
            update.effective_message.from_user.id,
        )
        isadmin = getstatusadmin.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]
        ismember = getstatusadmin.status == ChatMemberStatus.MEMBER
        isallow = sql.allow_connect_to_chat(chat.id)
        if (isadmin) or (isallow and ismember) or (user.id in DRAGONS):
            connection_status = sql.connect(
                update.effective_message.from_user.id,
                chat.id,
            )
            if connection_status:
                chat_obj = await exon.bot.getChat(chat.id)
                chat_name = chat_obj.title
                await send_message(
                    update.effective_message,
                    "sᴜᴄᴄᴇssғᴜʟʟʏ ᴄᴏɴɴᴇᴄᴛᴇᴅ ᴛᴏ *{}*.".format(chat_name),
                    parse_mode=ParseMode.MARKDOWN,
                )
                try:
                    sql.add_history_conn(user.id, str(chat.id), chat_name)
                    await context.bot.send_message(
                        update.effective_message.from_user.id,
                        "ʏᴏᴜ ᴀʀᴇ ᴄᴏɴɴᴇᴄᴛᴇᴅ ᴛᴏ *{}*. \nᴜsᴇ `/helpconnect` ᴛᴏ ᴄʜᴇᴄᴋ ᴀᴠᴀɪʟᴀʙʟᴇ ᴄᴏᴍᴍᴀɴᴅs.".format(
                            chat_name,
                        ),
                        parse_mode=ParseMode.MARKDOWN",
                    )
                except BadRequest:
                    pass
                except Forbidden:
                    pass
            else:
                await send_message(update.effective_message, "ᴄᴏɴɴᴇᴄᴛɪᴏɴ ғᴀɪʟᴇᴅ!")
        else:
            await send_message(
                update.effective_message,
                "ᴄᴏɴɴᴇᴄᴛɪᴏɴ ᴛᴏ ᴛʜɪs ᴄʜᴀᴛ ɪs ɴᴏᴛ ᴀʟʟᴏᴡᴇᴅ!",
            )


async def disconnect_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.effective_chat.type == "ChatType.PRIVATE":
        disconnection_status = sql.disconnect(update.effective_message.from_user.id)
        if disconnection_status:
            sql.disconnected_chat = await send_message(
                update.effective_message,
                "ᴅɪsᴄᴏɴɴᴇᴄᴛᴇᴅ ғʀᴏᴍ ᴄʜᴀᴛ!",
            )
        else:
            await send_message(update.effective_message, "ʏᴏᴜ'ʀᴇ ɴᴏᴛ ᴄᴏɴɴᴇᴄᴛᴇᴅ!")
    else:
        await send_message(
            update.effective_message, "ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ ɪs ᴏɴʟʏ ᴀᴠᴀɪʟᴀʙʟᴇ ɪɴ ᴘᴍ."
        )


async def connected(bot: Bot, update: Update, chat, user_id, need_admin=True):
    user = update.effective_user

    if chat.type == ChatType.PRIVATE and sql.get_connected_chat(user_id):

        conn_id = sql.get_connected_chat(user_id).chat_id
        getstatusadmin = await bot.get_chat_member(
            conn_id,
            update.effective_message.from_user.id,
        )
        isadmin = getstatusadmin.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]
        ismember = getstatusadmin.status == ChatMemberStatus.MEMBER
        isallow = sql.allow_connect_to_chat(conn_id)

        if (
            (isadmin)
            or (isallow and ismember)
            or (user.id in DRAGONS)
            or (user.id in DEV_USERS)
        ):
            if need_admin is True:
                if (
                    getstatusadmin.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]
                    or user_id in DRAGONS
                    or user.id in DEV_USERS
                ):
                    return conn_id
                else:
                    await send_message(
                        update.effective_message,
                        "ʏᴏᴜ ᴍᴜsᴛ ʙᴇ ᴀɴ ᴀᴅᴍɪɴ ɪɴ ᴛʜᴇ ᴄᴏɴɴᴇᴄᴛᴇᴅ ɢʀᴏᴜᴘ!",
                    )
            else:
                return conn_id
        else:
            await send_message(
                update.effective_message,
                "ᴛʜᴇ ɢʀᴏᴜᴘ ᴄʜᴀɴɢᴇᴅ ᴛʜᴇ ᴄᴏɴɴᴇᴄᴛɪᴏɴ ʀɪɢʜᴛs or ʏᴏᴜ ᴀʀᴇ ɴᴏ ʟᴏɴɢᴇʀ ᴀɴ ᴀᴅᴍɪɴ.\nI'ᴠᴇ ᴅɪsᴄᴏɴɴᴇᴄᴛᴇᴅ ʏᴏᴜ .",
            )
            disconnect_chat(update, bot)
    else:
        return False


CONN_HELP = """
 ᴀᴄᴛɪᴏɴs ᴀʀᴇ ᴀᴠᴀɪʟᴀʙʟᴇ ᴡɪᴛʜ ᴄᴏɴɴᴇᴄᴛᴇᴅ ɢʀᴏᴜᴘs:
 • View and edit Notes.
 • View and edit Filters.
 • Get invite link of chat.
 • Set and control AntiFlood settings.
 • Set and control Blacklist settings.
 • Set Locks and Unlocks in chat.
 • Enable and Disable commands in chat.
 • Export and Imports of chat backup.
 """


async def help_connect_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):

    context.args

    if update.effective_message.chat.type != "ChatType.PRIVATE:
        await send_message(
            update.effective_message, "PM me with that command to get help."
        )
        return
    else:
        await send_message(update.effective_message, CONN_HELP, parse_mode=ParseMode.MARKDOWN)


async def connect_button(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    chat = update.effective_chat
    user = update.effective_user

    connect_match = re.match(r"connect\((.+?)\)", query.data)
    disconnect_match = query.data == "connect_disconnect"
    clear_match = query.data == "connect_clear"
    connect_close = query.data == "connect_close"

    if connect_match:
        target_chat = connect_match.group(1)
        getstatusadmin = await context.bot.get_chat_member(
            target_chat, query.from_user.id
        )
        isadmin = getstatusadmin.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]
        ismember = getstatusadmin.status == ChatMemberStatus.MEMBER
        isallow = sql.allow_connect_to_chat(target_chat)

        if (isadmin) or (isallow and ismember) or (user.id in DRAGONS):
            connection_status = sql.connect(query.from_user.id, target_chat)

            if connection_status:
                conn = await connected(
                    context.bot, update, chat, user.id, need_admin=False
                )
                conn_chat = await exon.bot.getChat(conn)
                chat_name = conn_chat.title
                await query.message.edit_text(
                    "sᴜᴄᴄᴇssғᴜʟʟʏ ᴄᴏɴɴᴇᴄᴛᴇᴅ ᴛᴏ *{}*. \n ᴍᴜsᴇ `/helpconnect` ᴛᴏ ᴄʜᴇᴄᴋ ᴀᴠᴀɪʟᴀʙʟᴇ ᴄᴏᴍᴍᴀɴᴅs.".format(
                        chat_name,
                    ),
                    parse_mode=ParseMode.MARKDOWN,
                )
                sql.add_history_conn(user.id, str(conn_chat.id), chat_name)
            else:
                await query.message.edit_text("Connection failed!")
        else:
            await context.bot.answer_callback_query(
                query.id,
                "ᴄᴏɴɴᴇᴄᴛɪᴏɴ ᴛᴏ ᴛʜɪs ᴄʜᴀᴛ ɪs ɴᴏᴛ ᴀʟʟᴏᴡᴇᴅ!",
                show_alert=True,
            )
    elif disconnect_match:
        disconnection_status = sql.disconnect(query.from_user.id)
        if disconnection_status:
            sql.disconnected_chat = await query.message.edit_text(
                "ᴅɪsᴄᴏɴɴᴇᴄᴛᴇᴅ ғʀᴏᴍ ᴄʜᴀᴛ!"
            )
        else:
            await context.bot.answer_callback_query(
                query.id,
                "ʏᴏᴜ'ʀᴇ ɴᴏᴛ ᴄᴏɴɴᴇᴄᴛᴇᴅ!",
                show_alert=True,
            )
    elif clear_match:
        sql.clear_history_conn(query.from_user.id)
        await query.message.edit_text("ʜɪsᴛᴏʀʏ ᴄᴏɴɴᴇᴄᴛᴇᴅ ʜᴀs ʙᴇᴇɴ ᴄʟᴇᴀʀᴇᴅ!")
    elif connect_close:
        await query.message.edit_text("ᴄʟᴏsᴇᴅ.\nᴛᴏ ᴏᴘᴇɴ ᴀɢᴀɪɴ, ᴛʏᴘᴇ /connect")
    else:
        connect_chat(update, context)


__help__ = """
sᴏᴍᴇᴛɪᴍᴇs ʏᴏᴜ ᴊᴜsᴛ ᴡᴀɴᴛ ᴛᴏ ᴀᴅᴅ sᴏᴍᴇ ɴᴏᴛᴇs ᴀɴᴅ ғɪʟᴛᴇʀs ᴛᴏ a ɢʀᴏᴜᴘ ᴄʜᴀᴛ, ʙᴜᴛ ʏᴏᴜ ᴅᴏɴ'ᴛ ᴡᴀɴᴛ ᴇᴠᴇʀʏᴏɴᴇ ᴛᴏ sᴇᴇ ᴛʜɪs ɪs ᴡʜᴇʀᴇ ᴄᴏɴɴᴇᴄᴛɪᴏɴs ᴄᴏᴍᴇ ɪɴ...
ᴛʜɪs ᴀʟʟᴏᴡs ʏᴏᴜ ᴛᴏ ᴄᴏɴɴᴇᴄᴛ ᴛᴏ ᴀ ᴄʜᴀᴛ's ᴅᴀᴛᴀʙᴀsᴇ, ᴀɴᴅ ᴀᴅᴅ ᴛʜɪɴɢs ᴛᴏ ɪᴛ ᴡɪᴛʜᴏᴜᴛ ᴛʜᴇ ᴄᴏᴍᴍᴀɴᴅs ᴀᴘᴘᴇᴀʀɪɴɢ ɪɴ ᴄʜᴀᴛ! ғᴏʀ ᴏʙᴠɪᴏᴜs ʀᴇᴀsᴏɴs, ʏᴏᴜ ɴᴇᴇᴅ ᴛᴏ ʙᴇ ᴀɴ ᴀᴅᴍɪɴ ᴛᴏ ᴀᴅᴅ ᴛʜɪɴɢs; ʙᴜᴛ ᴀɴʏ ᴍᴇᴍʙᴇʀ ɪɴ ᴛʜᴇ ɢʀᴏᴜᴘ ᴄᴀɴ ᴠɪᴇᴡ ʏᴏᴜʀ ᴅᴀᴛᴀ.

• /connect: ᴄᴏɴɴᴇᴄᴛs ᴛᴏ ᴄʜᴀᴛ ᴄᴀɴ ʙᴇ ᴅᴏɴᴇ ɪɴ ᴀ ɢʀᴏᴜᴘ ʙʏ /connect ᴏʀ /connect <chat id> ɪɴ ᴘᴍ
• /connection: ʟɪsᴛ ᴄᴏɴɴᴇᴄᴛᴇᴅ ᴄʜᴀᴛs
• /disconnect: ᴅɪsᴄᴏɴɴᴇᴄᴛ ғʀᴏᴍ ᴀ ᴄʜᴀᴛ
• /helpconnect: ʟɪsᴛ ᴀᴠᴀɪʟᴀʙʟᴇ ᴄᴏᴍᴍᴀɴᴅs ᴛʜᴀᴛ ᴄᴀɴ ʙᴇ ᴜsᴇᴅ ʀᴇᴍᴏᴛᴇʟʏ

*ᴀᴅᴍɪɴ ᴏɴʟʏ:*
• /allowconnect <ʏᴇs/ɴᴏ>: ᴀʟʟᴏᴡ ᴀ ᴜsᴇʀ ᴛᴏ ᴄᴏɴɴᴇᴄᴛ ᴛᴏ ᴀ ᴄʜᴀᴛ
"""


__mod_name__ = "𝐂ᴏɴɴᴇᴄᴛ"


CONNECT_CHAT_HANDLER = CommandHandler("connect", connect_chat)
CONNECTION_CHAT_HANDLER = CommandHandler("connection", connection_chat)
DISCONNECT_CHAT_HANDLER = CommandHandler("disconnect", disconnect_chat)
ALLOW_CONNECTIONS_HANDLER = CommandHandler("allowconnect", allow_connections)
HELP_CONNECT_CHAT_HANDLER = CommandHandler("helpconnect", help_connect_chat)
CONNECT_BTN_HANDLER = CallbackQueryHandler(connect_button, pattern=r"connect")

exon.add_handler(CONNECT_CHAT_HANDLER)
exon.add_handler(CONNECTION_CHAT_HANDLER)
exon.add_handler(DISCONNECT_CHAT_HANDLER)
exon.add_handler(ALLOW_CONNECTIONS_HANDLER)
exon.add_handler(HELP_CONNECT_CHAT_HANDLER)
exon.add_handler(CONNECT_BTN_HANDLER)
