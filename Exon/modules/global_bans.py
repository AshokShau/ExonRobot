import html
import time
from datetime import datetime
from io import BytesIO

from telegram import ChatMemberAdministrator, Update
from telegram.constants import ParseMode
from telegram.error import BadRequest, Forbidden, TelegramError
from telegram.ext import CommandHandler, ContextTypes, MessageHandler, filters
from telegram.helpers import mention_html

import Exon.modules.sql.global_bans_sql as sql
from Exon import (
    DEV_USERS,
    DRAGONS,
    EVENT_LOGS,
    OWNER_ID,
    STRICT_GBAN,
    SUPPORT_CHAT,
    exon,
)
from Exon.modules.helper_funcs.chat_status import (
    check_admin,
    is_user_admin,
    support_plus,
)
from Exon.modules.helper_funcs.extraction import extract_user, extract_user_and_text
from Exon.modules.helper_funcs.misc import send_to_list
from Exon.modules.sql.users_sql import get_user_com_chats

GBAN_ENFORCE_GROUP = 6

GBAN_ERRORS = {
    "ᴜsᴇʀ ɪs ᴀɴ ᴀᴅᴍɪɴɪsᴛʀᴀᴛᴏʀ ᴏғ ᴛʜᴇ ᴄʜᴀᴛ",
    "ᴄʜᴀᴛ ɴᴏᴛ ғᴏᴜɴᴅ",
    "ɴᴏᴛ ᴇɴᴏᴜɢʜ ʀɪɢʜᴛs ᴛᴏ ʀᴇsᴛʀɪᴄᴛ/ᴜɴʀᴇsᴛʀɪᴄᴛ ᴄʜᴀᴛ ᴍᴇᴍʙᴇʀ",
    "ᴜsᴇʀ_ɴᴏᴛ_ᴘᴀʀᴛɪᴄɪᴘᴀɴᴛ",
    "ᴘᴇᴇʀ_ɪᴅ_ɪɴᴠᴀʟɪᴅ",
    "ɢʀᴏᴜᴘ ᴄʜᴀᴛ ᴡᴀs ᴅᴇᴀᴄᴛɪᴠᴀᴛᴇᴅ",
    "ɴᴇᴇᴅ to be inviter of a user to kick it from a basic group",
    "ᴄʜᴀᴛ_ᴀᴅᴍɪɴ_ʀᴇǫᴜɪʀᴇᴅ",
    "ᴏɴʟʏ ᴛʜᴇ ᴄʀᴇᴀᴛᴏʀ ᴏғ ᴀ ʙᴀsɪᴄ ɢʀᴏᴜᴘ ᴄᴀɴ ᴋɪᴄᴋ ɢʀᴏᴜᴘ ᴀᴅᴍɪɴɪsᴛʀᴀᴛᴏʀs",
    "ᴄʜᴀɴɴᴇʟ_ᴘʀɪᴠᴀᴛᴇ",
    "ɴᴏᴛ in the chat",
    "ᴄᴀɴ'ᴛ ʀᴇᴍᴏᴠᴇ ᴄʜᴀᴛ ᴏᴡɴᴇʀ",
}

