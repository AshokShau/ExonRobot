import html

from telegram import (
    ChatMemberAdministrator,
    ChatMemberOwner,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Update,
)
from telegram.constants import ChatID, ChatMemberStatus, ChatType, ParseMode
from telegram.error import BadRequest
from telegram.ext import CallbackQueryHandler, CommandHandler, ContextTypes, filters
from telegram.helpers import mention_html

from Exon import DRAGONS, application
from Exon.modules.disable import DisableAbleCommandHandler
from Exon.modules.helper_funcs.alternate import send_message
from Exon.modules.helper_funcs.chat_status import (
    ADMIN_CACHE,
    check_admin,
    connection_status,
)
from Exon.modules.helper_funcs.extraction import extract_user, extract_user_and_text
from Exon.modules.log_channel import loggable


@connection_status
@loggable
@check_admin(permission="can_promote_members", is_both=True)
async def promote(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    bot = context.bot
    args = context.args

    message = update.effective_message
    chat = update.effective_chat
    user = update.effective_user

    user_id = await extract_user(message, context, args)
    await chat.get_member(user.id)

    if message.from_user.id == ChatID.ANONYMOUS_ADMIN:

        await message.reply_text(
            text="ʏᴏᴜ ᴀʀᴇ ᴀɴ ᴀɴᴏɴʏᴍᴏᴜs ᴀᴅᴍɪɴ.",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text="ᴄʟɪᴄᴋ ᴛᴏ ᴘʀᴏᴠᴇ ᴀᴅᴍɪɴ.",
                            callback_data=f"admin_=promote={user_id}",
                        ),
                    ],
                ],
            ),
        )

        return

    if not user_id:
        await message.reply_text(
            "ʏᴏᴜ ᴅᴏɴ'ᴛ sᴇᴇᴍ ᴛᴏ ʙᴇ ʀᴇғᴇʀʀɪɴɢ ᴛᴏ ᴀ ᴜsᴇʀ ᴏʀ ᴛʜᴇ ID sᴘᴇᴄɪғɪᴇᴅ ɪs ɪɴᴄᴏʀʀᴇᴄᴛ..",
        )
        return

    try:
        user_member = await chat.get_member(user_id)
    except:
        return

    if (
        user_member.status == ChatMemberStatus.ADMINISTRATOR
        or user_member.status == ChatMemberStatus.OWNER
    ):
        await message.reply_text(
            "ʜᴏᴡ ᴀᴍ ɪ ᴍᴇᴀɴᴛ ᴛᴏ ᴘʀᴏᴍᴏᴛᴇ sᴏᴍᴇᴏɴᴇ ᴛʜᴀᴛ's ᴀʟʀᴇᴀᴅʏ ᴀɴ ᴀᴅᴍɪɴ?"
        )
        return

    if user_id == bot.id:
        await message.reply_text(
            "I ᴄᴀɴ'ᴛ ᴘʀᴏᴍᴏᴛᴇ ᴍʏsᴇʟғ! ɢᴇᴛ ᴀɴ ᴀᴅᴍɪɴ ᴛᴏ ᴅᴏ ɪᴛ ғᴏʀ ᴍᴇ."
        )
        return

    # set same perms as bot - bot can't assign higher perms than itself!
    bot_member = await chat.get_member(bot.id)

    if isinstance(bot_member, ChatMemberAdministrator):
        try:
            await bot.promoteChatMember(
                chat.id,
                user_id,
                can_change_info=bot_member.can_change_info,
                can_post_messages=bot_member.can_post_messages,
                can_edit_messages=bot_member.can_edit_messages,
                can_delete_messages=bot_member.can_delete_messages,
                can_invite_users=bot_member.can_invite_users,
                # can_promote_members=bot_member.can_promote_members,
                can_restrict_members=bot_member.can_restrict_members,
                can_pin_messages=bot_member.can_pin_messages,
                can_manage_chat=bot_member.can_manage_chat,
                can_manage_video_chats=bot_member.can_manage_video_chats,
                can_manage_topics=bot_member.can_manage_topics,
            )
        except BadRequest as err:
            if err.message == "User_not_mutual_contact":
                await message.reply_text(
                    "I ᴄᴀɴ'ᴛ ᴘʀᴏᴍᴏᴛᴇ sᴏᴍᴇᴏɴᴇ ᴡʜᴏ ɪsɴ'ᴛ ɪɴ ᴛʜᴇ ɢʀᴏᴜᴘ."
                )
            else:
                await message.reply_text("ᴀɴ ᴇʀʀᴏʀ ᴏᴄᴄᴜʀʀᴇᴅ ᴡʜɪʟᴇ ᴘʀᴏᴍᴏᴛɪɴɢ.")
            return

    await bot.sendMessage(
        chat.id,
        f"sᴜᴄᴄᴇssғᴜʟʟʏ ᴘʀᴏᴍᴏᴛᴇᴅ <b>{user_member.user.first_name or user_id}</b>!",
        parse_mode=ParseMode.HTML,
        message_thread_id=message.message_thread_id if chat.is_forum else None,
    )

    log_message = (
        f"<b>{html.escape(chat.title)}:</b>\n"
        f"#𝐏𝐑𝐎𝐌𝐎𝐓𝐄𝐃\n"
        f"<b>ᴀᴅᴍɪɴ:</b> {mention_html(user.id, user.first_name)}\n"
        f"<b>ᴜsᴇʀ:</b> {mention_html(user_member.user.id, user_member.user.first_name)}"
    )

    return log_message


