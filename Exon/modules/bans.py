import html

from telegram import (
    ChatMemberAdministrator,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Update,
)
from telegram.constants import ParseMode
from telegram.error import BadRequest
from telegram.ext import CallbackQueryHandler, CommandHandler, ContextTypes, filters
from telegram.helpers import mention_html

from Exon import BAN_STICKER, DEV_USERS, DRAGONS, LOGGER, OWNER_ID, application, KICK_STICKER
from Exon.modules.disable import DisableAbleCommandHandler
from Exon.modules.helper_funcs.chat_status import (
    can_delete,
    check_admin,
    connection_status,
    is_user_admin,
    is_user_ban_protected,
    is_user_in_chat,
)
from Exon.modules.helper_funcs.extraction import extract_user_and_text
from Exon.modules.helper_funcs.misc import mention_username
from Exon.modules.helper_funcs.string_handling import extract_time
from Exon.modules.log_channel import gloggable, loggable


@connection_status
@loggable
@check_admin(permission="can_restrict_members", is_both=True)
async def ban(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    chat = update.effective_chat
    user = update.effective_user
    message = update.effective_message
    log_message = ""
    bot = context.bot
    args = context.args
    user_id, reason = await extract_user_and_text(message, context, args)

    member = await chat.get_member(user.id)
    SILENT = bool(True if message.text.startswith("/s") else False)

    # if update is coming from anonymous admin then send button and return.
    if message.from_user.id == 1087968824:

        if SILENT:
            await message.reply_text("ᴄᴜʀʀᴇɴᴛʟʏ /sban ᴡᴏɴ'ᴛ ᴡᴏʀᴋ ғᴏʀ ᴀɴᴏʏᴍᴏᴜs ᴀᴅᴍɪɴs.")
            return log_message
        # Need chat title to be forwarded on callback data to mention channel after banning.
        try:
            chat_title = message.reply_to_message.sender_chat.title
        except AttributeError:
            chat_title = None
        await update.effective_message.reply_text(
            text="ʏᴏᴜ ᴀʀᴇ ᴀɴ ᴀɴᴏɴʏᴍᴏᴜs ᴀᴅᴍɪɴ.",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text="ᴄʟɪᴄᴋ ᴛᴏ ᴘʀᴏᴠᴇ ᴀᴅᴍɪɴ.",
                            callback_data=f"bans_{chat.id}=ban={user_id}={reason}={chat_title}",
                        ),
                    ],
                ]
            ),
        )

        return log_message
    elif (
        not (
            (
                member.can_restrict_members
                if isinstance(member, ChatMemberAdministrator)
                else None
            )
            or member.status == "creator"
        )
        and user.id not in DRAGONS
    ):
        await update.effective_message.reply_text(
            "sᴏʀʀʏ sᴏɴ, ʙᴜᴛ ʏᴏᴜ'ʀᴇ ɴᴏᴛ ᴡᴏʀᴛʜʏ ᴛᴏ ᴡɪᴇʟᴅ ᴛʜᴇ ʙᴀɴʜᴀᴍᴍᴇʀ.",
        )
        return log_message

    if user_id == bot.id:
        await message.reply_text("ᴏʜ ʏᴇᴀʜ, ʙᴀɴ ᴍʏsᴇʟғ, ɴᴏᴏʙ!")
        return log_message

    if user_id is not None and user_id < 0:
        CHAT_SENDER = True
        chat_sender = message.reply_to_message.sender_chat
    else:
        CHAT_SENDER = False
        try:
            member = await chat.get_member(user_id)
        except BadRequest as excp:
            if excp.message == "User not found":
                raise
            elif excp == "Invalid user_id specified":
                await message.reply_text("I ᴅᴏᴜʙᴛ ᴛʜᴀᴛ's ᴀ ᴜsᴇʀ.")
            await message.reply_text("ᴄᴀɴ'ᴛ ғɪɴᴅ ᴛʜɪs ᴘᴇʀsᴏɴ ʜᴇʀᴇ.")
            return log_message

        if await is_user_ban_protected(chat, user_id, member) and user not in DEV_USERS:
            if user_id == OWNER_ID:
                await message.reply_text(
                    "ᴛʀʏɪɴɢ ᴛᴏ ᴘᴜᴛ ᴍᴇ ᴀɢᴀɪɴsᴛ ᴀ ɢᴏᴅ ʟᴇᴠᴇʟ ᴅɪsᴀsᴛᴇʀ ʜᴜʜ?"
                )
            elif user_id in DEV_USERS:
                await message.reply_text("I ᴄᴀɴ'ᴛ ᴀᴄᴛ ᴀɢᴀɪɴsᴛ ᴏᴜʀ ᴏᴡɴ.")
            elif user_id in DRAGONS:
                await message.reply_text(
                    "ғɪɢʜᴛɪɴɢ ᴛʜɪs ᴅʀᴀɢᴏɴ ʜᴇʀᴇ ᴡɪʟʟ ᴘᴜᴛ ᴍᴇ ᴀɴᴅ ᴍʏ ᴘᴇᴏᴘʟᴇ's ᴀᴛ ʀɪsᴋ.",
                )
            else:
                await message.reply_text("ᴛʜɪs ᴜsᴇʀ ʜᴀs ɪᴍᴍᴜɴɪᴛʏ ᴀɴᴅ ᴄᴀɴɴᴏᴛ ʙᴇ ʙᴀɴɴᴇᴅ.")
            return log_message

    if SILENT:
        silent = True
        if not await can_delete(chat, context.bot.id):
            return ""
    else:
        silent = False

    log = (
        f"<b>{html.escape(chat.title)}:</b>\n"
        f"#{'S' if silent else ''} _𝐁𝐀𝐍𝐍𝐄𝐃\n"
        f"<b>ᴀᴅᴍɪɴ:</b> {mention_html(user.id, html.escape(user.first_name))}\n"
    )

    reply = f"<code>❕</code><b>ʙᴀɴ ᴇᴠᴇɴᴛ</b>\n"

    if CHAT_SENDER:
        log += f"<b>ᴄʜᴀɴɴᴇʟ:</b> {mention_username(chat_sender.username, html.escape(chat_sender.title))}"
        reply += f"<code> </code><b>• ᴄʜᴀɴɴᴇʟ:</b> {mention_username(chat_sender.username, html.escape(chat_sender.title))}"

    else:
        log += f"<b>ᴜsᴇʀ:</b> {mention_html(member.user.id, html.escape(member.user.first_name))}"
        reply += f"<code> </code><b>•  User:</b> {mention_html(member.user.id, html.escape(member.user.first_name))}"

    if reason:
        log += "\n<b>ʀᴇᴀsᴏɴ:</b> {}".format(reason)

    try:
        if CHAT_SENDER:
            await chat.ban_sender_chat(sender_chat_id=chat_sender.id)
        else:
            await chat.ban_member(user_id)

        if silent:
            if message.reply_to_message:
                await message.reply_to_message.delete()
            await message.delete()
            return log

        await bot.send_sticker(
            chat.id,
            BAN_STICKER,
            message_thread_id=message.message_thread_id if chat.is_forum else None,
        )  # banhammer marie sticker

        if reason:
            reply += f"\n<code> </code><b>• ʀᴇᴀsᴏɴ:</b> \n{html.escape(reason)}"
        await bot.sendMessage(
            chat.id,
            reply,
            parse_mode=ParseMode.HTML,
            message_thread_id=message.message_thread_id if chat.is_forum else None,
        )
        return log

    except BadRequest as excp:
        if excp.message == "ʀᴇᴘʟʏ ᴍᴇssᴀɢᴇ ɴᴏᴛ ғᴏᴜɴᴅ":
            # Do not reply
            if silent:
                return log
            await message.reply_text("ʙᴀɴɴᴇᴅ!", quote=False)
            return log
        else:
            LOGGER.warning(update)
            LOGGER.exception(
                "ᴇʀʀᴏʀ ʙᴀɴɴɪɴɢ ᴜsᴇʀ %s ɪɴ ᴄʜᴀᴛ %s (%s) ᴅᴜᴇ ᴛᴏ %s",
                user_id,
                chat.title,
                chat.id,
                excp.message,
            )
            await message.reply_text("ᴜʜᴍ...ᴛʜᴀᴛ ᴅɪᴅɴ'ᴛ ᴡᴏʀᴋ...")

    return log_message


