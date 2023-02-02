import html

from telegram import Update
from telegram.constants import ParseMode
from telegram.error import BadRequest
from telegram.ext import CommandHandler, ContextTypes
from telegram.helpers import mention_html

import Exon.modules.sql.blacklistusers_sql as sql
from Exon import DEV_USERS, DRAGONS, OWNER_ID, exon
from Exon.modules.helper_funcs.chat_status import check_admin
from Exon.modules.helper_funcs.extraction import extract_user, extract_user_and_text
from Exon.modules.log_channel import gloggable

BLACKLISTWHITELIST = [OWNER_ID] + DEV_USERS + DRAGONS
BLABLEUSERS = [OWNER_ID] + DEV_USERS


@gloggable
@check_admin(only_dev=True)
async def bl_user(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    message = update.effective_message
    user = update.effective_user
    bot, args = context.bot, context.args
    user_id, reason = await extract_user_and_text(message, context, args)

    if not user_id:
        await message.reply_text("I ᴅᴏᴜʙᴛ ᴛʜᴀᴛ's ᴀ ᴜsᴇʀ.")
        return ""

    if user_id == bot.id:
        await message.reply_text(
            "ʜᴏᴡ ᴀᴍ ɪ sᴜᴘᴘᴏsᴇᴅ ᴛᴏ ᴅᴏ ᴍʏ ᴡᴏʀᴋ ɪғ ɪ ᴀᴍ ɪɢɴᴏʀɪɴɢ ᴍʏsᴇʟғ?"
        )
        return ""

    if user_id in BLACKLISTWHITELIST:
        await message.reply_text("ɴᴏ!\nɴᴏᴛɪᴄɪɴɢ ᴅɪsᴀsᴛᴇʀs ɪs ᴍʏ ᴊᴏʙ.")
        return ""

    try:
        target_user = await bot.get_chat(user_id)
    except BadRequest as excp:
        if excp.message == "ᴜsᴇʀ ɴᴏᴛ ғᴏᴜɴᴅ":
            await message.reply_text("I ᴄᴀɴ'ᴛ sᴇᴇᴍ ᴛᴏ ғɪɴᴅ ᴛʜɪs ᴜsᴇʀ.")
            return ""
        else:
            raise

    sql.blacklist_user(user_id, reason)
    await message.reply_text("I sʜᴀʟʟ ɪɢɴᴏʀᴇ ᴛʜᴇ ᴇxɪsᴛᴇɴᴄᴇ ᴏғ ᴛʜɪs ᴜsᴇʀ!")
    log_message = (
        f"#𝐁𝐋𝐀𝐂𝐊𝐋𝐈𝐒𝐓\n"
        f"<b>ᴀᴅᴍɪɴ:</b> {mention_html(user.id, html.escape(user.first_name))}\n"
        f"<b>ᴜsᴇʀ:</b> {mention_html(target_user.id, html.escape(target_user.first_name))}"
    )
    if reason:
        log_message += f"\n<b>ʀᴇᴀsᴏɴ:</b> {reason}"

    return log_message


@check_admin(only_dev=True)
@gloggable
async def unbl_user(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    message = update.effective_message
    user = update.effective_user
    bot, args = context.bot, context.args
    user_id = await extract_user(message, context, args)

    if not user_id:
        await message.reply_text("I ᴅᴏᴜʙᴛ ᴛʜᴀᴛ's ᴀ ᴜsᴇʀ.")
        return ""

    if user_id == bot.id:
        await message.reply_text("I ᴀʟᴡᴀʏs ɴᴏᴛɪᴄᴇ ᴍʏsᴇʟғ.")
        return ""

    try:
        target_user = await bot.get_chat(user_id)
    except BadRequest as excp:
        if excp.message == "ᴜsᴇʀ ɴᴏᴛ ғᴏᴜɴᴅ":
            await message.reply_text("I ᴄᴀɴ'ᴛ sᴇᴇᴍ ᴛᴏ ғɪɴᴅ ᴛʜɪs ᴜsᴇʀ.")
            return ""
        else:
            raise

    if sql.is_user_blacklisted(user_id):
        sql.unblacklist_user(user_id)
        await message.reply_text("*notices user*")
        log_message = (
            f"#𝐔𝐍𝐁𝐋𝐀𝐂𝐊𝐋𝐈𝐒𝐓\n"
            f"<b>ᴀᴅᴍɪɴ:</b> {mention_html(user.id, html.escape(user.first_name))}\n"
            f"<b>ᴜsᴇʀ:</b> {mention_html(target_user.id, html.escape(target_user.first_name))}"
        )

        return log_message

    else:
        await message.reply_text("I ᴀᴍ ɴᴏᴛ ɪɢɴᴏʀɪɴɢ ᴛʜᴇᴍ ᴀᴛ ᴀʟʟ ᴛʜᴏᴜɢʜ!")
        return ""


@check_admin(only_dev=True)
async def bl_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    users = []
    bot = context.bot
    for each_user in sql.BLACKLIST_USERS:
        user = await bot.get_chat(each_user)
        reason = sql.get_reason(each_user)

        if reason:
            users.append(
                f"• {mention_html(user.id, html.escape(user.first_name))} :- {reason}",
            )
        else:
            users.append(f"• {mention_html(user.id, html.escape(user.first_name))}")

    message = "<b>ʙʟᴀᴄᴋʟɪsᴛᴇᴅ ᴜsᴇʀs</b>\n"
    if not users:
        message += "ɴᴏᴏɴᴇ ɪs ʙᴇɪɴɢ ɪɢɴᴏʀᴇᴅ ᴀs ᴏғ ʏᴇᴛ."
    else:
        message += "\n".join(users)

    await update.effective_message.reply_text(message, parse_mode=ParseMode.HTML)


def __user_info__(user_id):
    is_blacklisted = sql.is_user_blacklisted(user_id)

    text = "ʙʟᴀᴄᴋʟɪsᴛᴇᴅ: <b>{}</b>"
    if user_id in [777000, 1087968824]:
        return ""
    if user_id == exon.bot.id:
        return ""
    if int(user_id) in DRAGONS:
        return ""
    if is_blacklisted:
        text = text.format("Yes")
        reason = sql.get_reason(user_id)
        if reason:
            text += f"\nʀᴇᴀsᴏɴ: <code>{reason}</code>"
    else:
        text = text.format("No")

    return text


BL_HANDLER = CommandHandler("ignore", bl_user)
UNBL_HANDLER = CommandHandler("notice", unbl_user)
BLUSERS_HANDLER = CommandHandler("ignoredlist", bl_users)

exon.add_handler(BL_HANDLER)
exon.add_handler(UNBL_HANDLER)
exon.add_handler(BLUSERS_HANDLER)

__mod_name__ = "𝐁-ᴜsᴇʀs"
__handlers__ = [BL_HANDLER, UNBL_HANDLER, BLUSERS_HANDLER]
