"""
MIT License

Copyright (c) 2022 ABISHNOI69

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

# ""DEAR PRO PEOPLE,  DON'T REMOVE & CHANGE THIS LINE
# TG :- @Abishnoi1m
#     UPDATE   :- Abishnoi_bots
#     GITHUB :- ABISHNOI69 ""
import html

from telegram import ParseMode, Update
from telegram.error import BadRequest
from telegram.ext import CallbackContext, CommandHandler
from telegram.utils.helpers import mention_html

import Exon.modules.sql.blacklistusers_sql as sql
from Exon import DEMONS, DEV_USERS, DRAGONS, OWNER_ID, TIGERS, WOLVES, dispatcher
from Exon.modules.helper_funcs.chat_status import dev_plus
from Exon.modules.helper_funcs.extraction import extract_user, extract_user_and_text
from Exon.modules.log_channel import gloggable

BLACKLISTWHITELIST = [OWNER_ID] + DEV_USERS + DRAGONS + WOLVES + DEMONS
BLABLEUSERS = [OWNER_ID] + DEV_USERS


@dev_plus
@gloggable
def bl_user(update: Update, context: CallbackContext) -> str:
    message = update.effective_message
    user = update.effective_user
    bot, args = context.bot, context.args
    user_id, reason = extract_user_and_text(message, args)

    if not user_id:
        message.reply_text("I ᴅᴏᴜʙᴛs ᴛʜᴀᴛ's a ᴜsᴇʀ.")
        return ""

    if user_id == bot.id:
        message.reply_text("ʜᴏᴡ ᴀᴍ ɪ sᴜᴘᴘᴏsᴇᴅ ᴛᴏ ᴅᴏ ᴍʏ ᴡᴏʀᴋ ɪғ ɪ ᴀᴍ ɪɢɴᴏʀɪɴɢ ᴍʏsᴇʟғ?")
        return ""

    if user_id in BLACKLISTWHITELIST:
        message.reply_text("ɴᴏ!\nɴᴏᴛɪᴄɪɴɢ ᴅɪsᴀsᴛᴇʀs ɪs ᴍʏ ᴊᴏʙ.")
        return ""

    try:
        target_user = bot.get_chat(user_id)
    except BadRequest as excp:
        if excp.message != "ᴜsᴇʀ ɴᴏᴛ ғᴏᴜɴᴅ":
            raise
        message.reply_text("I ᴄᴀɴ'ᴛ sᴇᴇᴍ ᴛᴏ ғɪɴᴅ ᴛʜɪs ᴜsᴇʀ.")
        return ""
    sql.blacklist_user(user_id, reason)
    message.reply_text("I sʜᴀʟʟ ɪɢɴᴏʀᴇ ᴛʜᴇ ᴇxɪsᴛᴇɴᴄᴇ ᴏғ ᴛʜɪs ᴜsᴇʀ!")
    log_message = (
        f"#𝐁𝐋𝐀𝐂𝐊𝐋𝐈𝐒𝐓\n"
        f"<b>ᴀᴅᴍɪɴ:</b> {mention_html(user.id, html.escape(user.first_name))}\n"
        f"<b>ᴜsᴇʀ:</b> {mention_html(target_user.id, html.escape(target_user.first_name))}"
    )
    if reason:
        log_message += f"\n<b>ʀᴇᴀsᴏɴ:</b> {reason}"

    return log_message


@dev_plus
@gloggable
def unbl_user(update: Update, context: CallbackContext) -> str:
    message = update.effective_message
    user = update.effective_user
    bot, args = context.bot, context.args
    user_id = extract_user(message, args)

    if not user_id:
        message.reply_text("I ᴅᴏᴜʙᴛ ᴛʜᴀᴛ's ᴀ ᴜsᴇʀ.")
        return ""

    if user_id == bot.id:
        message.reply_text("I ᴀʟᴡᴀʏs ɴᴏᴛɪᴄᴇ ᴍʏsᴇʟғ.")
        return ""

    try:
        target_user = bot.get_chat(user_id)
    except BadRequest as excp:
        if excp.message == "ᴜsᴇʀ ɴᴏᴛ ғᴏᴜɴᴅ":
            message.reply_text("I ᴄᴀɴ'ᴛ sᴇᴇᴍ ᴛᴏ ғɪɴᴅ ᴛʜɪs ᴜsᴇʀ.")
            return ""
        raise

    if sql.is_user_blacklisted(user_id):
        sql.unblacklist_user(user_id)
        message.reply_text("*notices user*")
        log_message = (
            f"#𝐔𝐍𝐁𝐋𝐀𝐂𝐊𝐋𝐈𝐒𝐓\n"
            f"<b>ᴀᴅᴍɪɴ:</b> {mention_html(user.id, html.escape(user.first_name))}\n"
            f"<b>ᴜsᴇʀ:</b> {mention_html(target_user.id, html.escape(target_user.first_name))}"
        )

        return log_message
    message.reply_text("I ᴀᴍ ɴᴏᴛ ɪɢɴᴏʀɪɴɢ ᴛʜᴇᴍ ᴀᴛ ᴀʟʟ ᴛʜᴏᴜɢʜ!")
    return ""


@dev_plus
def bl_users(update: Update, context: CallbackContext):
    users = []
    bot = context.bot
    for each_user in sql.BLACKLIST_USERS:
        user = bot.get_chat(each_user)
        reason = sql.get_reason(each_user)

        if reason:
            users.append(
                f"• {mention_html(user.id, html.escape(user.first_name))} :- {reason}",
            )
        else:
            users.append(f"• {mention_html(user.id, html.escape(user.first_name))}")

    message = "<b>ʙʟᴀᴄᴋʟɪsᴛᴇᴅ ᴜsᴇʀs</b>\n"
    message += "\n".join(users) if users else "ɴᴏɴᴇ ɪs ʙᴇɪɴɢ ɪɢɴᴏʀᴇᴅ ᴀs ᴏғ ʏᴇᴛ."
    update.effective_message.reply_text(message, parse_mode=ParseMode.HTML)


def __user_info__(user_id):
    is_blacklisted = sql.is_user_blacklisted(user_id)

    text = "ʙʟᴀᴄᴋʟɪsᴛᴇᴅ: <b>{}</b>"
    if user_id in [777000, 1087968824]:
        return ""
    if user_id == dispatcher.bot.id:
        return ""
    if int(user_id) in DRAGONS + TIGERS + WOLVES:
        return ""
    if is_blacklisted:
        text = text.format("Yes")
        reason = sql.get_reason(user_id)
        if reason:
            text += f"\nʀᴇᴀsᴏɴ: <code>{reason}</code>"
    else:
        text = text.format("No")

    return text


BL_HANDLER = CommandHandler("ignore", bl_user, run_async=True)
UNBL_HANDLER = CommandHandler("notice", unbl_user, run_async=True)
BLUSERS_HANDLER = CommandHandler("ignoredlist", bl_users, run_async=True)

dispatcher.add_handler(BL_HANDLER)
dispatcher.add_handler(UNBL_HANDLER)
dispatcher.add_handler(BLUSERS_HANDLER)

__mod_name__ = "𝐁-ᴜsᴇʀs"
__handlers__ = [BL_HANDLER, UNBL_HANDLER, BLUSERS_HANDLER]

# ғᴏʀ ʜᴇʟᴘ ᴍᴇɴᴜ
# """
from Exon.modules.language import gs


def get_help(chat):
    return gs(chat, "buser_help")


# """