UNGBAN_ERRORS = {
    "ᴜsᴇʀ ɪs ᴀɴ ᴀᴅᴍɪɴɪsᴛʀᴀᴛᴏʀ ᴏғ ᴛʜᴇ ᴄʜᴀᴛ",
    "ᴄʜᴀᴛ ɴᴏᴛ ғᴏᴜɴᴅ",
    "ɴᴏᴛ ᴇɴᴏᴜɢʜ ʀɪɢʜᴛs ᴛᴏ ʀᴇsᴛʀɪᴄᴛ/ᴜɴʀᴇsᴛʀɪᴄᴛ ᴄʜᴀᴛ ᴍᴇᴍʙᴇʀ",
    "ᴜsᴇʀ_ɴᴏᴛ_ᴘᴀʀᴛɪᴄɪᴘᴀɴᴛ",
    "ᴍᴇᴛʜᴏᴅ ɪs ᴀᴠᴀɪʟᴀʙʟᴇ ғᴏʀ sᴜᴘᴇʀɢʀᴏᴜᴘ ᴀɴᴅ ᴄʜᴀɴɴᴇʟ ᴄʜᴀᴛs ᴏɴʟʏ",
    "ɴᴏᴛ ɪɴ ᴛʜᴇ ᴄʜᴀᴛ",
    "ᴄʜᴀɴɴᴇʟ_ᴘʀɪᴠᴀᴛᴇ",
    "ᴄʜᴀᴛ_ᴀᴅᴍɪɴ_ʀᴇǫᴜɪʀᴇᴅ",
    "ᴘᴇᴇʀ_id_ɪɴᴠᴀʟɪᴅ",
    "ᴜsᴇʀ ɴᴏᴛ ғᴏᴜɴᴅ",
}


