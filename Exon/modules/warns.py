import html
import re
from typing import Optional

from telegram import (
    CallbackQuery,
    Chat,
    ChatMemberAdministrator,
    ChatMemberOwner,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
    Update,
    User,
)
from telegram.constants import MessageLimit, ParseMode
from telegram.error import BadRequest
from telegram.ext import (
    ApplicationHandlerStop,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)
from telegram.helpers import mention_html

from Exon import BAN_STICKER, exon
from Exon.modules.disable import DisableAbleCommandHandler
from Exon.modules.helper_funcs.chat_status import check_admin, is_user_admin
from Exon.modules.helper_funcs.extraction import (
    extract_text,
    extract_user,
    extract_user_and_text,
)
from Exon.modules.helper_funcs.misc import split_message
from Exon.modules.helper_funcs.string_handling import split_quotes
from Exon.modules.log_channel import loggable
from Exon.modules.sql import warns_sql as sql
from Exon.modules.sql.approve_sql import is_approved

WARN_HANDLER_GROUP = 9
CURRENT_WARNING_FILTER_STRING = "<b>ᴄᴜʀʀᴇɴᴛ ᴡᴀʀɴɪɴɢ ғɪʟᴛᴇʀs ɪɴ ᴛʜɪs ᴄʜᴀᴛ:</b>\n"


# Not async
async def warn(
    user: User,
    chat: Chat,
    reason: str,
    message: Message,
    warner: User = None,
) -> str:
    if await is_user_admin(chat, user.id):
        await message.reply_text("ᴅᴀᴍɴ ᴀᴅᴍɪɴs, ᴛʜᴇʏ ᴀʀᴇ ᴛᴏᴏ ғᴀʀ ᴛᴏ ʙᴇ ᴡᴀʀɴᴇᴅ")
        return

    if warner:
        warner_tag = mention_html(warner.id, warner.first_name)
    else:
        warner_tag = "ᴀᴜᴛᴏᴍᴀᴛᴇᴅ ᴡᴀʀɴ ғɪʟᴛᴇʀ."

    limit, soft_warn = sql.get_warn_setting(chat.id)
    num_warns, reasons = sql.warn_user(user.id, chat.id, reason)
    if num_warns >= limit:
        sql.reset_warns(user.id, chat.id)
        if soft_warn:  # punch
            chat.unban_member(user.id)
            reply = (
                f"<code>❕</code><b>ᴋɪᴄᴋ ᴇᴠᴇɴᴛ</b>\n"
                f"<code> </code><b>• ᴜsᴇʀ:</b> {mention_html(user.id, user.first_name)}\n"
                f"<code> </code><b>• ᴄᴏᴜɴᴛ:</b> {limit}"
            )

        else:  # ban
            await chat.ban_member(user.id)
            reply = (
                f"<code>❕</code><b>ʙᴀɴ ᴇᴠᴇɴᴛ</b>\n"
                f"<code> </code><b>• ᴜsᴇʀ:</b> {mention_html(user.id, user.first_name)}\n"
                f"<code> </code><b>• ᴄᴏᴜɴᴛ:</b> {limit}"
            )

        for warn_reason in reasons:
            reply += f"\n - {html.escape(warn_reason)}"

        await message.reply_sticker(BAN_STICKER)  # Saitama's sticker
        keyboard = None
        log_reason = (
            f"<b>{html.escape(chat.title)}:</b>\n"
            f"#𝐖𝐀𝐑𝐍_𝐁𝐀𝐍\n"
            f"<b>ᴀᴅᴍɪɴ:</b> {warner_tag}\n"
            f"<b>ᴜsᴇʀ:</b> {mention_html(user.id, user.first_name)}\n"
            f"<b>ʀᴇᴀsᴏɴ:</b> {reason}\n"
            f"<b>ᴄᴏᴜɴᴛs:</b> <code>{num_warns}/{limit}</code>"
        )

    else:
        keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "ʀᴇᴍᴏᴠᴇ ᴡᴀʀɴ",
                        callback_data="rm_warn({})".format(user.id),
                    ),
                ],
            ],
        )

        reply = (
            f"<code>❕</code><b>ᴡᴀʀɴ ᴇᴠᴇɴᴛ</b>\n"
            f"<code> </code><b>• ᴜsᴇʀ:</b> {mention_html(user.id, user.first_name)}\n"
            f"<code> </code><b>• ᴄᴏᴜɴᴛ:</b> {num_warns}/{limit}"
        )
        if reason:
            reply += f"\n<code> </code><b>• ʀᴇᴀsᴏɴ:</b> {html.escape(reason)}"

        log_reason = (
            f"<b>{html.escape(chat.title)}:</b>\n"
            f"#𝐖𝐀𝐑𝐍\n"
            f"<b>ᴀᴅᴍɪɴ:</b> {warner_tag}\n"
            f"<b>ᴜsᴇʀ:</b> {mention_html(user.id, user.first_name)}\n"
            f"<b>ʀᴇᴀsᴏɴ:</b> {reason}\n"
            f"<b>ᴄᴏᴜɴᴛs:</b> <code>{num_warns}/{limit}</code>"
        )

    try:
        await message.reply_text(
            reply, reply_markup=keyboard, parse_mode=ParseMode.HTML
        )
    except BadRequest as excp:
        if excp.message == "ʀᴇᴘʟʏ ᴍᴇssᴀɢᴇ ɴᴏᴛ ғᴏᴜɴᴅ":
            # Do not reply
            await message.reply_text(
                reply,
                reply_markup=keyboard,
                parse_mode=ParseMode.HTML,
                quote=False,
            )
        else:
            raise
    return log_reason


