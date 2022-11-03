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
import html
import random
import re
import time
from functools import partial
from io import BytesIO

from telegram import (
    ChatPermissions,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ParseMode,
    Update,
    User,
)
from telegram.error import BadRequest, TelegramError
from telegram.ext import (
    CallbackContext,
    CallbackQueryHandler,
    CommandHandler,
    Filters,
    MessageHandler,
)
from telegram.utils.helpers import escape_markdown, mention_html, mention_markdown

import Exon.modules.sql.log_channel_sql as logsql
import Exon.modules.sql.welcome_sql as sql
from Exon import DEMONS, DEV_USERS, DRAGONS
from Exon import LOGGER as log
from Exon import OWNER_ID, WOLVES, dispatcher, sw
from Exon.modules.helper_funcs.anonymous import AdminPerms, user_admin
from Exon.modules.helper_funcs.chat_status import is_user_ban_protected
from Exon.modules.helper_funcs.chat_status import user_admin as u_admin
from Exon.modules.helper_funcs.misc import build_keyboard, revert_buttons
from Exon.modules.helper_funcs.msg_types import get_welcome_type
from Exon.modules.helper_funcs.string_handling import (
    escape_invalid_curly_brackets,
    markdown_parser,
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
    sql.Types.TEXT.value: dispatcher.bot.send_message,
    sql.Types.BUTTON_TEXT.value: dispatcher.bot.send_message,
    sql.Types.STICKER.value: dispatcher.bot.send_sticker,
    sql.Types.DOCUMENT.value: dispatcher.bot.send_document,
    sql.Types.PHOTO.value: dispatcher.bot.send_photo,
    sql.Types.AUDIO.value: dispatcher.bot.send_audio,
    sql.Types.VOICE.value: dispatcher.bot.send_voice,
    sql.Types.VIDEO.value: dispatcher.bot.send_video,
}

VERIFIED_USER_WAITLIST = {}
CAPTCHA_ANS_DICT = {}

from multicolorcaptcha import CaptchaGenerator

WHITELISTED = [OWNER_ID] + DEV_USERS + DRAGONS + DEMONS + WOLVES
# do not async
def send(update, message, keyboard, backup_message):
    chat = update.effective_chat
    cleanserv = sql.clean_service(chat.id)
    reply = update.message.message_id
    # Clean service welcome
    if cleanserv:
        try:
            dispatcher.bot.delete_message(chat.id, update.message.message_id)
        except BadRequest:
            pass
        reply = False
    try:
        msg = update.effective_message.reply_text(
            message,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=keyboard,
            reply_to_message_id=reply,
            allow_sending_without_reply=True,
        )
    except BadRequest as excp:
        if excp.message == "Button_url_invalid":
            msg = update.effective_message.reply_text(
                markdown_parser(
                    (
                        backup_message
                        + "\nɴᴏᴛᴇ: ᴛʜᴇ ᴄᴜʀʀᴇɴᴛ ᴍᴇssᴀɢᴇ ʜᴀs ᴀɴ ɪɴᴠᴀʟɪᴅ ᴜʀʟ ɪɴ ᴏɴᴇ ᴏғ ɪᴛs ʙᴜᴛᴛᴏɴs. ᴘʟᴇᴀsᴇ ᴜᴘᴅᴀᴛᴇ."
                    )
                ),
                parse_mode=ParseMode.MARKDOWN,
                reply_to_message_id=reply,
            )

        elif excp.message == "ʜᴀᴠᴇ ɴᴏ ʀɪɢʜᴛs ᴛᴏ sᴇɴᴅ ᴀ ᴍᴇssᴀɢᴇ":
            return
        elif excp.message == "ʀᴇᴘʟʏ ᴍᴇssᴀɢᴇ ɴᴏᴛ ғᴏᴜɴᴅ":
            msg = update.effective_message.reply_text(
                message,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=keyboard,
                quote=False,
            )

        elif excp.message == "Unsupported url protocol":
            msg = update.effective_message.reply_text(
                markdown_parser(
                    (
                        backup_message
                        + "\nNote: ᴛʜᴇ ᴄᴜʀʀᴇɴᴛ ᴍᴇssᴀɢᴇ ʜᴀs ʙᴜᴛᴛᴏɴs ᴡʜɪᴄʜ ᴜsᴇ ᴜʀʟ ᴘʀᴏᴛᴏᴄᴏʟs ᴛʜᴀᴛ ᴀʀᴇ ᴜɴsᴜᴘᴘᴏʀᴛᴇᴅ ʙʏ "
                        "ᴛᴇʟᴇɢʀᴀᴍ. ᴘʟᴇᴀsᴇ ᴜᴘᴅᴀᴛᴇ. "
                    )
                ),
                parse_mode=ParseMode.MARKDOWN,
                reply_to_message_id=reply,
            )

        elif excp.message == "Wrong url host":
            msg = update.effective_message.reply_text(
                markdown_parser(
                    (
                        backup_message
                        + "\nɴᴏᴛᴇ : ᴛʜᴇ ᴄᴜʀʀᴇɴᴛ ᴍᴇssᴀɢᴇ ʜᴀs sᴏᴍᴇ ʙᴀᴅ ᴜʀʟs. ᴘʟᴇᴀsᴇ ᴜᴘᴅᴀᴛᴇ."
                    )
                ),
                parse_mode=ParseMode.MARKDOWN,
                reply_to_message_id=reply,
            )

            log.warning(message)
            log.warning(keyboard)
            log.exception("ᴄᴏᴜʟᴅ ɴᴏᴛ ᴘᴀʀsᴇ! ɢᴏᴛ ɪɴᴠᴀʟɪᴅ ᴜʀʟ ʜᴏsᴛ ᴇʀʀᴏʀs")
        else:
            msg = update.effective_message.reply_text(
                markdown_parser(
                    (
                        backup_message
                        + "\nɴᴏᴛᴇ :: ᴀɴ ᴇʀʀᴏʀ ᴏᴄᴄᴜʀᴇᴅ ᴡʜᴇɴ sᴇɴᴅɪɴɢ ᴛʜᴇ ᴄᴜsᴛᴏᴍ ᴍᴇssᴀɢᴇ. ᴘʟᴇᴀsᴇ ᴜᴘᴅᴀᴛᴇ."
                    )
                ),
                parse_mode=ParseMode.MARKDOWN,
                reply_to_message_id=reply,
            )

            log.exception()
    return msg