@support_plus
async def gban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bot, args = context.bot, context.args
    message = update.effective_message
    user = update.effective_user
    chat = update.effective_chat
    log_message = ""

    user_id, reason = await extract_user_and_text(message, context, args)

    if not user_id:
        await message.reply_text(
            "ʏᴏᴜ ᴅᴏɴ'ᴛ sᴇᴇᴍ ᴛᴏ ʙᴇ ʀᴇғᴇʀʀɪɴɢ ᴛᴏ ᴀ ᴜsᴇʀ ᴏʀ ᴛʜᴇ ID sᴘᴇᴄɪғɪᴇᴅ ɪs ɪɴᴄᴏʀʀᴇᴄᴛ..",
        )
        return

    if int(user_id) in DEV_USERS:
        await message.reply_text(
            "ᴛʜᴀᴛ ᴜsᴇʀ ɪs ᴘᴀʀᴛ ᴏғ ᴛʜᴇ ᴀssᴏᴄɪᴀᴛɪᴏɴ\nI ᴄᴀɴ'ᴛ ᴀᴄᴛ ᴀɢᴀɪɴsᴛ ᴏᴜʀ ᴏᴡɴ.",
        )
        return

    if int(user_id) in DRAGONS:
        await message.reply_text(
            "I sᴘʏ, ᴡɪᴛʜ ᴍʏ ʟɪᴛᴛʟᴇ ᴇʏᴇ... ᴀ ᴅɪsᴀsᴛᴇʀ! ᴡʜʏ ᴀʀᴇ ʏᴏᴜ ɢᴜʏs ᴛᴜʀɴɪɴɢ ᴏɴ ᴇᴀᴄʜ ᴏᴛʜᴇʀ?",
        )
        return

    if user_id == bot.id:
        await message.reply_text("ʏᴏᴜ ᴜʜʜ...ᴡᴀɴᴛ ᴍᴇ ᴛᴏ ᴋɪᴄᴋ ᴍʏsᴇʟғ?")
        return

    if user_id in [777000, 1087968824]:
        await message.reply_text("ғᴏᴏʟ! ʏᴏᴜ ᴄᴀɴ'ᴛ ᴀᴛᴛᴀᴄᴋ ᴛᴇʟᴇɢʀᴀᴍ ɴᴀᴛɪᴠᴇ ᴛᴇᴄʜ!")
        return

    try:
        user_chat = await bot.get_chat(user_id)
    except BadRequest as excp:
        if excp.message == "User not found":
            await message.reply_text("I ᴄᴀɴ'ᴛ sᴇᴇᴍ ᴛᴏ ғɪɴᴅ ᴛʜɪs ᴜsᴇʀ.")
            return ""
        else:
            return

    if user_chat.type != "private":
        await message.reply_text("ᴛʜᴀᴛ's ɴᴏᴛ ᴀ ᴜsᴇʀ!")
        return

    if sql.is_user_gbanned(user_id):
        if not reason:
            await message.reply_text(
                "ᴛʜɪs ᴜsᴇʀ ɪs ᴀʟʀᴇᴀᴅʏ ɢʙᴀɴɴᴇᴅ; ɪᴅ ᴄʜᴀɴɢᴇ ᴛʜᴇ ʀᴇᴀsᴏɴ, ʙᴜᴛ ʏᴏᴜ ʜᴀᴠᴇɴ'ᴛ ɢɪᴠᴇɴ ᴍᴇ ᴏɴᴇ...",
            )
            return

        old_reason = sql.update_gban_reason(
            user_id,
            user_chat.username or user_chat.first_name,
            reason,
        )
        if old_reason:
            await message.reply_text(
                "ᴛʜɪs ᴜsᴇʀ ɪs ᴀʟʀᴇᴀᴅʏ ɢʙᴀɴɴᴇᴅ, ғᴏʀ ᴛʜᴇ ғᴏʟʟᴏᴡɪɴɢ ʀᴇᴀsᴏɴ:\n"
                "<code>{}</code>\n"
                "I'ᴠᴇ ɢᴏɴᴇ ᴀɴᴅ ᴜᴘᴅᴀᴛᴇᴅ ɪᴛ ᴡɪᴛʜ ʏᴏᴜʀ ɴᴇᴡ ʀᴇᴀsᴏɴ!".format(
                    html.escape(old_reason),
                ),
                parse_mode=ParseMode.HTML,
            )

        else:
            await message.reply_text(
                "ᴛʜɪs ᴜsᴇʀ ɪs ᴀʟʀᴇᴀᴅʏ ɢʙᴀɴɴᴇᴅ, ʙᴜᴛ ʜᴀᴅ ɴᴏ ʀᴇᴀsᴏɴ sᴇᴛ; I'ᴠᴇ ɢᴏɴᴇ ᴀɴᴅ ᴜᴘᴅᴀᴛᴇᴅ ɪᴛ!",
            )

        return

    await message.reply_text("On it!")

    start_time = time.time()
    datetime_fmt = "%Y-%m-%dT%H:%M"
    current_time = datetime.utcnow().strftime(datetime_fmt)

    if chat.type != "private":
        chat_origin = "<b>{} ({})</b>\n".format(html.escape(chat.title), chat.id)
    else:
        chat_origin = "<b>{}</b>\n".format(chat.id)

    log_message = (
        f"#𝐆𝐁𝐀𝐍𝐍𝐄𝐃\n"
        f"<b>ᴏʀɪɢɪɴᴀᴛᴇᴅ from:</b> <code>{chat_origin}</code>\n"
        f"<b>ᴀᴅᴍɪɴ:</b> {mention_html(user.id, user.first_name)}\n"
        f"<b>ʙᴀɴɴᴇᴅ ᴜsᴇʀ:</b> {mention_html(user_chat.id, user_chat.first_name)}\n"
        f"<b>ʙᴀɴɴᴇᴅ ᴜsᴇʀ ɪᴅ:</b> <code>{user_chat.id}</code>\n"
        f"<b>ᴇᴠᴇɴᴛ sᴛᴀᴍᴘ:</b> <code>{current_time}</code>"
    )

    if reason:
        if chat.type == chat.SUPERGROUP and chat.username:
            log_message += f'\n<b>ʀᴇᴀsᴏɴ:</b> <a href="https://telegram.me/{chat.username}/{message.message_id}">{reason}</a>'
        else:
            log_message += f"\n<b>ʀᴇᴀsᴏɴ:</b> <code>{reason}</code>"

    if EVENT_LOGS:
        try:
            log = await bot.send_message(
                EVENT_LOGS, log_message, parse_mode=ParseMode.HTML
            )
        except BadRequest:
            log = await bot.send_message(
                EVENT_LOGS,
                log_message
                + "\n\nғᴏʀᴍᴀᴛᴛɪɴɢ ʜᴀs ʙᴇᴇɴ ᴅɪsᴀʙʟᴇᴅ ᴅᴜᴇ ᴛᴏ ᴀɴ ᴜɴᴇxᴘᴇᴄᴛᴇᴅ ᴇʀʀᴏʀ.",
            )

    else:
        send_to_list(bot, DRAGONS, log_message, html=True)

    sql.gban_user(user_id, user_chat.username or user_chat.first_name, reason)

    chats = get_user_com_chats(user_id)
    gbanned_chats = 0

    for chat in chats:
        chat_id = int(chat)

        # Check if this group has disabled gbans
        if not sql.does_chat_gban(chat_id):
            continue

        try:
            await bot.ban_chat_member(chat_id, user_id)
            gbanned_chats += 1

        except BadRequest as excp:
            if excp.message in GBAN_ERRORS:
                pass
            else:
                await message.reply_text(f"ᴄᴏᴜʟᴅ ɴᴏᴛ ɢʙᴀɴ ᴅᴜᴇ ᴛᴏ: {excp.message}")
                if EVENT_LOGS:
                    await bot.send_message(
                        EVENT_LOGS,
                        f"ᴄᴏᴜʟᴅ ɴᴏᴛ ɢʙᴀɴ ᴅᴜᴇ ᴛᴏ {excp.message}",
                        parse_mode=ParseMode.HTML,
                    )
                else:
                    send_to_list(
                        bot,
                        DRAGONS,
                        f"ᴄᴏᴜʟᴅ ɴᴏᴛ ɢʙᴀɴ ᴅᴜᴇ ᴛᴏ: {excp.message}",
                    )
                sql.ungban_user(user_id)
                return
        except TelegramError:
            pass

    if EVENT_LOGS:
        await log.edit_text(
            log_message + f"\n<b>ᴄʜᴀᴛs ᴀғғᴇᴄᴛᴇᴅ:</b> <code>{gbanned_chats}</code>",
            parse_mode=ParseMode.HTML,
        )
    else:
        send_to_list(
            bot,
            DRAGONS,
            f"ɢʙᴀɴ ᴄᴏᴍᴘʟᴇᴛᴇ! (ᴜsᴇʀ ʙᴀɴɴᴇᴅ ɪɴ <code>{gbanned_chats}</code> ᴄʜᴀᴛs)",
            html=True,
        )

    end_time = time.time()
    gban_time = round((end_time - start_time), 2)

    if gban_time > 60:
        gban_time = round((gban_time / 60), 2)
        await message.reply_text("ᴅᴏɴᴇ! ɢʙᴀɴɴᴇᴅ.", parse_mode=ParseMode.HTML)
    else:
        await message.reply_text("ᴅᴏɴᴇ! ɢʙᴀɴɴᴇᴅ.", parse_mode=ParseMode.HTML)

    try:
        await bot.send_message(
            user_id,
            "#𝐄𝐕𝐄𝐍𝐓"
            "ʏᴏᴜ ʜᴀᴠᴇ ʙᴇᴇɴ ᴍᴀʀᴋᴇᴅ ᴀs ᴍᴀʟɪᴄɪᴏᴜs ᴀɴᴅ ᴀs sᴜᴄʜ ʜᴀᴠᴇ ʙᴇᴇɴ ʙᴀɴɴᴇᴅ ғʀᴏᴍ ᴀɴʏ ғᴜᴛᴜʀᴇ ɢʀᴏᴜᴘs ᴡᴇ ᴍᴀɴᴀɢᴇ."
            f"\n<b>ʀᴇᴀsᴏɴ:</b> <code>{html.escape(user.reason)}</code>"
            f"</b>ᴀᴘᴘᴇᴀʟ ᴄʜᴀᴛ:</b> @{SUPPORT_CHAT}",
            parse_mode=ParseMode.HTML,
        )
    except:
        pass  # bot probably blocked by user


