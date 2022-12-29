import html
import random
import re
import time
from contextlib import suppress
from functools import partial

from telegram import ChatPermissions, InlineKeyboardButton, InlineKeyboardMarkup, Update

# from Exon.modules.sql.topics_sql import get_action_topic
from telegram.constants import ParseMode
from telegram.error import BadRequest
from telegram.ext import (
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)
from telegram.helpers import escape_markdown, mention_html, mention_markdown

import Exon
import Exon.modules.sql.welcome_sql as sql
from Exon import DEV_USERS, DRAGONS, EVENT_LOGS, LOGGER, OWNER_ID, application
from Exon.modules.helper_funcs.chat_status import check_admin, is_user_ban_protected
from Exon.modules.helper_funcs.misc import build_keyboard, revert_buttons
from Exon.modules.helper_funcs.msg_types import get_welcome_type
from Exon.modules.helper_funcs.string_handling import (
    escape_invalid_curly_brackets,
    markdown_parser,
    markdown_to_html,
)
from Exon.modules.log_channel import loggable
from Exon.modules.sql.global_bans_sql import is_user_gbanned

VALID_WELCOME_FORMATTERS = [
    "first",
    "last",
    "fullname",
    "username",
    "id",
    "count",
    "chatname",
    "mention",
]

ENUM_FUNC_MAP = {
    sql.Types.TEXT.value: application.bot.send_message,
    sql.Types.BUTTON_TEXT.value: application.bot.send_message,
    sql.Types.STICKER.value: application.bot.send_sticker,
    sql.Types.DOCUMENT.value: application.bot.send_document,
    sql.Types.PHOTO.value: application.bot.send_photo,
    sql.Types.AUDIO.value: application.bot.send_audio,
    sql.Types.VOICE.value: application.bot.send_voice,
    sql.Types.VIDEO.value: application.bot.send_video,
}

VERIFIED_USER_WAITLIST = {}


# do not async
async def send(update: Update, message, keyboard, backup_message):
    chat = update.effective_chat
    cleanserv = sql.clean_service(chat.id)
    reply = update.effective_message.message_id
    # topic_chat = get_action_topic(chat.id)
    # Clean service welcome
    if cleanserv:
        try:
            await application.bot.delete_message(chat.id, update.message.message_id)
        except BadRequest:
            pass
        reply = False
    try:
        try:
            msg = await application.bot.send_message(
                chat.id,
                markdown_to_html(message),
                parse_mode=ParseMode.HTML,
                reply_markup=keyboard,
            )
        except:
            msg = await update.effective_message.reply_text(
                markdown_to_html(message),
                parse_mode=ParseMode.HTML,
                reply_markup=keyboard,
                reply_to_message_id=reply,
            )
    except BadRequest as excp:
        if excp.message == "ʀᴇᴘʟʏ ᴍᴇssᴀɢᴇ ɴᴏᴛ ғᴏᴜɴᴅ":
            msg = await update.effective_message.reply_text(
                markdown_to_html(message),
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=keyboard,
                quote=False,
            )
        elif excp.message == "Button_url_invalid":
            try:
                msg = await application.bot.send_message(
                    chat.id,
                    markdown_parser(
                        backup_message
                        + "\nɴᴏᴛᴇ: ᴛʜᴇ ᴄᴜʀʀᴇɴᴛ ᴍᴇssᴀɢᴇ ʜᴀs ᴀɴ ɪɴᴠᴀʟɪᴅ ᴜʀʟ "
                        "ɪɴ ᴏɴᴇ ᴏғ ɪᴛs ʙᴜᴛᴛᴏɴs. ᴘʟᴇᴀsᴇ ᴜᴘᴅᴀᴛᴇ.",
                    ),
                    parse_mode=ParseMode.MARKDOWN,
                )
            except:
                msg = await update.effective_message.reply_text(
                    markdown_parser(
                        backup_message
                        + "\ɴɴᴏᴛᴇ: ᴛʜᴇ ᴄᴜʀʀᴇɴᴛ ᴍᴇssᴀɢᴇ ʜᴀs ᴀɴ ɪɴᴠᴀʟɪᴅ ᴜʀʟ "
                        "ɪɴ ᴏɴᴇ ᴏғ ɪᴛs ʙᴜᴛᴛᴏɴs. ᴘʟᴇᴀsᴇ ᴜᴘᴅᴀᴛᴇ.",
                    ),
                    parse_mode=ParseMode.MARKDOWN,
                    reply_to_message_id=reply,
                )
        elif excp.message == "ᴜɴsᴜᴘᴘᴏʀᴛᴇᴅ ᴜʀʟ ᴘʀᴏᴛᴏᴄᴏʟ":
            try:
                msg = await application.bot.send_message(
                    chat.id,
                    markdown_parser(
                        backup_message
                        + "\nɴᴏᴛᴇ: ᴛʜᴇ ᴄᴜʀʀᴇɴᴛ ᴍᴇssᴀɢᴇ ʜᴀs ʙᴜᴛᴛᴏɴs ᴡʜɪᴄʜ "
                        "ᴜsᴇ ᴜʀʟ ᴘʀᴏᴛᴏᴄᴏʟs ᴛʜᴀᴛ ᴀʀᴇ ᴜɴsᴜᴘᴘᴏʀᴛᴇᴅ ʙʏ "
                        "ᴛᴇʟᴇɢʀᴀᴍ. ᴘʟᴇᴀsᴇ ᴜᴘᴅᴀᴛᴇ.",
                    ),
                    parse_mode=ParseMode.MARKDOWN,
                )
            except:
                msg = await update.effective_message.reply_text(
                    markdown_parser(
                        backup_message
                        + "\nɴᴏᴛᴇ: ᴛʜᴇ ᴄᴜʀʀᴇɴᴛ ᴍᴇssᴀɢᴇ ʜᴀs ʙᴜᴛᴛᴏɴs ᴡʜɪᴄʜ "
                        "ᴜsᴇ ᴜʀʟ ᴘʀᴏᴛᴏᴄᴏʟs ᴛʜᴀᴛ ᴀʀᴇ ᴜɴsᴜᴘᴘᴏʀᴛᴇᴅ ʙʏ "
                        "ᴛᴇʟᴇɢʀᴀᴍ. ᴘʟᴇᴀsᴇ ᴜᴘᴅᴀᴛᴇ.",
                    ),
                    parse_mode=ParseMode.MARKDOWN,
                    reply_to_message_id=reply,
                )
        elif excp.message == "ᴡʀᴏɴɢ ᴜʀʟ ʜᴏsᴛ":
            try:
                msg = await application.bot.send_message(
                    chat.id,
                    markdown_parser(
                        backup_message
                        + "\nɴᴏᴛᴇ: ᴛʜᴇ ᴄᴜʀʀᴇɴᴛ ᴍᴇssᴀɢᴇ ʜᴀs sᴏᴍᴇ ʙᴀᴅ ᴜʀʟs. "
                        "ᴘʟᴇᴀsᴇ ᴜᴘᴅᴀᴛᴇ.",
                    ),
                    parse_mode=ParseMode.MARKDOWN,
                )
            except:
                msg = await update.effective_message.reply_text(
                    markdown_parser(
                        backup_message
                        + "\nɴᴏᴛᴇ: ᴛʜᴇ ᴄᴜʀʀᴇɴᴛ ᴍᴇssᴀɢᴇ ʜᴀs sᴏᴍᴇ ʙᴀᴅ ᴜʀʟs. "
                        "ᴘʟᴇᴀsᴇ ᴜᴘᴅᴀᴛᴇ.",
                    ),
                    parse_mode=ParseMode.MARKDOWN,
                    reply_to_message_id=reply,
                )
            LOGGER.warning(message)
            LOGGER.warning(keyboard)
            LOGGER.exception("ᴄᴏᴜʟᴅ ɴᴏᴛ ᴘᴀʀsᴇ! ɢᴏᴛ ɪɴᴠᴀʟɪᴅ ᴜʀʟ ʜᴏsᴛ ᴇʀʀᴏʀs")
        elif excp.message == "ʜᴀᴠᴇ ɴᴏ ʀɪɢʜᴛs ᴛᴏ sᴇɴᴅ ᴀ ᴍᴇssᴀɢᴇ":
            return
        else:
            try:
                msg = await application.bot.send_message(
                    chat.id,
                    markdown_parser(
                        backup_message + "\nɴᴏᴛᴇ: ᴀɴ ᴇʀʀᴏʀ ᴏᴄᴄᴜʀᴇᴅ ᴡʜᴇɴ sᴇɴᴅɪɴɢ ᴛʜᴇ "
                        "ᴄᴜsᴛᴏᴍ ᴍᴇssᴀɢᴇ. ᴘʟᴇᴀsᴇ ᴜᴘᴅᴀᴛᴇ.",
                    ),
                    parse_mode=ParseMode.MARKDOWN,
                )
            except:
                msg = await update.effective_message.reply_text(
                    markdown_parser(
                        backup_message + "\nɴᴏᴛᴇ: ᴀɴ ᴇʀʀᴏʀ ᴏᴄᴄᴜʀᴇᴅ ᴡʜᴇɴ sᴇɴᴅɪɴɢ ᴛʜᴇ "
                        "ᴄᴜsᴛᴏᴍ ᴍᴇssᴀɢᴇ. ᴘʟᴇᴀsᴇ ᴜᴘᴅᴀᴛᴇ.",
                    ),
                    parse_mode=ParseMode.MARKDOWN,
                    reply_to_message_id=reply,
                )
            LOGGER.exception()
    return msg