@loggable
def new_member(update: Update, context: CallbackContext):  # sourcery no-metrics
    bot, job_queue = context.bot, context.job_queue
    chat = update.effective_chat
    user = update.effective_user
    msg = update.effective_message
    log_setting = logsql.get_chat_setting(chat.id)
    if not log_setting:
        logsql.set_chat_setting(
            logsql.LogChannelSettings(chat.id, True, True, True, True, True)
        )
        log_setting = logsql.get_chat_setting(chat.id)
    should_welc, cust_welcome, cust_content, welc_type = sql.get_welc_pref(chat.id)
    welc_mutes = sql.welcome_mutes(chat.id)
    human_checks = sql.get_human_checks(user.id, chat.id)
    raid, _, deftime = sql.getRaidStatus(str(chat.id))

    new_members = update.effective_message.new_chat_members

    for new_mem in new_members:

        welcome_log = None
        res = None
        sent = None
        should_mute = True
        welcome_bool = True
        media_wel = False

        if raid and new_mem.id not in WHITELISTED:
            bantime = deftime
            try:
                chat.ban_member(new_mem.id, until_date=bantime)
            except BadRequest:
                pass
            return

        if sw != None:
            sw_ban = sw.get_ban(new_mem.id)
            if sw_ban:
                return

        reply = update.message.message_id
        cleanserv = sql.clean_service(chat.id)
        # Clean service welcome
        if cleanserv:
            try:
                dispatcher.bot.delete_message(chat.id, update.message.message_id)
            except BadRequest:
                pass
            reply = False

        if should_welc:

            # Give the owner a special welcome
            if new_mem.id == OWNER_ID:
                update.effective_message.reply_text(
                    "ᴏɴɪᴄʜᴀɴ ᴀʀʀɪᴠᴇᴅ~ ᴍʏ ʜᴇᴀʀᴛ ɢᴏᴇs ᴍᴇᴏᴡ ᴍᴇᴏᴡ :3",
                    reply_to_message_id=reply,
                )
                welcome_log = (
                    f"{html.escape(chat.title)}\n"
                    f"#ᴜsᴇʀ_ᴊᴏɪɴᴇᴅ\n"
                    f"ʙᴏᴛ ᴏᴡɴᴇʀ ᴊᴜsᴛ ᴊᴏɪɴᴇᴅ ᴛʜᴇ ᴄʜᴀᴛ 🥰"
                )
                continue

            # Welcome Devs
            if new_mem.id in DEV_USERS:
                update.effective_message.reply_text(
                    "ᴡʜᴏ ᴀ! ᴀ ᴍᴇᴍʙᴇʀ ᴏғ ᴍʏ ғᴀᴍɪʟʏ ᴊᴜsᴛ ᴊᴏɪɴᴇᴅ!",
                    reply_to_message_id=reply,
                )
                continue

            # Welcome Sudos
            elif new_mem.id in DRAGONS:
                update.effective_message.reply_text(
                    "ʜᴜʜ! ᴍʏ ʙᴇsᴛғʀɪᴇɴᴅ ᴊᴜsᴛ ᴊᴏɪɴᴇᴅ! sᴛᴀʏ ᴀʟᴇʀᴛ !",
                    reply_to_message_id=reply,
                )
                continue

            # Welcome Support
            elif new_mem.id in DEMONS:
                update.effective_message.reply_text(
                    "ʜᴜʜ! ɪs ᴛʜᴀᴛ ᴀ ғʀɪᴇɴᴅ <3",
                    reply_to_message_id=reply,
                )
                continue

            # Welcome WOLVES
            elif new_mem.id in WOLVES:
                update.effective_message.reply_text(
                    "ᴏᴏғ! ᴍʏ ᴄʟᴀssᴍᴀᴛᴇ ᴊᴜsᴛ ᴊᴏɪɴᴇᴅ!", reply_to_message_id=reply
                )
                continue

            # Welcome yourself
            elif new_mem.id == bot.id:
                update.effective_message.reply_text(
                    "ᴛʜᴀɴᴋs ғᴏʀ ᴀᴅᴅɪɴɢ ᴍᴇ! ᴄʜᴇᴄᴋᴏᴜᴛ @AbishnoiMF ғᴏʀ ᴍᴏʀᴇ.",
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
                            sql.DEFAULT_WELCOME_MESSAGES
                        ).format(first=escape_markdown(first_name))

                    if new_mem.last_name:
                        fullname = escape_markdown(f"{first_name} {new_mem.last_name}")
                    else:
                        fullname = escape_markdown(first_name)
                    count = chat.get_member_count()
                    mention = mention_markdown(new_mem.id, escape_markdown(first_name))
                    if new_mem.username:
                        username = "@" + escape_markdown(new_mem.username)
                    else:
                        username = mention

                    valid_format = escape_invalid_curly_brackets(
                        cust_welcome, VALID_WELCOME_FORMATTERS
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
                        first=escape_markdown(first_name)
                    )
                    keyb = []

                backup_message = random.choice(sql.DEFAULT_WELCOME_MESSAGES).format(
                    first=escape_markdown(first_name)
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
            is_user_ban_protected(chat, new_mem.id, chat.get_member(new_mem.id))
            or human_checks
        ):
            should_mute = False
        # Join welcome: soft mute
        if new_mem.is_bot:
            should_mute = False

        if user.id == new_mem.id and should_mute:
            if welc_mutes == "soft":
                bot.restrict_chat_member(
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
                    ),
                    until_date=(int(time.time() + 24 * 60 * 60)),
                )
                sql.set_human_checks(user.id, chat.id)
            if welc_mutes == "strong":
                welcome_bool = False
                if not media_wel:
                    VERIFIED_USER_WAITLIST.update(
                        {
                            (chat.id, new_mem.id): {
                                "should_welc": should_welc,
                                "media_wel": False,
                                "status": False,
                                "update": update,
                                "res": res,
                                "keyboard": keyboard,
                                "backup_message": backup_message,
                            }
                        }
                    )
                else:
                    VERIFIED_USER_WAITLIST.update(
                        {
                            (chat.id, new_mem.id): {
                                "should_welc": should_welc,
                                "chat_id": chat.id,
                                "status": False,
                                "media_wel": True,
                                "cust_content": cust_content,
                                "welc_type": welc_type,
                                "res": res,
                                "keyboard": keyboard,
                            }
                        }
                    )
                new_join_mem = (
                    f"[{escape_markdown(new_mem.first_name)}](tg://user?id={user.id})"
                )
                message = msg.reply_text(
                    f"{new_join_mem}, ᴄʟɪᴄᴋ ᴛʜᴇ ʙᴜᴛᴛᴏɴ ʙᴇʟᴏᴡ ᴛᴏ ᴘʀᴏᴠᴇ ʏᴏᴜ'ʀᴇ ʜᴜᴍᴀɴ.\nʏᴏᴜ ʜᴀᴠᴇ 119 sᴇᴄᴏɴᴅs.",
                    reply_markup=InlineKeyboardMarkup(
                        [
                            [
                                InlineKeyboardButton(
                                    text="ʏᴇs, I'ᴍ ʜᴜᴍᴀɴ.",
                                    callback_data=f"user_join_({new_mem.id})",
                                )
                            ]
                        ]
                    ),
                    parse_mode=ParseMode.MARKDOWN,
                    reply_to_message_id=reply,
                    allow_sending_without_reply=True,
                )
                bot.restrict_chat_member(
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
                    ),
                )
                job_queue.run_once(
                    partial(check_not_bot, new_mem, chat.id, message.message_id),
                    120,
                    name="welcomemute",
                )
            if welc_mutes == "captcha":
                btn = []
                # Captcha image size number (2 -> 640x360)
                CAPCTHA_SIZE_NUM = 2
                # Create Captcha Generator object of specified size
                generator = CaptchaGenerator(CAPCTHA_SIZE_NUM)

                # Generate a captcha image
                captcha = generator.gen_captcha_image(difficult_level=3)
                # Get information
                image = captcha["image"]
                characters = captcha["characters"]
                # print(characters)
                fileobj = BytesIO()
                fileobj.name = f"captcha_{new_mem.id}.png"
                image.save(fp=fileobj)
                fileobj.seek(0)
                CAPTCHA_ANS_DICT[(chat.id, new_mem.id)] = int(characters)
                welcome_bool = False
                if not media_wel:
                    VERIFIED_USER_WAITLIST.update(
                        {
                            (chat.id, new_mem.id): {
                                "should_welc": should_welc,
                                "media_wel": False,
                                "status": False,
                                "update": update,
                                "res": res,
                                "keyboard": keyboard,
                                "backup_message": backup_message,
                                "captcha_correct": characters,
                            }
                        }
                    )
                else:
                    VERIFIED_USER_WAITLIST.update(
                        {
                            (chat.id, new_mem.id): {
                                "should_welc": should_welc,
                                "chat_id": chat.id,
                                "status": False,
                                "media_wel": True,
                                "cust_content": cust_content,
                                "welc_type": welc_type,
                                "res": res,
                                "keyboard": keyboard,
                                "captcha_correct": characters,
                            }
                        }
                    )

                nums = [random.randint(1000, 9999) for _ in range(7)]
                nums.append(characters)
                random.shuffle(nums)
                to_append = []
                # print(nums)
                for a in nums:
                    to_append.append(
                        InlineKeyboardButton(
                            text=str(a),
                            callback_data=f"user_captchajoin_({chat.id},{new_mem.id})_({a})",
                        )
                    )
                    if len(to_append) > 2:
                        btn.append(to_append)
                        to_append = []
                if to_append:
                    btn.append(to_append)

                message = msg.reply_photo(
                    fileobj,
                    caption=f"ᴡᴇʟᴄᴏᴍᴇ [{escape_markdown(new_mem.first_name)}](tg://user?id={user.id}). ᴄʟɪᴄᴋ ᴛʜᴇ ᴄᴏʀʀᴇᴄᴛ ʙᴜᴛᴛᴏɴ ᴛᴏ ɢᴇᴛ ᴜɴᴍᴜᴛᴇᴅ!\n"
                    f"ʏᴏᴜ ɢᴏᴛ 119 sᴇᴄᴏɴᴅs ғᴏʀ ᴛʜɪs.",
                    reply_markup=InlineKeyboardMarkup(btn),
                    parse_mode=ParseMode.MARKDOWN,
                    reply_to_message_id=reply,
                    allow_sending_without_reply=True,
                )
                bot.restrict_chat_member(
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
                    ),
                )
                job_queue.run_once(
                    partial(check_not_bot, new_mem, chat.id, message.message_id),
                    120,
                    name="welcomemute",
                )

        if welcome_bool:
            if media_wel:
                if ENUM_FUNC_MAP[welc_type] == dispatcher.bot.send_sticker:
                    sent = ENUM_FUNC_MAP[welc_type](
                        chat.id,
                        cust_content,
                        reply_markup=keyboard,
                        reply_to_message_id=reply,
                    )
                else:
                    sent = ENUM_FUNC_MAP[welc_type](
                        chat.id,
                        cust_content,
                        caption=res,
                        reply_markup=keyboard,
                        reply_to_message_id=reply,
                        parse_mode="markdown",
                    )
            else:
                sent = send(update, res, keyboard, backup_message)
            prev_welc = sql.get_clean_pref(chat.id)
            if prev_welc:
                try:
                    bot.delete_message(chat.id, prev_welc)
                except BadRequest:
                    pass

                if sent:
                    sql.set_clean_welcome(chat.id, sent.message_id)

        if not log_setting.log_joins:
            return ""
        if welcome_log:
            return welcome_log

    return ""