@loggable
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    query: Optional[CallbackQuery] = update.callback_query
    user: Optional[User] = update.effective_user
    match = re.match(r"rm_warn\((.+?)\)", query.data)
    if match:
        user_id = match.group(1)
        chat: Optional[Chat] = update.effective_chat
        chat_member = await chat.get_member(user.id)
        if isinstance(chat_member, (ChatMemberAdministrator, ChatMemberOwner)):
            pass
        else:
            await query.answer("ʏᴏᴜ ɴᴇᴇᴅ ᴛᴏ ʙᴇ ᴀᴅᴍɪɴ ᴛᴏ ᴅᴏ ᴛʜɪs!")
            return
        res = sql.remove_warn(user_id, chat.id)
        if res:
            await update.effective_message.edit_text(
                "ᴡᴀʀɴ ʀᴇᴍᴏᴠᴇᴅ ʙʏ {}.".format(mention_html(user.id, user.first_name)),
                parse_mode=ParseMode.HTML,
            )
            user_member = await chat.get_member(user_id)
            return (
                f"<b>{html.escape(chat.title)}:</b>\n"
                f"#𝐔𝐍𝐖𝐀𝐑𝐍\n"
                f"<b>ᴀᴅᴍɪɴ:</b> {mention_html(user.id, user.first_name)}\n"
                f"<b>ᴜsᴇʀ:</b> {mention_html(user_member.user.id, user_member.user.first_name)}"
            )
        else:
            await update.effective_message.edit_text(
                "ᴜsᴇʀ ᴀʟʀᴇᴀᴅʏ ʜᴀs ɴᴏ ᴡᴀʀɴs.",
                parse_mode=ParseMode.HTML,
            )

    return ""