@loggable
async def new_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bot, job_queue = context.bot, context.job_queue
    chat = update.effective_chat
    user = update.effective_user
    msg = update.effective_message

    # topic_chat = get_action_topic(chat.id)

    should_welc, cust_welcome, cust_content, welc_type = sql.get_welc_pref(chat.id)
    welc_mutes = sql.welcome_mutes(chat.id)
    human_checks = sql.get_human_checks(user.id, chat.id)

    new_members = update.effective_message.new_chat_members

    for new_mem in new_members:

        if new_mem.id == bot.id and not Exon.ALLOW_CHATS:
            with suppress(BadRequest):
                await update.effective_message.reply_text(
                    f"ɢʀᴏᴜᴘs ᴀʀᴇ ᴅɪsᴀʙʟᴇᴅ ғᴏʀ {bot.first_name}, ɪ'ᴍ ᴏᴜᴛᴛᴀ ʜᴇʀᴇ."
                )
            await bot.leave_chat(update.effective_chat.id)
            return

        welcome_log = None
        res = None
        sent = None
        should_mute = True
        welcome_bool = True
        media_wel = False

        if is_user_gbanned(new_mem.id):
            return

        if should_welc:

            reply = update.message.message_id
            cleanserv = sql.clean_service(chat.id)
            # Clean service welcome
            if cleanserv:
                try:
                    await application.bot.delete_message(
                        chat.id, update.message.message_id
                    )
                except BadRequest:
                    pass
                reply = False

            # Give the owner a special welcome
            if new_mem.id == OWNER_ID:
                await update.effective_message.reply_text(
                    "ᴏʜ, ᴅᴀʀʟɪɴɢ ɪ ʜᴀᴠᴇ sᴇᴀʀᴄʜᴇᴅ ғᴏʀ ʏᴏᴜ ᴇᴠᴇʀʏᴡʜᴇʀᴇ",
                    reply_to_message_id=reply,
                )
                welcome_log = (
                    f"{html.escape(chat.title)}\n"
                    f"#𝐔𝐒𝐄𝐑_𝐉𝐎𝐈𝐍𝐄𝐃\n"
                    f"ʙᴏᴛ ᴏᴡɴᴇʀ ᴊᴜsᴛ ᴊᴏɪɴᴇᴅ ᴛʜᴇ ɢʀᴏᴜᴘ"
                )
                continue

            # Welcome Devs
            elif new_mem.id in DEV_USERS:
                await update.effective_message.reply_text(
                    "ʙᴇ ᴄᴏᴏʟ! ᴀ ᴍᴇᴍʙᴇʀ ᴏғ ᴛʜᴇ ᴛᴇᴀᴍ ᴀʙɪsʜɴᴏɪ ᴊᴜsᴛ ᴊᴏɪɴᴇᴅ.",
                    reply_to_message_id=reply,
                )
                welcome_log = (
                    f"{html.escape(chat.title)}\n"
                    f"#𝐔𝐒𝐄𝐑_𝐉𝐎𝐈𝐍𝐄𝐃\n"
                    f"ʙᴏᴛ ᴅᴇᴠ ᴊᴜsᴛ ᴊᴏɪɴᴇᴅ ᴛʜᴇ ɢʀᴏᴜᴘ"
                )
                continue

            # Welcome Sudos
            elif new_mem.id in DRAGONS:
                await update.effective_message.reply_text(
                    "ᴡʜᴏᴀ! ᴀ ᴅʀᴀɢᴏɴ ᴅɪsᴀsᴛᴇʀ ᴊᴜsᴛ ᴊᴏɪɴᴇᴅ! sᴛᴀʏ ᴀʟᴇʀᴛ !",
                    reply_to_message_id=reply,
                )
                welcome_log = (
                    f"{html.escape(chat.title)}\n"
                    f"#𝐔𝐒𝐄𝐑_𝐉𝐎𝐈𝐍𝐄𝐃\n"
                    f"ʙᴏᴛ sᴜᴅᴏ ᴊᴜsᴛ ᴊᴏɪɴᴇᴅ ᴛʜᴇ ɢʀᴏᴜᴘ"
                )
                continue

            # ᴡᴇʟᴄᴏᴍᴇ ʏᴏᴜʀsᴇʟғ
            elif new_mem.id == bot.id:
                creator = None
                for x in await bot.get_chat_administrators(update.effective_chat.id):
                    if x.status == "creator":
                        creator = x.user
                        break
                if creator:
                    reply = f"""#𝐍𝐄𝐖𝐆𝐑𝐎𝐔𝐏 \
                        \nɪᴅ:   `{chat.id}` \
                    """

                    if chat.title:
                        reply += f"\nɢʀᴏᴜᴘ ɴᴀᴍᴇ:   **{escape_markdown(chat.title)}**"

                    if chat.username:
                        reply += f"\nᴜsᴇʀɴᴀᴍᴇ: @{escape_markdown(chat.username)}"

                    reply += f"\nᴄʀᴇᴀᴛᴏʀ ɪᴅ:   `{creator.id}`"

                    if creator.username:
                        reply += f"\nᴄʀᴇᴀᴛᴏʀ ᴜsᴇʀɴᴀᴍᴇ: @{creator.username}"

                    await bot.send_message(
                        EVENT_LOGS,
                        reply,
                        parse_mode="markdown",
                    )
                else:
                    await bot.send_message(
                        EVENT_LOGS,
                        "#𝐍𝐄𝐖_𝐆𝐑𝐎𝐔𝐏\n<b>ɢʀᴏᴜᴘ ɴᴀᴍᴇ:</b> {}\n<b>ɪᴅ:</b> <code>{}</code>".format(
                            html.escape(chat.title),
                            chat.id,
                        ),
                        parse_mode=ParseMode.HTML,
                    )
                await update.effective_message.reply_text(
                    "I ғᴇᴇʟ ʟɪᴋᴇ I'ᴍ ɢᴏɴɴᴀ sᴜғғᴏᴄᴀᴛᴇ ɪɴ ʜᴇʀᴇ.",
                    reply_to_message_id=reply,
                )
                continue

            else:
                buttons = sql.get_welc_buttons(chat.id)
                keyb = build_keyboard(buttons)

                if welc_type not in (sql.Types.TEXT, sql.Types.BUTTON_TEXT):
                    media_wel = True

                first_name = (
                    new_mem.first_name or "PersonWithNoName"
                )  # edge case of empty name - occurs for some bugs.

                if cust_welcome:
                    if cust_welcome == sql.DEFAULT_WELCOME:
                        cust_welcome = random.choice(
                            sql.DEFAULT_WELCOME_MESSAGES,
                        ).format(first=escape_markdown(first_name))

                    if new_mem.last_name:
                        fullname = escape_markdown(f"{first_name} {new_mem.last_name}")
                    else:
                        fullname = escape_markdown(first_name)
                    count = await chat.get_member_count()
                    mention = mention_markdown(new_mem.id, escape_markdown(first_name))
                    if new_mem.username:
                        username = "@" + escape_markdown(new_mem.username)
                    else:
                        username = mention

                    valid_format = escape_invalid_curly_brackets(
                        cust_welcome,
                        VALID_WELCOME_FORMATTERS,
                    )
                    res = valid_format.format(
                        first=escape_markdown(first_name),
                        last=escape_markdown(new_mem.last_name or first_name),
                        fullname=escape_markdown(fullname),
                        username=username,
                        mention=mention,
                        count=count,
                        chatname=escape_markdown(chat.title),
                        id=new_mem.id,
                    )

                else:
                    res = random.choice(sql.DEFAULT_WELCOME_MESSAGES).format(
                        first=escape_markdown(first_name),
                    )
                    keyb = []

                backup_message = random.choice(sql.DEFAULT_WELCOME_MESSAGES).format(
                    first=escape_markdown(first_name),
                )
                keyboard = InlineKeyboardMarkup(keyb)

        else:
            welcome_bool = False
            res = None
            keyboard = None
            backup_message = None
            reply = None

        # User exceptions from welcomemutes
        if (
            await is_user_ban_protected(
                chat, new_mem.id, await chat.get_member(new_mem.id)
            )
            or human_checks
        ):
            should_mute = False
        # Join welcome: soft mute
        if new_mem.is_bot:
            should_mute = False

        if user.id == new_mem.id:
            if should_mute:
                if welc_mutes == "soft":
                    await bot.restrict_chat_member(
                        chat.id,
                        new_mem.id,
                        permissions=ChatPermissions(
                            can_send_messages=True,
                            can_send_media_messages=False,
                            can_send_other_messages=False,
                            can_invite_users=False,
                            can_pin_messages=False,
                            can_send_polls=False,
                            can_change_info=False,
                            can_add_web_page_previews=False,
                            can_manage_topics=False,
                        ),
                        until_date=(int(time.time() + 24 * 60 * 60)),
                    )
                if welc_mutes == "strong":
                    welcome_bool = False
                    if not media_wel:
                        VERIFIED_USER_WAITLIST.update(
                            {
                                new_mem.id: {
                                    "should_welc": should_welc,
                                    "media_wel": False,
                                    "status": False,
                                    "update": update,
                                    "res": res,
                                    "keyboard": keyboard,
                                    "backup_message": backup_message,
                                },
                            },
                        )
                    else:
                        VERIFIED_USER_WAITLIST.update(
                            {
                                new_mem.id: {
                                    "should_welc": should_welc,
                                    "chat_id": chat.id,
                                    "status": False,
                                    "media_wel": True,
                                    "cust_content": cust_content,
                                    "welc_type": welc_type,
                                    "res": res,
                                    "keyboard": keyboard,
                                },
                            },
                        )
                    new_join_mem = f'<a href="tg://user?id={user.id}">{html.escape(new_mem.first_name)}</a>'
                    message = await msg.reply_text(
                        f"{new_join_mem}, ᴄʟɪᴄᴋ ᴛʜᴇ ʙᴜᴛᴛᴏɴ ʙᴇʟᴏᴡ ᴛᴏ ᴘʀᴏᴠᴇ ʏᴏᴜ'ʀᴇ ʜᴜᴍᴀɴ.\nʏᴏᴜ ʜᴀᴠᴇ 120 sᴇᴄᴏɴᴅs ᴏɴʟʏ.",
                        reply_markup=InlineKeyboardMarkup(
                            [
                                [
                                    InlineKeyboardButton(
                                        text="👩‍💼 ʏᴇs, I'ᴍ ʜᴜᴍᴀɴ 👨‍💼.",
                                        callback_data=f"user_join_({new_mem.id})",
                                    ),
                                ],
                            ],
                        ),
                        parse_mode=ParseMode.HTML,
                        reply_to_message_id=reply,
                    )
                    await bot.restrict_chat_member(
                        chat.id,
                        new_mem.id,
                        permissions=ChatPermissions(
                            can_send_messages=False,
                            can_invite_users=False,
                            can_pin_messages=False,
                            can_send_polls=False,
                            can_change_info=False,
                            can_send_media_messages=False,
                            can_send_other_messages=False,
                            can_add_web_page_previews=False,
                            can_manage_topics=False,
                        ),
                    )
                    job_queue.run_once(
                        partial(check_not_bot, new_mem, chat.id, message.message_id),
                        120,
                        name="welcomemute",
                    )

        if welcome_bool:
            if media_wel:
                sent = await ENUM_FUNC_MAP[welc_type](
                    chat.id,
                    cust_content,
                    caption=res,
                    reply_markup=keyboard,
                    reply_to_message_id=reply,
                    parse_mode="markdown",
                )
            else:
                sent = await send(update, res, keyboard, backup_message)
            prev_welc = sql.get_clean_pref(chat.id)
            if prev_welc:
                try:
                    await bot.delete_message(chat.id, prev_welc)
                except BadRequest:
                    pass

                if sent:
                    sql.set_clean_welcome(chat.id, sent.message_id)

        if welcome_log:
            return welcome_log

        if user.id == new_mem.id:
            welcome_log = (
                f"{html.escape(chat.title)}\n"
                f"#𝐔𝐒𝐄𝐑_𝐉𝐎𝐈𝐍𝐄𝐃\n"
                f"<b>ᴜsᴇʀ</b>: {mention_html(user.id, user.first_name)}\n"
                f"<b>ɪᴅ</b>: <code>{user.id}</code>"
            )
        elif new_mem.is_bot and user.id != new_mem.id:
            welcome_log = (
                f"{html.escape(chat.title)}\n"
                f"#𝐁𝐎𝐓_𝐀𝐃𝐃𝐄𝐃\n"
                f"<b>ʙᴏᴛ</b>: {mention_html(new_mem.id, new_mem.first_name)}\n"
                f"<b>ɪᴅ</b>: <code>{new_mem.id}</code>"
            )
        else:
            welcome_log = (
                f"{html.escape(chat.title)}\n"
                f"#𝐔𝐒𝐄𝐑_𝐀𝐃𝐃𝐄𝐃\n"
                f"<b>ᴜsᴇʀ</b>: {mention_html(new_mem.id, new_mem.first_name)}\n"
                f"<b>ɪᴅ</b>: <code>{new_mem.id}</code>"
            )
        return welcome_log

    return ""