@support_plus
async def ungban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bot, args = context.bot, context.args
    message = update.effective_message
    user = update.effective_user
    chat = update.effective_chat
    log_message = ""

    user_id = await extract_user(message, context, args)

    if not user_id:
        await message.reply_text(
            "ʏᴏᴜ ᴅᴏɴ'ᴛ sᴇᴇᴍ ᴛᴏ ʙᴇ ʀᴇғᴇʀʀɪɴɢ ᴛᴏ ᴀ ᴜsᴇʀ ᴏʀ ᴛʜᴇ ID sᴘᴇᴄɪғɪᴇᴅ ɪs ɪɴᴄᴏʀʀᴇᴄᴛ..",
        )
        return

    user_chat = await bot.get_chat(user_id)
    if user_chat.type != "private":
        await message.reply_text("ᴛʜᴀᴛ's ɴᴏᴛ ᴀ ᴜsᴇʀ!")
        return

    if not sql.is_user_gbanned(user_id):
        await message.reply_text("ᴛʜɪs ᴜsᴇʀ ɪs ɴᴏᴛ ɢʙᴀɴɴᴇᴅ!")
        return

    await message.reply_text(
        f"I'ʟʟ ɢɪᴠᴇ {user_chat.first_name} ᴀ sᴇᴄᴏɴᴅ ᴄʜᴀɴᴄᴇ, ɢʟᴏʙᴀʟʟʏ."
    )

    start_time = time.time()
    datetime_fmt = "%Y-%m-%dT%H:%M"
    current_time = datetime.utcnow().strftime(datetime_fmt)

    if chat.type != "private":
        chat_origin = f"<b>{html.escape(chat.title)} ({chat.id})</b>\n"
    else:
        chat_origin = f"<b>{chat.id}</b>\n"

    log_message = (
        f"#𝐔𝐍𝐆𝐁𝐀𝐍𝐍𝐄𝐃\n"
        f"<b>ᴏʀɪɢɪɴᴀᴛᴇᴅ ғʀᴏᴍ:</b> <code>{chat_origin}</code>\n"
        f"<b>ᴀᴅᴍɪɴ:</b> {mention_html(user.id, user.first_name)}\n"
        f"<b>ᴜɴʙᴀɴɴᴇᴅ ᴜsᴇʀ:</b> {mention_html(user_chat.id, user_chat.first_name)}\n"
        f"<b>ᴜɴʙᴀɴɴᴇᴅ ᴜsᴇʀ ID:</b> <code>{user_chat.id}</code>\n"
        f"<b>ᴇᴠᴇɴᴛ sᴛᴀᴍᴘ:</b> <code>{current_time}</code>"
    )

    if EVENT_LOGS:
        try:
            log = await bot.send_message(
                EVENT_LOGS, log_message, parse_mode=ParseMode.HTML
            )
        except BadRequest:
            log = await bot.send_message(
                EVENT_LOGS,
                log_message
                + "\n\nғᴏʀᴍᴀᴛᴛɪɴɢ ʜᴀs ʙᴇᴇɴ ᴅɪsᴀʙʟᴇᴅ due ᴛᴏ ᴀɴ ᴜɴᴇxᴘᴇᴄᴛᴇᴅ ᴇʀʀᴏʀ.",
            )
    else:
        send_to_list(bot, DRAGONS, log_message, html=True)

    chats = get_user_com_chats(user_id)
    ungbanned_chats = 0

    for chat in chats:
        chat_id = int(chat)

        # Check if this group has disabled gbans
        if not sql.does_chat_gban(chat_id):
            continue

        try:
            member = await bot.get_chat_member(chat_id, user_id)
            if member.status == "kicked":
                await bot.unban_chat_member(chat_id, user_id)
                ungbanned_chats += 1

        except BadRequest as excp:
            if excp.message in UNGBAN_ERRORS:
                pass
            else:
                await message.reply_text(f"ᴄᴏᴜʟᴅ ɴᴏᴛ ᴜɴ-ɢᴀɴ ᴅᴜᴇ ᴛᴏ: {excp.message}")
                if EVENT_LOGS:
                    await bot.send_message(
                        EVENT_LOGS,
                        f"ᴄᴏᴜʟᴅ ɴᴏᴛ ᴜɴ-ɢᴀɴ ᴅᴜᴇ ᴛᴏ: {excp.message}",
                        parse_mode=ParseMode.HTML,
                    )
                else:
                    await bot.send_message(
                        OWNER_ID,
                        f"ᴄᴏᴜʟᴅ ɴᴏᴛ ᴜɴ-ɢᴀɴ ᴅᴜᴇ ᴛᴏ: {excp.message}",
                    )
                return
        except TelegramError:
            pass

    sql.ungban_user(user_id)

    if EVENT_LOGS:
        await log.edit_text(
            log_message + f"\n<b>ᴄʜᴀᴛs ᴀғғᴇᴄᴛᴇᴅ:</b> {ungbanned_chats}",
            parse_mode=ParseMode.HTML,
        )
    else:
        send_to_list(bot, DRAGONS, "ᴜɴᴀ-ɢʙᴀɴ ᴄᴏᴍᴘʟᴇᴛᴇ!")

    end_time = time.time()
    ungban_time = round((end_time - start_time), 2)

    if ungban_time > 60:
        ungban_time = round((ungban_time / 60), 2)
        await message.reply_text(f"ᴘᴇʀsᴏɴ ʜᴀs ʙᴇᴇɴ ᴜɴ-ɢᴀɴɴᴇᴅ. ᴛᴏᴏᴋ {ungban_time} ᴍɪɴ")
    else:
        await message.reply_text(f"ᴘᴇʀsᴏɴ ʜᴀs ʙᴇᴇɴ ᴜɴ-ɢᴀɴɴᴇᴅ. ᴛᴏᴏᴋ {ungban_time} sᴇᴄ")