def check_not_bot(
    member: User, chat_id: int, message_id: int, context: CallbackContext
):
    bot = context.bot
    member_dict = VERIFIED_USER_WAITLIST.pop((chat_id, member.id))
    member_status = member_dict.get("status")
    if not member_status:
        try:
            bot.unban_chat_member(chat_id, member.id)
        except BadRequest:
            pass

        try:
            bot.edit_message_text(
                "*ᴋɪᴄᴋs ᴜsᴇʀ*\nᴛʜᴇʏ ᴄᴀɴ ᴀʟᴡᴀʏs ʀᴇᴊᴏɪɴ ᴀɴᴅ ᴛʀʏ.",
                chat_id=chat_id,
                message_id=message_id,
            )
        except TelegramError:
            bot.delete_message(chat_id=chat_id, message_id=message_id)
            bot.send_message(
                "{} ᴡᴀs ᴋɪᴄᴋᴇᴅ ᴀs ᴛʜᴇʏ ғᴀɪʟᴇᴅ ᴛᴏ ᴠᴇʀɪғʏ ᴛʜᴇᴍsᴇʟᴠᴇs".format(
                    mention_html(member.id, member.first_name)
                ),
                chat_id=chat_id,
                parse_mode=ParseMode.HTML,
            )


def left_member(update: Update, context: CallbackContext):  # sourcery no-metrics
    bot = context.bot
    chat = update.effective_chat
    user = update.effective_user
    should_goodbye, cust_goodbye, goodbye_type = sql.get_gdbye_pref(chat.id)

    if user.id == bot.id:
        return

    reply = update.message.message_id
    cleanserv = sql.clean_service(chat.id)
    # Clean service welcome
    if cleanserv:
        try:
            dispatcher.bot.delete_message(chat.id, update.message.message_id)
        except BadRequest:
            pass
        reply = False

    if should_goodbye:

        left_mem = update.effective_message.left_chat_member
        if left_mem:

            # Thingy for spamwatched users
            if sw:
                sw_ban = sw.get_ban(left_mem.id)
                if sw_ban:
                    return

            # Dont say goodbyes to gbanned users
            if is_user_gbanned(left_mem.id):
                return

            # Ignore bot being kicked
            if left_mem.id == bot.id:
                return

            # Give the owner a special goodbye
            if left_mem.id == OWNER_ID:
                update.effective_message.reply_text(
                    "sᴏʀʀʏ ᴛᴏ sᴇᴇ ʏᴏᴜ ʟᴇᴀᴠᴇ :(", reply_to_message_id=reply
                )
                return

            # Give the devs a special goodbye
            elif left_mem.id in DEV_USERS:
                update.effective_message.reply_text(
                    "sᴇᴇ ʏᴏᴜ ʟᴀᴛᴇʀ ᴀᴛ ᴛʜᴇ ᴇᴀɢʟᴇ ᴜɴɪᴏɴ!",
                    reply_to_message_id=reply,
                )
                return

            # if media goodbye, use appropriate function for it
            if goodbye_type not in [sql.Types.TEXT, sql.Types.BUTTON_TEXT]:
                ENUM_FUNC_MAP[goodbye_type](chat.id, cust_goodbye)
                return

            first_name = (
                left_mem.first_name or "PersonWithNoName"
            )  # edge case of empty name - occurs for some bugs.
            if cust_goodbye:
                if cust_goodbye == sql.DEFAULT_GOODBYE:
                    cust_goodbye = random.choice(sql.DEFAULT_GOODBYE_MESSAGES).format(
                        first=escape_markdown(first_name)
                    )
                if left_mem.last_name:
                    fullname = escape_markdown(f"{first_name} {left_mem.last_name}")
                else:
                    fullname = escape_markdown(first_name)
                count = chat.get_member_count()
                mention = mention_markdown(left_mem.id, first_name)
                if left_mem.username:
                    username = "@" + escape_markdown(left_mem.username)
                else:
                    username = mention

                valid_format = escape_invalid_curly_brackets(
                    cust_goodbye, VALID_WELCOME_FORMATTERS
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
                    first=first_name
                )
                keyb = []

            keyboard = InlineKeyboardMarkup(keyb)

            send(
                update,
                res,
                keyboard,
                random.choice(sql.DEFAULT_GOODBYE_MESSAGES).format(first=first_name),
            )