async def check_not_bot(member, chat_id, message_id, context):
    bot = context.bot
    member_dict = VERIFIED_USER_WAITLIST.pop(member.id)
    member_status = member_dict.get("status")
    if not member_status:
        try:
            await bot.unban_chat_member(chat_id, member.id)
        except:
            pass

        try:
            await bot.edit_message_text(
                "*ᴋɪᴄᴋs ᴜsᴇʀ*\nᴛʜᴇʏ ᴄᴀɴ ᴀʟᴡᴀʏs ʀᴇᴊᴏɪɴ ᴀɴᴅ ᴛʀʏ.",
                chat_id=chat_id,
                message_id=message_id,
            )
        except:
            pass


async def left_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bot = context.bot
    chat = update.effective_chat
    user = update.effective_user
    should_goodbye, cust_goodbye, goodbye_type = sql.get_gdbye_pref(chat.id)

    if user.id == bot.id:
        return

    if should_goodbye:
        reply = update.message.message_id
        cleanserv = sql.clean_service(chat.id)
        # Clean service welcome
        if cleanserv:
            try:
                await application.bot.delete_message(chat.id, update.message.message_id)
            except BadRequest:
                pass
            reply = False

        left_mem = update.effective_message.left_chat_member
        if left_mem:

            if is_user_gbanned(left_mem.id):
                return

            if left_mem.id == bot.id:
                return

            if left_mem.id == OWNER_ID:
                await update.effective_message.reply_text(
                    "ᴏɪ! ɢᴇɴᴏs! ʜᴇ ʟᴇғᴛ..",
                    reply_to_message_id=reply,
                )
                return

            elif left_mem.id in DEV_USERS:
                await update.effective_message.reply_text(
                    "sᴇᴇ ʏᴏᴜ ʟᴀᴛᴇʀ ᴀᴛ ᴛʜᴇ @AbishnoiMF!",
                    reply_to_message_id=reply,
                )
                return

            # if media goodbye, use appropriate function for it
            if goodbye_type != sql.Types.TEXT and goodbye_type != sql.Types.BUTTON_TEXT:
                # topic_chat = get_action_topic(chat.id)
                await ENUM_FUNC_MAP[goodbye_type](chat.id, cust_goodbye)
                return

            first_name = (
                left_mem.first_name or "PersonWithNoName"
            )  # edge case of empty name - occurs for some bugs.
            if cust_goodbye:
                if cust_goodbye == sql.DEFAULT_GOODBYE:
                    cust_goodbye = random.choice(sql.DEFAULT_GOODBYE_MESSAGES).format(
                        first=escape_markdown(first_name),
                    )
                if left_mem.last_name:
                    fullname = escape_markdown(f"{first_name} {left_mem.last_name}")
                else:
                    fullname = escape_markdown(first_name)
                count = await chat.get_member_count()
                mention = mention_markdown(left_mem.id, first_name)
                if left_mem.username:
                    username = "@" + escape_markdown(left_mem.username)
                else:
                    username = mention

                valid_format = escape_invalid_curly_brackets(
                    cust_goodbye,
                    VALID_WELCOME_FORMATTERS,
                )
                res = valid_format.format(
                    first=escape_markdown(first_name),
                    last=escape_markdown(left_mem.last_name or first_name),
                    fullname=escape_markdown(fullname),
                    username=username,
                    mention=mention,
                    count=count,
                    chatname=escape_markdown(chat.title),
                    id=left_mem.id,
                )
                buttons = sql.get_gdbye_buttons(chat.id)
                keyb = build_keyboard(buttons)

            else:
                res = random.choice(sql.DEFAULT_GOODBYE_MESSAGES).format(
                    first=first_name,
                )
                keyb = []

            keyboard = InlineKeyboardMarkup(keyb)

            await send(
                update,
                res,
                keyboard,
                random.choice(sql.DEFAULT_GOODBYE_MESSAGES).format(first=first_name),
            )