@support_plus
async def gbanlist(update: Update, context: ContextTypes.DEFAULT_TYPE):
    banned_users = sql.get_gban_list()

    if not banned_users:
        await update.effective_message.reply_text(
            "ᴛʜᴇʀᴇ ᴀʀᴇɴ'ᴛ ᴀɴʏ ɢʙᴀɴɴᴇᴅ ᴜsᴇʀs! ʏᴏᴜ'ʀᴇ ᴋɪɴᴅᴇʀ ᴛʜᴀɴ I ᴇxᴘᴇᴄᴛᴇᴅ...",
        )
        return

    banfile = "sᴄʀᴇᴡ ᴛʜᴇsᴇ ɢᴜʏs.\n"
    for user in banned_users:
        banfile += f"[x] {user['name']} - {user['user_id']}\n"
        if user["reason"]:
            banfile += f"ʀᴇᴀsᴏɴ: {user['reason']}\n"

    with BytesIO(str.encode(banfile)) as output:
        output.name = "gbanlist.txt"
        await update.effective_message.reply_document(
            document=output,
            filename="gbanlist.txt",
            caption="ʜᴇʀᴇ ɪs ᴛʜᴇ ʟɪsᴛ ᴏғ ᴄᴜʀʀᴇɴᴛʟʏ ɢʙᴀɴɴᴇᴅ ᴜsᴇʀs.",
        )