@u_admin
def welcome(update: Update, context: CallbackContext):
    args = context.args
    chat = update.effective_chat
    # if no args, show current replies.
    if not args or args[0].lower() == "noformat":
        noformat = True
        pref, welcome_m, cust_content, welcome_type = sql.get_welc_pref(chat.id)
        update.effective_message.reply_text(
            f"ᴛʜɪs ᴄʜᴀᴛ ʜᴀs ɪᴛ's ᴡᴇʟᴄᴏᴍᴇ sᴇᴛᴛɪɴɢ sᴇᴛ ᴛᴏ: `{pref}`.\n"
            f"*ᴛʜᴇ ᴡᴇʟᴄᴏᴍᴇ ᴍᴇssᴀɢᴇ (not filling the {{}}) ɪs:*",
            parse_mode=ParseMode.MARKDOWN,
        )

        if welcome_type in [sql.Types.BUTTON_TEXT, sql.Types.TEXT]:
            buttons = sql.get_welc_buttons(chat.id)
            if noformat:
                welcome_m += revert_buttons(buttons)
                update.effective_message.reply_text(welcome_m)

            else:
                keyb = build_keyboard(buttons)
                keyboard = InlineKeyboardMarkup(keyb)

                send(update, welcome_m, keyboard, sql.DEFAULT_WELCOME)
        else:
            buttons = sql.get_welc_buttons(chat.id)
            if noformat:
                welcome_m += revert_buttons(buttons)
                ENUM_FUNC_MAP[welcome_type](chat.id, cust_content, caption=welcome_m)

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
            update.effective_message.reply_text(
                "ᴏᴋᴀʏ! I'll ɢʀᴇᴇᴛ ᴍᴇᴍʙᴇʀs ᴡʜᴇɴ ᴛʜᴇʏ ᴊᴏɪɴ."
            )

        elif args[0].lower() in ("off", "no"):
            sql.set_welc_preference(str(chat.id), False)
            update.effective_message.reply_text(
                "I'll ɢᴏ ʟᴏᴀғ ᴀʀᴏᴜɴᴅ ᴀɴᴅ ɴᴏᴛ ᴡᴇʟᴄᴏᴍᴇ ᴀɴʏᴏɴᴇ ᴛʜᴇɴ."
            )

        else:
            update.effective_message.reply_text(
                "I ᴜɴᴅᴇʀsᴛᴀɴᴅ 'on/yes' ᴏʀ 'off/no' ᴏɴʟʏ!"
            )


@u_admin
def goodbye(update: Update, context: CallbackContext):
    args = context.args
    chat = update.effective_chat

    if not args or args[0] == "noformat":
        noformat = True
        pref, goodbye_m, goodbye_type = sql.get_gdbye_pref(chat.id)
        update.effective_message.reply_text(
            f"ᴛʜɪs ᴄʜᴀᴛ ʜᴀs ɪᴛ's ɢᴏᴏᴅʙʏᴇ sᴇᴛᴛɪɴɢ sᴇᴛ ᴛᴏ: `{pref}`.\n"
            f"*ᴛʜᴇ ɢᴏᴏᴅʙʏᴇ  ᴍᴇssᴀɢᴇ (not filling the {{}}) ɪs:*",
            parse_mode=ParseMode.MARKDOWN,
        )

        if goodbye_type == sql.Types.BUTTON_TEXT:
            buttons = sql.get_gdbye_buttons(chat.id)
            if noformat:
                goodbye_m += revert_buttons(buttons)
                update.effective_message.reply_text(goodbye_m)

            else:
                keyb = build_keyboard(buttons)
                keyboard = InlineKeyboardMarkup(keyb)

                send(update, goodbye_m, keyboard, sql.DEFAULT_GOODBYE)

        elif noformat:
            ENUM_FUNC_MAP[goodbye_type](chat.id, goodbye_m)

        else:
            ENUM_FUNC_MAP[goodbye_type](
                chat.id, goodbye_m, parse_mode=ParseMode.MARKDOWN
            )

    elif len(args) >= 1:
        if args[0].lower() in ("on", "yes"):
            sql.set_gdbye_preference(str(chat.id), True)
            update.effective_message.reply_text("Ok!")

        elif args[0].lower() in ("off", "no"):
            sql.set_gdbye_preference(str(chat.id), False)
            update.effective_message.reply_text("Ok!")

        else:
            # idek what you're writing, say yes or no
            update.effective_message.reply_text(
                "I ᴜɴᴅᴇʀsᴛᴀɴᴅ 'on/yes' ᴏʀ 'off/no' ᴏɴʟʏ!"
            )


@user_admin(AdminPerms.CAN_CHANGE_INFO)
@loggable
def set_welcome(update: Update, context: CallbackContext) -> str:
    chat = update.effective_chat
    user = update.effective_user
    msg = update.effective_message

    text, data_type, content, buttons = get_welcome_type(msg)

    if data_type is None:
        msg.reply_text("ʏᴏᴜ ᴅɪᴅɴ'ᴛ sᴘᴇᴄɪғʏ ᴡʜᴀᴛ ᴛᴏ ʀᴇᴘʟʏ ᴡɪᴛʜ!")
        return ""

    sql.set_custom_welcome(chat.id, content, text, data_type, buttons)
    msg.reply_text("sᴜᴄᴄᴇssғᴜʟʟʏ sᴇᴛ ᴄᴜsᴛᴏᴍ ᴡᴇʟᴄᴏᴍᴇ ᴍᴇssᴀɢᴇ!")

    return (
        f"<b>{html.escape(chat.title)}:</b>\n"
        f"#sᴇᴛ_ᴡᴇʟᴄᴏᴍᴇ\n"
        f"<b>ᴀᴅᴍɪɴ:</b> {mention_html(user.id, user.first_name)}\n"
        f"sᴇᴛ ᴛʜᴇ welcome ᴍᴇssᴀɢᴇ."
    )