@connection_status
@loggable
@check_admin(permission="can_promote_members", is_both=True)
async def demote(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    bot = context.bot
    args = context.args

    chat = update.effective_chat
    message = update.effective_message
    user = update.effective_user

    user_id = await extract_user(message, context, args)
    await chat.get_member(user.id)

    if message.from_user.id == ChatID.ANONYMOUS_ADMIN:

        await message.reply_text(
            text="ʏᴏᴜ ᴀʀᴇ ᴀɴ ᴀɴᴏɴʏᴍᴏᴜs ᴀᴅᴍɪɴ.",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text="ᴄʟɪᴄᴋ ᴛᴏ ᴘʀᴏᴠᴇ ᴀᴅᴍɪɴ.",
                            callback_data=f"admin_=demote={user_id}",
                        ),
                    ],
                ],
            ),
        )

        return

    if not user_id:
        await message.reply_text(
            "ʏᴏᴜ ᴅᴏɴ'ᴛ sᴇᴇᴍ ᴛᴏ ʙᴇ ʀᴇғᴇʀʀɪɴɢ ᴛᴏ ᴀ ᴜsᴇʀ ᴏʀ ᴛʜᴇ ɪᴅ sᴘᴇᴄɪғɪᴇᴅ ɪs ɪɴᴄᴏʀʀᴇᴄᴛ..",
        )
        return

    try:
        user_member = await chat.get_member(user_id)
    except:
        return

    if user_member.status == ChatMemberStatus.OWNER:
        await message.reply_text(
            "ᴛʜɪs ᴘᴇʀsᴏɴ CREATED ᴛʜᴇ ᴄʜᴀᴛ, ʜᴏᴡ ᴡᴏᴜʟᴅ ɪ ᴅᴇᴍᴏᴛᴇ ᴛʜᴇᴍ?"
        )
        return

    if not user_member.status == ChatMemberStatus.ADMINISTRATOR:
        await message.reply_text("ᴄᴀɴ'ᴛ ᴅᴇᴍᴏᴛᴇ ᴡʜᴀᴛ ᴡᴀsɴ'ᴛ ᴘʀᴏᴍᴏᴛᴇᴅ!")
        return

    if user_id == bot.id:
        await message.reply_text("I ᴄᴀɴ'ᴛ ᴅᴇᴍᴏᴛᴇ ᴍʏsᴇʟғ !.")
        return

    try:
        await bot.promote_chat_member(
            chat.id,
            user_id,
            can_change_info=False,
            can_post_messages=False,
            can_edit_messages=False,
            can_delete_messages=False,
            can_invite_users=False,
            can_restrict_members=False,
            can_pin_messages=False,
            can_promote_members=False,
            can_manage_chat=False,
            can_manage_video_chats=False,
            can_manage_topics=False,
        )

        await bot.sendMessage(
            chat.id,
            f"sᴜᴄᴇssғᴜʟʟʏ ᴅᴇᴍᴏᴛᴇᴅ <b>{user_member.user.first_name or user_id}</b>!",
            parse_mode=ParseMode.HTML,
            message_thread_id=message.message_thread_id if chat.is_forum else None,
        )

        log_message = (
            f"<b>{html.escape(chat.title)}:</b>\n"
            f"#𝐃𝐄𝐌𝐎𝐓𝐄𝐃\n"
            f"<b>ᴀᴅᴍɪɴ:</b> {mention_html(user.id, user.first_name)}\n"
            f"<b>ᴜsᴇʀ:</b> {mention_html(user_member.user.id, user_member.user.first_name)}"
        )

        return log_message
    except BadRequest:
        await message.reply_text(
            "ᴄᴏᴜʟᴅ ɴᴏᴛ ᴅᴇᴍᴏᴛᴇ. I ᴍɪɢʜᴛ ɴᴏᴛ ʙᴇ ᴀᴅᴍɪɴ, ᴏʀ ᴛʜᴇ ᴀᴅᴍɪɴ sᴛᴀᴛᴜs ᴡᴀs ᴀᴘᴘᴏɪɴᴛᴇᴅ ʙʏ ᴀɴᴏᴛʜᴇʀ"
            " ᴜsᴇʀ, sᴏ I ᴄᴀɴ'ᴛ ᴀᴄᴛ ᴜᴘᴏɴ ᴛʜᴇᴍ!",
        )
        raise


@check_admin(is_user=True)
async def refresh_admin(update, _):
    try:
        ADMIN_CACHE.pop(update.effective_chat.id)
    except KeyError:
        pass

    await update.effective_message.reply_text("ᴀᴅᴍɪɴs ᴄᴀᴄʜᴇ ʀᴇғʀᴇsʜᴇᴅ!")