async def check_and_ban(update, user_id, should_message=True):
    if sql.is_user_gbanned(user_id):
        await update.effective_chat.ban_member(user_id)
        if should_message:
            text = (
                f"<b>ᴀʟᴇʀᴛ</b>: ᴛʜɪs ᴜsᴇʀ ɪs ɢʟᴏʙᴀʟʟʏ ʙᴀɴɴᴇᴅ.\n"
                f"<code>*ʙᴀɴs ᴛʜᴇᴍ ғʀᴏᴍ ʜᴇʀᴇ*</code>.\n"
                f"<b>ᴀᴘᴘᴇᴀʟ ᴄʜᴀᴛ</b>: @{SUPPORT_CHAT}\n"
                f"<b>ᴜsᴇʀ ɪᴅ</b>: <code>{user_id}</code>"
            )
            user = sql.get_gbanned_user(user_id)
            if user.reason:
                text += f"\n<b>ʙᴀɴ ʀᴇᴀsᴏɴ:</b> <code>{html.escape(user.reason)}</code>"
            await update.effective_message.reply_text(text, parse_mode=ParseMode.HTML)


async def enforce_gban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Not using @restrict handler to avoid spamming - just ignore if cant gban.
    bot = context.bot
    try:
        get_member = await update.effective_chat.get_member(
            bot.id,
        )
        if isinstance(get_member, ChatMemberAdministrator):
            restrict_permission = get_member.can_restrict_members
        else:
            return
    except Forbidden:
        return
    if sql.does_chat_gban(update.effective_chat.id) and restrict_permission:
        user = update.effective_user
        chat = update.effective_chat
        msg = update.effective_message

        if user and not await is_user_admin(chat, user.id):
            await check_and_ban(update, user.id)
            return

        if msg.new_chat_members:
            new_members = update.effective_message.new_chat_members
            for mem in new_members:
                await check_and_ban(update, mem.id)

        if msg.reply_to_message:
            user = msg.reply_to_message.from_user
            if user and not await is_user_admin(chat, user.id):
                await check_and_ban(update, user.id, should_message=False)