@user_admin(AdminPerms.CAN_CHANGE_INFO)
@loggable
def reset_welcome(update: Update, context: CallbackContext) -> str:
    chat = update.effective_chat
    user = update.effective_user

    sql.set_custom_welcome(chat.id, None, sql.DEFAULT_WELCOME, sql.Types.TEXT)
    update.effective_message.reply_text(
        "sᴜᴄᴄᴇssғᴜʟʟʏ ʀᴇsᴇᴛ ᴡᴇʟᴄᴏᴍᴇ ᴍᴇssᴀɢᴇ ᴛᴏ ᴅᴇғᴀᴜʟᴛ!"
    )

    return (
        f"<b>{html.escape(chat.title)}:</b>\n"
        f"#ʀᴇsᴇᴛ_ᴡᴇʟᴄᴏᴍᴇ\n"
        f"<b>ᴀᴅᴍɪɴ:</b> {mention_html(user.id, user.first_name)}\n"
        f"ʀᴇsᴇᴛ ᴛʜᴇ ᴡᴇʟᴄᴏᴍᴇ ᴍᴇssᴀɢᴇ ᴛᴏ ᴅᴇғᴀᴜʟᴛ."
    )


@user_admin(AdminPerms.CAN_CHANGE_INFO)
@loggable
def set_goodbye(update: Update, context: CallbackContext) -> str:
    chat = update.effective_chat
    user = update.effective_user
    msg = update.effective_message
    text, data_type, content, buttons = get_welcome_type(msg)

    if data_type is None:
        msg.reply_text("You ᴅɪᴅɴ'ᴛ sᴘᴇᴄɪғʏ ᴡʜᴀᴛ ᴛᴏ ʀᴇᴘʟʏ ᴡɪᴛʜ!")
        return ""

    sql.set_custom_gdbye(chat.id, content or text, data_type, buttons)
    msg.reply_text("sᴜᴄᴄᴇssғᴜʟʟʏ sᴇᴛ ᴄᴜsᴛᴏᴍ ɢᴏᴏᴅʙʏᴇ ᴍᴇssᴀɢᴇ!")
    return (
        f"<b>{html.escape(chat.title)}:</b>\n"
        f"#sᴇᴛ_ɢᴏᴏᴅʙʏᴇ\n"
        f"<b>ᴀᴅᴍɪɴ:</b> {mention_html(user.id, user.first_name)}\n"
        f"sᴇᴛ ᴛʜᴇ ɢᴏᴏᴅʙʏᴇ ᴍᴇssᴀɢᴇ."
    )


@user_admin(AdminPerms.CAN_CHANGE_INFO)
@loggable
def reset_goodbye(update: Update, context: CallbackContext) -> str:
    chat = update.effective_chat
    user = update.effective_user

    sql.set_custom_gdbye(chat.id, sql.DEFAULT_GOODBYE, sql.Types.TEXT)
    update.effective_message.reply_text(
        "sᴜᴄᴄᴇssғᴜʟʟʏ ʀᴇsᴇᴛ ɢᴏᴏᴅʙʏᴇ ᴍᴇssᴀɢᴇ ᴛᴏ ᴅᴇғᴀᴜʟᴛ!"
    )

    return (
        f"<b>{html.escape(chat.title)}:</b>\n"
        f"#ʀᴇsᴇᴛ_ɢᴏᴏᴅʙʏᴇ\n"
        f"<b>ᴀᴅᴍɪɴ:</b> {mention_html(user.id, user.first_name)}\n"
        f"ʀᴇsᴇᴛ ᴛʜᴇ ɢᴏᴏᴅʙʏᴇ ᴍᴇssᴀɢᴇ."
    )


@user_admin(AdminPerms.CAN_CHANGE_INFO)
@loggable
def welcomemute(update: Update, context: CallbackContext) -> str:
    args = context.args
    chat = update.effective_chat
    user = update.effective_user
    msg = update.effective_message

    if len(args) >= 1:
        if args[0].lower() in ("off", "no"):
            sql.set_welcome_mutes(chat.id, False)
            msg.reply_text("I ᴡɪʟʟ ɴᴏ ʟᴏɴɢᴇʀ ᴍᴜᴛᴇ ᴘᴇᴏᴘʟᴇ ᴏɴ ᴊᴏɪɴɪɴɢ!")
            return (
                f"<b>{html.escape(chat.title)}:</b>\n"
                f"#ᴡᴇʟᴄᴏᴍᴇ_ᴍᴜᴛᴇ\n"
                f"<b>• ᴀᴅᴍɪɴ:</b> {mention_html(user.id, user.first_name)}\n"
                f"ʜᴀs ᴛᴏɢɢʟᴇᴅ ᴡᴇʟᴄᴏᴍᴇ ᴍᴜᴛᴇ ᴛᴏ <b>ᴏғғ</b>."
            )
        elif args[0].lower() in ["soft"]:
            sql.set_welcome_mutes(chat.id, "soft")
            msg.reply_text(
                "I ᴡɪʟʟ ʀᴇsᴛʀɪᴄᴛ ᴜsᴇʀ's ᴘᴇʀᴍɪssɪᴏɴ ᴛᴏ sᴇɴᴅ ᴍᴇᴅɪᴀ ғᴏʀ 24 ʜᴏᴜʀs."
            )
            return (
                f"<b>{html.escape(chat.title)}:</b>\n"
                f"#ᴡᴇʟᴄᴏᴍᴇ_ᴍᴜᴛᴇ\n"
                f"<b>• ᴀᴅᴍɪɴ:</b> {mention_html(user.id, user.first_name)}\n"
                f"ʜᴀs ᴛᴏɢɢʟᴇᴅ ᴡᴇʟᴄᴏᴍᴇ ᴍᴜᴛᴇ ᴛᴏ <b>sᴏғᴛ</b>."
            )
        elif args[0].lower() in ["strong"]:
            sql.set_welcome_mutes(chat.id, "strong")
            msg.reply_text(
                "I ᴡɪʟʟ ɴᴏᴡ ᴍᴜᴛᴇ ᴘᴇᴏᴘʟᴇ ᴡʜᴇɴ ᴛʜᴇʏ ᴊᴏɪɴ ᴜɴᴛɪʟ ᴛʜᴇʏ ᴘʀᴏᴠᴇ ᴛʜᴇʏ'ʀᴇ  ɴᴏᴛ ᴀ ʙᴏᴛ.\nᴛʜᴇʏ ᴡɪʟʟ ʜᴀᴠᴇ 119 sᴇᴄᴏɴᴅs "
                "ʙᴇғᴏʀᴇ ᴛʜᴇʏ ɢᴇᴛ ᴋɪᴄᴋᴇᴅ. "
            )
            return (
                f"<b>{html.escape(chat.title)}:</b>\n"
                f"#ᴡᴇʟᴄᴏᴍᴇ_ᴍᴜᴛᴇ\n"
                f"<b>• ᴀᴅᴍɪɴ:</b> {mention_html(user.id, user.first_name)}\n"
                f"ʜᴀs ᴛᴏɢɢʟᴇᴅ ᴛᴏɢɢʟᴇᴅ ᴍᴜᴛᴇ ᴛᴏ <b>sᴛʀᴏɴɢ</b>."
            )
        elif args[0].lower() in ["captcha"]:
            sql.set_welcome_mutes(chat.id, "captcha")
            msg.reply_text(
                "I ᴡɪʟʟ ɴᴏᴡ ᴍᴜᴛᴇ ᴘᴇᴏᴘʟᴇ ᴡʜᴇɴ ᴛʜᴇʏ ᴊᴏɪɴ ᴜɴᴛɪʟ ᴛʜᴇʏ ᴘʀᴏᴠᴇ ᴛʜᴇʏ'ʀᴇ  ɴᴏᴛ ᴀ ʙᴏᴛ.\n ᴛʜᴇʏ ʜᴀᴠᴇ ᴛᴏ sᴏʟᴠᴇ a "
                "ᴄᴀᴘᴛᴄʜᴀ ᴛᴏ ɢᴇᴛ ᴜɴᴍᴜᴛᴇᴅ. "
            )
            return (
                f"<b>{html.escape(chat.title)}:</b>\n"
                f"#ᴡᴇʟᴄᴏᴍᴇ_ᴍᴜᴛᴇ\n"
                f"<b>• ᴀᴅᴍɪɴ:</b> {mention_html(user.id, user.first_name)}\n"
                f"ʜᴀs ᴛᴏɢɢʟᴇᴅ ᴡᴇʟᴄᴏᴍᴇ ᴍᴜᴛᴇ ᴛᴏ <b>ᴄᴀᴘᴛᴄʜᴀ</b>."
            )
        else:
            msg.reply_text(
                "ᴘʟᴇᴀsᴇ ᴇɴᴛᴇʀ `off`/`no`/`soft`/`strong`/`captcha`!",
                parse_mode=ParseMode.MARKDOWN,
            )
            return ""
    else:
        curr_setting = sql.welcome_mutes(chat.id)
        reply = (
            f"\n ɢɪᴠᴇ ᴍᴇ ᴀ sᴇᴛᴛɪɴɢ!\nᴄʜᴏᴏsᴇ ᴏɴᴇ ᴏᴜᴛ ᴏғ: `off`/`no` ᴏʀ `soft`, `strong` ᴏʀ `captcha` ᴏɴʟʏ! \n"
            f"ᴄᴜʀʀᴇɴᴛ sᴇᴛᴛɪɴɢ: `{curr_setting}`"
        )
        msg.reply_text(reply, parse_mode=ParseMode.MARKDOWN)
        return ""