@connection_status
@loggable
@check_admin(permission="can_restrict_members", is_both=True)
async def temp_ban(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    chat = update.effective_chat
    user = update.effective_user
    message = update.effective_message
    log_message = ""
    bot, args = context.bot, context.args
    user_id, reason = await extract_user_and_text(message, context, args)

    if not user_id:
        await message.reply_text("I ᴅᴏᴜʙᴛ ᴛʜᴀᴛ's ᴀ ᴜsᴇʀ.")
        return log_message

    try:
        member = await chat.get_member(user_id)
    except BadRequest as excp:
        if excp.message != "User not found":
            raise
        await message.reply_text("I ᴄᴀɴ'ᴛ sᴇᴇᴍ ᴛᴏ ғɪɴᴅ ᴛʜɪs ᴜsᴇʀ.")
        return log_message
    if user_id == bot.id:
        await message.reply_text("I'm ɴᴏᴛ ɢᴏɴɴᴀ ʙᴀɴ ᴍʏsᴇʟғ, ᴀʀᴇ ʏᴏᴜ ᴄʀᴀᴢʏ?")
        return log_message

    if await is_user_ban_protected(chat, user_id, member):
        await message.reply_text("I ᴅᴏɴ'ᴛ ғᴇᴇʟ ʟɪᴋᴇ ɪᴛ.")
        return log_message

    if not reason:
        await message.reply_text("ʏᴏᴜ ʜᴀᴠᴇɴ'ᴛ sᴘᴇᴄɪғɪᴇᴅ ᴀ ᴛɪᴍᴇ ᴛᴏ ʙᴀɴ ᴛʜɪs ᴜsᴇʀ ғᴏʀ!")
        return log_message

    split_reason = reason.split(None, 1)

    time_val = split_reason[0].lower()
    reason = split_reason[1] if len(split_reason) > 1 else ""
    bantime = await extract_time(message, time_val)

    if not bantime:
        return log_message

    log = (
        f"<b>{html.escape(chat.title)}:</b>\n"
        "#𝐓𝐄𝐌𝐏 𝐁𝐀𝐍𝐍𝐄𝐃\n"
        f"<b>ᴀᴅᴍɪɴ:</b> {mention_html(user.id, html.escape(user.first_name))}\n"
        f"<b>ᴜsᴇʀ:</b> {mention_html(member.user.id, html.escape(member.user.first_name))}\n"
        f"<b>ᴛɪᴍᴇ:</b> {time_val}"
    )
    if reason:
        log += "\n<b>ʀᴇᴀsᴏɴ:</b> {}".format(reason)

    try:
        await chat.ban_member(user_id, until_date=bantime)
        await bot.send_sticker(
            chat.id,
            BAN_STICKER,
            message_thread_id=message.message_thread_id if chat.is_forum else None,
        )  # banhammer marie sticker
        await bot.sendMessage(
            chat.id,
            f"ʙᴀɴɴᴇᴅ! ᴜsᴇʀ {mention_html(member.user.id, html.escape(member.user.first_name))} "
            f"ᴡɪʟʟ ʙᴇ ʙᴀɴɴᴇᴅ ғᴏʀ {time_val}.",
            parse_mode=ParseMode.HTML,
            message_thread_id=message.message_thread_id if chat.is_forum else None,
        )
        return log

    except BadRequest as excp:
        if excp.message == "ʀᴇᴘʟʏ ᴍᴇssᴀɢᴇ ɴᴏᴛ ғᴏᴜɴᴅ":
            # Do not reply
            await message.reply_text(
                f"ʙᴀɴɴᴇᴅ! ᴜsᴇʀ ᴡɪʟʟ ʙᴇ ʙᴀɴɴᴇᴅ ғᴏʀ {time_val}.",
                quote=False,
            )
            return log
        else:
            LOGGER.warning(update)
            LOGGER.exception(
                "ᴇʀʀᴏʀ ʙᴀɴɴɪɴɢ ᴜsᴇʀ %s ɪɴ ᴄʜᴀᴛ %s (%s) ᴅᴜᴇ ᴛᴏ %s",
                user_id,
                chat.title,
                chat.id,
                excp.message,
            )
            await message.reply_text("ᴡᴇʟʟ ᴅᴀᴍɴ, I ᴄᴀɴ'ᴛ ʙᴀɴ ᴛʜᴀᴛ ᴜsᴇʀ.")

    return log_message


@connection_status
@loggable
@check_admin(permission="can_restrict_members", is_both=True)
async def kick(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    chat = update.effective_chat
    user = update.effective_user
    message = update.effective_message
    log_message = ""
    bot, args = context.bot, context.args
    user_id, reason = await extract_user_and_text(message, context, args)

    if not user_id:
        await message.reply_text("I ᴅᴏᴜʙᴛ ᴛʜᴀᴛ's  ᴜsᴇʀ.")
        return log_message

    try:
        member = await chat.get_member(user_id)
    except BadRequest as excp:
        if excp.message != "ᴜsᴇʀ ɴᴏᴛ ғᴏᴜɴᴅ":
            raise

        await message.reply_text("I ᴄᴀɴ'ᴛ sᴇᴇᴍ ᴛᴏ ғɪɴᴅ ᴛʜɪs ᴜsᴇʀ.")
        return log_message
    if user_id == bot.id:
        await message.reply_text("ʏᴇᴀʜʜʜ I'ᴍ ɴᴏᴛ ɢᴏɴɴᴀ ᴅᴏ ᴛʜᴀᴛ.")
        return log_message

    if await is_user_ban_protected(chat, user_id):
        await message.reply_text("I ʀᴇᴀʟʟʏ ᴡɪsʜ ɪ ᴄᴏᴜʟᴅ ᴋɪᴄᴋ ᴛʜɪs ᴜsᴇʀ....")
        return log_message

    res = chat.unban_member(user_id)  # unban on current user = kick
    if res:
        await bot.send_sticker(
            chat.id,
            KICK_STICKER,
            message_thread_id=message.message_thread_id if chat.is_forum else None,
        )  # banhammer marie sticker
        await bot.sendMessage(
            chat.id,
            f"ᴄᴀᴘɪᴛᴀɪɴ I ʜᴀᴠᴇ ᴋɪᴄᴋᴇᴅ, {mention_html(member.user.id, html.escape(member.user.first_name))}.",
            parse_mode=ParseMode.HTML,
            message_thread_id=message.message_thread_id if chat.is_forum else None,
        )
        log = (
            f"<b>{html.escape(chat.title)}:</b>\n"
            f"#𝐊𝐈𝐂𝐊𝐄𝐃\n"
            f"<b>ᴀᴅᴍɪɴ:</b> {mention_html(user.id, html.escape(user.first_name))}\n"
            f"<b>ᴜsᴇʀ:</b> {mention_html(member.user.id, html.escape(member.user.first_name))}"
        )
        if reason:
            log += f"\n<b>ʀᴇᴀsᴏɴ:</b> {reason}"

        return log

    else:
        await message.reply_text("ᴡᴇʟʟ ᴅᴀᴍɴ, I ᴄᴀɴ'ᴛ ᴋɪᴄᴋ ᴛʜᴀᴛ ᴜsᴇʀ.")

    return log_message


@check_admin(permission="can_restrict_members", is_bot=True)
async def kickme(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_message.from_user.id
    if await is_user_admin(update.effective_chat, user_id):
        await update.effective_message.reply_text(
            "I ᴡɪsʜ ɪ ᴄᴏᴜʟᴅ... ʙᴜᴛ ʏᴏᴜ'ʀᴇ ᴀɴ ᴀᴅᴍɪɴ."
        )
        return

    res = await update.effective_chat.unban_member(
        user_id
    )  # unban on current user = kick
    # BUG: parsing not working
    if res:
        await update.effective_message.reply_text(
            html.escape("ʏᴏᴜ ɢᴏᴛ ᴛʜᴇ ᴅᴇᴠɪʟ's ᴋɪss, ɴᴏᴡ ᴅɪᴇ ɪɴ ᴘᴇᴀᴄᴇ"), parse_mode="html"
        )
    else:
        await update.effective_message.reply_text("ʜᴜʜ? I ᴄᴀɴ'ᴛ :/")


@connection_status
@loggable
@check_admin(permission="can_restrict_members", is_both=True)
async def unban(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    message = update.effective_message
    user = update.effective_user
    chat = update.effective_chat
    log_message = ""
    bot, args = context.bot, context.args
    user_id, reason = await extract_user_and_text(message, context, args)

    if message.from_user.id == 1087968824:
        try:
            chat_title = message.reply_to_message.sender_chat.title
        except AttributeError:
            chat_title = None

        await message.reply_text(
            text="ʏᴏᴜ ᴀʀᴇ ᴀɴ ᴀɴᴏɴʏᴍᴏᴜs ᴀᴅᴍɪɴ.",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text="ᴄʟɪᴄᴋ ᴛᴏ ᴘʀᴏᴠᴇ ᴀᴅᴍɪɴ.",
                            callback_data=f"bans_{chat.id}=unban={user_id}={reason}={chat_title}",
                        ),
                    ],
                ]
            ),
        )

        return log_message

    if not user_id:
        await message.reply_text("I ᴅᴏᴜʙᴛ ᴛʜᴀᴛ's ᴀ user.")
        return log_message

    if user_id == bot.id:
        await message.reply_text(
            "ʜᴏᴡ ᴡᴏᴜʟᴅ I ᴜɴʙᴀɴ ᴍʏsᴇʟғ ɪғ ɪ ᴡᴀsɴ'ᴛ ʜᴇʀᴇ ᴡᴛғ ʙᴀʙʏ...?"
        )
        return log_message

    if user_id is not None and user_id < 0:
        CHAT_SENDER = True
        chat_sender = message.reply_to_message.sender_chat
    else:
        CHAT_SENDER = False
        try:
            member = await chat.get_member(user_id)

            if isinstance(member, ChatMemberAdministrator):
                await message.reply_text(
                    "ᴛʜɪs ᴘᴇʀsᴏɴ ɪs ᴀɴ ᴀᴅᴍɪɴ ʜᴇʀᴇ, ᴀʀᴇ ʏᴏᴜ ᴅʀᴜɴᴋ???"
                )
                return log_message

        except BadRequest as excp:
            raise
            if excp.message != "User not found":
                ʀᴀɪsᴇ
            await message.reply_text("I ᴄᴀɴ'ᴛ sᴇᴇᴍ ᴛᴏ ғɪɴᴅ ᴛʜɪs ᴜsᴇʀ.")
            return log_message

        if await is_user_in_chat(chat, user_id):
            await message.reply_text("ɪsɴ'ᴛ ᴛʜɪs ᴘᴇʀsᴏɴ ᴀʟʀᴇᴀᴅʏ ʜᴇʀᴇ??")
            return log_message

    log = (
        f"<b>{html.escape(chat.title)}:</b>\n"
        f"#𝐔𝐍𝐁𝐀𝐍𝐍𝐄𝐃\n"
        f"<b>ᴀᴅᴍɪɴ:</b> {mention_html(user.id, html.escape(user.first_name))}\n"
    )

    if CHAT_SENDER:
        log += f"<b>ᴜsᴇʀ:</b> {mention_username(chat_sender.id, html.escape(chat_sender.title))}"
        await chat.unban_sender_chat(chat_sender.id)
        await message.reply_text("ʏᴇᴀʜ, ᴛʜɪs ᴄʜᴀɴɴᴇʟ ᴄᴀɴ sᴘᴇᴀᴋ ᴀɢᴀɪɴ.")
    else:
        log += f"<b>ᴜsᴇʀ:</b> {mention_html(member.user.id, html.escape(member.user.first_name))}"
        await chat.unban_member(user_id)
        await message.reply_text("ʏᴇᴀʜ, ᴛʜɪs ᴜsᴇʀ ᴄᴀɴ ᴊᴏɪɴ!")

    if reason:
        log += f"\n<b>ʀᴇᴀsᴏɴ:</b> {reason}"

    return log