@check_admin(is_user=True)
async def gbanstat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if len(args) > 0:
        if args[0].lower() in ["on", "yes"]:
            sql.enable_gbans(update.effective_chat.id)
            await update.effective_message.reply_text(
                "ᴀɴᴛɪsᴘᴀᴍ ɪs ɴᴏᴡ ᴇɴᴀʙʟᴇᴅ ✅ "
                "I ᴀᴍ ɴᴏᴡ ᴘʀᴏᴛᴇᴄᴛɪɴɢ ʏᴏᴜʀ ɢʀᴏᴜᴘ ғʀᴏᴍ ᴘᴏᴛᴇɴᴛɪᴀʟ ʀᴇᴍᴏᴛᴇ ᴛʜʀᴇᴀᴛs!",
            )
        elif args[0].lower() in ["off", "no"]:
            sql.disable_gbans(update.effective_chat.id)
            await update.effective_message.reply_text(
                "I ᴀᴍ ɴᴏᴛ ɴᴏᴡ ᴘʀᴏᴛᴇᴄᴛɪɴɢ ʏᴏᴜʀ ɢʀᴏᴜᴘ ғʀᴏᴍ ᴘᴏᴛᴇɴᴛɪᴀʟ ʀᴇᴍᴏᴛᴇ ᴛʜʀᴇᴀᴛs!",
            )
    else:
        await update.effective_message.reply_text(
            "ɢɪᴠᴇ ᴍᴇ sᴏᴍᴇ ᴀʀɢᴜᴍᴇɴᴛs ᴛᴏ ᴄʜᴏᴏsᴇ ᴀ sᴇᴛᴛɪɴɢ! ᴏɴ/ᴏғғ, ʏᴇs/ɴᴏ!\n\n"
            "ʏᴏᴜʀ ᴄᴜʀʀᴇɴᴛ sᴇᴛᴛɪɴɢ is: {}\n"
            "ᴡʜᴇɴ ᴛʀᴜᴇ, ᴀɴʏ ɢʙᴀɴs ᴛʜᴀᴛ ʜᴀᴘᴘᴇɴ ᴡɪʟʟ ᴀʟsᴏ ʜᴀᴘᴘᴇɴ ɪɴ ʏᴏᴜʀ ɢʀᴏᴜᴘ. "
            "ᴡʜᴇɴ ғᴀʟsᴇ, ᴛʜᴇʏ ᴡᴏɴ'ᴛ, ʟᴇᴀᴠɪɴɢ ʏᴏᴜ ᴀᴛ ᴛʜᴇ ᴘᴏssɪʙʟᴇ ᴍᴇʀᴄʏ ᴏғ "
            "sᴘᴀᴍᴍᴇʀs.".format(sql.does_chat_gban(update.effective_chat.id)),
        )


def __stats__():
    return f"• {sql.num_gbanned_users()} ɢʙᴀɴɴᴇᴅ ᴜsᴇʀs."