@connection_status
@check_admin(permission="can_promote_members", is_both=True)
async def set_title(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bot = context.bot
    args = context.args

    chat = update.effective_chat
    message = update.effective_message

    user_id, title = await extract_user_and_text(message, context, args)

    if message.from_user.id == 1087968824:

        await message.reply_text(
            text="ʏᴏᴜ ᴀʀᴇ ᴀɴ ᴀɴᴏɴʏᴍᴏᴜs ᴀᴅᴍɪɴ.",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text="ᴄʟɪᴄᴋ ᴛᴏ ᴘʀᴏᴠᴇ ᴀᴅᴍɪɴ.",
                            callback_data=f"admin_=title={user_id}={title}",
                        ),
                    ],
                ],
            ),
        )

        return

    try:
        user_member = await chat.get_member(user_id)
    except:
        return

    if not user_id:
        await message.reply_text(
            "You ᴅᴏɴ'ᴛ sᴇᴇᴍ ᴛᴏ ʙᴇ ʀᴇғᴇʀʀɪɴɢ ᴛᴏ ᴀ ᴜsᴇʀ ᴏʀ ᴛʜᴇ ID sᴘᴇᴄɪғɪᴇᴅ ɪs ɪɴᴄᴏʀʀᴇᴄᴛ..",
        )
        return

    if user_member.status == ChatMemberStatus.OWNER:
        await message.reply_text(
            "ᴛʜɪs ᴘᴇʀsᴏɴ CREATED ᴛʜᴇ ᴄʜᴀᴛ, ʜᴏᴡ ᴄᴀɴ ɪ sᴇᴛ ᴄᴜsᴛᴏᴍ ᴛɪᴛʟᴇ ғᴏʀ ʜɪᴍ?",
        )
        return

    if user_member.status != ChatMemberStatus.ADMINISTRATOR:
        await message.reply_text(
            "ᴄᴀɴ'ᴛ sᴇᴛ ᴛɪᴛʟᴇ ғᴏʀ ɴᴏɴ-ᴀᴅᴍɪɴs!\nᴘʀᴏᴍᴏᴛᴇ ᴛʜᴇᴍ ғɪʀsᴛ ᴛᴏ sᴇᴛ ᴄᴜsᴛᴏᴍ ᴛɪᴛʟᴇ!",
        )
        return

    if user_id == bot.id:
        await message.reply_text(
            "I ᴄᴀɴ'ᴛ sᴇᴛ ᴍʏ ᴏᴡɴ ᴛɪᴛʟᴇ ᴍʏsᴇʟғ! ɢᴇᴛ ᴛʜᴇ ᴏɴᴇ ᴡʜᴏ ᴍᴀᴅᴇ ᴍᴇ ᴀᴅᴍɪɴ ᴛᴏ ᴅᴏ ɪᴛ ғᴏʀ ᴍᴇ.",
        )
        return

    if not title:
        await message.reply_text("sᴇᴛᴛɪɴɢ ʙʟᴀɴᴋ ᴛɪᴛʟᴇ ᴅᴏᴇsɴ'ᴛ ᴅᴏ ᴀɴʏᴛʜɪɴɢ!")
        return

    if len(title) > 16:
        await message.reply_text(
            "ᴛʜᴇ ᴛɪᴛʟᴇ ʟᴇɴɢᴛʜ ɪs ʟᴏɴɢᴇʀ ᴛʜᴀɴ 16 ᴄʜᴀʀᴀᴄᴛᴇʀs.\nᴛʀᴜɴᴄᴀᴛɪɴɢ ɪᴛ ᴛᴏ 16 ᴄʜᴀʀᴀᴄᴛᴇʀs.",
        )

    try:
        await bot.setChatAdministratorCustomTitle(chat.id, user_id, title)
    except BadRequest:
        await message.reply_text(
            "ᴇɪᴛʜᴇʀ ᴛʜᴇʏ ᴀʀᴇɴ'ᴛ ᴘʀᴏᴍᴏᴛᴇᴅ ʙʏ ᴍᴇ ᴏʀ ʏᴏᴜ sᴇᴛ ᴀ ᴛɪᴛʟᴇ ᴛᴇxᴛ ᴛʜᴀᴛ ɪs ɪᴍᴘᴏssɪʙʟᴇ ᴛᴏ sᴇᴛ."
        )
        raise

    await bot.sendMessage(
        chat.id,
        f"sᴜᴄᴄᴇssғᴜʟʟʏ sᴇᴛ ᴛɪᴛʟᴇ ғᴏʀ <code>{user_member.user.first_name or user_id}</code> "
        f"ᴛᴏ <code>{html.escape(title[:16])}</code>!",
        parse_mode=ParseMode.HTML,
        message_thread_id=message.message_thread_id if chat.is_forum else None,
    )


@loggable
@check_admin(permission="can_pin_messages", is_both=True)
async def pin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    bot = context.bot
    args = context.args

    user = update.effective_user
    chat = update.effective_chat
    message = update.effective_message

    is_group = chat.type != "private" and chat.type != "channel"
    prev_message = update.effective_message.reply_to_message

    is_silent = True
    if len(args) >= 1:
        is_silent = not (
            args[0].lower() == "notify"
            or args[0].lower() == "loud"
            or args[0].lower() == "violent"
        )

    if not prev_message:
        await message.reply_text("ᴘʟᴇᴀsᴇ ʀᴇᴘʟʏ ᴛᴏ ᴍᴇssᴀɢᴇ ᴡʜɪᴄʜ ʏᴏᴜ ᴡᴀɴᴛ ᴛᴏ ᴘɪɴ.")
        return

    if message.from_user.id == 1087968824:

        await message.reply_text(
            text="ʏᴏᴜ ᴀʀᴇ ᴀɴ ᴀɴᴏɴʏᴍᴏᴜs ᴀᴅᴍɪɴ.",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text="ᴄʟɪᴄᴋ ᴛᴏ ᴘʀᴏᴠᴇ ᴀᴅᴍɪɴ.",
                            callback_data=f"admin_=pin={prev_message.message_id}={is_silent}",
                        ),
                    ],
                ],
            ),
        )

        return

    if prev_message and is_group:
        try:
            await bot.pinChatMessage(
                chat.id,
                prev_message.message_id,
                disable_notification=is_silent,
            )
        except BadRequest as excp:
            if excp.message == "Chat_not_modified":
                pass
            else:
                raise
        log_message = (
            f"<b>{html.escape(chat.title)}:</b>\n"
            f"#𝐏𝐈𝐍𝐍𝐄𝐃\n"
            f"<b>ᴀᴅᴍɪɴ:</b> {mention_html(user.id, html.escape(user.first_name))}"
        )

        return log_message


