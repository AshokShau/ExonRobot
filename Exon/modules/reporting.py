import html

from telegram import Chat, InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.constants import ParseMode
from telegram.error import BadRequest, Forbidden
from telegram.ext import (
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)
from telegram.helpers import mention_html

from Exon import DRAGONS, LOGGER, exon
from Exon.modules.helper_funcs.chat_status import check_admin, user_not_admin
from Exon.modules.log_channel import loggable
from Exon.modules.sql import reporting_sql as sql

REPORT_GROUP = 12


@check_admin(is_user=True)
async def report_setting(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bot, args = context.bot, context.args
    chat = update.effective_chat
    msg = update.effective_message

    if chat.type == chat.PRIVATE:
        if len(args) >= 1:
            if args[0] in ("yes", "on"):
                sql.set_user_setting(chat.id, True)
                await msg.reply_text(
                    "ᴛᴜʀɴᴇᴅ ᴏɴ ʀᴇᴘᴏʀᴛɪɴɢ! ʏᴏᴜ'ʟʟ  ʙᴇ ɴᴏᴛɪғɪᴇᴅ ᴡʜᴇɴᴇᴠᴇʀ ᴀɴʏᴏɴᴇ ʀᴇᴘᴏʀᴛs sᴏᴍᴇᴛʜɪɴɢ.",
                )

            elif args[0] in ("no", "off"):
                sql.set_user_setting(chat.id, False)
                await msg.reply_text("ᴛᴜʀɴᴇᴅ ᴏғғ ʀᴇᴘᴏʀᴛɪɴɢ! ʏᴏᴜ ᴡᴏɴᴛ ɢᴇᴛ ᴀɴʏ ʀᴇᴘᴏʀᴛs.")
        else:
            await msg.reply_text(
                f"ʏᴏᴜʀ ᴄᴜʀʀᴇɴᴛ ʀᴇᴘᴏʀᴛ ᴘʀᴇғᴇʀᴇɴᴄᴇ ɪs: `{sql.user_should_report(chat.id)}`",
                parse_mode=ParseMode.MARKDOWN,
            )

    else:
        if len(args) >= 1:
            if args[0] in ("yes", "on"):
                sql.set_chat_setting(chat.id, True)
                await msg.reply_text(
                    "ᴛᴜʀɴᴇᴅ ᴏɴ ʀᴇᴘᴏʀᴛɪɴɢ! ᴀᴅᴍɪɴs ᴡʜᴏ ʜᴀᴠᴇ ᴛᴜʀɴᴇᴅ ᴏɴ ʀᴇᴘᴏʀᴛs ᴡɪʟʟ ʙᴇ ɴᴏᴛɪғɪᴇᴅ ᴡʜᴇɴ /report "
                    "ᴏʀ @admin ɪs ᴄᴀʟʟᴇᴅ.",
                )

            elif args[0] in ("no", "off"):
                sql.set_chat_setting(chat.id, False)
                await msg.reply_text(
                    "ᴛᴜʀɴᴇᴅ ᴏғғ ʀᴇᴘᴏʀᴛɪɴɢ! ɴᴏ ᴀᴅᴍɪɴs ᴡɪʟʟ ʙᴇ ɴᴏᴛɪғɪᴇᴅ ᴏɴ /report ᴏʀ @admin.",
                )
        else:
            await msg.reply_text(
                f"ᴛʜɪs ɢʀᴏᴜᴘ's ᴄᴜʀʀᴇɴᴛ sᴇᴛᴛɪɴɢ ɪs -: `{sql.chat_should_report(chat.id)}`",
                parse_mode=ParseMode.MARKDOWN,
            )


@user_not_admin
@loggable
async def report(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    bot = context.bot
    args = context.args
    message = update.effective_message
    chat = update.effective_chat
    user = update.effective_user

    if (
        chat
        and message.reply_to_message
        and not message.reply_to_message.forum_topic_created
        and sql.chat_should_report(chat.id)
    ):
        reported_user = message.reply_to_message.from_user
        chat_name = chat.title or chat.first or chat.username
        admin_list = await chat.get_administrators()
        message = update.effective_message

        if not args:
            await message.reply_text("ᴀᴅᴅ ᴀ ʀᴇᴀsᴏɴ ғᴏʀ ʀᴇᴘᴏʀᴛɪɴɢ ғɪʀsᴛ.")
            return ""

        if user.id == reported_user.id:
            await message.reply_text("ᴜʜ ʏᴇᴀʜ, sᴜʀᴇ sᴜʀᴇ...ᴍᴀsᴏ ᴍᴜᴄʜ?")
            return ""

        if user.id == bot.id:
            await message.reply_text("ɴɪᴄᴇ ᴛʀʏ.")
            return ""

        if reported_user.id in DRAGONS:
            await message.reply_text("ᴜʜ? ʏᴏᴜ ʀᴇᴘᴏʀᴛɪɴɢ ᴀ ᴅɪsᴀsᴛᴇʀ?")
            return ""

        if chat.username and chat.type == Chat.SUPERGROUP:

            reported = f"{mention_html(user.id, user.first_name)} ʀᴇᴘᴏʀᴛᴇᴅ {mention_html(reported_user.id, reported_user.first_name)} ᴛᴏ ᴛʜᴇ ᴀᴅᴍɪɴs!"

            msg = (
                f"<b>⚠️ ʀᴇᴘᴏʀᴛ: </b>{html.escape(chat.title)}\n"
                f"<b> • ʀᴇᴘᴏʀᴛ ʙʏ:</b> {mention_html(user.id, user.first_name)}(<code>{user.id}</code>)\n"
                f"<b> • Reported ᴜsᴇʀ:</b> {mention_html(reported_user.id, reported_user.first_name)} (<code>{reported_user.id}</code>)\n"
            )
            link = f'<b> • ʀᴇᴘᴏʀᴛᴇᴅ ᴍᴇssᴀɢᴇ:</b> <a href="https://t.me/{chat.username}/{message.reply_to_message.message_id}">click here</a>'
            should_forward = False
            keyboard = [
                [
                    InlineKeyboardButton(
                        "➡ ᴍᴇssᴀɢᴇ",
                        url=f"https://t.me/{chat.username}/{message.reply_to_message.message_id}",
                    ),
                ],
                [
                    InlineKeyboardButton(
                        "⚠ ᴋɪᴄᴋ",
                        callback_data=f"report_{chat.id}=kick={reported_user.id}={reported_user.first_name}",
                    ),
                    InlineKeyboardButton(
                        "⛔️ ʙᴀɴ",
                        callback_data=f"report_{chat.id}=banned={reported_user.id}={reported_user.first_name}",
                    ),
                ],
                [
                    InlineKeyboardButton(
                        "❎ ᴅᴇʟᴇᴛᴇ ᴍᴇssᴀɢᴇ",
                        callback_data=f"report_{chat.id}=delete={reported_user.id}={message.reply_to_message.message_id}",
                    ),
                ],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
        else:
            reported = (
                f"{mention_html(user.id, user.first_name)} ʀᴇᴘᴏʀᴛᴇᴅ "
                f"{mention_html(reported_user.id, reported_user.first_name)} ᴛᴏ ᴛʜᴇ ᴀᴅᴍɪɴs!"
            )

            msg = f'{mention_html(user.id, user.first_name)} ɪs ᴄᴀʟʟɪɴɢ ғᴏʀ ᴀᴅᴍɪɴs ɪɴ "{html.escape(chat_name)}"!'
            link = ""
            should_forward = True

        for admin in admin_list:
            if admin.user.is_bot:  # can't message bots
                continue

            if sql.user_should_report(admin.user.id):
                try:
                    if not chat.type == Chat.SUPERGROUP:
                        await bot.send_message(
                            admin.user.id,
                            msg + link,
                            parse_mode=ParseMode.HTML,
                        )

                        if should_forward:
                            await message.reply_to_message.forward(admin.user.id)

                            if (
                                len(message.text.split()) > 1
                            ):  # If user is giving a reason, send his message too
                                await message.forward(admin.user.id)
                    if not chat.username:
                        await bot.send_message(
                            admin.user.id,
                            msg + link,
                            parse_mode=ParseMode.HTML,
                        )

                        if should_forward:
                            await message.reply_to_message.forward(admin.user.id)

                            if (
                                len(message.text.split()) > 1
                            ):  # If user is giving a reason, send his message too
                                await message.forward(admin.user.id)

                    if chat.username and chat.type == Chat.SUPERGROUP:
                        await bot.send_message(
                            admin.user.id,
                            msg + link,
                            parse_mode=ParseMode.HTML,
                            reply_markup=reply_markup,
                        )

                        if should_forward:
                            await message.reply_to_message.forward(admin.user.id)

                            if (
                                len(message.text.split()) > 1
                            ):  # If user is giving a reason, send his message too
                                await message.forward(admin.user.id)

                except Forbidden:
                    pass
                except BadRequest as excp:  # TODO: cleanup exceptions
                    LOGGER.exception("ᴇxᴄᴇᴘᴛɪᴏɴ ᴡʜɪʟᴇ ʀᴇᴘᴏʀᴛɪɴɢ ᴜsᴇʀ")

        await message.reply_to_message.reply_text(
            f"{mention_html(user.id, user.first_name)} ʀᴇᴘᴏʀᴛᴇᴅ ᴛʜᴇ ᴍᴇssᴀɢᴇ ᴛᴏ ᴛʜᴇ ᴀᴅᴍɪɴs.",
            parse_mode=ParseMode.HTML,
        )
        return msg

    return ""


def __migrate__(old_chat_id, new_chat_id):
    sql.migrate_chat(old_chat_id, new_chat_id)


def __chat_settings__(chat_id, _):
    return f"ᴛʜɪs ᴄʜᴀᴛ ɪs sᴇᴛᴜᴘ ᴛᴏ sᴇɴᴅ ᴜsᴇʀ ʀᴇᴘᴏʀᴛs ᴛᴏ ᴀᴅᴍɪɴs, ᴠɪᴀ /report ᴀɴᴅ @admin: `{sql.chat_should_report(chat_id)}`"


def __user_settings__(user_id):
    if sql.user_should_report(user_id) is True:
        text = "ʏᴏᴜ ᴡɪʟʟ ʀᴇᴄᴇɪᴠᴇ ʀᴇᴘᴏʀᴛs ғʀᴏᴍ ᴄʜᴀᴛs ʏᴏᴜ'ʀᴇ ᴀᴅᴍɪɴ."
    else:
        text = "ʏᴏᴜ ᴡɪʟʟ *ɴᴏᴛ* ʀᴇᴄᴇɪᴠᴇ ʀᴇᴘᴏʀᴛs ғʀᴏᴍ ᴄʜᴀᴛs ʏᴏᴜ'ʀᴇ ᴀᴅᴍɪɴ."
    return text


async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bot = context.bot
    query = update.callback_query
    splitter = query.data.replace("report_", "").split("=")
    if splitter[1] == "kick":
        try:
            await bot.banChatMember(splitter[0], splitter[2])
            await bot.unbanChatMember(splitter[0], splitter[2])
            await query.answer("✅ sᴜᴄᴄᴇsғᴜʟʟʏ ᴋɪᴄᴋᴇᴅ")
            return ""
        except Exception as err:
            await query.answer("🛑 ғᴀɪʟᴇᴅ ᴛᴏ ᴋɪᴄᴋ")
            await bot.sendMessage(
                text=f"ᴇʀʀᴏʀ: {err}",
                chat_id=query.message.chat_id,
                parse_mode=ParseMode.HTML,
            )
    elif splitter[1] == "banned":
        try:
            await bot.banChatMember(splitter[0], splitter[2])
            await query.answer("✅  sᴜᴄᴄᴇsғᴜʟʟʏ ʙᴀɴɴᴇᴅ")
            return ""
        except Exception as err:
            await bot.sendMessage(
                text=f"ᴇʀʀᴏʀ: {err}",
                chat_id=query.message.chat_id,
                parse_mode=ParseMode.HTML,
            )
            await query.answer("🛑 ғᴀɪʟᴇᴅ ᴛᴏ ʙᴀɴ")
    elif splitter[1] == "delete":
        try:
            await bot.deleteMessage(splitter[0], splitter[3])
            await query.answer("✅ ᴍᴇssᴀɢᴇ ᴅᴇʟᴇᴛᴇᴅ")
            return ""
        except Exception as err:
            await bot.sendMessage(
                text=f"ᴇʀʀᴏʀ: {err}",
                chat_id=query.message.chat_id,
                parse_mode=ParseMode.HTML,
            )
            await query.answer("🛑 ғᴀɪʟᴇᴅ ᴛᴏ ᴅᴇʟᴇᴛᴇ ᴍᴇssᴀɢᴇ!")


__help__ = """
• /report <ʀᴇᴀsᴏɴ>*:* ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴍᴇssᴀɢᴇ ᴛᴏ ʀᴇᴘᴏʀᴛ ɪᴛ ᴛᴏ ᴀᴅᴍɪɴs.
• @admin*:* ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴍᴇssᴀɢᴇ ᴛᴏ ʀᴇᴘᴏʀᴛ ɪᴛ ᴛᴏ ᴀᴅᴍɪɴs.

*ᴀᴅᴍɪɴs ᴏɴʟʏ:*
• /reports <ᴏɴ/ᴏғғ>*:* ᴄʜᴀɴɢᴇ ʀᴇᴘᴏʀᴛ sᴇᴛᴛɪɴɢ, ᴏʀ ᴠɪᴇᴡ ᴄᴜʀʀᴇɴᴛ sᴛᴀᴛᴜs.
  • ɪғ ᴅᴏɴᴇ ɪɴ ᴘᴍ, ᴛᴏɢɢʟᴇs ʏᴏᴜʀ sᴛᴀᴛᴜs.
  • ɪғ ɪɴ ɢʀᴏᴜᴘ, ᴛᴏɢɢʟᴇs ᴛʜᴀᴛ ɢʀᴏᴜᴘ's sᴛᴀᴛᴜs.
"""

SETTING_HANDLER = CommandHandler("reports", report_setting)
REPORT_HANDLER = CommandHandler(
    "report", report, filters=filters.ChatType.GROUPS
)
ADMIN_REPORT_HANDLER = MessageHandler(
    filters.Regex(r"(?i)@admin(s)?"), report
)

REPORT_BUTTON_USER_HANDLER = CallbackQueryHandler(buttons, pattern=r"report_")
exon.add_handler(REPORT_BUTTON_USER_HANDLER)

exon.add_handler(SETTING_HANDLER)
exon.add_handler(REPORT_HANDLER, REPORT_GROUP)
exon.add_handler(ADMIN_REPORT_HANDLER, REPORT_GROUP)

__mod_name__ = "𝐑ᴇᴘᴏʀᴛs"

__handlers__ = [
    (REPORT_HANDLER, REPORT_GROUP),
    (ADMIN_REPORT_HANDLER, REPORT_GROUP),
    (SETTING_HANDLER),
]