def __user_info__(user_id):
    is_gbanned = sql.is_user_gbanned(user_id)
    text = "ᴍᴀʟɪᴄɪᴏᴜs: <b>{}</b>"
    if user_id in [777000, 1087968824]:
        return ""
    if user_id == exon.bot.id:
        return ""
    if int(user_id) in DRAGONS:
        return ""
    if is_gbanned:
        text = text.format("Yes")
        user = sql.get_gbanned_user(user_id)
        if user.reason:
            text += f"\n<b>ʀᴇᴀsᴏɴ:</b> <code>{html.escape(user.reason)}</code>"
        text += f"\n<b>ᴀᴘᴘᴇᴀʟ ᴄʜᴀᴛ:</b> @{SUPPORT_CHAT}"
    else:
        text = text.format("???")
    return text


def __migrate__(old_chat_id, new_chat_id):
    sql.migrate_chat(old_chat_id, new_chat_id)


def __chat_settings__(chat_id, user_id):
    return f"ᴛʜɪs ᴄʜᴀᴛ ɪs ᴇɴғᴏʀᴄɪɴɢ *ɢʙᴀɴs*: `{sql.does_chat_gban(chat_id)}`."


__help__ = f"""
*ᴀᴅᴍɪɴs ᴏɴʟʏ:*
• /antispam <ᴏɴ/ᴏғғ/ʏᴇs/ɴᴏ>*:* ᴡɪʟʟ ᴛᴏɢɢʟᴇ ᴏᴜʀ ᴀɴᴛɪsᴘᴀᴍ ᴛᴇᴄʜ ᴏʀ ʀᴇᴛᴜʀɴ ʏᴏᴜʀ ᴄᴜʀʀᴇɴᴛ sᴇᴛᴛɪɴɢs.

ᴀɴᴛɪ-sᴘᴀᴍ, ᴜsᴇᴅ ʙʏ ʙᴏᴛ ᴅᴇᴠs ᴛᴏ ʙᴀɴ sᴘᴀᴍᴍᴇʀs ᴀᴄʀᴏss ᴀʟʟ ɢʀᴏᴜᴘs. ᴛʜɪs ʜᴇʟᴘs ᴘʀᴏᴛᴇᴄᴛ \
ʏᴏᴜ ᴀɴᴅ ʏᴏᴜʀ ɢʀᴏᴜᴘs ʙʏ ʀᴇᴍᴏᴠɪɴɢ sᴘᴀᴍ ғʟᴏᴏᴅᴇʀs ᴀs ǫᴜɪᴄᴋʟʏ ᴀs ᴘᴏssɪʙʟᴇ

*ɴᴏᴛᴇ:* ᴜsᴇʀs ᴄᴀɴ ᴀᴘᴘᴇᴀʟ ɢʙᴀɴs ᴏʀ ʀᴇᴘᴏʀᴛ sᴘᴀᴍᴍᴇʀs ᴀᴛ @{SUPPORT_CHAT}
"""

GBAN_HANDLER = CommandHandler("gban", gban)
UNGBAN_HANDLER = CommandHandler("ungban", ungban)
GBAN_LIST = CommandHandler("gbanlist", gbanlist)

GBAN_STATUS = CommandHandler("antispam", gbanstat, filters=filters.ChatType.GROUPS)

GBAN_ENFORCER = MessageHandler(filters.ALL & filters.ChatType.GROUPS, enforce_gban)

exon.add_handler(GBAN_HANDLER)
exon.add_handler(UNGBAN_HANDLER)
exon.add_handler(GBAN_LIST)
exon.add_handler(GBAN_STATUS)

__mod_name__ = "𝐀-sᴘᴀᴍ"
__handlers__ = [GBAN_HANDLER, UNGBAN_HANDLER, GBAN_LIST, GBAN_STATUS]

if STRICT_GBAN:  # enforce GBANS if this is set
    exon.add_handler(GBAN_ENFORCER, GBAN_ENFORCE_GROUP)
    __handlers__.append((GBAN_ENFORCER, GBAN_ENFORCE_GROUP))