@loggable
@check_admin(permission="can_restrict_members", is_both=True)
async def warn_user(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    args = context.args
    message: Optional[Message] = update.effective_message
    chat: Optional[Chat] = update.effective_chat
    warner: Optional[User] = update.effective_user

    user_id, reason = await extract_user_and_text(message, context, args)
    if (
        message.text.startswith("/d")
        and message.reply_to_message
        and not message.reply_to_message.forum_topic_created
    ):
        await message.reply_to_message.delete()
    if user_id:
        if (
            message.reply_to_message
            and message.reply_to_message.from_user.id == user_id
        ):
            return await warn(
                message.reply_to_message.from_user,
                chat,
                reason,
                message.reply_to_message,
                warner,
            )
        else:
            member = await chat.get_member(user_id)
            return await warn(member.user, chat, reason, message, warner)
    else:
        await message.reply_text("ᴛʜᴀᴛ ʟᴏᴏᴋs ʟɪᴋᴇ ᴀɴ ɪɴᴠᴀʟɪᴅ ᴜsᴇʀ ID ᴛᴏ ᴍᴇ.")
    return ""


@loggable
@check_admin(is_both=True)
async def reset_warns(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    args = context.args
    message: Optional[Message] = update.effective_message
    chat: Optional[Chat] = update.effective_chat
    user: Optional[User] = update.effective_user

    user_id = await extract_user(message, context, args)

    if user_id:
        sql.reset_warns(user_id, chat.id)
        await message.reply_text("Warns have been reset!")
        warned = await chat.get_member(user_id).user
        return (
            f"<b>{html.escape(chat.title)}:</b>\n"
            f"#𝐑𝐄𝐒𝐄𝐓-𝐖𝐀𝐑𝐍𝐒\n"
            f"<b>ᴀᴅᴍɪɴ:</b> {mention_html(user.id, user.first_name)}\n"
            f"<b>ᴜsᴇʀ:</b> {mention_html(warned.id, warned.first_name)}"
        )
    else:
        await message.reply_text("ɴᴏ ᴜsᴇʀ ʜᴀs ʙᴇᴇɴ ᴅᴇsɪɢɴᴀᴛᴇᴅ!")
    return ""


async def warns(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    message: Optional[Message] = update.effective_message
    chat: Optional[Chat] = update.effective_chat
    user_id = await extract_user(message, context, args) or update.effective_user.id
    result = sql.get_warns(user_id, chat.id)

    if result and result[0] != 0:
        num_warns, reasons = result
        limit, soft_warn = sql.get_warn_setting(chat.id)

        if reasons:
            text = (
                f"ᴛʜɪs ᴜsᴇʀ ʜᴀs {num_warns}/{limit} ᴡᴀʀɴs, ғᴏʀ ᴛʜᴇ ғᴏʟʟᴏᴡɪɴɢ ʀᴇᴀsᴏɴs:"
            )
            for reason in reasons:
                text += f"\n • {reason}"

            msgs = split_message(text)
            for msg in msgs:
                await update.effective_message.reply_text(msg)
        else:
            await update.effective_message.reply_text(
                f"ᴜsᴇʀ ʜᴀs {num_warns}/{limit} ᴡᴀʀɴs, ʙᴜᴛ ɴᴏ ʀᴇᴀsᴏɴs ғᴏʀ ᴀɴʏ ᴏғ ᴛʜᴇᴍ.",
            )
    else:
        await update.effective_message.reply_text("ᴛʜɪs ᴜsᴇʀ ᴅᴏᴇsɴ'ᴛ ʜᴀᴠᴇ ᴀɴʏ ᴡᴀʀɴs!")


# Dispatcher handler stop - do not async
@check_admin(is_user=True)
async def add_warn_filter(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat: Optional[Chat] = update.effective_chat
    msg: Optional[Message] = update.effective_message

    args = msg.text.split(
        None,
        1,
    )  # use python's maxsplit to separate Cmd, keyword, and reply_text

    if len(args) < 2:
        return

    extracted = split_quotes(args[1])

    if len(extracted) >= 2:
        # set trigger -> lower, so as to avoid adding duplicate filters with different cases
        keyword = extracted[0].lower()
        content = extracted[1]

    else:
        return

    # Note: perhaps handlers can be removed somehow using sql.get_chat_filters
    for handler in exon.handlers.get(WARN_HANDLER_GROUP, []):
        if handler.filters == (keyword, chat.id):
            exon.remove_handler(handler, WARN_HANDLER_GROUP)

    sql.add_warn_filter(chat.id, keyword, content)

    await update.effective_message.reply_text(f"ᴡᴀʀɴ ʜᴀɴᴅʟᴇʀ ᴀᴅᴅᴇᴅ ғᴏʀ '{keyword}'!")
    raise ApplicationHandlerStop


@check_admin(is_user=True)
async def remove_warn_filter(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat: Optional[Chat] = update.effective_chat
    msg: Optional[Message] = update.effective_message

    args = msg.text.split(
        None,
        1,
    )  # use python's maxsplit to separate Cmd, keyword, and reply_text

    if len(args) < 2:
        return

    extracted = split_quotes(args[1])

    if len(extracted) < 1:
        return

    to_remove = extracted[0]

    chat_filters = sql.get_chat_warn_triggers(chat.id)

    if not chat_filters:
        await msg.reply_text("ɴᴏ ᴡᴀʀɴɪɴɢ ғɪʟᴛᴇʀs ᴀʀᴇ ᴀᴄᴛɪᴠᴇ ʜᴇʀᴇ!")
        return

    for filt in chat_filters:
        if filt == to_remove:
            sql.remove_warn_filter(chat.id, to_remove)
            await msg.reply_text("ᴏᴋᴀʏ, I'ʟʟ sᴛᴏᴘ ᴡᴀʀɴɪɴɢ ᴘᴇᴏᴘʟᴇ ғᴏʀ ᴛʜᴀᴛ.")
            raise ApplicationHandlerStop

    await msg.reply_text(
        "ᴛʜᴀᴛ's ɴᴏᴛ ᴀ ᴄᴜʀʀᴇɴᴛ ᴡᴀʀɴɪɴɢ ғɪʟᴛᴇʀ - ʀᴜɴ /warnlist ғᴏʀ ᴀʟʟ ᴀᴄᴛɪᴠᴇ ᴡᴀʀɴɪɴɢ ғɪʟᴛᴇʀs.",
    )


async def list_warn_filters(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat: Optional[Chat] = update.effective_chat
    all_handlers = sql.get_chat_warn_triggers(chat.id)

    if not all_handlers:
        await update.effective_message.reply_text("ɴᴏ ᴡᴀʀɴɪɴɢ ғɪʟᴛᴇʀs ᴀʀᴇ ᴀᴄᴛɪᴠᴇ ʜᴇʀᴇ!")
        return

    filter_list = CURRENT_WARNING_FILTER_STRING
    for keyword in all_handlers:
        entry = f" - {html.escape(keyword)}\n"
        if len(entry) + len(filter_list) > MessageLimit.MAX_TEXT_LENGTH:
            await update.effective_message.reply_text(
                filter_list, parse_mode=ParseMode.HTML
            )
            filter_list = entry
        else:
            filter_list += entry

    if filter_list != CURRENT_WARNING_FILTER_STRING:
        await update.effective_message.reply_text(
            filter_list, parse_mode=ParseMode.HTML
        )


@loggable
async def reply_filter(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    chat: Optional[Chat] = update.effective_chat
    message: Optional[Message] = update.effective_message
    user: Optional[User] = update.effective_user

    if not user:  # Ignore channel
        return

    if user.id == 777000:
        return
    if is_approved(chat.id, user.id):
        return
    chat_warn_filters = sql.get_chat_warn_triggers(chat.id)
    to_match = await extract_text(message)
    if not to_match:
        return ""

    for keyword in chat_warn_filters:
        pattern = r"( |^|[^\w])" + re.escape(keyword) + r"( |$|[^\w])"
        if re.search(pattern, to_match, flags=re.IGNORECASE):
            user: Optional[User] = update.effective_user
            warn_filter = sql.get_warn_filter(chat.id, keyword)
            return await warn(user, chat, warn_filter.reply, message)
    return ""


@check_admin(is_user=True)
@loggable
async def set_warn_limit(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    args = context.args
    chat: Optional[Chat] = update.effective_chat
    user: Optional[User] = update.effective_user
    msg: Optional[Message] = update.effective_message

    if args:
        if args[0].isdigit():
            if int(args[0]) < 3:
                await msg.reply_text("ᴛʜᴇ ᴍɪɴɪᴍᴜᴍ ᴡᴀʀɴ ʟɪᴍɪᴛ ɪs 3!")
            else:
                sql.set_warn_limit(chat.id, int(args[0]))
                await msg.reply_text("ᴜᴘᴅᴀᴛᴇᴅ the warn limit to {}".format(args[0]))
                return (
                    f"<b>{html.escape(chat.title)}:</b>\n"
                    f"#SET_WARN_LIMIT\n"
                    f"<b>ᴀᴅᴍɪɴ:</b> {mention_html(user.id, user.first_name)}\n"
                    f"sᴇᴛ ᴛʜᴇ ᴡᴀʀɴ ʟɪᴍɪᴛ ᴛᴏ <code>{args[0]}</code>"
                )
        else:
            await msg.reply_text("ɢɪᴠᴇ ᴍᴇ ᴀ ɴᴜᴍʙᴇʀ ᴀs ᴀɴ ᴀʀɢ!")
    else:
        limit, soft_warn = sql.get_warn_setting(chat.id)

        await msg.reply_text("ᴛʜᴇ ᴄᴜʀʀᴇɴᴛ ᴡᴀʀɴ ʟɪᴍɪᴛ ɪs {}".format(limit))
    return ""


@check_admin(is_user=True)
async def set_warn_strength(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    chat: Optional[Chat] = update.effective_chat
    user: Optional[User] = update.effective_user
    msg: Optional[Message] = update.effective_message

    if args:
        if args[0].lower() in ("on", "yes"):
            sql.set_warn_strength(chat.id, False)
            await msg.reply_text("ᴛᴏᴏ ᴍᴀɴʏ ᴡᴀʀɴs ᴡɪʟʟ ɴᴏᴡ ʀᴇsᴜʟᴛ ɪɴ ᴀ ʙᴀɴ!")
            return (
                f"<b>{html.escape(chat.title)}:</b>\n"
                f"<b>ᴀᴅᴍɪɴ:</b> {mention_html(user.id, user.first_name)}\n"
                f"ʜᴀs ᴇɴᴀʙʟᴇᴅ sᴛʀᴏɴɢ ᴡᴀʀɴs. ᴜsᴇʀs ᴡɪʟʟ ʙᴇ sᴇʀɪᴏᴜsʟʏ ᴋɪᴄᴋᴇᴅ.(ʙᴀɴɴᴇᴅ)"
            )

        elif args[0].lower() in ("off", "no"):
            sql.set_warn_strength(chat.id, True)
            await msg.reply_text(
                "ᴛᴏᴏ ᴍᴀɴʏ ᴡᴀʀɴs ᴡɪʟʟ ɴᴏᴡ ʀᴇsᴜʟᴛ ɪɴ ᴀ ɴᴏʀᴍᴀʟ ᴋɪᴄᴋ! ᴜsᴇʀs ᴡɪʟʟ ʙᴇ ᴀʙʟᴇ ᴛᴏ ᴊᴏɪɴ ᴀɢᴀɪɴ ᴀғᴛᴇʀ.",
            )
            return (
                f"<b>{html.escape(chat.title)}:</b>\n"
                f"<b>ᴀᴅᴍɪɴ:</b> {mention_html(user.id, user.first_name)}\n"
                f"ʜᴀs ᴅɪsᴀʙʟᴇᴅ sᴛʀᴏɴɢ ᴋɪᴄᴋs. ɪ ᴡɪʟʟ ᴜsᴇ ɴᴏʀᴍᴀʟ ᴋɪᴄᴋ on ᴜsᴇʀs."
            )

        else:
            await msg.reply_text("I only understand on/yes/no/off!")
    else:
        limit, soft_warn = sql.get_warn_setting(chat.id)
        if soft_warn:
            await msg.reply_text(
                "ᴡᴀʀɴs ᴀʀᴇ ᴄᴜʀʀᴇɴᴛʟʏ sᴇᴛ ᴛᴏ *ᴋɪᴄᴋ* ᴜsᴇʀs ᴡʜᴇɴ ᴛʜᴇʏ ᴇxᴄᴇᴇᴅ ᴛʜᴇ ʟɪᴍɪᴛs.",
                parse_mode=ParseMode.MARKDOWN,
            )
        else:
            await msg.reply_text(
                "ᴡᴀʀɴs ᴀʀᴇ ᴄᴜʀʀᴇɴᴛʟʏ sᴇᴛ ᴛᴏ *ʙᴀɴ* ᴜsᴇʀs ᴡʜᴇɴ ᴛʜᴇʏ ᴇxᴄᴇᴇᴅ ᴛʜᴇ ʟɪᴍɪᴛs.",
                parse_mode=ParseMode.MARKDOWN,
            )
    return ""


def __stats__():
    return (
        f"• {sql.num_warns()} ᴏᴠᴇʀᴀʟʟ ᴡᴀʀɴs, ᴀᴄʀᴏss {sql.num_warn_chats()} ᴄʜᴀᴛs.\n"
        f"• {sql.num_warn_filters()} ᴡᴀʀɴ ғɪʟᴛᴇʀs, ᴀᴄʀᴏss {sql.num_warn_filter_chats()} ᴄʜᴀᴛs."
    )


async def __import_data__(chat_id, data, message):
    for user_id, count in data.get("warns", {}).items():
        for x in range(int(count)):
            sql.warn_user(user_id, chat_id)


def __migrate__(old_chat_id, new_chat_id):
    sql.migrate_chat(old_chat_id, new_chat_id)


def __chat_settings__(chat_id, user_id):
    num_warn_filters = sql.num_warn_chat_filters(chat_id)
    limit, soft_warn = sql.get_warn_setting(chat_id)
    return (
        f"ᴛʜɪs ᴄʜᴀᴛ ʜᴀs `{num_warn_filters}` ᴡᴀʀɴ ғɪʟᴛᴇʀs. "
        f"ɪᴛ ᴛᴀᴋᴇs `{limit}` ᴡᴀʀɴs ʙᴇғᴏʀᴇ ᴛʜᴇ ᴜsᴇʀ ɢᴇᴛs *{'kicked' if soft_warn else 'banned'}*."
    )


__help__ = """
 • /warns <ᴜsᴇʀʜᴀɴᴅʟᴇ>*:* ɢᴇᴛ ᴀ ᴜsᴇʀ's ɴᴜᴍʙᴇʀ, ᴀɴᴅ ʀᴇᴀsᴏɴ, ᴏғ ᴡᴀʀɴs.
 • /warnlist*:* ʟɪsᴛ ᴏғ ᴀʟʟ ᴄᴜʀʀᴇɴᴛ ᴡᴀʀɴɪɴɢ ғɪʟᴛᴇʀs

*ᴀᴅᴍɪɴs ᴏɴʟʏ:*
 • /warn <ᴜsᴇʀʜᴀɴᴅʟᴇ>*:* ᴡᴀʀɴ a user. ᴀғᴛᴇʀ 3 ᴡᴀʀɴs, ᴛʜᴇ ᴜsᴇʀ ᴡɪʟʟ ʙᴇ ʙᴀɴɴᴇᴅ ғʀᴏᴍ ᴛʜᴇ ɢʀᴏᴜᴘ. ᴄᴀɴ ᴀʟsᴏ ʙᴇ ᴜsᴇᴅ ᴀs ᴀ ʀᴇᴘʟʏ.
 • /dwarn <ᴜsᴇʀʜᴀɴᴅʟᴇ>*:* ᴡᴀʀɴ ᴀ ᴜsᴇʀ ᴀɴᴅ ᴅᴇʟᴇᴛᴇ ᴛʜᴇ message. ᴀғᴛᴇʀ 3 ᴡᴀʀɴs, ᴛʜᴇ ᴜsᴇʀ ᴡɪʟʟ ʙᴇ ʙᴀɴɴᴇᴅ ғʀᴏᴍ ᴛʜᴇ ɢʀᴏᴜᴘ. ᴄᴀɴ ᴀʟsᴏ ʙᴇ ᴜsᴇᴅ ᴀs ᴀ ʀᴇᴘʟʏ.
 • /resetwarn <userhandle>*:* ʀᴇsᴇᴛ ᴛʜᴇ ᴡᴀʀɴs ғᴏʀ ᴀ ᴜsᴇʀ. ᴄᴀɴ ᴀʟsᴏ ʙᴇ ᴜsᴇᴅ ᴀs ᴀ ʀᴇᴘʟʏ.
 • /addwarn <ᴋᴇʏᴡᴏʀᴅ> <ʀᴇᴘʟʏ ᴍᴇssᴀɢᴇ>*:* sᴇᴛ ᴀ ᴡᴀʀɴɪɴɢ ғɪʟᴛᴇʀ on ᴀ ᴄᴇʀᴛᴀɪɴ ᴋᴇʏᴡᴏʀᴅ. ɪғ ʏᴏᴜ ᴡᴀɴᴛ ʏᴏᴜʀ ᴋᴇʏᴡᴏʀᴅ ᴛᴏ \
ʙᴇ ᴀ sᴇɴᴛᴇɴᴄᴇ, ᴇɴᴄᴏᴍᴘᴀss ɪᴛ ᴡɪᴛʜ ǫᴜᴏᴛᴇs, as such: `/addwarn "very angry" ᴛʜɪs ɪs ᴀɴ ᴀɴɢʀʏ user`.
 • /nowarn <ᴋᴇʏᴡᴏʀᴅ>*:* sᴛᴏᴘ ᴀ ᴡᴀʀɴɪɴɢ ғɪʟᴛᴇʀ
 • /warnlimit <ɴᴜᴍ>*:* sᴇᴛ ᴛʜᴇ ᴡᴀʀɴɪɴɢ limit
 • /strongwarn <on/yes/off/no>*:* ɪғ sᴇᴛ ᴛᴏ ᴏɴ, ᴇxᴄᴇᴇᴅɪɴɢ ᴛʜᴇ ᴡᴀʀɴ ʟɪᴍɪᴛ ᴡɪʟʟ ʀᴇsᴜʟᴛ ɪɴ ᴀ ʙᴀɴ. ᴇʟsᴇ, ᴡɪʟʟ ᴊᴜsᴛ ᴋɪᴄᴋ.
"""

__mod_name__ = "𝐖ᴀʀɴs"

WARN_HANDLER = CommandHandler(
    ["warn", "dwarn"], warn_user, filters=filters.ChatType.GROUPS
)
RESET_WARN_HANDLER = CommandHandler(
    ["resetwarn", "resetwarns"],
    reset_warns,
    filters=filters.ChatType.GROUPS
)
CALLBACK_QUERY_HANDLER = CallbackQueryHandler(button, pattern=r"rm_warn", block=False)
MYWARNS_HANDLER = DisableAbleCommandHandler(
    "warns", warns, filters=filters.ChatType.GROUPS
)
ADD_WARN_HANDLER = CommandHandler(
    "addwarn", add_warn_filter, filters=filters.ChatType.GROUPS
)
RM_WARN_HANDLER = CommandHandler(
    ["nowarn", "stopwarn"],
    remove_warn_filter,
    filters=filters.ChatType.GROUPS,
)
LIST_WARN_HANDLER = DisableAbleCommandHandler(
    ["warnlist", "warnfilters"],
    list_warn_filters,
    filters=filters.ChatType.GROUPS,
    admin_ok=True,
)
WARN_FILTER_HANDLER = MessageHandler(
    filters.TEXT & filters.ChatType.GROUPS, reply_filter
)
WARN_LIMIT_HANDLER = CommandHandler(
    "warnlimit", set_warn_limit, filters=filters.ChatType.GROUPS
)
WARN_STRENGTH_HANDLER = CommandHandler(
    "strongwarn", set_warn_strength, filters=filters.ChatType.GROUPS
)

exon.add_handler(WARN_HANDLER)
exon.add_handler(CALLBACK_QUERY_HANDLER)
exon.add_handler(RESET_WARN_HANDLER)
exon.add_handler(MYWARNS_HANDLER)
exon.add_handler(ADD_WARN_HANDLER)
exon.add_handler(RM_WARN_HANDLER)
exon.add_handler(LIST_WARN_HANDLER)
exon.add_handler(WARN_LIMIT_HANDLER)
exon.add_handler(WARN_STRENGTH_HANDLER)
exon.add_handler(WARN_FILTER_HANDLER, WARN_HANDLER_GROUP)
