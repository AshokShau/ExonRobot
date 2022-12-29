import html

from telegram import ChatMemberAdministrator, Update
from telegram.constants import ParseMode
from telegram.ext import CommandHandler, ContextTypes, MessageHandler, filters

from Exon import ALLOW_EXCL, CustomCommandHandler, application
from Exon.modules.disable import DisableAbleCommandHandler
from Exon.modules.helper_funcs.chat_status import check_admin, connection_status
from Exon.modules.sql import cleaner_sql as sql

CMD_STARTERS = ("/", "!", ".", "+", "-", "*", "^") if ALLOW_EXCL else "/"
BLUE_TEXT_CLEAN_GROUP = 13
CommandHandlerList = (CommandHandler, CustomCommandHandler, DisableAbleCommandHandler)
command_list = [
    "cleanblue",
    "ignoreblue",
    "unignoreblue",
    "listblue",
    "ungignoreblue",
    "gignoreblue" "start",
    "help",
    "settings",
    "donate",
    "stalk",
    "aka",
    "leaderboard",
]


for handler_list in application.handlers:
    for handler in application.handlers[handler_list]:
        if any(isinstance(handler, cmd_handler) for cmd_handler in CommandHandlerList):
            command_list += handler.commands


async def clean_blue_text_must_click(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    bot = context.bot
    chat = update.effective_chat
    message = update.effective_message
    member = await chat.get_member(bot.id)

    if isinstance(member, ChatMemberAdministrator):
        if (
            member.can_delete_messages
            if isinstance(member, ChatMemberAdministrator)
            else None
        ) and sql.is_enabled(chat.id):
            fst_word = message.text.strip().split(None, 1)[0]

            if len(fst_word) > 1 and any(
                fst_word.startswith(start) for start in CMD_STARTERS
            ):

                command = fst_word[1:].split("@")
                chat = update.effective_chat

                ignored = sql.is_command_ignored(chat.id, command[0])
                if ignored:
                    return

                if command[0] not in command_list:
                    await message.delete()


@connection_status
@check_admin(permission="can_delete_messages", is_both=True)
async def set_blue_text_must_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    message = update.effective_message
    bot, args = context.bot, context.args
    if len(args) >= 1:
        val = args[0].lower()
        if val in ("off", "no"):
            sql.set_cleanbt(chat.id, False)
            reply = "ʙʟᴜᴇᴛᴇxᴛ ᴄʟᴇᴀɴɪɴɢ ʜᴀs ʙᴇᴇɴ ᴅɪsᴀʙʟᴇᴅ ғᴏʀ <b>{}</b>".format(
                html.escape(chat.title),
            )
            await message.reply_text(reply, parse_mode=ParseMode.HTML)

        elif val in ("yes", "on"):
            sql.set_cleanbt(chat.id, True)
            reply = "ʙʟᴜᴇᴛᴇxᴛ ᴄʟᴇᴀɴɪɴɢ ʜᴀs ʙᴇᴇɴ ᴇɴᴀʙʟᴇᴅ ғᴏʀ <b>{}</b>".format(
                html.escape(chat.title),
            )
            await message.reply_text(reply, parse_mode=ParseMode.HTML)

        else:
            reply = "ɪɴᴠᴀʟɪᴅ ᴀʀɢᴜᴍᴇɴᴛ.ᴀᴄᴄᴇᴘᴛᴇᴅ ᴠᴀʟᴜᴇs ᴀʀᴇ 'yes', 'on', 'no', 'off'"
            await message.reply_text(reply)
    else:
        clean_status = sql.is_enabled(chat.id)
        clean_status = "Enabled" if clean_status else "Disabled"
        reply = "ʙʟᴜᴇᴛᴇxᴛ ᴄʟᴇᴀɴɪɴɢ ғᴏʀ <b>{}</b> : <b>{}</b>".format(
            html.escape(chat.title),
            clean_status,
        )
        await message.reply_text(reply, parse_mode=ParseMode.HTML)


@check_admin(is_user=True)
async def add_bluetext_ignore(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.effective_message
    chat = update.effective_chat
    args = context.args
    if len(args) >= 1:
        val = args[0].lower()
        added = sql.chat_ignore_command(chat.id, val)
        if added:
            reply = "<b>{}</b> ʜᴀs ʙᴇᴇɴ ᴀᴅᴅᴇᴅ ᴛᴏ ʙʟᴜᴇᴛᴇxᴛ ᴄʟᴇᴀɴᴇʀ ɪɢɴᴏʀᴇ ʟɪsᴛ.".format(
                args[0],
            )
        else:
            reply = "ᴄᴏᴍᴍᴀɴᴅ ɪs ᴀʟʀᴇᴀᴅʏ ɪɢɴᴏʀᴇᴅ."
        await message.reply_text(reply, parse_mode=ParseMode.HTML)

    else:
        reply = "ɴᴏ ᴄᴏᴍᴍᴀɴᴅ sᴜᴘᴘʟɪᴇᴅ ᴛᴏ ʙᴇ ɪɢɴᴏʀᴇᴅ."
        await message.reply_text(reply)


@check_admin(is_user=True)
async def remove_bluetext_ignore(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.effective_message
    chat = update.effective_chat
    args = context.args
    if len(args) >= 1:
        val = args[0].lower()
        removed = sql.chat_unignore_command(chat.id, val)
        if removed:
            reply = (
                "<b>{}</b> ʜᴀs ʙᴇᴇɴ ʀᴇᴍᴏᴠᴇᴅ ғʀᴏᴍ ʙʟᴜᴇᴛᴇxᴛ ᴄʟᴇᴀɴᴇʀ ɪɢɴᴏʀᴇ ʟɪsᴛ.".format(
                    args[0],
                )
            )
        else:
            reply = "ᴄᴏᴍᴍᴀɴᴅ ɪsɴ'ᴛ ɪɢɴᴏʀᴇᴅ ᴄᴜʀʀᴇɴᴛʟʏ."
        await message.reply_text(reply, parse_mode=ParseMode.HTML)

    else:
        reply = "ɴᴏ ᴄᴏᴍᴍᴀɴᴅ sᴜᴘᴘʟɪᴇᴅ ᴛᴏ ʙᴇ ᴜɴɪɢɴᴏʀᴇᴅ."
        await message.reply_text(reply)


@check_admin(is_user=True)
async def add_bluetext_ignore_global(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    message = update.effective_message
    args = context.args
    if len(args) >= 1:
        val = args[0].lower()
        added = sql.global_ignore_command(val)
        if added:
            reply = "<b>{}</b> ʜᴀs ʙᴇᴇɴ ᴀᴅᴅᴇᴅ ᴛᴏ ɢʟᴏʙᴀʟ ʙʟᴜᴇᴛᴇxᴛ ᴄʟᴇᴀɴᴇʀ ɪɢɴᴏʀᴇ ʟɪsᴛ.".format(
                args[0],
            )
        else:
            reply = "ᴄᴏᴍᴍᴀɴᴅ ɪs ᴀʟʀᴇᴀᴅʏ ɪɢɴᴏʀᴇᴅ."
        await message.reply_text(reply, parse_mode=ParseMode.HTML)

    else:
        reply = "ɴᴏ ᴄᴏᴍᴍᴀɴᴅ sᴜᴘᴘʟɪᴇᴅ ᴛᴏ ʙᴇ ɪɢɴᴏʀᴇᴅ."
        await message.reply_text(reply)


@check_admin(only_dev=True)
async def remove_bluetext_ignore_global(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    message = update.effective_message
    args = context.args
    if len(args) >= 1:
        val = args[0].lower()
        removed = sql.global_unignore_command(val)
        if removed:
            reply = "<b>{}</b> ʜᴀs ʙᴇᴇɴ ʀᴇᴍᴏᴠᴇᴅ ғʀᴏᴍ ɢʟᴏʙᴀʟ ʙʟᴜᴇᴛᴇxᴛ ᴄʟᴇᴀɴᴇʀ ɪɢɴᴏʀᴇ ʟɪsᴛ.".format(
                args[0],
            )
        else:
            reply = "ᴄᴏᴍᴍᴀɴᴅ ɪsɴ'ᴛ ɪɢɴᴏʀᴇᴅ ᴄᴜʀʀᴇɴᴛʟʏ."
        await message.reply_text(reply, parse_mode=ParseMode.HTML)

    else:
        reply = "ɴᴏ ᴄᴏᴍᴍᴀɴᴅ sᴜᴘᴘʟɪᴇᴅ ᴛᴏ ʙᴇ ᴜɴɪɢɴᴏʀᴇᴅ."
        await message.reply_text(reply)


@check_admin(only_dev=True)
async def bluetext_ignore_list(update: Update, context: ContextTypes.DEFAULT_TYPE):

    message = update.effective_message
    chat = update.effective_chat

    global_ignored_list, local_ignore_list = sql.get_all_ignored(chat.id)
    text = ""

    if global_ignored_list:
        text = "ᴛʜᴇ ғᴏʟʟᴏᴡɪɴɢ ᴄᴏᴍᴍᴀɴᴅs ᴀʀᴇ ᴄᴜʀʀᴇɴᴛʟʏ ɪɢɴᴏʀᴇᴅ ɢʟᴏʙᴀʟʟʏ ғʀᴏᴍ ʙʟᴜᴇᴛᴇxᴛ ᴄʟᴇᴀɴɪɴɢ :\n"

        for x in global_ignored_list:
            text += f" - <code>{x}</code>\n"

    if local_ignore_list:
        text += "\nᴛʜᴇ ғᴏʟʟᴏᴡɪɴɢ ᴄᴏᴍᴍᴀɴᴅs ᴀʀᴇ ᴄᴜʀʀᴇɴᴛʟʏ ɪɢɴᴏʀᴇᴅ ʟᴏᴄᴀʟʟʏ ғʀᴏᴍ ʙʟᴜᴇᴛᴇxᴛ ᴄʟᴇᴀɴɪɴɢ :\n"

        for x in local_ignore_list:
            text += f" - <code>{x}</code>\n"

    if text == "":
        text = "ɴᴏ ᴄᴏᴍᴍᴀɴᴅs ᴀʀᴇ ᴄᴜʀʀᴇɴᴛʟʏ ɪɢɴᴏʀᴇᴅ ғʀᴏᴍ ʙʟᴜᴇᴛᴇxᴛ ᴄʟᴇᴀɴɪɴɢ."
        await message.reply_text(text)
        return

    await message.reply_text(text, parse_mode=ParseMode.HTML)
    return


__help__ = """
*ʙʟᴜᴇ ᴛᴇxᴛ ᴄʟᴇᴀɴᴇʀ ʀᴇᴍᴏᴠᴇᴅ ᴀɴʏ ᴍᴀᴅᴇ ᴜᴘ ᴄᴏᴍᴍᴀɴᴅs ᴛʜᴀᴛ ᴘᴇᴏᴘʟᴇ sᴇɴᴅ ɪɴ ʏᴏᴜʀ ᴄʜᴀᴛ.*

• /cleanblue <ᴏɴ/ᴏғғ/ʏᴇs/ɴᴏ>*:* ᴄʟᴇᴀɴ ᴄᴏᴍᴍᴀɴᴅs ᴀғᴛᴇʀ sᴇɴᴅɪɴɢ
• /ignoreblue <ᴡᴏʀᴅ>*:* ᴘʀᴇᴠᴇɴᴛ ᴀᴜᴛᴏ ᴄʟᴇᴀɴɪɴɢ ᴏғ ᴛʜᴇ ᴄᴏᴍᴍᴀɴᴅ
• /unignoreblue <ᴡᴏʀᴅ>*:* ʀᴇᴍᴏᴠᴇ ᴘʀᴇᴠᴇɴᴛ ᴀᴜᴛᴏ ᴄʟᴇᴀɴɪɴɢ ᴏғ ᴛʜᴇ ᴄᴏᴍᴍᴀɴᴅ
• /listblue*:* ʟɪsᴛ ᴄᴜʀʀᴇɴᴛʟʏ ᴡʜɪᴛᴇʟɪsᴛᴇᴅ ᴄᴏᴍᴍᴀɴᴅs

 *ғᴏʟʟᴏᴡɪɴɢ ᴀʀᴇ ᴅɪsᴀsᴛᴇʀs ᴏɴʟʏ ᴄᴏᴍᴍᴀɴᴅs, ᴀᴅᴍɪɴs ᴄᴀɴɴᴏᴛ ᴜsᴇ ᴛʜᴇsᴇ:*
 
 • /gignoreblue <ᴡᴏʀᴅ>*:* ɢʟᴏʙᴀʟʟʏ ɪɢɴᴏʀᴇᴀ ʙʟᴜᴇᴛᴇxᴛ ᴄʟᴇᴀɴɪɴɢ ᴏғ sᴀᴠᴇᴅ ᴡᴏʀᴅ ᴀᴄʀᴏss ᴢᴇʀᴏ ᴛᴡᴏ.
 • /ungignoreblue <ᴡᴏʀᴅ>*:* ʀᴇᴍᴏᴠᴇ sᴀɪᴅ ᴄᴏᴍᴍᴀɴᴅ ғʀᴏᴍ ɢʟᴏʙᴀʟ ᴄʟᴇᴀɴɪɴɢ ʟɪsᴛ
"""

SET_CLEAN_BLUE_TEXT_HANDLER = CommandHandler(
    "cleanblue", set_blue_text_must_click, block=False
)
ADD_CLEAN_BLUE_TEXT_HANDLER = CommandHandler(
    "ignoreblue", add_bluetext_ignore, block=False
)
REMOVE_CLEAN_BLUE_TEXT_HANDLER = CommandHandler(
    "unignoreblue", remove_bluetext_ignore, block=False
)
ADD_CLEAN_BLUE_TEXT_GLOBAL_HANDLER = CommandHandler(
    "gignoreblue", add_bluetext_ignore_global, block=False
)
REMOVE_CLEAN_BLUE_TEXT_GLOBAL_HANDLER = CommandHandler(
    "ungignoreblue", remove_bluetext_ignore_global, block=False
)
LIST_CLEAN_BLUE_TEXT_HANDLER = CommandHandler(
    "listblue", bluetext_ignore_list, block=False
)
CLEAN_BLUE_TEXT_HANDLER = MessageHandler(
    filters.COMMAND & filters.ChatType.GROUPS, clean_blue_text_must_click, block=False
)

application.add_handler(SET_CLEAN_BLUE_TEXT_HANDLER)
application.add_handler(ADD_CLEAN_BLUE_TEXT_HANDLER)
application.add_handler(REMOVE_CLEAN_BLUE_TEXT_HANDLER)
application.add_handler(ADD_CLEAN_BLUE_TEXT_GLOBAL_HANDLER)
application.add_handler(REMOVE_CLEAN_BLUE_TEXT_GLOBAL_HANDLER)
application.add_handler(LIST_CLEAN_BLUE_TEXT_HANDLER)
application.add_handler(CLEAN_BLUE_TEXT_HANDLER, BLUE_TEXT_CLEAN_GROUP)

__mod_name__ = "𝐂ʟᴇᴀɴ"
__handlers__ = [
    SET_CLEAN_BLUE_TEXT_HANDLER,
    ADD_CLEAN_BLUE_TEXT_HANDLER,
    REMOVE_CLEAN_BLUE_TEXT_HANDLER,
    ADD_CLEAN_BLUE_TEXT_GLOBAL_HANDLER,
    REMOVE_CLEAN_BLUE_TEXT_GLOBAL_HANDLER,
    LIST_CLEAN_BLUE_TEXT_HANDLER,
    (CLEAN_BLUE_TEXT_HANDLER, BLUE_TEXT_CLEAN_GROUP),
]