@connection_status
@gloggable
@check_admin(permission="can_restrict_members", is_bot=True)
async def selfunban(context: ContextTypes.DEFAULT_TYPE, update: Update) -> str:
    message = update.effective_message
    user = update.effective_user
    bot, args = context.bot, context.args
    if user.id not in DRAGONS:
        return

    try:
        chat_id = int(args[0])
    except:
        await message.reply_text("ɢɪᴠᴇ ᴀ ᴠᴀʟɪᴅ ᴄʜᴀᴛ ɪᴅ.")
        return

    chat = await bot.getChat(chat_id)

    try:
        member = await chat.get_member(user.id)
    except BadRequest as excp:
        if excp.message == "ᴜsᴇʀ ɴᴏᴛ ғᴏᴜɴᴅ":
            await message.reply_text("I ᴄᴀɴ'ᴛ sᴇᴇᴍ ᴛᴏ ғɪɴᴅ ᴛʜɪs ᴜsᴇʀ.")
            return
        else:
            raise

    if await is_user_in_chat(chat, user.id):
        await message.reply_text("ᴀʀᴇɴ'ᴛ ʏᴏᴜ ᴀʟʀᴇᴀᴅʏ ɪɴ ᴛʜᴇ ᴄʜᴀᴛ??")
        return

    await chat.unban_member(user.id)
    await message.reply_text("ʏᴇᴘ, ɪ ʜᴀᴠᴇ ᴜɴʙᴀɴɴᴇᴅ ʏᴏᴜ.")

    log = (
        f"<b>{html.escape(chat.title)}:</b>\n"
        f"#𝐔𝐍𝐁𝐀𝐍𝐍𝐄𝐃\n"
        f"<b>ᴜsᴇʀ:</b> {mention_html(member.user.id, html.escape(member.user.first_name))}"
    )

    return log