@check_admin(is_user=True)
async def welcome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    chat = update.effective_chat
    # topic_chat = get_action_topic(chat.id)
    # if no args, show current replies.
    if not args or args[0].lower() == "noformat":
        noformat = True
        pref, welcome_m, cust_content, welcome_type = sql.get_welc_pref(chat.id)
        await update.effective_message.reply_text(
            f"ᴛʜɪs ᴄʜᴀᴛ ʜᴀs ɪᴛ's ᴡᴇʟᴄᴏᴍᴇ sᴇᴛᴛɪɴɢ sᴇᴛ ᴛᴏ: `{pref}`.\n"
            f"*The welcome message (not filling the {{}}) is:*",
            parse_mode=ParseMode.MARKDOWN,
        )

        if welcome_type == sql.Types.BUTTON_TEXT or welcome_type == sql.Types.TEXT:
            buttons = sql.get_welc_buttons(chat.id)
            if noformat:
                welcome_m += revert_buttons(buttons)
                await update.effective_message.reply_text(welcome_m)

            else:
                keyb = build_keyboard(buttons)
                keyboard = InlineKeyboardMarkup(keyb)

                await send(update, welcome_m, keyboard, sql.DEFAULT_WELCOME)
        else:
            buttons = sql.get_welc_buttons(chat.id)
            if noformat:
                welcome_m += revert_buttons(buttons)
                await ENUM_FUNC_MAP[welcome_type](
                    chat.id, cust_content, caption=welcome_m
                )

            else:
                keyb = build_keyboard(buttons)
                keyboard = InlineKeyboardMarkup(keyb)
                ENUM_FUNC_MAP[welcome_type](
                    chat.id,
                    cust_content,
                    caption=welcome_m,
                    reply_markup=keyboard,
                    parse_mode=ParseMode.MARKDOWN,
                    disable_web_page_preview=True,
                )

    elif len(args) >= 1:
        if args[0].lower() in ("on", "yes"):
            sql.set_welc_preference(str(chat.id), True)
            await update.effective_message.reply_text(
                "ᴏᴋᴀʏ! I'ʟʟ ɢʀᴇᴇᴛ ᴍᴇᴍʙᴇʀs ᴡʜᴇɴ ᴛʜᴇʏ ᴊᴏɪɴ.",
            )

        elif args[0].lower() in ("off", "no"):
            sql.set_welc_preference(str(chat.id), False)
            await update.effective_message.reply_text(
                "I'ʟʟ ɢᴏ ʟᴏᴀғ ᴀʀᴏᴜɴᴅ ᴀɴᴅ ɴᴏᴛ ᴡᴇʟᴄᴏᴍᴇ ᴀɴʏᴏɴᴇ ᴛʜᴇɴ.",
            )

        else:
            await update.effective_message.reply_text(
                "I ᴜɴᴅᴇʀsᴛᴀɴᴅ 'ᴏɴ/ʏᴇs ᴏʀ 'off/no' ᴏɴʟʏ!",
            )