@user_admin(AdminPerms.CAN_CHANGE_INFO)
@loggable
def clean_welcome(update: Update, context: CallbackContext) -> str:
    args = context.args
    chat = update.effective_chat
    user = update.effective_user

    if not args:
        clean_pref = sql.get_clean_pref(chat.id)
        if clean_pref:
            update.effective_message.reply_text(
                "I sʜᴏᴜʟᴅ ʙᴇ ᴅᴇʟᴇᴛɪɴɢ ᴡᴇʟᴄᴏᴍᴇ ᴍᴇssᴀɢᴇs ᴜᴘ ᴛᴏ ᴛᴡᴏ ᴅᴀʏs ᴏʟᴅ."
            )
        else:
            update.effective_message.reply_text(
                "I'ᴍ ᴄᴜʀʀᴇɴᴛʟʏ not ᴅᴇʟᴇᴛɪɴɢ ᴏʟᴅ ᴡᴇʟᴄᴏᴍᴇ ᴍᴇssᴀɢᴇs!"
            )
        return ""

    if args[0].lower() in ("on", "yes"):
        sql.set_clean_welcome(str(chat.id), True)
        update.effective_message.reply_text("I'ʟʟ ᴛʀʏ ᴛᴏ ᴅᴇʟᴇᴛᴇ ᴏʟᴅ ᴡᴇʟᴄᴏᴍᴇ ᴍᴇssᴀɢᴇs!")
        return (
            f"<b>{html.escape(chat.title)}:</b>\n"
            f"#ᴄʟᴇᴀɴ_ᴡᴇʟᴄᴏᴍᴇ\n"
            f"<b>ᴀᴅᴍɪɴ:</b> {mention_html(user.id, user.first_name)}\n"
            f"ʜᴀs ᴛᴏɢɢʟᴇᴅ ᴄʟᴇᴀɴ ᴡᴇʟᴄᴏᴍᴇs ᴛᴏ <code>ON</code>."
        )
    elif args[0].lower() in ("off", "no"):
        sql.set_clean_welcome(str(chat.id), False)
        update.effective_message.reply_text("I ᴡᴏɴ'ᴛ ᴅᴇʟᴇᴛᴇ ᴏʟᴅ ᴡᴇʟᴄᴏᴍᴇ ᴍᴇssᴀɢᴇs.")
        return (
            f"<b>{html.escape(chat.title)}:</b>\n"
            f"#ᴄʟᴇᴀɴ_ᴡᴇʟᴄᴏᴍᴇ\n"
            f"<b>ᴀᴅᴍɪɴ:</b> {mention_html(user.id, user.first_name)}\n"
            f"ʜᴀs ᴛᴏɢɢʟᴇᴅ ᴄʟᴇᴀɴ ᴡᴇʟᴄᴏᴍᴇs ᴛᴏ <code>OFF</code>."
        )
    else:
        update.effective_message.reply_text("I ᴜɴᴅᴇʀsᴛᴀɴᴅ 'on/yes' ᴏʀ 'off/no' only!")
        return ""


def user_button(update: Update, context: CallbackContext):
    chat = update.effective_chat
    user = update.effective_user
    query = update.callback_query
    bot = context.bot
    match = re.match(r"user_join_\((.+?)\)", query.data)
    message = update.effective_message
    join_user = int(match.group(1))

    if join_user == user.id:
        sql.set_human_checks(user.id, chat.id)
        member_dict = VERIFIED_USER_WAITLIST[(chat.id, user.id)]
        member_dict["status"] = True
        query.answer(text="ʏᴇᴇᴛ ! ʏᴏᴜ'ʀᴇ ᴀ ʜᴜᴍᴀɴ, ᴜɴᴍᴜᴛᴇᴅ!")
        bot.restrict_chat_member(
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
            ),
        )
        try:
            bot.deleteMessage(chat.id, message.message_id)
        except:
            pass
        if member_dict["should_welc"]:
            if member_dict["media_wel"]:
                sent = ENUM_FUNC_MAP[member_dict["welc_type"]](
                    member_dict["chat_id"],
                    member_dict["cust_content"],
                    caption=member_dict["res"],
                    reply_markup=member_dict["keyboard"],
                    parse_mode="markdown",
                )
            else:
                sent = send(
                    member_dict["update"],
                    member_dict["res"],
                    member_dict["keyboard"],
                    member_dict["backup_message"],
                )

            prev_welc = sql.get_clean_pref(chat.id)
            if prev_welc:
                try:
                    bot.delete_message(chat.id, prev_welc)
                except BadRequest:
                    pass

                if sent:
                    sql.set_clean_welcome(chat.id, sent.message_id)

    else:
        query.answer(text="ʏᴏᴜ'ʀᴇ ɴᴏᴛ ᴀʟʟᴏᴡᴇᴅ ᴛᴏ ᴅᴏ ᴛʜɪs!")