@loggable
async def bans_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    bot = context.bot
    chat = update.effective_chat
    message = update.effective_message
    context.args
    log_message = ""
    splitter = query.data.replace("bans_", "").split("=")

    admin_user = query.from_user
    member = await chat.get_member(admin_user.id)

    if splitter[1] == "ban":
        # workaround for checking user admin status
        try:
            user_id = int(splitter[2])
        except ValueError:
            user_id = splitter[2]
        reason = splitter[3]
        chat_name = splitter[4]

        if not (
            (
                member.can_restrict_members
                if isinstance(member, ChatMemberAdministrator)
                else None
            )
            or member.status == "creator"
        ) and (admin_user.id not in DRAGONS):
            await query.answer(
                "sᴏʀʀʏ sᴏɴ, ʙᴜᴛ ʏᴏᴜ'ʀᴇ ɴᴏᴛ ᴡᴏʀᴛʜʏ ᴛᴏ ᴡɪᴇʟᴅ ᴛʜᴇ ʙᴀɴʜᴀᴍᴍᴇʀ.",
                show_alert=True,
            )
            return log_message

        if user_id == bot.id:
            await message.edit_text("ᴏʜ ʏᴇᴀʜ, ʙᴀɴ ᴍʏsᴇʟғ, ɴᴏᴏʙ!")
            return log_message

        if isinstance(user_id, str):
            await message.edit_text("I ᴅᴏᴜʙᴛ ᴛʜᴀᴛ's ᴀ ᴜsᴇʀ.")
            return log_message

        if user_id < 0:
            CHAT_SENDER = True
        else:
            CHAT_SENDER = False
            try:
                member = await chat.get_member(user_id)
            except BadRequest as excp:
                if excp.message == "ᴜsᴇʀ ɴᴏᴛ ғᴏᴜɴᴅ.":
                    raise
                elif excp == "Invalid user_id specified":
                    await message.edit_text("I ᴅᴏᴜʙᴛ ᴛʜᴀᴛ's ᴀ ᴜsᴇʀ.")
                await message.edit_text("ᴄᴀɴ'ᴛ ғɪɴᴅ ᴛʜɪs ᴘᴇʀsᴏɴ ʜᴇʀᴇ.")

                return log_message

            if (
                await is_user_ban_protected(chat, user_id, member)
                and admin_user not in DEV_USERS
            ):
                if user_id == OWNER_ID:
                    await message.edit_text(
                        "ᴛʀʏɪɴɢ ᴛᴏ ᴘᴜᴛ ᴍᴇ ᴀɢᴀɪɴsᴛ ᴀ ɢᴏᴅ ʟᴇᴠᴇʟ ᴅɪsᴀsᴛᴇʀ ʜᴜʜ?"
                    )
                elif user_id in DEV_USERS:
                    await message.edit_text("I ᴄᴀɴ'ᴛ ᴀᴄᴛ ᴀɢᴀɪɴsᴛ ᴏᴜʀ own.")
                elif user_id in DRAGONS:
                    await message.edit_text(
                        "ғɪɢʜᴛɪɴɢ ᴛʜɪs ᴅʀᴀɢᴏɴ ʜᴇʀᴇ ᴡɪʟʟ ᴘᴜᴛ ᴍᴇ ᴀɴᴅ ᴍʏ ᴘᴇᴏᴘʟᴇ's ᴀᴛ ʀɪsᴋ.",
                    )
                else:
                    await message.edit_text(
                        "ᴛʜɪs ᴜsᴇʀ ʜᴀs ɪᴍᴍᴜɴɪᴛʏ ᴀɴᴅ ᴄᴀɴɴᴏᴛ ʙᴇ ʙᴀɴɴᴇᴅ."
                    )
                return log_message

        log = (
            f"<b>{html.escape(chat.title)}:</b>\n"
            f"#𝐁𝐀𝐍𝐍𝐄𝐃\n"
            f"<b>ᴀᴅᴍɪɴ:</b> {mention_html(admin_user.id, html.escape(admin_user.first_name))}\n"
        )

        reply = f"<code>❕</code><b>ʙᴀɴ ᴇᴠᴇɴᴛ</b>\n"

        if CHAT_SENDER:
            log += f"<b>ᴄʜᴀɴɴᴇʟ:</b> {html.escape(chat_name)}"
            reply += f"<code> </code><b>•  Channel:</b> {html.escape(chat_name)}"

        else:
            log += f"<b>ᴜsᴇʀ:</b> {mention_html(member.user.id, html.escape(member.user.first_name))}"
            reply += f"<code> </code><b>•  User:</b> {mention_html(member.user.id, html.escape(member.user.first_name))}"

        if reason:
            log += "\n<b>ʀᴇᴀsᴏɴ:</b> {}".format(reason)

        try:
            if CHAT_SENDER:
                await chat.ban_sender_chat(sender_chat_id=user_id)
            else:
                await chat.ban_member(user_id)

            await bot.send_sticker(
                chat.id,
                BAN_STICKER,
                message_thread_id=message.message_thread_id if chat.is_forum else None,
            )  # banhammer marie sticker

            if reason:
                reply += f"\n<code> </code><b>• ʀᴇᴀsᴏɴ:</b> \n{html.escape(reason)}"
            await bot.sendMessage(
                chat.id,
                reply,
                parse_mode=ParseMode.HTML,
                message_thread_id=message.message_thread_id if chat.is_forum else None,
            )
            await query.answer(f"ᴅᴏɴᴇ ʙᴀɴɴᴇᴅ ᴜsᴇʀ.")
            return log

        except BadRequest as excp:
            if excp.message == "ʀᴇᴘʟʏ ᴍᴇssᴀɢᴇ ɴᴏᴛ ғᴏᴜɴᴅ":
                # Do not reply
                await message.edit_text("ʙᴀɴɴᴇᴅ!")
                return log
            else:
                LOGGER.warning(update)
                LOGGER.exception(
                    "ᴇʀʀᴏʀ ʙᴀɴɴɪɴɢ ᴜsᴇʀ %s ɪɴ ᴄʜᴀᴛ %s (%s) ᴅᴜᴇ ᴛᴏ %s",
                    user_id,
                    chat.title,
                    chat.id,
                    excp.message,
                )
                await message.edit_text("ᴜʜᴍ...ᴛʜᴀᴛ ᴅɪᴅɴ'ᴛ ᴡᴏʀᴋ...")

        return log_message

    elif splitter[1] == "unban":
        try:
            user_id = int(splitter[2])
        except ValueError:
            user_id = splitter[2]
        reason = splitter[3]

        if isinstance(user_id, str):
            await message.edit_text("I ᴅᴏᴜʙᴛ ᴛʜᴀᴛ's ᴀ ᴜsᴇʀ.")
            return log_message

        if user_id == bot.id:
            await message.edit_text("ʜᴏᴡ ᴡᴏᴜʟᴅ ɪ ᴜɴʙᴀɴ ᴍʏsᴇʟғ ɪғ ɪ ᴡᴀsɴ'ᴛ ʜᴇʀᴇ...?")
            return log_message

        if user_id < 0:
            CHAT_SENDER = True
            chat_title = splitter[4]
        else:
            CHAT_SENDER = False

            try:
                member = await chat.get_member(user_id)
            except BadRequest as excp:
                if excp.message != "User not found":
                    raise
                await message.edit_text("I ᴄᴀɴ'ᴛ sᴇᴇᴍ ᴛᴏ ғɪɴᴅ ᴛʜɪs ᴜsᴇʀ.")
                return log_message

            if await is_user_in_chat(chat, user_id):
                await message.edit_text("ɪsɴ'ᴛ ᴛʜɪs ᴘᴇʀsᴏɴ ᴀʟʀᴇᴀᴅʏ ʜᴇʀᴇ??")
                return log_message

        log = (
            f"<b>{html.escape(chat.title)}:</b>\n"
            f"#𝐔𝐍𝐁𝐀𝐍𝐍𝐄𝐃\n"
            f"<b>ᴀᴅᴍɪɴ:</b> {mention_html(admin_user.id, html.escape(admin_user.first_name))}\n"
        )

        if CHAT_SENDER:
            log += f"<b>ᴜsᴇʀ:</b> {html.escape(chat_title)}"
            await chat.unban_sender_chat(user_id)
            await message.reply_text("ʏᴇᴀʜ, ᴛʜɪs ᴄʜᴀɴɴᴇʟ ᴄᴀɴ sᴘᴇᴀᴋ ᴀɢᴀɪɴ.")
        else:
            log += f"<b>ᴜsᴇʀ:</b> {mention_html(member.user.id, html.escape(member.user.first_name))}"
            await chat.unban_member(user_id)
            await message.reply_text("ʏᴇᴀʜ, ᴛʜɪs ᴜsᴇʀ ᴄᴀɴ ᴊᴏɪɴ!")

        if reason:
            log += f"\n<b>ʀᴇᴀsᴏɴ:</b> {reason}"

        return log