@check_admin(is_user=True)
async def goodbye(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    chat = update.effective_chat
    # topic_chat = get_action_topic(chat.id)

    if not args or args[0] == "noformat":
        noformat = True
        pref, goodbye_m, goodbye_type = sql.get_gdbye_pref(chat.id)
        await update.effective_message.reply_text(
            f"ᴛʜɪs ᴄʜᴀᴛ ʜᴀs ɪᴛ's ɢᴏᴏᴅʙʏᴇ sᴇᴛᴛɪɴɢ sᴇᴛ ᴛᴏ: `{pref}`.\n"
            f"*ᴛʜᴇ ɢᴏᴏᴅʙʏᴇ  ᴍᴇssᴀɢᴇ (ɴᴏᴛ ғɪʟʟɪɴɢ ᴛʜᴇ {{}}) ɪs:*",
            parse_mode=ParseMode.MARKDOWN,
        )

        if goodbye_type == sql.Types.BUTTON_TEXT:
            buttons = sql.get_gdbye_buttons(chat.id)
            if noformat:
                goodbye_m += revert_buttons(buttons)
                await update.effective_message.reply_text(goodbye_m)

            else:
                keyb = build_keyboard(buttons)
                keyboard = InlineKeyboardMarkup(keyb)

                await send(update, goodbye_m, keyboard, sql.DEFAULT_GOODBYE)

        else:
            if noformat:
                await ENUM_FUNC_MAP[goodbye_type](chat.id, goodbye_m)

            else:
                await ENUM_FUNC_MAP[goodbye_type](
                    chat.id, goodbye_m, parse_mode=ParseMode.MARKDOWN
                )

    elif len(args) >= 1:
        if args[0].lower() in ("on", "yes"):
            sql.set_gdbye_preference(str(chat.id), True)
            await update.effective_message.reply_text("ᴏᴋ ʙᴀʙʏ!")

        elif args[0].lower() in ("off", "no"):
            sql.set_gdbye_preference(str(chat.id), False)
            await update.effective_message.reply_text("ᴏᴋ ʙᴀʙʏ!")

        else:
            # idek what you're writing, say yes or no
            await update.effective_message.reply_text(
                "I ᴜɴᴅᴇʀsᴛᴀɴᴅ 'ᴏɴ/ʏᴇs ᴏʀ 'off/no' ᴏɴʟʏ!",
            )


@check_admin(is_user=True)
@loggable
async def set_welcome(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    chat = update.effective_chat
    user = update.effective_user
    msg = update.effective_message

    text, data_type, content, buttons = get_welcome_type(msg)

    if data_type is None:
        await msg.reply_text("ʏᴏᴜ ᴅɪᴅɴ'ᴛ sᴘᴇᴄɪғʏ ᴡʜᴀᴛ ᴛᴏ ʀᴇᴘʟʏ ᴡɪᴛʜ!")
        return ""

    sql.set_custom_welcome(chat.id, content, text, data_type, buttons)
    await msg.reply_text("sᴜᴄᴄᴇssғᴜʟʟʏ sᴇᴛ ᴄᴜsᴛᴏᴍ ᴡᴇʟᴄᴏᴍᴇ ᴍᴇssᴀɢᴇ!")

    return (
        f"<b>{html.escape(chat.title)}:</b>\n"
        f"#𝐒𝐄𝐓_𝐖𝐄𝐋𝐂𝐎𝐌𝐄\n"
        f"<b>ᴀᴅᴍɪɴ:</b> {mention_html(user.id, user.first_name)}\n"
        f"sᴇᴛ ᴛʜᴇ ᴡᴇʟᴄᴏᴍᴇ ᴍᴇssᴀɢᴇ."
    )


@check_admin(is_user=True)
@loggable
async def reset_welcome(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    chat = update.effective_chat
    user = update.effective_user

    sql.set_custom_welcome(chat.id, None, sql.DEFAULT_WELCOME, sql.Types.TEXT)
    await update.effective_message.reply_text(
        "sᴜᴄᴄᴇssғᴜʟʟʏ ʀᴇsᴇᴛ ᴡᴇʟᴄᴏᴍᴇ ᴍᴇssᴀɢᴇ ᴛᴏ ᴅᴇғᴀᴜʟᴛ!",
    )

    return (
        f"<b>{html.escape(chat.title)}:</b>\n"
        f"#𝐑𝐄𝐒𝐄𝐓_𝐖𝐄𝐋𝐂𝐎𝐌𝐄\n"
        f"<b>ᴀᴅᴍɪɴ:</b> {mention_html(user.id, user.first_name)}\n"
        f"ʀᴇsᴇᴛ ᴛʜᴇ ᴡᴇʟᴄᴏᴍᴇ ᴍᴇssᴀɢᴇ ᴛᴏ ᴅᴇғᴀᴜʟᴛ."
    )


@check_admin(is_user=True)
@loggable
async def set_goodbye(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    chat = update.effective_chat
    user = update.effective_user
    msg = update.effective_message
    text, data_type, content, buttons = get_welcome_type(msg)

    if data_type is None:
        await msg.reply_text("ʏᴏᴜ ᴅɪᴅɴ'ᴛ sᴘᴇᴄɪғʏ ᴡʜᴀᴛ ᴛᴏ ʀᴇᴘʟʏ ᴡɪᴛʜ!")
        return ""

    sql.set_custom_gdbye(chat.id, content or text, data_type, buttons)
    await msg.reply_text("sᴜᴄᴄᴇssғᴜʟʟʏ sᴇᴛ ᴄᴜsᴛᴏᴍ ɢᴏᴏᴅʙʏᴇ ᴍᴇssᴀɢᴇ!")
    return (
        f"<b>{html.escape(chat.title)}:</b>\n"
        f"#𝐒𝐄𝐓_𝐆𝐎𝐎𝐃𝐁𝐘𝐄\n"
        f"<b>ᴀᴅᴍɪɴ:</b> {mention_html(user.id, user.first_name)}\n"
        f"sᴇᴛ ᴛʜᴇ ɢᴏᴏᴅʙʏᴇ ᴍᴇssᴀɢᴇ."
    )


@check_admin(is_user=True)
@loggable
async def reset_goodbye(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    chat = update.effective_chat
    user = update.effective_user

    sql.set_custom_gdbye(chat.id, sql.DEFAULT_GOODBYE, sql.Types.TEXT)
    await update.effective_message.reply_text(
        "sᴜᴄᴄᴇssғᴜʟʟʏ ʀᴇsᴇᴛ ɢᴏᴏᴅʙʏᴇ ᴍᴇssᴀɢᴇ ᴛᴏ ᴅᴇғᴀᴜʟᴛ!",
    )

    return (
        f"<b>{html.escape(chat.title)}:</b>\n"
        f"#RESET_GOODBYE\n"
        f"<b>ᴀᴅᴍɪɴ:</b> {mention_html(user.id, user.first_name)}\n"
        f"ʀᴇsᴇᴛ ᴛʜᴇ ɢᴏᴏᴅʙʏᴇ ᴍᴇssᴀɢᴇ."
    )


@check_admin(is_user=True)
@loggable
async def welcomemute(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    args = context.args
    chat = update.effective_chat
    user = update.effective_user
    msg = update.effective_message

    if len(args) >= 1:
        if args[0].lower() in ("off", "no"):
            sql.set_welcome_mutes(chat.id, False)
            await msg.reply_text("I will no longer mute people on joining!")
            return (
                f"<b>{html.escape(chat.title)}:</b>\n"
                f"#WELCOME_MUTE\n"
                f"<b>•ᴀᴅᴍɪɴ:</b> {mention_html(user.id, user.first_name)}\n"
                f"ʜᴀs ᴛᴏɢɢʟᴇᴅ ᴡᴇʟᴄᴏᴍᴇ ᴍᴜᴛᴇ ᴛᴏ <b>ᴏғғ</b>."
            )
        elif args[0].lower() in ["soft"]:
            sql.set_welcome_mutes(chat.id, "soft")
            await msg.reply_text(
                "I ᴡɪʟʟ ʀᴇsᴛʀɪᴄᴛ ᴜsᴇʀs ᴘᴇʀᴍɪssɪᴏɴ ᴛᴏ sᴇɴᴅ ᴍᴇᴅɪᴀ ғᴏʀ 24 ʜᴏᴜʀs.",
            )
            return (
                f"<b>{html.escape(chat.title)}:</b>\n"
                f"#𝐖𝐄𝐋𝐂𝐎𝐌𝐄_𝐌𝐔𝐓𝐄\n"
                f"<b>•ᴀᴅᴍɪɴ:</b> {mention_html(user.id, user.first_name)}\n"
                f"ʜᴀs ᴛᴏɢɢʟᴇᴅ ᴡᴇʟᴄᴏᴍᴇ ᴍᴜᴛᴇ ᴛᴏ <b>sᴏғᴛ</b>."
            )
        elif args[0].lower() in ["strong"]:
            sql.set_welcome_mutes(chat.id, "strong")
            await msg.reply_text(
                "I ᴡɪʟʟ ɴᴏᴡ ᴍᴜᴛᴇ ᴘᴇᴏᴘʟᴇ ᴡʜᴇɴ ᴛʜᴇʏ ᴊᴏɪɴ ᴜɴᴛɪʟ ᴛʜᴇʏ ᴘʀᴏᴠᴇ ᴛʜᴇʏ'ʀᴇ ɴᴏᴛ ᴀ ʙᴏᴛ.\nᴛʜᴇʏ ᴡɪʟʟ ʜᴀᴠᴇ 120sᴇᴄᴏɴᴅs ʙᴇғᴏʀᴇ ᴛʜᴇʏ ɢᴇᴛ ᴋɪᴄᴋᴇᴅ.",
            )
            return (
                f"<b>{html.escape(chat.title)}:</b>\n"
                f"#𝐖𝐄𝐋𝐂𝐎𝐌𝐄_𝐌𝐔𝐓𝐄\n"
                f"<b>•ᴀᴅᴍɪɴ:</b> {mention_html(user.id, user.first_name)}\n"
                f"ʜᴀs ᴛᴏɢɢʟᴇᴅ ᴡᴇʟᴄᴏᴍᴇ ᴍᴜᴛᴇ ᴛᴏ <b>sᴛʀᴏɴɢ</b>."
            )
        else:
            await msg.reply_text(
                "ᴘʟᴇᴀsᴇ ᴇɴᴛᴇʀ <code>ᴏғғ</code>/<code>ɴᴏ</code>/<code>sᴏғᴛ</code>/<code>sᴛʀᴏɴɢ</code>!",
                parse_mode=ParseMode.HTML,
            )
            return ""
    else:
        curr_setting = sql.welcome_mutes(chat.id)
        reply = (
            f"\nɢɪᴠᴇ ᴍᴇ ᴀ sᴇᴛᴛɪɴɢ!\nᴄʜᴏᴏsᴇ ᴏɴᴇ ᴏᴜᴛ ᴏғ: <code>ᴏғғ</code>/<code>ɴᴏ</code> ᴏʀ <code>sᴏғᴛ</code> or <code>sᴛʀᴏɴɢ</code> ᴏɴʟʏ! \n"
            f"ᴄᴜʀʀᴇɴᴛ sᴇᴛᴛɪɴɢ: <code>{curr_setting}</code>"
        )
        await msg.reply_text(reply, parse_mode=ParseMode.HTML)
        return ""


@check_admin(is_user=True)
@loggable
async def clean_welcome(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    args = context.args
    chat = update.effective_chat
    user = update.effective_user

    if not args:
        clean_pref = sql.get_clean_pref(chat.id)
        if clean_pref:
            await update.effective_message.reply_text(
                "I sʜᴏᴜʟᴅ ʙᴇ ᴅᴇʟᴇᴛɪɴɢ ᴡᴇʟᴄᴏᴍᴇ ᴍᴇssᴀɢᴇs ᴜᴘ ᴛᴏ ᴛᴡᴏ ᴅᴀʏs ᴏʟᴅ.",
            )
        else:
            await update.effective_message.reply_text(
                "I'ᴍ ᴄᴜʀʀᴇɴᴛʟʏ ɴᴏᴛ ᴅᴇʟᴇᴛɪɴɢ ᴏʟᴅ ᴡᴇʟᴄᴏᴍᴇ ᴍᴇssᴀɢᴇs!",
            )
        return ""

    if args[0].lower() in ("on", "yes"):
        sql.set_clean_welcome(str(chat.id), True)
        await update.effective_message.reply_text(
            "I'ʟʟ ᴛʀʏ ᴛᴏ ᴅᴇʟᴇᴛᴇ ᴏʟᴅ ᴡᴇʟᴄᴏᴍᴇ ᴍᴇssᴀɢᴇs!"
        )
        return (
            f"<b>{html.escape(chat.title)}:</b>\n"
            f"#𝐂𝐋𝐄𝐀𝐍_𝐖𝐄𝐋𝐂𝐎𝐌𝐄\n"
            f"<b>ᴀᴅᴍɪɴ:</b> {mention_html(user.id, user.first_name)}\n"
            f"ʜᴀs ᴛᴏɢɢʟᴇᴅ ᴄʟᴇᴀɴ ᴡᴇʟᴄᴏᴍᴇs ᴛᴏ <code>ᴏɴ</code>."
        )
    elif args[0].lower() in ("off", "no"):
        sql.set_clean_welcome(str(chat.id), False)
        await update.effective_message.reply_text(
            "I won't delete old welcome messages."
        )
        return (
            f"<b>{html.escape(chat.title)}:</b>\n"
            f"#𝐂𝐋𝐄𝐀𝐍_𝐖𝐄𝐋𝐂𝐎𝐌𝐄\n"
            f"<b>ᴀᴅᴍɪɴ:</b> {mention_html(user.id, user.first_name)}\n"
            f"ʜᴀs ᴛᴏɢɢʟᴇᴅ ᴄʟᴇᴀɴ ᴡᴇʟᴄᴏᴍᴇs ᴛᴏ <code>ᴏғғ</code>."
        )
    else:
        await update.effective_message.reply_text(
            "I ᴜɴᴅᴇʀsᴛᴀɴᴅ 'ᴏɴ/ʏᴇs ᴏʀ 'ᴏғғ/ɴᴏ ᴏɴʟʏ!"
        )
        return ""


@check_admin(is_user=True)
async def cleanservice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    args = context.args
    chat = update.effective_chat  # type: Optional[Chat]
    if chat.type != chat.PRIVATE:
        if len(args) >= 1:
            var = args[0]
            if var in ("no", "off"):
                sql.set_clean_service(chat.id, False)
                await update.effective_message.reply_text(
                    "ᴡᴇʟᴄᴏᴍᴇ ᴄʟᴇᴀɴ sᴇʀᴠɪᴄᴇ ɪs : off"
                )
            elif var in ("yes", "on"):
                sql.set_clean_service(chat.id, True)
                await update.effective_message.reply_text(
                    "ᴡᴇʟᴄᴏᴍᴇ ᴄʟᴇᴀɴ sᴇʀᴠɪᴄᴇ ɪs : on"
                )
            else:
                await update.effective_message.reply_text(
                    "ɪɴᴠᴀʟɪᴅ ᴏᴘᴛɪᴏɴ",
                    parse_mode=ParseMode.HTML,
                )
        else:
            await update.effective_message.reply_text(
                "ᴜsᴀɢᴇ ɪs <code>ᴏɴ</code>/<code>ʏᴇs</code> ᴏʀ <code>ᴏғғ</code>/<code>ɴᴏ</code>",
                parse_mode=ParseMode.HTML,
            )
    else:
        curr = sql.clean_service(chat.id)
        if curr:
            await update.effective_message.reply_text(
                "ᴡᴇʟᴄᴏᴍᴇ ᴄʟᴇᴀɴ sᴇʀᴠɪᴄᴇ ɪs : <code>on</code>",
                parse_mode=ParseMode.HTML,
            )
        else:
            await update.effective_message.reply_text(
                "ᴡᴇʟᴄᴏᴍᴇ ᴄʟᴇᴀɴ sᴇʀᴠɪᴄᴇ ɪs : <code>ᴏғғ</code>",
                parse_mode=ParseMode.HTML,
            )


async def user_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    user = update.effective_user
    query = update.callback_query
    bot = context.bot
    match = re.match(r"user_join_\((.+?)\)", query.data)
    message = update.effective_message
    join_user = int(match.group(1))

    if join_user == user.id:
        sql.set_human_checks(user.id, chat.id)
        member_dict = VERIFIED_USER_WAITLIST.pop(user.id)
        member_dict["status"] = True
        VERIFIED_USER_WAITLIST.update({user.id: member_dict})
        await query.answer(text="ʏᴇᴇᴛ! ʏᴏᴜ'ʀᴇ ᴀ ʜᴜᴍᴀɴ, ᴜɴᴍᴜᴛᴇᴅ!")
        await bot.restrict_chat_member(
            chat.id,
            user.id,
            permissions=ChatPermissions(
                can_send_messages=True,
                can_invite_users=True,
                can_pin_messages=True,
                can_send_polls=True,
                can_change_info=True,
                can_send_media_messages=True,
                can_send_other_messages=True,
                can_add_web_page_previews=True,
                can_manage_topics=False,
            ),
        )
        try:
            await bot.deleteMessage(chat.id, message.message_id)
        except:
            pass
        if member_dict["should_welc"]:
            if member_dict["media_wel"]:
                # topic_chat = get_action_topic(chat.id)
                sent = await ENUM_FUNC_MAP[member_dict["welc_type"]](
                    member_dict["chat_id"],
                    member_dict["cust_content"],
                    caption=member_dict["res"],
                    reply_markup=member_dict["keyboard"],
                    parse_mode="markdown",
                )
            else:
                sent = await send(
                    member_dict["update"],
                    member_dict["res"],
                    member_dict["keyboard"],
                    member_dict["backup_message"],
                )

            prev_welc = sql.get_clean_pref(chat.id)
            if prev_welc:
                try:
                    await bot.delete_message(chat.id, prev_welc)
                except BadRequest:
                    pass

                if sent:
                    sql.set_clean_welcome(chat.id, sent.message_id)

    else:
        await query.answer(text="ʏᴏᴜ'ʀᴇ ɴᴏᴛ ᴀʟʟᴏᴡᴇᴅ ᴛᴏ ᴅᴏ ᴛʜɪs!")


WELC_MUTE_HELP_TXT = (
    "ʏᴏᴜ ᴄᴀɴ ɢᴇᴛ ᴛʜᴇ ʙᴏᴛ ᴛᴏ ᴍᴜᴛᴇ ɴᴇᴡ ᴘᴇᴏᴘʟᴇ ᴡʜᴏ ᴊᴏɪɴ ʏᴏᴜʀ ɢʀᴏᴜᴘ ᴀɴᴅ ʜᴇɴᴄᴇ ᴘʀᴇᴠᴇɴᴛ sᴘᴀᴍʙᴏᴛs ғʀᴏᴍ ғʟᴏᴏᴅɪɴɢ ʏᴏᴜʀ ɢʀᴏᴜᴘ. "
    "The following options are ᴘᴏssɪʙʟᴇ:\n"
    "• `/welcomemute sᴏғᴛ`*:* ʀᴇsᴛʀɪᴄᴛs ɴᴇᴡ ᴍᴇᴍʙᴇʀs ғʀᴏᴍ sᴇɴᴅɪɴɢ ᴍᴇᴅɪᴀ ғᴏʀ 24 ʜᴏᴜʀs.\n"
    "• `/welcomemute sᴛʀᴏɴɢ`*:* ᴍᴜᴛᴇs ɴᴇᴡ ᴍᴇᴍʙᴇʀs ᴛɪʟʟ ᴛʜᴇʏ ᴛᴀᴘ ᴏɴ ᴀ ʙᴜᴛᴛᴏɴ ᴛʜᴇʀᴇʙʏ ᴠᴇʀɪғʏɪɴɢ ᴛʜᴇʏ'ʀᴇ ʜᴜᴍᴀɴ.\n"
    "• `/welcomemute off`*:* ᴛᴜʀɴs ᴏғғ ᴡᴇʟᴄᴏᴍᴇᴍᴜᴛᴇ.\n"
    "*ɴᴏᴛᴇ:* sᴛʀᴏɴɢ ᴍᴏᴅᴇ ᴋɪᴄᴋs ᴀ ᴜsᴇʀ ғʀᴏᴍ ᴛʜᴇ ᴄʜᴀᴛ ɪғ ᴛʜᴇʏ ᴅᴏɴ'ᴛ ᴠᴇʀɪғʏ ɪɴ 120sᴇᴄᴏɴᴅs. ᴛʜᴇʏ ᴄᴀɴ ᴀʟᴡᴀʏs ʀᴇᴊᴏɪɴ ᴛʜᴏᴜɢʜ"
)


@check_admin(is_user=True)
async def welcome_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    WELC_HELP_TXT = (
        "ʏᴏᴜʀ ɢʀᴏᴜᴘ's ᴡᴇʟᴄᴏᴍᴇ/ɢᴏᴏᴅʙʏᴇ ᴍᴇssᴀɢᴇs ᴄᴀɴ ʙᴇ ᴘᴇʀsᴏɴᴀʟɪsᴇᴅ ɪɴ ᴍᴜʟᴛɪᴘʟᴇ ᴡᴀʏs. ɪғ ʏᴏᴜ ᴡᴀɴᴛ ᴛʜᴇ ᴍᴇssᴀɢᴇs"
        " ᴛᴏ ʙᴇ ɪɴᴅɪᴠɪᴅᴜᴀʟʟʏ ɢᴇɴᴇʀᴀᴛᴇᴅ, ʟɪᴋᴇ ᴛʜᴇ ᴅᴇғᴀᴜʟᴛ ᴡᴇʟᴄᴏᴍᴇ ᴍᴇssᴀɢᴇ ɪs, ʏᴏᴜ ᴄᴀɴ ᴜsᴇ *ᴛʜᴇsᴇ* ᴠᴀʀɪᴀʙʟᴇs:\n"
        " • `{first}`*:* ᴛʜɪs ʀᴇᴘʀᴇsᴇɴᴛs ᴛʜᴇ ᴜsᴇʀ's *ғɪʀsᴛ* ɴᴀᴍᴇ\n"
        " • `{last}`*:* ᴛʜɪs ʀᴇᴘʀᴇsᴇɴᴛs ᴛʜᴇ ᴜsᴇʀ's *ʟᴀsᴛ* ɴᴀᴍᴇ. ᴅᴇғᴀᴜʟᴛs ᴛᴏ *ғɪʀsᴛ ɴᴀᴍᴇ* ɪғ user ʜᴀs ɴᴏ "
        "ʟᴀsᴛ ɴᴀᴍᴇ.\n"
        " • `{fullname}`*:* ᴛʜɪs ʀᴇᴘʀᴇsᴇɴᴛs ᴛʜᴇ ᴜsᴇʀ's *ғᴜʟʟ* ɴᴀᴍᴇ. ᴅᴇғᴀᴜʟᴛs ᴛᴏ *ғɪʀsᴛ ɴᴀᴍᴇ* ɪғ ᴜsᴇʀ ʜᴀs ɴᴏ "
        "last name.\n"
        " • `{username}`*:* ᴛʜɪs ʀᴇᴘʀᴇsᴇɴᴛs ᴛʜᴇ ᴜsᴇʀ's *ᴜsᴇʀɴᴀᴍᴇ*. ᴅᴇғᴀᴜʟᴛs ᴛᴏ ᴀ *ᴍᴇɴᴛɪᴏɴ* ᴏғ ᴛʜᴇ ᴜsᴇʀ's "
        "ғɪʀsᴛ ɴᴀᴍᴇ ɪғ ʜᴀs ɴᴏ ᴜsᴇʀɴᴀᴍᴇ.\n"
        " • `{mention}`*:* ᴛʜɪs sɪᴍᴘʟʏ *ᴍᴇɴᴛɪᴏɴs* ᴀ ᴜsᴇʀ - ᴛᴀɢɢɪɴɢ ᴛʜᴇᴍ ᴡɪᴛʜ ᴛʜᴇɪʀ ғɪʀsᴛ ɴᴀᴍᴇ.\n"
        " • `{id}`*:* ᴛʜɪs ʀᴇᴘʀᴇsᴇɴᴛs ᴛʜᴇ ᴜsᴇʀ's *ɪᴅ*\n"
        " • `{count}`*:* ᴛʜɪs ʀᴇᴘʀᴇsᴇɴᴛs ᴛʜᴇ ᴜsᴇʀ's *ᴍᴇᴍʙᴇʀ ɴᴜᴍʙᴇʀ*.\n"
        " • `{chatname}`*:* ᴛʜɪs ʀᴇᴘʀᴇsᴇɴᴛs ᴛʜᴇ *ᴄᴜʀʀᴇɴᴛ ᴄʜᴀᴛ ɴᴀᴍᴇ*.\n"
        "\nᴇᴀᴄʜ ᴠᴀʀɪᴀʙʟᴇ MUST ʙᴇ sᴜʀʀᴏᴜɴᴅᴇᴅ ʙʏ `{}` ᴛᴏ ʙᴇ ʀᴇᴘʟᴀᴄᴇᴅ.\n"
        "ᴡᴇʟᴄᴏᴍᴇ ᴍᴇssᴀɢᴇs ᴀʟsᴏ sᴜᴘᴘᴏʀᴛ ᴍᴀʀᴋᴅᴏᴡɴ, sᴏ ʏᴏᴜ ᴄᴀɴ ᴍᴀᴋᴇ ᴀɴʏ ᴇʟᴇᴍᴇɴᴛs ʙᴏʟᴅ/ɪᴛᴀʟɪᴄ/ᴄᴏᴅᴇ/ʟɪɴᴋs. "
        "ʙᴜᴛᴛᴏɴs ᴀʀᴇ ᴀʟsᴏ sᴜᴘᴘᴏʀᴛᴇᴅ, sᴏ ʏᴏᴜ can ᴍᴀᴋᴇ ʏᴏᴜʀ ᴡᴇʟᴄᴏᴍᴇs ʟᴏᴏᴋ ᴀᴡᴇsᴏᴍᴇ ᴡɪᴛʜ sᴏᴍᴇ ɴɪᴄᴇ intro "
        "buttons.\n"
        f"ᴛᴏ ᴄʀᴇᴀᴛᴇ ᴀ ʙᴜᴛᴛᴏɴ ʟɪɴᴋɪɴɢ ᴛᴏ ʏᴏᴜʀ ʀᴜʟᴇs, ᴜsᴇ ᴛʜɪs: `[ʀᴜʟᴇs](buttonurl://t.me/{context.bot.username}?start=group_id)`. "
        "sɪᴍᴘʟʏ ʀᴇᴘʟᴀᴄᴇ `group_id` ᴡɪᴛʜ ʏᴏᴜʀ ɢʀᴏᴜᴘ's ɪᴅ, ᴡʜɪᴄʜ ᴄᴀɴ ʙᴇ ᴏʙᴛᴀɪɴᴇᴅ ᴠɪᴀ /id, ᴀɴᴅ ʏᴏᴜ'ʀᴇ ɢᴏᴏᴅ ᴛᴏ "
        "ɢᴏ. ɴᴏᴛᴇ ᴛʜᴀᴛ ɢʀᴏᴜᴘ ɪᴅs ᴀʀᴇ ᴜsᴜᴀʟʟʏ ᴘʀᴇᴄᴇᴅᴇᴅ ʙʏ ᴀ `-` sɪɢɴ; ᴛʜɪs ɪs ʀᴇǫᴜɪʀᴇᴅ, sᴏ ᴘʟᴇᴀsᴇ ᴅᴏɴ'ᴛ "
        "ʀᴇᴍᴏᴠᴇ ɪᴛ.\n"
        "ʏᴏᴜ ᴄᴀɴ ᴇᴠᴇɴ sᴇᴛ ɪᴍᴀɢᴇs/ɢɪғs/ᴠɪᴅᴇᴏs/ᴠᴏɪᴄᴇ ᴍᴇssᴀɢᴇs ᴀs ᴛʜᴇ ᴡᴇʟᴄᴏᴍᴇ ᴍᴇssᴀɢᴇ ʙʏ "
        "ʀᴇᴘʟʏɪɴɢ ᴛᴏ ᴛʜᴇ ᴅᴇsɪʀᴇᴅ ᴍᴇᴅɪᴀ, ᴀɴᴅ ᴄᴀʟʟɪɴɢ `/setwelcome`."
    )

    await update.effective_message.reply_text(
        WELC_HELP_TXT, parse_mode=ParseMode.MARKDOWN
    )


@check_admin(is_user=True)
async def welcome_mute_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.effective_message.reply_text(
        WELC_MUTE_HELP_TXT,
        parse_mode=ParseMode.MARKDOWN,
    )


# TODO: get welcome data from group butler snap
# def __import_data__(chat_id, data):
#     welcome = data.get('info', {}).get('rules')
#     welcome = welcome.replace('$username', '{username}')
#     welcome = welcome.replace('$name', '{fullname}')
#     welcome = welcome.replace('$id', '{id}')
#     welcome = welcome.replace('$title', '{chatname}')
#     welcome = welcome.replace('$surname', '{lastname}')
#     welcome = welcome.replace('$rules', '{rules}')
#     sql.set_custom_welcome(chat_id, welcome, sql.Types.TEXT)


def __migrate__(old_chat_id, new_chat_id):
    sql.migrate_chat(old_chat_id, new_chat_id)


def __chat_settings__(chat_id, user_id):
    welcome_pref = sql.get_welc_pref(chat_id)[0]
    goodbye_pref = sql.get_gdbye_pref(chat_id)[0]
    return (
        "ᴛʜɪs ᴄʜᴀᴛ ʜᴀs ɪᴛ's ᴡᴇʟᴄᴏᴍᴇ ᴘʀᴇғᴇʀᴇɴᴄᴇ sᴇᴛ ᴛᴏ `{}`.\n"
        "ɪᴛ's ɢᴏᴏᴅʙʏᴇ ᴘʀᴇғᴇʀᴇɴᴄᴇ ɪs `{}`.".format(welcome_pref, goodbye_pref)
    )


__help__ = """
*ᴀᴅᴍɪɴs ᴏɴʟʏ:*
• /welcome <ᴏɴ/ᴏғғ>*:* ᴇɴᴀʙʟᴇ/ᴅɪsᴀʙʟᴇ ᴡᴇʟᴄᴏᴍᴇ ᴍᴇssᴀɢᴇs.
• /welcome*:* sʜᴏᴡs ᴄᴜʀʀᴇɴᴛ ᴡᴇʟᴄᴏᴍᴇ sᴇᴛᴛɪɴɢs.
• /welcome noformat*:* sʜᴏᴡs ᴄᴜʀʀᴇɴᴛ ᴡᴇʟᴄᴏᴍᴇ sᴇᴛᴛɪɴɢs, ᴡɪᴛʜᴏᴜᴛ ᴛʜᴇ ғᴏʀᴍᴀᴛᴛɪɴɢ - ᴜsᴇғᴜʟ ᴛᴏ ʀᴇᴄʏᴄʟᴇ ʏᴏᴜʀ ᴡᴇʟᴄᴏᴍᴇ ᴍᴇssᴀɢᴇs!
• /goodbye*:* sᴀᴍᴇ ᴜsᴀɢᴇ ᴀɴᴅ ᴀʀɢs ᴀs `/welcome`
• /setwelcome <sᴏᴍᴇᴛᴇxᴛ>*:* sᴇᴛ ᴀ ᴄᴜsᴛᴏᴍ ᴡᴇʟᴄᴏᴍᴇ ᴍᴇssᴀɢᴇ. ɪғ ᴜsᴇᴅ ʀᴇᴘʟʏɪɴɢ ᴛᴏ ᴍᴇᴅɪᴀ, ᴜsᴇs ᴛʜᴀᴛ ᴍᴇᴅɪᴀ.
• /setgoodbye <sᴏᴍᴇᴛᴇxᴛ>*:* sᴇᴛ ᴀ ᴄᴜsᴛᴏᴍ ɢᴏᴏᴅʙʏᴇ ᴍᴇssᴀɢᴇ. ɪғ ᴜsᴇᴅ ʀᴇᴘʟʏɪɴɢ ᴛᴏ ᴍᴇᴅɪᴀ, ᴜsᴇs ᴛʜᴀᴛ ᴍᴇᴅɪᴀ.
• /resetwelcome*:* ʀᴇsᴇᴛ ᴛᴏ ᴛʜᴇ ᴅᴇғᴀᴜʟᴛ ᴡᴇʟᴄᴏᴍᴇ ᴍᴇssᴀɢᴇ.
• /resetgoodbye*:* ʀᴇsᴇᴛ ᴛᴏ ᴛʜᴇ ᴅᴇғᴀᴜʟᴛ ɢᴏᴏᴅʙʏᴇ ᴍᴇssᴀɢᴇ.
• /cleanwelcome <ᴏɴ/ᴏғғ>*:* ᴏɴ ɴᴇᴡ ᴍᴇᴍʙᴇʀ, ᴛʀʏ ᴛᴏ ᴅᴇʟᴇᴛᴇ ᴛʜᴇ ᴘʀᴇᴠɪᴏᴜs ᴡᴇʟᴄᴏᴍᴇ ᴍᴇssᴀɢᴇ ᴛᴏ ᴀᴠᴏɪᴅ sᴘᴀᴍᴍɪɴɢ ᴛʜᴇ ᴄʜᴀᴛ.
• /welcomemutehelp*:* ɢɪᴠᴇs ɪɴғᴏʀᴍᴀᴛɪᴏɴ ᴀʙᴏᴜᴛ ᴡᴇʟᴄᴏᴍᴇ ᴍᴜᴛᴇs.
• /cleanservice <ᴏɴ/ᴏғғ*:* ᴅᴇʟᴇᴛᴇs ᴛᴇʟᴇɢʀᴀᴍs ᴡᴇʟᴄᴏᴍᴇ/ʟᴇғᴛ sᴇʀᴠɪᴄᴇ ᴍᴇssᴀɢᴇs.

*ᴇxᴀᴍᴘʟᴇ:*
ᴜsᴇʀ ᴊᴏɪɴᴇᴅ ᴄʜᴀᴛ, ᴜsᴇʀ ʟᴇғᴛ ᴄʜᴀᴛ.

*ᴡᴇʟᴄᴏᴍᴇ ᴍᴀʀᴋᴅᴏᴡɴ:*
• /welcomehelp*:* ᴠɪᴇᴡ ᴍᴏʀᴇ ғᴏʀᴍᴀᴛᴛɪɴɢ ɪɴғᴏʀᴍᴀᴛɪᴏɴ ғᴏʀ ᴄᴜsᴛᴏᴍ ᴡᴇʟᴄᴏᴍᴇ/ɢᴏᴏᴅʙʏᴇ ᴍᴇssᴀɢᴇs.
"""

NEW_MEM_HANDLER = MessageHandler(
    filters.StatusUpdate.NEW_CHAT_MEMBERS, new_member, allow_edit=True, block=False
)
LEFT_MEM_HANDLER = MessageHandler(
    filters.StatusUpdate.LEFT_CHAT_MEMBER, left_member, allow_edit=True, block=False
)
WELC_PREF_HANDLER = CommandHandler(
    "welcome", welcome, filters=filters.ChatType.GROUPS, block=False
)
GOODBYE_PREF_HANDLER = CommandHandler(
    "goodbye", goodbye, filters=filters.ChatType.GROUPS, block=False
)
SET_WELCOME = CommandHandler(
    "setwelcome", set_welcome, filters=filters.ChatType.GROUPS, block=False
)
SET_GOODBYE = CommandHandler(
    "setgoodbye", set_goodbye, filters=filters.ChatType.GROUPS, block=False
)
RESET_WELCOME = CommandHandler(
    "resetwelcome", reset_welcome, filters=filters.ChatType.GROUPS, block=False
)
RESET_GOODBYE = CommandHandler(
    "resetgoodbye", reset_goodbye, filters=filters.ChatType.GROUPS, block=False
)
WELCOMEMUTE_HANDLER = CommandHandler(
    "welcomemute", welcomemute, filters=filters.ChatType.GROUPS, block=False
)
CLEAN_SERVICE_HANDLER = CommandHandler(
    "cleanservice", cleanservice, filters=filters.ChatType.GROUPS, block=False
)
CLEAN_WELCOME = CommandHandler(
    "cleanwelcome", clean_welcome, filters=filters.ChatType.GROUPS, block=False
)
WELCOME_HELP = CommandHandler("welcomehelp", welcome_help, block=False)
WELCOME_MUTE_HELP = CommandHandler("welcomemutehelp", welcome_mute_help, block=False)
BUTTON_VERIFY_HANDLER = CallbackQueryHandler(
    user_button, pattern=r"user_join_", block=False
)

application.add_handler(NEW_MEM_HANDLER)
application.add_handler(LEFT_MEM_HANDLER)
application.add_handler(WELC_PREF_HANDLER)
application.add_handler(GOODBYE_PREF_HANDLER)
application.add_handler(SET_WELCOME)
application.add_handler(SET_GOODBYE)
application.add_handler(RESET_WELCOME)
application.add_handler(RESET_GOODBYE)
application.add_handler(CLEAN_WELCOME)
application.add_handler(WELCOME_HELP)
application.add_handler(WELCOMEMUTE_HANDLER)
application.add_handler(CLEAN_SERVICE_HANDLER)
application.add_handler(BUTTON_VERIFY_HANDLER)
application.add_handler(WELCOME_MUTE_HELP)

__mod_name__ = "𝐖ᴇʟᴄᴏᴍᴇ"
__command_list__ = []
__handlers__ = [
    NEW_MEM_HANDLER,
    LEFT_MEM_HANDLER,
    WELC_PREF_HANDLER,
    GOODBYE_PREF_HANDLER,
    SET_WELCOME,
    SET_GOODBYE,
    RESET_WELCOME,
    RESET_GOODBYE,
    CLEAN_WELCOME,
    WELCOME_HELP,
    WELCOMEMUTE_HANDLER,
    CLEAN_SERVICE_HANDLER,
    BUTTON_VERIFY_HANDLER,
    WELCOME_MUTE_HELP,
]
