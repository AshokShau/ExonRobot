import html

from telegram import ChatPermissions, Update
from telegram.constants import ParseMode
from telegram.error import BadRequest
from telegram.ext import CommandHandler, ContextTypes, MessageHandler, filters
from telegram.helpers import mention_html, mention_markdown

import Exon.modules.sql.blsticker_sql as sql
from Exon import LOGGER, application
from Exon.modules.connection import connected
from Exon.modules.disable import DisableAbleCommandHandler
from Exon.modules.helper_funcs.alternate import send_message
from Exon.modules.helper_funcs.chat_status import check_admin, user_not_admin
from Exon.modules.helper_funcs.misc import split_message
from Exon.modules.helper_funcs.string_handling import extract_time
from Exon.modules.log_channel import loggable
from Exon.modules.warns import warn


async def blackliststicker(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.effective_message  # type: Optional[Message]
    chat = update.effective_chat  # type: Optional[Chat]
    user = update.effective_user  # type: Optional[User]
    bot, args = context.bot, context.args
    conn = await connected(bot, update, chat, user.id, need_admin=False)
    if conn:
        chat_id = conn
        chat_obj = await application.bot.getChat(conn)
        chat_name = chat_obj.title
    else:
        if chat.type == "private":
            return
        chat_id = update.effective_chat.id
        chat_name = chat.title

    sticker_list = "<b>ʟɪsᴛ ʙʟᴀᴄᴋʟɪsᴛᴇᴅ sᴛɪᴄᴋᴇʀs ᴄᴜʀʀᴇɴᴛʟʏ ɪɴ {}:</b>\n".format(
        chat_name,
    )

    all_stickerlist = sql.get_chat_stickers(chat_id)

    if len(args) > 0 and args[0].lower() == "copy":
        for trigger in all_stickerlist:
            sticker_list += "<code>{}</code>\n".format(html.escape(trigger))
    elif len(args) == 0:
        for trigger in all_stickerlist:
            sticker_list += " - <code>{}</code>\n".format(html.escape(trigger))

    split_text = split_message(sticker_list)
    for text in split_text:
        if sticker_list == "<b>ʟɪsᴛ ʙʟᴀᴄᴋʟɪsᴛᴇᴅ sᴛɪᴄᴋᴇʀs ᴄᴜʀʀᴇɴᴛʟʏ ɪɴ {}:</b>\n".format(
            chat_name,
        ).format(html.escape(chat_name)):
            await send_message(
                update.effective_message,
                "ᴛʜᴇʀᴇ ᴀʀᴇ ɴᴏ ʙʟᴀᴄᴋʟɪsᴛ sᴛɪᴄᴋᴇʀs ɪɴ <b>{}</b>!".format(
                    html.escape(chat_name),
                ),
                parse_mode=ParseMode.HTML,
            )
            return
    await send_message(
        update.effective_message,
        text,
        parse_mode=ParseMode.HTML,
    )


@check_admin(is_user=True)
async def add_blackliststicker(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bot = context.bot
    msg = update.effective_message  # type: Optional[Message]
    chat = update.effective_chat  # type: Optional[Chat]
    user = update.effective_user  # type: Optional[User]
    words = msg.text.split(None, 1)
    bot = context.bot
    conn = await connected(bot, update, chat, user.id)
    if conn:
        chat_id = conn
        chat_obj = await application.bot.getChat(conn)
        chat_name = chat_obj.title
    else:
        chat_id = update.effective_chat.id
        if chat.type == "private":
            return
        else:
            chat_name = chat.title

    if len(words) > 1:
        text = words[1].replace("https://t.me/addstickers/", "")
        to_blacklist = list(
            {trigger.strip() for trigger in text.split("\n") if trigger.strip()},
        )

        added = 0
        for trigger in to_blacklist:
            try:
                await bot.getStickerSet(trigger)
                sql.add_to_stickers(chat_id, trigger.lower())
                added += 1
            except BadRequest:
                await send_message(
                    update.effective_message,
                    "sᴛɪᴄᴋᴇʀ `{}` ᴄᴀɴ ɴᴏᴛ ʙᴇ ғᴏᴜɴᴅ!".format(trigger),
                    parse_mode="markdown",
                )

        if added == 0:
            return

        if len(to_blacklist) == 1:
            await send_message(
                update.effective_message,
                "sᴛɪᴄᴋᴇʀ <code>{}</code> ᴀᴅᴅᴇᴅ ᴛᴏ ʙʟᴀᴄᴋʟɪsᴛ sᴛɪᴄᴋᴇʀs ɪɴ <b>{}</b>!".format(
                    html.escape(to_blacklist[0]),
                    html.escape(chat_name),
                ),
                parse_mode=ParseMode.HTML,
            )
        else:
            await send_message(
                update.effective_message,
                "<code>{}</code> sᴛɪᴄᴋᴇʀs ᴀᴅᴅᴇᴅ ᴛᴏ ʙʟᴀᴄᴋʟɪsᴛ sᴛɪᴄᴋᴇʀ ɪɴ <b>{}</b>!".format(
                    added,
                    html.escape(chat_name),
                ),
                parse_mode=ParseMode.HTML,
            )
    elif msg.reply_to_message:
        added = 0
        trigger = msg.reply_to_message.sticker.set_name
        if trigger is None:
            await send_message(
                update.effective_message,
                "sᴛɪᴄᴋᴇʀ ɪs ɪɴᴠᴀʟɪᴅ!",
            )
            return
        try:
            await bot.getStickerSet(trigger)
            sql.add_to_stickers(chat_id, trigger.lower())
            added += 1
        except BadRequest:
            await send_message(
                update.effective_message,
                "sᴛɪᴄᴋᴇʀ `{}` ᴄᴀɴ ɴᴏᴛ ʙᴇ ғᴏᴜɴᴅ!".format(trigger),
                parse_mode="markdown",
            )

        if added == 0:
            return

        await send_message(
            update.effective_message,
            "sᴛɪᴄᴋᴇʀ <code>{}</code> ᴀᴅᴅᴇᴅ ᴛᴏ ʙʟᴀᴄᴋʟɪsᴛ sᴛɪᴄᴋᴇʀs ɪɴ <b>{}</b>!".format(
                trigger,
                html.escape(chat_name),
            ),
            parse_mode=ParseMode.HTML,
        )
    else:
        await send_message(
            update.effective_message,
            "ᴛᴇʟʟ ᴍᴇ ᴡʜᴀᴛ sᴛɪᴄᴋᴇʀs ʏᴏᴜ ᴡᴀɴᴛ ᴛᴏ ᴀᴅᴅ ᴛᴏ ᴛʜᴇ ʙʟᴀᴄᴋʟɪsᴛ.",
        )


@check_admin(is_user=True)
async def unblackliststicker(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bot = context.bot
    msg = update.effective_message  # type: Optional[Message]
    chat = update.effective_chat  # type: Optional[Chat]
    user = update.effective_user  # type: Optional[User]
    words = msg.text.split(None, 1)
    bot = context.bot
    conn = await connected(bot, update, chat, user.id)
    if conn:
        chat_id = conn
        chat_obj = await application.bot.getChat(conn)
        chat_name = chat_obj.title
    else:
        chat_id = update.effective_chat.id
        if chat.type == "private":
            return
        else:
            chat_name = chat.title

    if len(words) > 1:
        text = words[1].replace("https://t.me/addstickers/", "")
        to_unblacklist = list(
            {trigger.strip() for trigger in text.split("\n") if trigger.strip()},
        )

        successful = 0
        for trigger in to_unblacklist:
            success = sql.rm_from_stickers(chat_id, trigger.lower())
            if success:
                successful += 1

        if len(to_unblacklist) == 1:
            if successful:
                await send_message(
                    update.effective_message,
                    "sᴛɪᴄᴋᴇʀ <code>{}</code> ᴅᴇʟᴇᴛᴇᴅ ғʀᴏᴍ ʙʟᴀᴄᴋʟɪsᴛ ɪɴ <b>{}</b>!".format(
                        html.escape(to_unblacklist[0]),
                        html.escape(chat_name),
                    ),
                    parse_mode=ParseMode.HTML,
                )
            else:
                await send_message(
                    update.effective_message,
                    "ᴛʜɪs sᴛɪᴄᴋᴇʀ ɪs ɴᴏᴛ ᴏɴ ᴛʜᴇ ʙʟᴀᴄᴋʟɪsᴛ...!",
                )

        elif successful == len(to_unblacklist):
            await send_message(
                update.effective_message,
                "sᴛɪᴄᴋᴇʀ <code>{}</code> ᴅᴇʟᴇᴛᴇᴅ ғʀᴏᴍ ʙʟᴀᴄᴋʟɪsᴛ ɪɴ <b>{}</b>!".format(
                    successful,
                    html.escape(chat_name),
                ),
                parse_mode=ParseMode.HTML,
            )

        elif not successful:
            await send_message(
                update.effective_message,
                "ɴᴏɴᴇ ᴏғ ᴛʜᴇsᴇ sᴛɪᴄᴋᴇʀs ᴇxɪsᴛ, sᴏ ᴛʜᴇʏ ᴄᴀɴɴᴏᴛ ʙᴇ ʀᴇᴍᴏᴠᴇᴅ.",
                parse_mode=ParseMode.HTML,
            )

        else:
            await send_message(
                update.effective_message,
                "sᴛɪᴄᴋᴇʀ <code>{}</code> ᴅᴇʟᴇᴛᴇᴅ ғʀᴏᴍ ʙʟᴀᴄᴋʟɪsᴛ. {} ᴅɪᴅ ɴᴏᴛ ᴇxɪsᴛ, sᴏ ɪᴛ's ɴᴏᴛ ᴅᴇʟᴇᴛᴇᴅ.".format(
                    successful,
                    len(to_unblacklist) - successful,
                ),
                parse_mode=ParseMode.HTML,
            )
    elif msg.reply_to_message:
        trigger = msg.reply_to_message.sticker.set_name
        if trigger is None:
            await send_message(
                update.effective_message,
                "sᴛɪᴄᴋᴇʀ ɪs ɪɴᴠᴀʟɪᴅ!",
            )
            return
        success = sql.rm_from_stickers(chat_id, trigger.lower())

        if success:
            await send_message(
                update.effective_message,
                "sᴛɪᴄᴋᴇʀ <code>{}</code> ᴅᴇʟᴇᴛᴇᴅ ғʀᴏᴍ ʙʟᴀᴄᴋʟɪsᴛ ɪɴ <b>{}</b>!".format(
                    trigger,
                    chat_name,
                ),
                parse_mode=ParseMode.HTML,
            )
        else:
            await send_message(
                update.effective_message,
                "{} ɴᴏᴛ ғᴏᴜɴᴅ ᴏɴ ʙʟᴀᴄᴋʟɪsᴛᴇᴅ sᴛɪᴄᴋᴇʀs...!".format(trigger),
            )
    else:
        await send_message(
            update.effective_message,
            "ᴛᴇʟʟ ᴍᴇ ᴡʜᴀᴛ sᴛɪᴄᴋᴇʀs ʏᴏᴜ ᴡᴀɴᴛ ᴛᴏ ᴀᴅᴅ ᴛᴏ ᴛʜᴇ ʙʟᴀᴄᴋʟɪsᴛ.",
        )


@loggable
@check_admin(is_user=True)
async def blacklist_mode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat  # type: Optional[Chat]
    user = update.effective_user  # type: Optional[User]
    msg = update.effective_message  # type: Optional[Message]
    bot, args = context.bot, context.args
    conn = await connected(bot, update, chat, user.id, need_admin=True)
    if conn:
        chat = await application.bot.getChat(conn)
        chat_id = conn
        chat_obj = await application.bot.getChat(conn)
        chat_name = chat_obj.title
    else:
        if update.effective_message.chat.type == "private":
            await send_message(
                update.effective_message,
                "ʏᴏᴜ ᴄᴀɴ ᴅᴏ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ ɪɴ ɢʀᴏᴜᴘs, ɴᴏᴛ ᴘᴍ",
            )
            return ""
        chat = update.effective_chat
        chat_id = update.effective_chat.id
        chat_name = update.effective_message.chat.title

    if args:
        if args[0].lower() in ["off", "nothing", "no"]:
            settypeblacklist = "ᴛᴜʀɴ ᴏғғ"
            sql.set_blacklist_strength(chat_id, 0, "0")
        elif args[0].lower() in ["del", "delete"]:
            settypeblacklist = "ʟᴇғᴛ, ᴛʜᴇ ᴍᴇssᴀɢᴇ ᴡɪʟʟ ʙᴇ ᴅᴇʟᴇᴛᴇᴅ"
            sql.set_blacklist_strength(chat_id, 1, "0")
        elif args[0].lower() == "warn":
            settypeblacklist = "ᴡᴀʀɴᴇᴅ"
            sql.set_blacklist_strength(chat_id, 2, "0")
        elif args[0].lower() == "mute":
            settypeblacklist = "ᴍᴜᴛᴇᴅ"
            sql.set_blacklist_strength(chat_id, 3, "0")
        elif args[0].lower() == "kick":
            settypeblacklist = "ᴋɪᴄᴋᴇᴅ"
            sql.set_blacklist_strength(chat_id, 4, "0")
        elif args[0].lower() == "ban":
            settypeblacklist = "ʙᴀɴɴᴇᴅ"
            sql.set_blacklist_strength(chat_id, 5, "0")
        elif args[0].lower() == "tban":
            if len(args) == 1:
                teks = """ɪᴛ ʟᴏᴏᴋs ʟɪᴋᴇ ʏᴏᴜ ᴀʀᴇ ᴛʀʏɪɴɢ ᴛᴏ sᴇᴛ ᴀ ᴛᴇᴍᴘᴏʀᴀʀʏ ᴠᴀʟᴜᴇ ᴛᴏ ʙʟᴀᴄᴋʟɪsᴛ, ʙᴜᴛ ʜᴀs ɴᴏᴛ ᴅᴇᴛᴇʀᴍɪɴᴇᴅ ᴛʜᴇ ᴛɪᴍᴇ; use `/blstickermode tban <ᴛɪᴍᴇᴠᴀʟᴜᴇ>`.
                                          ᴇxᴀᴍᴘʟᴇs ᴏғ ᴛɪᴍᴇ ᴠᴀʟᴜᴇs: 4m = 4 ᴍɪɴᴜᴛᴇ, 3h = 3 ʜᴏᴜʀs, 6d = 6 ᴅᴀʏs, 5w = 5 ᴡᴇᴇᴋs."""
                await send_message(
                    update.effective_message,
                    teks,
                    parse_mode="markdown",
                )
                return
            settypeblacklist = "ᴛᴇᴍᴘᴏʀᴀʀʏ ʙᴀɴɴᴇᴅ ғᴏʀ {}".format(args[1])
            sql.set_blacklist_strength(chat_id, 6, str(args[1]))
        elif args[0].lower() == "tmute":
            if len(args) == 1:
                teks = """ɪᴛ ʟᴏᴏᴋs ʟɪᴋᴇ ʏᴏᴜ ᴀʀᴇ ᴛʀʏɪɴɢ ᴛᴏ sᴇᴛ ᴀ ᴛᴇᴍᴘᴏʀᴀʀʏ ᴠᴀʟᴜᴇ ᴛᴏ ʙʟᴀᴄᴋʟɪsᴛ, ʙᴜᴛ ʜᴀs ɴᴏᴛ ᴅᴇᴛᴇʀᴍɪɴᴇᴅ ᴛʜᴇ ᴛɪᴍᴇ; ᴜsᴇ `/blstickermode tmute <ᴛɪᴍᴇᴠᴀʟᴜᴇ>`.
                                          ᴇxᴀᴍᴘʟᴇs ᴏғ ᴛɪᴍᴇ values: 4m = 4 ᴍɪɴᴜᴛᴇ, 3h = 3 ʜᴏᴜʀs, 6d = 6 ᴅᴀʏs, 5w = 5 ᴡᴇᴇᴋs."""
                await send_message(
                    update.effective_message,
                    teks,
                    parse_mode="markdown",
                )
                return
            settypeblacklist = "ᴛᴇᴍᴘᴏʀᴀʀʏ ᴍᴜᴛᴇᴅ ғᴏʀ {}".format(args[1])
            sql.set_blacklist_strength(chat_id, 7, str(args[1]))
        else:
            await send_message(
                update.effective_message,
                "I ᴏɴʟʏ ᴜɴᴅᴇʀsᴛᴀɴᴅ ᴏғғ/ᴅᴇʟ/ᴡᴀʀɴ/ʙᴀɴ/ᴋɪᴄᴋ/ᴍᴜᴛᴇ/ᴛʙᴀɴ/ᴛᴍᴜᴛᴇ!",
            )
            return
        if conn:
            text = "ʙʟᴀᴄᴋʟɪsᴛ sᴛɪᴄᴋᴇʀ ᴍᴏᴅᴇ ᴄʜᴀɴɢᴇᴅ, ᴜsᴇʀs ᴡɪʟʟ ʙᴇ `{}` ᴀᴛ *{}*!".format(
                settypeblacklist,
                chat_name,
            )
        else:
            text = "ʙʟᴀᴄᴋʟɪsᴛ sᴛɪᴄᴋᴇʀ ᴍᴏᴅᴇ ᴄʜᴀɴɢᴇᴅ, ᴜsᴇʀs ᴡɪʟʟ ʙᴇ `{}`!".format(
                settypeblacklist,
            )
        await send_message(
            update.effective_message,
            text,
            parse_mode="markdown",
        )
        return (
            "<b>{}:</b>\n"
            "<b>ᴀᴅᴍɪɴ:</b> {}\n"
            "ᴄʜᴀɴɢᴇᴅ sᴛɪᴄᴋᴇʀ ʙʟᴀᴄᴋʟɪsᴛ ᴍᴏᴅᴇ. ᴜsᴇʀs ᴡɪʟʟ ʙᴇ {}.".format(
                html.escape(chat.title),
                mention_html(user.id, html.escape(user.first_name)),
                settypeblacklist,
            )
        )
    else:
        getmode, getvalue = sql.get_blacklist_setting(chat.id)
        if getmode == 0:
            settypeblacklist = "ɴᴏᴛ ᴀᴄᴛɪᴠᴇ"
        elif getmode == 1:
            settypeblacklist = "ᴅᴇʟᴇᴛᴇ"
        elif getmode == 2:
            settypeblacklist = "ᴡᴀʀɴ"
        elif getmode == 3:
            settypeblacklist = "ᴍᴜᴛᴇ"
        elif getmode == 4:
            settypeblacklist = "ᴋɪᴄᴋ"
        elif getmode == 5:
            settypeblacklist = "ʙᴀɴ"
        elif getmode == 6:
            settypeblacklist = "ᴛᴇᴍᴘᴏʀᴀʀɪʟʏ ʙᴀɴɴᴇᴅ ғᴏʀ {}".format(getvalue)
        elif getmode == 7:
            settypeblacklist = "ᴛᴇᴍᴘᴏʀᴀʀɪʟʏ ᴍᴜᴛᴇᴅ ғᴏʀ {}".format(getvalue)
        if conn:
            text = "ʙʟᴀᴄᴋʟɪsᴛ sᴛɪᴄᴋᴇʀ ᴍᴏᴅᴇ ɪs ᴄᴜʀʀᴇɴᴛʟʏ sᴇᴛ ᴛᴏ *{}* ɪɴ *{}*.".format(
                settypeblacklist,
                chat_name,
            )
        else:
            text = "ʙʟᴀᴄᴋʟɪsᴛ sᴛɪᴄᴋᴇʀ ᴍᴏᴅᴇ ɪs ᴄᴜʀʀᴇɴᴛʟʏ sᴇᴛ ᴛᴏ *{}*.".format(
                settypeblacklist,
            )
        await send_message(
            update.effective_message,
            text,
            parse_mode=ParseMode.MARKDOWN,
        )
    return ""


@user_not_admin
async def del_blackliststicker(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bot = context.bot
    chat = update.effective_chat  # type: Optional[Chat]
    message = update.effective_message  # type: Optional[Message]
    user = update.effective_user
    to_match = message.sticker
    if not to_match or not to_match.set_name:
        return
    bot = context.bot
    getmode, value = sql.get_blacklist_setting(chat.id)

    chat_filters = sql.get_chat_stickers(chat.id)
    for trigger in chat_filters:
        if to_match.set_name.lower() == trigger.lower():
            try:
                if getmode == 0:
                    return
                elif getmode == 1:
                    await message.delete()
                elif getmode == 2:
                    await message.delete()
                    warn(
                        update.effective_user,
                        chat,
                        "ᴜsɪɴɢ sᴛɪᴄᴋᴇʀ '{}' ᴡʜɪᴄʜ ɪɴ ʙʟᴀᴄᴋʟɪsᴛ sᴛɪᴄᴋᴇʀs".format(
                            trigger,
                        ),
                        message,
                        update.effective_user,
                        # conn=False,
                    )
                    return
                elif getmode == 3:
                    await message.delete()
                    await bot.restrict_chat_member(
                        chat.id,
                        update.effective_user.id,
                        permissions=ChatPermissions(can_send_messages=False),
                    )
                    await bot.sendMessage(
                        chat.id,
                        "{} ᴍᴜᴛᴇᴅ ʙᴇᴄᴀᴜsᴇ ᴜsɪɴɢ '{}' ᴡʜɪᴄʜ ɪɴ ʙʟᴀᴄᴋʟɪsᴛ sᴛɪᴄᴋᴇʀs".format(
                            mention_markdown(user.id, user.first_name),
                            trigger,
                        ),
                        parse_mode="markdown",
                        message_thread_id=message.message_thread_id
                        if chat.is_forum
                        else None,
                    )
                    return
                elif getmode == 4:
                    await message.delete()
                    res = chat.unban_member(update.effective_user.id)
                    if res:
                        await bot.sendMessage(
                            chat.id,
                            "{} ᴋɪᴄᴋᴇᴅ ʙᴇᴄᴀᴜsᴇ ᴜsɪɴɢ '{}' ᴡʜɪᴄʜ ɪɴ ʙʟᴀᴄᴋʟɪsᴛ sᴛɪᴄᴋᴇʀs".format(
                                mention_markdown(user.id, user.first_name),
                                trigger,
                            ),
                            parse_mode="markdown",
                            message_thread_id=message.message_thread_id
                            if chat.is_forum
                            else None,
                        )
                    return
                elif getmode == 5:
                    await message.delete()
                    await chat.ban_member(user.id)
                    await bot.sendMessage(
                        chat.id,
                        "{} ʙᴀɴɴᴇᴅ ʙᴇᴄᴀᴜsᴇ ᴜsɪɴɢ '{}' ᴡʜɪᴄʜ ɪɴ ʙʟᴀᴄᴋʟɪsᴛ sᴛɪᴄᴋᴇʀs".format(
                            mention_markdown(user.id, user.first_name),
                            trigger,
                        ),
                        parse_mode="markdown",
                        message_thread_id=message.message_thread_id
                        if chat.is_forum
                        else None,
                    )
                    return
                elif getmode == 6:
                    await message.delete()
                    bantime = await extract_time(message, value)
                    await chat.ban_member(user.id, until_date=bantime)
                    await bot.sendMessage(
                        chat.id,
                        "{} ʙᴀɴɴᴇᴅ ғᴏʀ {} ʙᴇᴄᴀᴜsᴇ ᴜsɪɴɢ '{}' ᴡʜɪᴄʜ ɪɴ ʙʟᴀᴄᴋʟɪsᴛ sᴛɪᴄᴋᴇʀs".format(
                            mention_markdown(user.id, user.first_name),
                            value,
                            trigger,
                        ),
                        parse_mode="markdown",
                        message_thread_id=message.message_thread_id
                        if chat.is_forum
                        else None,
                    )
                    return
                elif getmode == 7:
                    await message.delete()
                    mutetime = await extract_time(message, value)
                    await bot.restrict_chat_member(
                        chat.id,
                        user.id,
                        permissions=ChatPermissions(can_send_messages=False),
                        until_date=mutetime,
                    )
                    await bot.sendMessage(
                        chat.id,
                        "{} ᴍᴜᴛᴇᴅ ғᴏʀ {} ʙᴇᴄᴀᴜsᴇ ᴜsɪɴɢ '{}' ᴡʜɪᴄʜ ɪɴ ʙʟᴀᴄᴋʟɪsᴛ sᴛɪᴄᴋᴇʀs".format(
                            mention_markdown(user.id, user.first_name),
                            value,
                            trigger,
                        ),
                        parse_mode="markdown",
                        message_thread_id=message.message_thread_id
                        if chat.is_forum
                        else None,
                    )
                    return
            except BadRequest as excp:
                if excp.message != "ᴍᴇssᴀɢᴇ ᴛᴏ ᴅᴇʟᴇᴛᴇ ɴᴏᴛ ғᴏᴜɴᴅ":
                    LOGGER.exception("ᴇʀʀᴏʀ ᴡʜɪʟᴇ ᴅᴇʟᴇᴛɪɴɢ ʙʟᴀᴄᴋʟɪsᴛ ᴍᴇssᴀɢᴇ.")
                break


async def __import_data__(chat_id, data, message):
    # set chat blacklist
    blacklist = data.get("sticker_blacklist", {})
    for trigger in blacklist:
        sql.add_to_stickers(chat_id, trigger)


def __migrate__(old_chat_id, new_chat_id):
    sql.migrate_chat(old_chat_id, new_chat_id)


def __chat_settings__(chat_id, user_id):
    blacklisted = sql.num_stickers_chat_filters(chat_id)
    return "ᴛʜᴇʀᴇ ᴀʀᴇ `{} `ʙʟᴀᴄᴋʟɪsᴛᴇᴅ sᴛɪᴄᴋᴇʀs.".format(blacklisted)


def __stats__():
    return "• {} ʙʟᴀᴄᴋʟɪsᴛ sᴛɪᴄᴋᴇʀs, ᴀᴄʀᴏss {} ᴄʜᴀᴛs.".format(
        sql.num_stickers_filters(),
        sql.num_stickers_filter_chats(),
    )


__mod_name__ = "𝐒-ʙʟᴀᴄᴋʟɪsᴛ"

__help__ = """
ʙʟᴀᴄᴋʟɪsᴛ sᴛɪᴄᴋᴇʀ ɪs ᴜsᴇᴅ ᴛᴏ sᴛᴏᴘ ᴄᴇʀᴛᴀɪɴ sᴛɪᴄᴋᴇʀs. ᴡʜᴇɴᴇᴠᴇʀ ᴀ sᴛɪᴄᴋᴇʀ ɪs sᴇɴᴛ, ᴛʜᴇ ᴍᴇssᴀɢᴇ ᴡɪʟʟ ʙᴇ ᴅᴇʟᴇᴛᴇᴅ ɪᴍᴍᴇᴅɪᴀᴛᴇʟʏ.

*ɴᴏᴛᴇ:* ʙʟᴀᴄᴋʟɪsᴛ sᴛɪᴄᴋᴇʀs ᴅᴏ ɴᴏᴛ ᴀғғᴇᴄᴛ ᴛʜᴇ ɢʀᴏᴜᴘ ᴀᴅᴍɪɴ

• /blsticker*:* sᴇᴇ ᴄᴜʀʀᴇɴᴛ ʙʟᴀᴄᴋʟɪsᴛᴇᴅ sᴛɪᴄᴋᴇʀ

*ᴏɴʟʏ ᴀᴅᴍɪɴ:*
• /addblsticker <sᴛɪᴄᴋᴇʀ ʟɪɴᴋ>*:* ᴀᴅᴅ ᴛʜᴇ sᴛɪᴄᴋᴇʀ ᴛʀɪɢɢᴇʀ ᴛᴏ ᴛʜᴇ ʙʟᴀᴄᴋ ʟɪsᴛ. ᴄᴀɴ ʙᴇ ᴀᴅᴅᴇᴅ ᴠɪᴀ ʀᴇᴘʟʏ sᴛɪᴄᴋᴇʀ
• /unblsticker <sᴛɪᴄᴋᴇʀ ʟɪɴᴋ>*:* ʀᴇᴍᴏᴠᴇ ᴛʀɪɢɢᴇʀs ғʀᴏᴍ ʙʟᴀᴄᴋʟɪsᴛ. ᴛʜᴇ sᴀᴍᴇ ɴᴇᴡʟɪɴᴇ ʟᴏɢɪᴄ ᴀᴘᴘʟɪᴇs ʜᴇʀᴇ, sᴏ ʏᴏᴜ ᴄᴀɴ ᴅᴇʟᴇᴛᴇ ᴍᴜʟᴛɪᴘʟᴇ ᴛʀɪɢɢᴇʀs ᴀᴛ once
• /rmblsticker <sᴛɪᴄᴋᴇʀ ʟɪɴᴋ>*:* sᴀᴍᴇ ᴀs ᴀʙᴏᴠᴇ
• /blstickermode <delete/ban/tban/mute/tmute>*:* sᴇᴛs ᴜᴘ ᴀ ᴅᴇғᴀᴜʟᴛ ᴀᴄᴛɪᴏɴ ᴏɴ ᴡʜᴀᴛ ᴛᴏ ᴅᴏ ɪғ ᴜsᴇʀs ᴜsᴇ ʙʟᴀᴄᴋʟɪsᴛᴇᴅ sᴛɪᴄᴋᴇʀs

"""

BLACKLIST_STICKER_HANDLER = DisableAbleCommandHandler(
    "blsticker", blackliststicker, admin_ok=True, block=False
)
ADDBLACKLIST_STICKER_HANDLER = DisableAbleCommandHandler(
    "addblsticker", add_blackliststicker, block=False
)
UNBLACKLIST_STICKER_HANDLER = CommandHandler(
    ["unblsticker", "rmblsticker"], unblackliststicker, block=False
)
BLACKLISTMODE_HANDLER = CommandHandler("blstickermode", blacklist_mode, block=False)
BLACKLIST_STICKER_DEL_HANDLER = MessageHandler(
    filters.Sticker.ALL & filters.ChatType.GROUPS, del_blackliststicker, block=False
)

application.add_handler(BLACKLIST_STICKER_HANDLER)
application.add_handler(ADDBLACKLIST_STICKER_HANDLER)
application.add_handler(UNBLACKLIST_STICKER_HANDLER)
application.add_handler(BLACKLISTMODE_HANDLER)
application.add_handler(BLACKLIST_STICKER_DEL_HANDLER)