def user_captcha_button(update: Update, context: CallbackContext):
    # sourcery no-metrics
    chat = update.effective_chat
    user = update.effective_user
    query = update.callback_query
    bot = context.bot
    # print(query.data)
    match = re.match(r"user_captchajoin_\(([\d\-]+),(\d+)\)_\((\d{4})\)", query.data)
    message = update.effective_message
    join_chat = int(match.group(1))
    join_user = int(match.group(2))
    captcha_ans = int(match.group(3))
    join_usr_data = bot.getChat(join_user)

    if join_user == user.id:
        c_captcha_ans = CAPTCHA_ANS_DICT.pop((join_chat, join_user))
        if c_captcha_ans == captcha_ans:
            sql.set_human_checks(user.id, chat.id)
            member_dict = VERIFIED_USER_WAITLIST[(chat.id, user.id)]
            member_dict["status"] = True
            query.answer(text="ʏᴇᴇᴛ! ʏᴏᴜ'ʀᴇ a ʜᴜᴍᴀɴ, ᴜɴᴍᴜᴛᴇᴅ!")
            bot.restrict_chat_member(
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
                ),
            )
            try:
                bot.deleteMessage(chat.id, message.message_id)
            except:
                pass
            if member_dict["should_welc"]:
                if member_dict["media_wel"]:
                    sent = ENUM_FUNC_MAP[member_dict["welc_type"]](
                        member_dict["chat_id"],
                        member_dict["cust_content"],
                        caption=member_dict["res"],
                        reply_markup=member_dict["keyboard"],
                        parse_mode="markdown",
                    )
                else:
                    sent = send(
                        member_dict["update"],
                        member_dict["res"],
                        member_dict["keyboard"],
                        member_dict["backup_message"],
                    )

                prev_welc = sql.get_clean_pref(chat.id)
                if prev_welc:
                    try:
                        bot.delete_message(chat.id, prev_welc)
                    except BadRequest:
                        pass

                    if sent:
                        sql.set_clean_welcome(chat.id, sent.message_id)
        else:
            try:
                bot.deleteMessage(chat.id, message.message_id)
            except:
                pass
            kicked_msg = f"""
            ❌ [{escape_markdown(join_usr_data.first_name)}](tg://user?id={join_user}) ғᴀɪʟᴇᴅ ᴛʜᴇ ᴄᴀᴘᴛᴄʜᴀ ᴀɴᴅ ᴡᴀs ᴋɪᴄᴋᴇᴅ.
            """
            query.answer(text="ᴡʀᴏɴɢ ᴀɴsᴡᴇʀ")
            res = chat.unban_member(join_user)
            if res:
                bot.sendMessage(
                    chat_id=chat.id, text=kicked_msg, parse_mode=ParseMode.MARKDOWN
                )

    else:
        query.answer(text="ᴀʙᴇ ʟᴇᴠᴅᴇ ᴀᴘɴᴀ ᴋᴀᴍ ᴋᴀʀ ɴᴀ!")


WELC_HELP_TXT = (
    "Your group's welcome/goodbye messages can be personalised in multiple ways. If you want the messages"
    " to be individually generated, like the default welcome message is, you can use *these* variables:\n"
    " • `{first}`*:* this represents the user's *first* name\n"
    " • `{last}`*:* this represents the user's *last* name. Defaults to *first name* if user has no "
    "last name.\n"
    " • `{fullname}`*:* this represents the user's *full* name. Defaults to *first name* if user has no "
    "last name.\n"
    " • `{username}`*:* this represents the user's *username*. Defaults to a *mention* of the user's "
    "first name if has no username.\n"
    " • `{mention}`*:* this simply *mentions* a user - tagging them with their first name.\n"
    " • `{id}`*:* this represents the user's *id*\n"
    " • `{count}`*:* this represents the user's *member number*.\n"
    " • `{chatname}`*:* this represents the *current chat name*.\n"
    "\nEach variable MUST be surrounded by `{}` to be replaced.\n"
    "Welcome messages also support markdown, so you can make any elements bold/italic/code/links. "
    "Buttons are also supported, so you can make your welcomes look awesome with some nice intro "
    "buttons.\n"
    f"To create a button linking to your rules, use this: `[Rules](buttonurl://t.me/{dispatcher.bot.username}?start=group_id)`. "
    "Simply replace `group_id` with your group's id, which can be obtained via /id, and you're good to "
    "go. Note that group ids are usually preceded by a `-` sign; this is required, so please don't "
    "remove it.\n"
    "You can even set images/gifs/videos/voice messages as the welcome message by "
    "replying to the desired media, and calling `/setwelcome`."
)

WELC_MUTE_HELP_TXT = (
    "You can get the bot to mute new people who join your group and hence prevent spambots from flooding your group. "
    "The following options are possible:\n"
    "• `/welcomemute soft`*:* restricts new members from sending media for 24 hours.\n"
    "• `/welcomemute strong`*:* mutes new members till they tap on a button thereby verifying they're human.\n"
    "• `/welcomemute captcha`*:*  mutes new members till they solve a button captcha thereby verifying they're human.\n"
    "• `/welcomemute off`*:* turns off welcomemute.\n"
    "*Note:* Strong mode kicks a user from the chat if they dont verify in 120seconds. They can always rejoin though"
)


@u_admin
def welcome_help(update: Update, context: CallbackContext):
    update.effective_message.reply_text(WELC_HELP_TXT, parse_mode=ParseMode.MARKDOWN)


@u_admin
def welcome_mute_help(update: Update, context: CallbackContext):
    update.effective_message.reply_text(
        WELC_MUTE_HELP_TXT, parse_mode=ParseMode.MARKDOWN
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
        "It's ɢᴏᴏᴅʙʏᴇ ᴘʀᴇғᴇʀᴇɴᴄᴇ ɪs `{}`.".format(welcome_pref, goodbye_pref)
    )