__help__ = """
 • /kickme*:* ᴋɪᴄᴋs ᴛʜᴇ ᴜsᴇʀ ᴡʜᴏ ɪssᴜᴇᴅ ᴛʜᴇ ᴄᴏᴍᴍᴀɴᴅ

*ᴀᴅᴍɪɴs ᴏɴʟʏ:*
 • /ban <ᴜsᴇʀʜᴀɴᴅʟᴇ>*:* ʙᴀɴs ᴀ ᴜsᴇʀ/ᴄʜᴀɴɴᴇʟ. (ᴠɪᴀ ʜᴀɴᴅʟᴇ, ᴏʀ ʀᴇᴘʟʏ)
 • /sban <ᴜsᴇʀʜᴀɴᴅʟᴇ>*:* sɪʟᴇɴᴛʟʏ ʙᴀɴ ᴀ ᴜsᴇʀ. ᴅᴇʟᴇᴛᴇs ᴄᴏᴍᴍᴀɴᴅ, ʀᴇᴘʟɪᴇᴅ ᴍᴇssᴀɢᴇ ᴀɴᴅ ᴅᴏᴇsɴ'ᴛ ʀᴇᴘʟʏ. (ᴠɪᴀ ʜᴀɴᴅʟᴇ, ᴏʀ ʀᴇᴘʟʏ)
 • /tban <ᴜsᴇʀʜᴀɴᴅʟᴇ> x(m/h/d)*:* ʙᴀɴs ᴀ ᴜsᴇʀ ғᴏʀ `x` ᴛɪᴍᴇ. (ᴠɪᴀ ʜᴀɴᴅʟᴇ, or reply). `ᴍ` = `ᴍɪɴᴜᴛᴇs`, `ʜ` = `ʜᴏᴜʀs`, `d` = `ᴅᴀʏs`.
 • /unban <ᴜsᴇʀʜᴀɴᴅʟᴇ>*:* ᴜɴʙᴀɴs ᴀ ᴜsᴇʀ/ᴄʜᴀɴɴᴇʟ. (ᴠɪᴀ ʜᴀɴᴅʟᴇ, ᴏʀ ʀᴇᴘʟʏ)
 • /kick <ᴜsᴇʀʜᴀɴᴅʟᴇ>*:* ᴋɪᴄᴋs ᴀ ᴜsᴇʀ ᴏᴜᴛ ᴏғ ᴛʜᴇ ɢʀᴏᴜᴘ, (ᴠɪᴀ ʜᴀɴᴅʟᴇ, ᴏʀ ʀᴇᴘʟʏ)
"""