@loggable
@check_admin(permission="can_pin_messages", is_both=True)
async def unpin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    bot = context.bot
    chat = update.effective_chat
    user = update.effective_user
    message = update.effective_message

    if message.from_user.id == 1087968824:

        await message.reply_text(
            text="ʏᴏᴜ ᴀʀᴇ ᴀɴ ᴀɴᴏɴʏᴍᴏᴜs ᴀᴅᴍɪɴ.",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text="ᴄʟɪᴄᴋ ᴛᴏ prove Admin.",
                            callback_data=f"admin_=unpin",
                        ),
                    ],
                ],
            ),
        )

        return

    try:
        await bot.unpinChatMessage(chat.id)
    except BadRequest as excp:
        if excp.message == "Chat_not_modified":
            pass
        elif excp.message == "ᴍᴇssᴀɢᴇ ᴛᴏ ᴜɴᴘɪɴ ɴᴏᴛ ғᴏᴜɴᴅ":
            await message.reply_text("ɴᴏ ᴘɪɴɴᴇᴅ ᴍᴇssᴀɢᴇ ғᴏᴜɴᴅ")
            return
        else:
            raise

    log_message = (
        f"<b>{html.escape(chat.title)}:</b>\n"
        f"#𝐔𝐍𝐏𝐈𝐍𝐍𝐄𝐃\n"
        f"<b>ᴀᴅᴍɪɴ:</b> {mention_html(user.id, html.escape(user.first_name))}"
    )

    return log_message


@loggable
@check_admin(permission="can_pin_messages", is_both=True)
async def unpinall(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    bot = context.bot
    chat = update.effective_chat
    user = update.effective_user
    message = update.effective_message
    admin_member = await chat.get_member(user.id)

    if message.from_user.id == 1087968824:

        await message.reply_text(
            text="ʏᴏᴜ ᴀʀᴇ ᴀɴ ᴀɴᴏɴʏᴍᴏᴜs ᴀᴅᴍɪɴ.",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text="ᴄʟɪᴄᴋ ᴛᴏ ᴘʀᴏᴠᴇ ᴀᴅᴍɪɴ.",
                            callback_data=f"admin_=unpinall",
                        ),
                    ],
                ],
            ),
        )

        return
    elif not admin_member.status == ChatMemberStatus.OWNER and user.id not in DRAGONS:
        await message.reply_text("ᴏɴʟʏ ᴄʜᴀᴛ OWNER ᴄᴀɴ ᴜɴᴘɪɴ ᴀʟʟ ᴍᴇssᴀɢᴇs.")
        return

    try:
        if chat.is_forum:
            await bot.unpin_all_forum_topic_messages(chat.id, message.message_thread_id)
        else:
            await bot.unpin_all_chat_messages(chat.id)
    except BadRequest as excp:
        if excp.message == "Chat_not_modified":
            pass
        else:
            raise

    log_message = (
        f"<b>{html.escape(chat.title)}:</b>\n"
        f"#𝐔𝐍𝐏𝐈𝐍𝐍𝐄𝐃_𝐀𝐋𝐋\n"
        f"<b>ᴀᴅᴍɪɴ:</b> {mention_html(user.id, html.escape(user.first_name))}"
    )

    return log_message