__help__ = """
*ᴀᴅᴍɪɴs ᴏɴʟʏ:*

❂ /welcome <ᴏɴ/ᴏғғ>*:* `ᴇɴᴀʙʟᴇ/ᴅɪsᴀʙʟᴇ ᴡᴇʟᴄᴏᴍᴇ ᴍᴇssᴀɢᴇs.`

❂ /welcome *:* `sʜᴏᴡs ᴄᴜʀʀᴇɴᴛ ᴡᴇʟᴄᴏᴍᴇ sᴇᴛᴛɪɴɢs.`

❂ /welcome noformat *:* `sʜᴏᴡs ᴄᴜʀʀᴇɴᴛ ᴡᴇʟᴄᴏᴍᴇ sᴇᴛᴛɪɴɢs, ᴡɪᴛʜᴏᴜᴛ ᴛʜᴇ ғᴏʀᴍᴀᴛᴛɪɴɢ - ᴜsᴇғᴜʟ ᴛᴏ ʀᴇᴄʏᴄʟᴇ ʏᴏᴜʀ ᴡᴇʟᴄᴏᴍᴇ ᴍᴇssᴀɢᴇs!`

❂ /goodbye *:* `sᴀᴍᴇ ᴜsᴀɢᴇ ᴀɴᴅ ᴀʀɢs ᴀs` `/ᴡᴇʟᴄᴏᴍᴇ`.

❂ /setwelcome  <sᴏᴍᴇᴛᴇxᴛ>*:* `sᴇᴛ ᴀ ᴄᴜsᴛᴏᴍ ᴡᴇʟᴄᴏᴍᴇ ᴍᴇssᴀɢᴇ. ɪғ ᴜsᴇᴅ ʀᴇᴘʟʏɪɴɢ ᴛᴏ ᴍᴇᴅɪᴀ, ᴜsᴇs ᴛʜᴀᴛ ᴍᴇᴅɪᴀ.`

❂ /setgoodbye <sᴏᴍᴇᴛᴇxᴛ>*:* `sᴇᴛ ᴀ ᴄᴜsᴛᴏᴍ ɢᴏᴏᴅʙʏᴇ ᴍᴇssᴀɢᴇ. ɪғ ᴜsᴇᴅ ʀᴇᴘʟʏɪɴɢ ᴛᴏ ᴍᴇᴅɪᴀ, ᴜsᴇs ᴛʜᴀᴛ ᴍᴇᴅɪᴀ.`

❂ /resetwelcome *:* `ʀᴇsᴇᴛ ᴛᴏ ᴛʜᴇ ᴅᴇғᴀᴜʟᴛ ᴡᴇʟᴄᴏᴍᴇ ᴍᴇssᴀɢᴇ.`

❂ /resetgoodbye *:* `ʀᴇsᴇᴛ ᴛᴏ ᴛʜᴇ ᴅᴇғᴀᴜʟᴛ ɢᴏᴏᴅʙʏᴇ ᴍᴇssᴀɢᴇ.`

❂ /cleanwelcome  <ᴏɴ/ᴏғғ>*:* `ᴏɴ ɴᴇᴡ ᴍᴇᴍʙᴇʀ, ᴛʀʏ ᴛᴏ ᴅᴇʟᴇᴛᴇ ᴛʜᴇ ᴘʀᴇᴠɪᴏᴜs ᴡᴇʟᴄᴏᴍᴇ ᴍᴇssᴀɢᴇ ᴛᴏ ᴀᴠᴏɪᴅ sᴘᴀᴍᴍɪɴɢ ᴛʜᴇ ᴄʜᴀᴛ`

❂ /welcomemutehelp *:* `ɢɪᴠᴇs ɪɴғᴏʀᴍᴀᴛɪᴏɴ ᴀʙᴏᴜᴛ ᴡᴇʟᴄᴏᴍᴇ ᴍᴜᴛᴇs.`

❂ /cleanservice <ᴏɴ/ᴏғғ*:* `ᴅᴇʟᴇᴛᴇs ᴛᴇʟᴇɢʀᴀᴍs ᴡᴇʟᴄᴏᴍᴇ/ʟᴇғᴛ sᴇʀᴠɪᴄᴇ ᴍᴇssᴀɢᴇs.`

"""

NEW_MEM_HANDLER = MessageHandler(
    Filters.status_update.new_chat_members, new_member, run_async=True
)
LEFT_MEM_HANDLER = MessageHandler(
    Filters.status_update.left_chat_member, left_member, run_async=True
)
WELC_PREF_HANDLER = CommandHandler(
    "welcome", welcome, filters=Filters.chat_type.groups, run_async=True
)
GOODBYE_PREF_HANDLER = CommandHandler(
    "goodbye", goodbye, filters=Filters.chat_type.groups, run_async=True
)
SET_WELCOME = CommandHandler(
    "setwelcome", set_welcome, filters=Filters.chat_type.groups, run_async=True
)
SET_GOODBYE = CommandHandler(
    "setgoodbye", set_goodbye, filters=Filters.chat_type.groups, run_async=True
)
RESET_WELCOME = CommandHandler(
    "resetwelcome", reset_welcome, filters=Filters.chat_type.groups, run_async=True
)
RESET_GOODBYE = CommandHandler(
    "resetgoodbye", reset_goodbye, filters=Filters.chat_type.groups, run_async=True
)
WELCOMEMUTE_HANDLER = CommandHandler(
    "welcomemute", welcomemute, filters=Filters.chat_type.groups, run_async=True
)
# CLEAN_SERVICE_HANDLER = CommandHandler(
# "cleanservice", cleanservice, filters=Filters.chat_type.groups, run_async=True
# )
CLEAN_WELCOME = CommandHandler(
    "cleanwelcome", clean_welcome, filters=Filters.chat_type.groups, run_async=True
)
WELCOME_HELP = CommandHandler("welcomehelp", welcome_help, run_async=True)
WELCOME_MUTE_HELP = CommandHandler("welcomemutehelp", welcome_mute_help, run_async=True)
BUTTON_VERIFY_HANDLER = CallbackQueryHandler(
    user_button, pattern=r"user_join_", run_async=True
)
CAPTCHA_BUTTON_VERIFY_HANDLER = CallbackQueryHandler(
    user_captcha_button,
    pattern=r"user_captchajoin_\([\d\-]+,\d+\)_\(\d{4}\)",
    run_async=True,
)

dispatcher.add_handler(NEW_MEM_HANDLER)
dispatcher.add_handler(LEFT_MEM_HANDLER)
dispatcher.add_handler(WELC_PREF_HANDLER)
dispatcher.add_handler(GOODBYE_PREF_HANDLER)
dispatcher.add_handler(SET_WELCOME)
dispatcher.add_handler(SET_GOODBYE)
dispatcher.add_handler(RESET_WELCOME)
dispatcher.add_handler(RESET_GOODBYE)
dispatcher.add_handler(CLEAN_WELCOME)
dispatcher.add_handler(WELCOME_HELP)
dispatcher.add_handler(WELCOMEMUTE_HANDLER)
# dispatcher.add_handler(CLEAN_SERVICE_HANDLER)
dispatcher.add_handler(BUTTON_VERIFY_HANDLER)
dispatcher.add_handler(WELCOME_MUTE_HELP)
dispatcher.add_handler(CAPTCHA_BUTTON_VERIFY_HANDLER)

__mod_name__ = "𝚆ᴇʟᴄᴏᴍᴇ"
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
    # CLEAN_SERVICE_HANDLER,
    BUTTON_VERIFY_HANDLER,
    CAPTCHA_BUTTON_VERIFY_HANDLER,
    WELCOME_MUTE_HELP,
]