BAN_HANDLER = CommandHandler(["ban", "sban"], ban, block=False)
TEMPBAN_HANDLER = CommandHandler(["tban"], temp_ban, block=False)
KICK_HANDLER = CommandHandler("kick", kick, block=False)
UNBAN_HANDLER = CommandHandler("unban", unban, block=False)
ROAR_HANDLER = CommandHandler("roar", selfunban, block=False)
KICKME_HANDLER = DisableAbleCommandHandler(
    "kickme", kickme, filters=filters.ChatType.GROUPS, block=False
)
BAN_CALLBACK_HANDLER = CallbackQueryHandler(
    bans_callback, block=False, pattern=r"bans_"
)

application.add_handler(BAN_HANDLER)
application.add_handler(TEMPBAN_HANDLER)
application.add_handler(KICK_HANDLER)
application.add_handler(UNBAN_HANDLER)
application.add_handler(ROAR_HANDLER)
application.add_handler(KICKME_HANDLER)
application.add_handler(BAN_CALLBACK_HANDLER)

__mod_name__ = "𝐁ᴀɴs"
__handlers__ = [
    BAN_HANDLER,
    TEMPBAN_HANDLER,
    KICK_HANDLER,
    UNBAN_HANDLER,
    ROAR_HANDLER,
    KICKME_HANDLER,
    BAN_CALLBACK_HANDLER,
]