@connection_status
@check_admin(permission="can_invite_users", is_bot=True)
async def invite(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bot = context.bot
    chat = update.effective_chat

    if chat.username:
        await update.effective_message.reply_text(f"https://t.me/{chat.username}")
    elif chat.type in [ChatType.SUPERGROUP, ChatType.CHANNEL]:
        bot_member = await chat.get_member(bot.id)
        if (
            bot_member.can_invite_users
            if isinstance(bot_member, ChatMemberAdministrator)
            else None
        ):
            invitelink = await bot.exportChatInviteLink(chat.id)
            await update.effective_message.reply_text(invitelink)
        else:
            await update.effective_message.reply_text(
                "I ᴅᴏɴ'ᴛ ʜᴀᴠᴇ ᴀᴄᴄᴇss ᴛᴏ ᴛʜᴇ ɪɴᴠɪᴛᴇ ʟɪɴᴋ, ᴛʀʏ ᴄʜᴀɴɢɪɴɢ ᴍʏ ᴘᴇʀᴍɪssɪᴏɴs!",
            )
    else:
        await update.effective_message.reply_text(
            "I ᴄᴀɴ ᴏɴʟʏ ɢɪᴠᴇ ʏᴏᴜ ɪɴᴠɪᴛᴇ ʟɪɴᴋs ғᴏʀ sᴜᴘᴇʀɢʀᴏᴜᴘs ᴀɴᴅ ᴄʜᴀɴɴᴇʟs, sᴏʀʀʏ!",
        )


@connection_status
async def adminlist(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user  # type: Optional[User]
    bot = context.bot

    if update.effective_message.chat.type == "private":
        await send_message(
            update.effective_message, "ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ ᴏɴʟʏ ᴡᴏʀᴋs ɪɴ ɢʀᴏᴜᴘs."
        )
        return

    chat_id = update.effective_chat.id

    try:
        msg = await update.effective_message.reply_text(
            "ғᴇᴛᴄʜɪɴɢ ɢʀᴏᴜᴘ ᴀᴅᴍɪɴs...",
            parse_mode=ParseMode.HTML,
        )
    except BadRequest:
        msg = await update.effective_message.reply_text(
            "ғᴇᴛᴄʜɪɴɢ ɢʀᴏᴜᴘ ᴀᴅᴍɪɴs...",
            quote=False,
            parse_mode=ParseMode.HTML,
        )

    administrators = await bot.getChatAdministrators(chat_id)
    text = "ᴀᴅᴍɪɴs ɪɴ <b>{}</b>:".format(html.escape(update.effective_chat.title))

    custom_admin_list = {}
    normal_admin_list = []

    for admin in administrators:
        if isinstance(admin, (ChatMemberAdministrator, ChatMemberOwner)):
            user = admin.user
            status = admin.status
            custom_title = admin.custom_title

            if user.first_name == "":
                name = "☠ ᴅᴇʟᴇᴛᴇᴅ ᴀᴄᴄᴏᴜɴᴛ"
            else:
                name = "{}".format(
                    mention_html(
                        user.id,
                        html.escape(user.first_name + " " + (user.last_name or "")),
                    ),
                )

            # if user.username:
            #    name = escape_markdown("@" + user.username)
            if status == ChatMemberStatus.OWNER:
                text += "\n 👑 ᴄʀᴇᴀᴛᴏʀ:"
                text += "\n<code> • </code>{}\n".format(name)

                if custom_title:
                    text += f"<code> ┗━ {html.escape(custom_title)}</code>\n"

            if status == ChatMemberStatus.ADMINISTRATOR:
                if custom_title:
                    try:
                        custom_admin_list[custom_title].append(name)
                    except KeyError:
                        custom_admin_list.update({custom_title: [name]})
                else:
                    normal_admin_list.append(name)

    text += "\n🔱 ᴀᴅᴍɪɴs:"

    for admin in normal_admin_list:
        text += "\n<code> • </code>{}".format(admin)

    for admin_group in custom_admin_list.copy():
        if len(custom_admin_list[admin_group]) == 1:
            text += "\n<code> • </code>{} | <code>{}</code>".format(
                custom_admin_list[admin_group][0],
                html.escape(admin_group),
            )
            custom_admin_list.pop(admin_group)

    text += "\n"
    for admin_group, value in custom_admin_list.items():
        text += "\n🚨 <code>{}</code>".format(admin_group)
        for admin in value:
            text += "\n<code> • </code>{}".format(admin)
        text += "\n"

    try:
        await msg.edit_text(text, parse_mode=ParseMode.HTML)
    except BadRequest:  # if original message is deleted
        return


@loggable
async def admin_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    bot = context.bot
    message = update.effective_message
    chat = update.effective_chat
    admin_user = query.from_user

    splitter = query.data.replace("admin_", "").split("=")

    if splitter[1] == "promote":

        promoter = await chat.get_member(admin_user.id)

        if (
            not (
                promoter.can_promote_members
                if isinstance(promoter, ChatMemberAdministrator)
                else None or promoter.status == ChatMemberStatus.OWNER
            )
            and admin_user.id not in DRAGONS
        ):
            await query.answer(
                "ʏᴏᴜ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ ᴛʜᴇ ɴᴇᴄᴇssᴀʀʏ ʀɪɢʜᴛs ᴛᴏ ᴅᴏ ᴛʜᴀᴛ!", show_alert=True
            )
            return

        try:
            user_id = int(splitter[2])
        except ValueError:
            user_id = splitter[2]
            await message.edit_text(
                "ʏᴏᴜ ᴅᴏɴ'ᴛ sᴇᴇᴍ ᴛᴏ ʙᴇ ʀᴇғᴇʀʀɪɴɢ ᴛᴏ ᴀ ᴜsᴇʀ ᴏʀ ᴛʜᴇ ID sᴘᴇᴄɪғɪᴇᴅ ɪs ɪɴᴄᴏʀʀᴇᴄᴛ..."
            )
            return

        try:
            user_member = await chat.get_member(user_id)
        except:
            return

        if (
            user_member.status == ChatMemberStatus.ADMINISTRATOR
            or user_member.status == ChatMemberStatus.OWNER
        ):
            await message.edit_text(
                "ʜᴏᴡ ᴀᴍ I ᴍᴇᴀɴᴛ ᴛᴏ ᴘʀᴏᴍᴏᴛᴇ sᴏᴍᴇᴏɴᴇ ᴛʜᴀᴛ's ᴀʟʀᴇᴀᴅʏ ᴀɴ ᴀᴅᴍɪɴ?"
            )
            return

        bot_member = await chat.get_member(bot.id)

        if isinstance(bot_member, ChatMemberAdministrator):
            try:
                await bot.promoteChatMember(
                    chat.id,
                    user_id,
                    can_change_info=bot_member.can_change_info,
                    can_post_messages=bot_member.can_post_messages,
                    can_edit_messages=bot_member.can_edit_messages,
                    can_delete_messages=bot_member.can_delete_messages,
                    can_invite_users=bot_member.can_invite_users,
                    # can_promote_members=bot_member.can_promote_members,
                    can_restrict_members=bot_member.can_restrict_members,
                    can_pin_messages=bot_member.can_pin_messages,
                    can_manage_chat=bot_member.can_manage_chat,
                    can_manage_video_chats=bot_member.can_manage_video_chats,
                )
            except BadRequest as err:
                if err.message == "User_not_mutual_contact":
                    await message.edit_text(
                        "I ᴄᴀɴ'ᴛ ᴘʀᴏᴍᴏᴛᴇ sᴏᴍᴇᴏɴᴇ ᴡʜᴏ ɪsɴ'ᴛ ɪɴ ᴛʜᴇ ɢʀᴏᴜᴘ"
                    )
                else:
                    await message.edit_text("An ᴇʀʀᴏʀ ᴏᴄᴄᴜʀᴇᴅ ᴡʜɪʟᴇ ᴘʀᴏᴍᴏᴛɪɴɢ.")
                return

        await message.edit_text(
            f"sᴜᴄᴇssғᴜʟʟʏ ᴘʀᴏᴍᴏᴛᴇᴅ <b>{user_member.user.first_name or user_id}</b>!",
            parse_mode=ParseMode.HTML,
        )
        await query.answer("Done")

        log_message = (
            f"<b>{html.escape(chat.title)}:</b>\n"
            f"#𝐏𝐑𝐎𝐌𝐎𝐓𝐄𝐃\n"
            f"<b>ᴀᴅᴍɪɴ:</b> {mention_html(admin_user.id, admin_user.first_name)}\n"
            f"<b>ᴜsᴇʀ:</b> {mention_html(user_member.user.id, user_member.user.first_name)}"
        )

        return log_message

    elif splitter[1] == "demote":

        demoter = await chat.get_member(admin_user.id)

        if not (
            demoter.can_promote_members
            if isinstance(demoter, ChatMemberAdministrator)
            else None or demoter.status == ChatMemberStatus.OWNER
        ):
            await query.answer(
                "ʏᴏᴜ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ ᴛʜᴇ ɴᴇᴄᴇssᴀʀʏ ʀɪɢʜᴛs ᴛᴏ ᴅᴏ ᴛʜᴀᴛ!", show_alert=True
            )
            return

        try:
            user_id = int(splitter[2])
        except:
            user_id = splitter[2]
            await message.edit_text(
                "ʏᴏᴜ ᴅᴏɴ'ᴛ sᴇᴇᴍ ᴛᴏ ʙᴇ ʀᴇғᴇʀʀɪɴɢ ᴛᴏ ᴀ ᴜsᴇʀ ᴏʀ ᴛʜᴇ ID sᴘᴇᴄɪғɪᴇᴅ ɪs ɪɴᴄᴏʀʀᴇᴄᴛ.."
            )
            return

        try:
            user_member = await chat.get_member(user_id)
        except:
            return

        if user_member.status == ChatMemberStatus.OWNER:
            await message.edit_text(
                "ᴛʜɪs ᴘᴇʀsᴏɴ CREATED ᴛʜᴇ ᴄʜᴀᴛ, ʜᴏᴡ ᴡᴏᴜʟᴅ I ᴅᴇᴍᴏᴛᴇ ᴛʜᴇᴍ?"
            )
            return

        if not user_member.status == ChatMemberStatus.ADMINISTRATOR:
            await message.edit_text("Can't demote what wasn't promoted!")
            return

        if user_id == bot.id:
            await message.edit_text(
                "I ᴄᴀɴ'ᴛ ᴅᴇᴍᴏᴛᴇ ᴍʏsᴇʟғ!, ɢᴇᴛ ᴀɴ ᴀᴅᴍɪɴ ᴛᴏ ᴅᴏ ɪᴛ ғᴏʀ ᴍᴇ."
            )
            return

        try:
            await bot.promoteChatMember(
                chat.id,
                user_id,
                can_change_info=False,
                can_post_messages=False,
                can_edit_messages=False,
                can_delete_messages=False,
                can_invite_users=False,
                can_restrict_members=False,
                can_pin_messages=False,
                can_promote_members=False,
                can_manage_chat=False,
                can_manage_video_chats=False,
            )

            await message.edit_text(
                f"sᴜᴄᴇssғᴜʟʟʏ ᴅᴇᴍᴏᴛᴇᴅ <b>{user_member.user.first_name or user_id}</b>!",
                parse_mode=ParseMode.HTML,
            )
            await query.answer("ᴅᴏɴᴇ")

            log_message = (
                f"<b>{html.escape(chat.title)}:</b>\n"
                f"#𝐃𝐄𝐌𝐎𝐓𝐄𝐃\n"
                f"<b>ᴀᴅᴍɪɴ:</b> {mention_html(admin_user.id, admin_user.first_name)}\n"
                f"<b>ᴜsᴇʀ:</b> {mention_html(user_member.user.id, user_member.user.first_name)}"
            )

            return log_message
        except BadRequest:
            await message.edit_text(
                "ᴄᴏᴜʟᴅ ɴᴏᴛ ᴅᴇᴍᴏᴛᴇ. I ᴍɪɢʜᴛ ɴᴏᴛ ʙᴇ ᴀᴅᴍɪɴ, ᴏʀ ᴛʜᴇ ᴀᴅᴍɪɴ sᴛᴀᴛᴜs ᴡᴀs ᴀᴘᴘᴏɪɴᴛᴇᴅ ʙʏ ᴀɴᴏᴛʜᴇʀ"
                " user, so I can't act upon them!",
            )
            return

    elif splitter[1] == "title":
        title = splitter[3]

        admin_member = await chat.get_member(admin_user.id)

        if (
            not (
                (
                    admin_member.can_promote_members
                    if isinstance(admin_member, ChatMemberAdministrator)
                    else None
                )
                or admin_member.status == ChatMemberStatus.OWNER
            )
            and admin_user.id not in DRAGONS
        ):
            await query.answer("ʏᴏᴜ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ ᴛʜᴇ ɴᴇᴄᴇssᴀʀʏ ʀɪɢʜᴛs ᴛᴏ ᴅᴏ ᴛʜᴀᴛ!")
            return

        try:
            user_id = int(splitter[2])
        except:
            await message.edit_text(
                "ʏᴏᴜ ᴅᴏɴ'ᴛ sᴇᴇᴍ ᴛᴏ ʙᴇ ʀᴇғᴇʀʀɪɴɢ ᴛᴏ ᴀ ᴜsᴇʀ ᴏʀ ᴛʜᴇ ID sᴘᴇᴄɪғɪᴇᴅ ɪs ɪɴᴄᴏʀʀᴇᴄᴛ..",
            )
            return

        try:
            user_member = await chat.get_member(user_id)
        except:
            return

        if user_member.status == ChatMemberStatus.OWNER:
            await message.edit_text(
                "ᴛʜɪs ᴘᴇʀsᴏɴ CREATED ᴛʜᴇ ᴄʜᴀᴛ, ʜᴏᴡ ᴄᴀɴ I sᴇᴛ ᴄᴜsᴛᴏᴍ ᴛɪᴛʟᴇ ғᴏʀ ʜɪᴍ?",
            )
            return

        if user_member.status != ChatMemberStatus.ADMINISTRATOR:
            await message.edit_text(
                "ᴄᴀɴ'ᴛ sᴇᴛ ᴛɪᴛʟᴇ ғᴏʀ ɴᴏɴ--ᴀᴅᴍɪɴs!\nᴘʀᴏᴍᴏᴛᴇ ᴛʜᴇᴍ ғɪʀsᴛ ᴛᴏ sᴇᴛ ᴄᴜsᴛᴏᴍ ᴛɪᴛʟᴇ!",
            )
            return

        if user_id == bot.id:
            await message.edit_text(
                "I ᴄᴀɴ'ᴛ sᴇᴛ ᴍʏ ᴏᴡɴ ᴛɪᴛʟᴇ ᴍʏsᴇʟғ! ɢᴇᴛ ᴛʜᴇ ᴏɴᴇ ᴡʜᴏ ᴍᴀᴅᴇ ᴍᴇ ᴀᴅᴍɪɴ ᴛᴏ ᴅᴏ ɪᴛ ғᴏʀ ᴍᴇ.",
            )
            return

        if not title:
            await message.edit_text("sᴇᴛᴛɪɴɢ ʙʟᴀɴᴋ ᴛɪᴛʟᴇ ᴅᴏᴇsɴ'ᴛ ᴅᴏ ᴀɴʏᴛʜɪɴɢ!")
            return

        if len(title) > 16:
            await message.edit_text(
                "ᴛʜᴇ ᴛɪᴛʟᴇ ʟᴇɴɢᴛʜ ɪs ʟᴏɴɢᴇʀ ᴛʜᴀɴ 16 ᴄʜᴀʀᴀᴄᴛᴇʀs.\nᴛʀᴜɴᴄᴀᴛɪɴɢ ɪᴛ ᴛᴏ 16 ᴄʜᴀʀᴀᴄᴛᴇʀs.",
            )

        try:
            await bot.setChatAdministratorCustomTitle(chat.id, user_id, title)
        except BadRequest:
            await message.edit_text(
                "ᴇɪᴛʜᴇʀ ᴛʜᴇʏ ᴀʀᴇɴ'ᴛ ᴘʀᴏᴍᴏᴛᴇᴅ ʙʏ ᴍᴇ ᴏʀ ʏᴏᴜ sᴇᴛ ᴀ ᴛɪᴛʟᴇ ᴛᴇxᴛ ᴛʜᴀᴛ ɪs ɪᴍᴘᴏssɪʙʟᴇ ᴛᴏ sᴇᴛ."
            )
            return

        await message.edit_text(
            text=f"sᴜᴄᴇssғᴜʟʟʏ sᴇᴛ ᴛɪᴛʟᴇ ғᴏʀ <code>{user_member.user.first_name or user_id}</code> "
            f"ᴛᴏ <code>{html.escape(title[:16])}</code>!",
            parse_mode=ParseMode.HTML,
        )

    elif splitter[1] == "pin":

        admin_member = await chat.get_member(admin_user.id)

        if (
            not (
                (
                    admin_member.can_pin_messages
                    if isinstance(admin_member, ChatMemberAdministrator)
                    else None
                )
                or admin_member.status == ChatMemberStatus.OWNER
            )
            and admin_user.id not in DRAGONS
        ):
            await query.answer(
                "ʏᴏᴜ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ ᴛʜᴇ ɴᴇᴄᴇssᴀʀʏ ʀɪɢʜᴛs ᴛᴏ ᴅᴏ ᴛʜᴀᴛ!", show_alert=True
            )
            return

        try:
            message_id = int(splitter[2])
        except:
            return

        is_silent = bool(splitter[3])
        is_group = chat.type != "private" and chat.type != "channel"

        if is_group:
            try:
                await bot.pinChatMessage(
                    chat.id,
                    message_id,
                    disable_notification=is_silent,
                )
            except BadRequest as excp:
                if excp.message == "Chat_not_modified":
                    pass
                else:
                    raise

            await message.edit_text("Done Pinned.")

            log_message = (
                f"<b>{html.escape(chat.title)}</b>\n"
                f"#𝐏𝐈𝐍𝐍𝐄𝐃\n"
                f"<b>ᴀᴅᴍɪɴ:</b> {mention_html(admin_user.id, html.escape(admin_user.first_name))}"
            )

            return log_message

    elif splitter[1] == "unpin":

        admin_member = await chat.get_member(admin_user.id)

        if (
            not (
                (
                    admin_member.can_pin_messages
                    if isinstance(admin_member, ChatMemberAdministrator)
                    else None
                )
                or admin_member.status == ChatMemberStatus.OWNER
            )
            and admin_user.id not in DRAGONS
        ):
            await query.answer(
                "ʏᴏᴜ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ ᴛʜᴇ ɴᴇᴄᴇssᴀʀʏ ʀɪɢʜᴛs ᴛᴏ ᴅᴏ ᴛʜᴀᴛ!",
                show_alert=True,
            )
            return

        try:
            await bot.unpinChatMessage(chat.id)
        except BadRequest as excp:
            if excp.message == "Chat_not_modified":
                pass
            elif excp.message == "ᴍᴇssᴀɢᴇ ᴛᴏ ᴜɴᴘɪɴ ɴᴏᴛ ғᴏᴜɴᴅ":
                await message.edit_text("ɴᴏ ᴘɪɴɴᴇᴅ ᴍᴇssᴀɢᴇ ғᴏᴜɴᴅ")
                return
            else:
                raise

        log_message = (
            f"<b>{html.escape(chat.title)}:</b>\n"
            f"#𝐔𝐍𝐏𝐈𝐍𝐍𝐄𝐃\n"
            f"<b>ᴀᴅᴍɪɴ:</b> {mention_html(admin_user.id, html.escape(admin_user.first_name))}"
        )

        return log_message

    elif splitter[1] == "unpinall":
        admin_member = await chat.get_member(admin_user.id)

        if (
            not admin_member.status == ChatMemberStatus.OWNER
            and admin_user.id not in DRAGONS
        ):
            await query.answer("ᴏɴʟʏ ᴄʜᴀᴛ OWNER ᴄᴀɴ ᴜɴᴘɪɴ ᴀʟʟ ᴍᴇssᴀɢᴇs.")
            return

        try:
            if chat.is_forum:
                await bot.unpin_all_forum_topic_messages(
                    chat.id, message.message_thread_id
                )
            else:
                await bot.unpin_all_chat_messages(chat.id)
        except BadRequest as excp:
            if excp.message == "Chat_not_modified":
                pass
            else:
                raise

        await message.edit_text("ᴅᴏɴᴇ ᴜɴᴘɪɴɴᴇᴅ ᴀʟʟ ᴍᴇssᴀɢᴇs.")
        log_message = (
            f"<b>{html.escape(chat.title)}:</b>\n"
            f"#𝐔𝐍𝐏𝐈𝐍𝐍𝐄𝐃_𝐀𝐋𝐋\n"
            f"<b>ᴀᴅᴍɪɴ:</b> {mention_html(admin_user.id, html.escape(admin_user.first_name))}"
        )

        return log_message


__help__ = """
 • /admins*:* ʟɪsᴛ ᴏғ ᴀᴅᴍɪɴs ɪɴ ᴛʜᴇ ᴄʜᴀᴛ

*ᴀᴅᴍɪɴs ᴏɴʟʏ:*
 • /pin*:* sɪʟᴇɴᴛʟʏ ᴘɪɴs ᴛʜᴇ ᴍᴇssᴀɢᴇ ʀᴇᴘʟɪᴇᴅ ᴛᴏ - ᴀᴅᴅ `'loud'` ᴏʀ `'notify'` ᴛᴏ ɢɪᴠᴇ ɴᴏᴛɪғs ᴛᴏ ᴜsᴇʀs
 • /unpin*:* ᴜɴᴘɪɴs ᴛʜᴇ ᴄᴜʀʀᴇɴᴛʟʏ ᴘɪɴɴᴇᴅ ᴍᴇssᴀɢᴇ
 • /unpinall*:* ᴜɴᴘɪɴs ᴀʟʟ ᴛʜᴇ ᴘɪɴɴᴇᴅ ᴍᴇssᴀɢᴇ, ᴡᴏʀᴋs ɪɴ ᴛᴏᴘɪᴄs ᴛᴏᴏ (ᴏɴʟʏ OWNER ᴄᴀɴ ᴅᴏ.)
 • /invitelink*:* ɢᴇᴛs ɪɴᴠɪᴛᴇʟɪɴᴋ
 • /promote*:* ᴘʀᴏᴍᴏᴛᴇs ᴛʜᴇ ᴜsᴇʀ ʀᴇᴘʟɪᴇᴅ ᴛᴏ
 • /demote*:* ᴅᴇᴍᴏᴛᴇs ᴛʜᴇ ᴜsᴇʀ ʀᴇᴘʟɪᴇᴅ to
 • /title <ᴛɪᴛʟᴇ ʜᴇʀᴇ>*:* sᴇᴛs ᴀ ᴄᴜsᴛᴏᴍ ᴛɪᴛʟᴇ ғᴏʀ ᴀɴ ᴀᴅᴍɪɴ ᴛʜᴀᴛ ᴛʜᴇ ʙᴏᴛ ᴘʀᴏᴍᴏᴛᴇᴅ
 • /admincache*:* ғᴏʀᴄᴇ ʀᴇғʀᴇsʜ ᴛʜᴇ ᴀᴅᴍɪɴs ʟɪsᴛ
"""

ADMINLIST_HANDLER = DisableAbleCommandHandler("admins", adminlist, block=False)

PIN_HANDLER = CommandHandler("pin", pin, filters=filters.ChatType.GROUPS, block=False)
UNPIN_HANDLER = CommandHandler(
    "unpin", unpin, filters=filters.ChatType.GROUPS, block=False
)
UNPINALL_HANDLER = CommandHandler(
    "unpinall", unpinall, filters=filters.ChatType.GROUPS, block=False
)

INVITE_HANDLER = DisableAbleCommandHandler("invitelink", invite, block=False)

PROMOTE_HANDLER = DisableAbleCommandHandler("promote", promote, block=False)
DEMOTE_HANDLER = DisableAbleCommandHandler("demote", demote, block=False)

SET_TITLE_HANDLER = CommandHandler("title", set_title, block=False)
ADMIN_REFRESH_HANDLER = CommandHandler(
    "admincache", refresh_admin, filters=filters.ChatType.GROUPS, block=False
)
ADMIN_CALLBACK_HANDLER = CallbackQueryHandler(
    admin_callback, block=False, pattern=r"admin_"
)

application.add_handler(ADMINLIST_HANDLER)
application.add_handler(PIN_HANDLER)
application.add_handler(UNPIN_HANDLER)
application.add_handler(UNPINALL_HANDLER)
application.add_handler(INVITE_HANDLER)
application.add_handler(PROMOTE_HANDLER)
application.add_handler(DEMOTE_HANDLER)
application.add_handler(SET_TITLE_HANDLER)
application.add_handler(ADMIN_REFRESH_HANDLER)
application.add_handler(ADMIN_CALLBACK_HANDLER)

__mod_name__ = "𝐀ᴅᴍɪɴ"
__command_list__ = [
    "adminlist",
    "admins",
    "invitelink",
    "promote",
    "demote",
    "admincache",
]
__handlers__ = [
    ADMINLIST_HANDLER,
    PIN_HANDLER,
    UNPIN_HANDLER,
    INVITE_HANDLER,
    PROMOTE_HANDLER,
    DEMOTE_HANDLER,
    SET_TITLE_HANDLER,
    ADMIN_REFRESH_HANDLER,
]
