import html
import json
import os
from typing import Optional

from telegram import Update
from telegram.constants import ParseMode
from telegram.error import TelegramError
from telegram.ext import CommandHandler, ContextTypes
from telegram.helpers import mention_html

from Exon import DEV_USERS, DRAGONS, OWNER_ID, SUPPORT_CHAT, exon
from Exon.modules.helper_funcs.chat_status import check_admin, whitelist_plus
from Exon.modules.helper_funcs.extraction import extract_user
from Exon.modules.log_channel import gloggable

ELEVATED_USERS_FILE = os.path.join(os.getcwd(), "Exon/elevated_users.json")


def check_user_id(user_id: int, context: ContextTypes.DEFAULT_TYPE) -> Optional[str]:
    bot = context.bot
    if not user_id:
        reply = "ᴛʜᴀᴛ...ɪs ᴀ ᴄʜᴀᴛ! ʙᴀᴋᴀ ᴋᴀ ᴏᴍᴀᴇ?"

    elif user_id == bot.id:
        reply = "ᴛʜɪs ᴅᴏᴇs ɴᴏᴛ ᴡᴏʀᴋ ᴛʜᴀᴛ ᴡᴀʏ."

    else:
        reply = None
    return reply


@gloggable
@check_admin(only_dev=True)
async def addsudo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    message = update.effective_message
    user = update.effective_user
    chat = update.effective_chat
    bot, args = context.bot, context.args
    user_id = await extract_user(message, context, args)
    user_member = await bot.getChat(user_id)

    reply = check_user_id(user_id, bot)
    if reply:
        await message.reply_text(reply)
        return ""

    with open(ELEVATED_USERS_FILE, "r") as infile:
        data = json.load(infile)

    if user_id in DRAGONS:
        await message.reply_text("ᴛʜɪs ᴍᴇᴍʙᴇʀ ɪs ᴀʟʀᴇᴀᴅʏ ᴀ ᴅʀᴀɢᴏɴ ᴅɪsᴀsᴛᴇʀ")
        return ""

    data["sudos"].append(user_id)
    DRAGONS.append(user_id)

    with open(ELEVATED_USERS_FILE, "w") as outfile:
        json.dump(data, outfile, indent=4)

    await update.effective_message.reply_text(
        ʀᴛ
        + "\nsᴜᴄᴄᴇssғᴜʟʟʏ sᴇᴛ ᴅɪsᴀsᴛᴇʀ ʟᴇᴠᴇʟ ᴏғ {} ᴛᴏ ᴅʀᴀɢᴏɴ!".format(
            user_member.first_name,
        ),
    )

    log_message = (
        f"#𝐒𝐔𝐃𝐎\n"
        f"<b>ᴀᴅᴍɪɴ:</b> {mention_html(user.id, html.escape(user.first_name))}\n"
        f"<b>ᴜsᴇʀ:</b> {mention_html(user_member.id, html.escape(user_member.first_name))}"
    )

    if chat.type != "private":
        log_message = f"<b>{html.escape(chat.title)}:</b>\n" + log_message

    return log_message


@gloggable
@check_admin(only_dev=True)
async def removesudo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    message = update.effective_message
    user = update.effective_user
    chat = update.effective_chat
    bot, args = context.bot, context.args
    user_id = await extract_user(message, context, args)
    user_member = await bot.getChat(user_id)

    reply = check_user_id(user_id, bot)
    if reply:
        await message.reply_text(reply)
        return ""

    with open(ELEVATED_USERS_FILE, "r") as infile:
        data = json.load(infile)

    if user_id in DRAGONS:
        await message.reply_text("ʀᴇǫᴜᴇsᴛᴇᴅ ʜᴀ ᴛᴏ ᴅᴇᴍᴏᴛᴇ ᴛʜɪs ᴜsᴇʀ ᴛᴏ ᴄɪᴠɪʟɪᴀɴ")
        DRAGONS.remove(user_id)
        data["sudos"].remove(user_id)

        with open(ELEVATED_USERS_FILE, "w") as outfile:
            json.dump(data, outfile, indent=4)

        log_message = (
            f"#𝐔𝐍𝐒𝐔𝐃𝐎\n"
            f"<b>ᴀᴅᴍɪɴ:</b> {mention_html(user.id, html.escape(user.first_name))}\n"
            f"<b>ᴜsᴇʀ:</b> {mention_html(user_member.id, html.escape(user_member.first_name))}"
        )

        if chat.type != "private":
            log_message = "<b>{}:</b>\n".format(html.escape(chat.title)) + log_message

        return log_message

    else:
        await message.reply_text("ᴛʜɪs ᴜsᴇʀ ɪs ɴᴏᴛ ᴀ ᴅʀᴀɢᴏɴ ᴅɪsᴀsᴛᴇʀ!")
        return ""


@whitelist_plus
async def sudolist(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bot = context.bot
    m = await update.effective_message.reply_text(
        "<code>ɢᴀᴛʜᴇʀɪɴɢ ɪɴᴛᴇʟ..</code>",
        parse_mode=ParseMode.HTML,
    )
    true_sudo = list(set(DRAGONS) - set(DEV_USERS))
    reply = "<b>ᴋɴᴏᴡɴ ᴅʀᴀɢᴏɴ ᴅɪsᴀsᴛᴇʀs 🐉:</b>\n"
    for each_user in true_sudo:
        user_id = int(each_user)
        try:
            user = await bot.get_chat(user_id)
            reply += f"• {mention_html(user_id, html.escape(user.first_name))}\n"
        except TelegramError:
            pass
    await m.edit_text(reply, parse_mode=ParseMode.HTML)


@whitelist_plus
async def devlist(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bot = context.bot
    m = await update.effective_message.reply_text(
        "<code>ɢᴀᴛʜᴇʀɪɴɢ ɪɴᴛᴇʟ..</code>",
        parse_mode=ParseMode.HTML,
    )
    true_dev = list(set(DEV_USERS) - {OWNER_ID})
    reply = "<b>ᴛᴇᴀᴍ ᴀʙɪsʜɴᴏɪ ᴍᴇᴍʙᴇʀs ⚡️:</b>\n"
    for each_user in true_dev:
        user_id = int(each_user)
        try:
            user = await bot.get_chat(user_id)
            reply += f"• {mention_html(user_id, html.escape(user.first_name))}\n"
        except TelegramError:
            pass
    await m.edit_text(reply, parse_mode=ParseMode.HTML)


__help__ = f"""
*⚠️ ɴᴏᴛɪᴄᴇ:*
ᴄᴏᴍᴍᴀɴᴅs ʟɪsᴛᴇᴅ ʜᴇʀᴇ ᴏɴʟʏ ᴡᴏʀᴋ ғᴏʀ ᴜsᴇʀs ᴡɪᴛʜ sᴘᴇᴄɪᴀʟ ᴀᴄᴄᴇss ᴀɴᴅ ᴀʀᴇ ᴍᴀɪɴʟʏ ᴜsᴇᴅ ғᴏʀ ᴛʀᴏᴜʙʟᴇsʜᴏᴏᴛɪɴɢ, ᴅᴇʙᴜɢɢɪɴɢ ᴘᴜʀᴘᴏsᴇs.
ɢʀᴏᴜᴘ ᴀᴅᴍɪɴs/ɢʀᴏᴜᴘ ᴏᴡɴᴇʀs ᴅᴏ ɴᴏᴛ ɴᴇᴇᴅ ᴛʜᴇsᴇ ᴄᴏᴍᴍᴀɴᴅs.

 ╔ *ʟɪsᴛ ᴀʟʟ sᴘᴇᴄɪᴀʟ ᴜsᴇʀs:*
 ╠ /dragons*:* ʟɪsᴛs ᴀʟʟ ᴅʀᴀɢᴏɴ ᴅɪsᴀsᴛᴇʀs
 ╠ /darlings*:* ʟɪsᴛs ᴀʟʟ ʙʟᴀᴄᴋ ʙᴜʟʟs ᴍᴇᴍʙᴇʀs
 ╠ /adddragon*:* ᴀᴅᴅs a user to Dragon
 ╚ ᴀᴅᴅ ᴅᴇᴠ ᴅᴏᴇsɴ'ᴛ ᴇxɪsᴛ, ᴅᴇᴠs sʜᴏᴜʟᴅ ᴋɴᴏᴡ ʜᴏᴡ ᴛᴏ ᴀᴅᴅ ᴛʜᴇᴍsᴇʟᴠᴇs

 ╔ *ɢʀᴏᴜᴘs ɪɴғᴏ:*
 ╠ /groups*:* ʟɪsᴛ ᴛʜᴇ ɢʀᴏᴜᴘs ᴡɪᴛʜ ɴᴀᴍᴇ, ɪᴅ, ᴍᴇᴍʙᴇʀs ᴄᴏᴜɴᴛ ᴀs ᴀ ᴛxᴛ
 ╠ /leave <ID>*:* ʟᴇᴀᴠᴇ ᴛʜᴇ ɢʀᴏᴜᴘ, ɪᴅ ᴍᴜsᴛ ʜᴀᴠᴇ ʜʏᴘʜᴇɴ (-)
 ╠ /stats*:* sʜᴏᴡs ᴏᴠᴇʀᴀʟʟ ʙᴏᴛ sᴛᴀᴛs
 ╚ /ginfo ᴜsᴇʀɴᴀᴍᴇ*:* ᴘᴜʟʟs ɪɴғᴏ ᴘᴀɴᴇʟ ғᴏʀ ᴇɴᴛɪʀᴇ ɢʀᴏᴜᴘ
 
 ╔ *ɢʟᴏʙᴀʟ ʙᴀɴs:*
 ╠ /gban ᴜsᴇʀ ʀᴇᴀsᴏɴ*:* ɢʟᴏʙᴀʟʟʏ ʙᴀɴs ᴀ ᴜsᴇʀ
 ╚ /ungban ᴜsᴇʀ ʀᴇᴀsᴏɴ*:* ᴜɴʙᴀɴs ᴛʜᴇ ᴜsᴇʀ ғʀᴏᴍ ᴛʜᴇ ɢʟᴏʙᴀʟ ʙᴀɴs ʟɪsᴛ

 ╔ *ɢʟᴏʙᴀʟ ʙᴀɴs:*
 ╠ /gban <id> <ʀᴇᴀsᴏɴ>*:* ɢʙᴀɴs ᴛʜᴇ ᴜsᴇʀ, ᴡᴏʀᴋs ʙʏ ʀᴇᴘʟʏ ᴛᴏᴏ
 ╠ /ungban*:* ᴜɴɢʙᴀɴs ᴛʜᴇ ᴜsᴇʀ, sᴀᴍᴇ ᴜsᴀɢᴇ ᴀs ɢʙᴀɴ
 ╚ /gbanlist*:* ᴏᴜᴛᴘᴜᴛs ᴀ ʟɪsᴛ ᴏғ ɢʙᴀɴɴᴇᴅ ᴜsᴇʀs

ᴠɪsɪᴛ @{SUPPORT_CHAT} ғᴏʀ ᴍᴏʀᴇ ɪɴғᴏʀᴍᴀᴛɪᴏɴ.
"""

SUDO_HANDLER = CommandHandler(("addsudo", "adddragon"), addsudo)
SUDOLIST_HANDLER = CommandHandler(["sudolist", "dragons"], sudolist)
DEVLIST_HANDLER = CommandHandler(["devlist", "darlings"], devlist)

exon.add_handler(SUDO_HANDLER)
exon.add_handler(SUDOLIST_HANDLER)
exon.add_handler(DEVLIST_HANDLER)

__mod_name__ = "𝐃ᴇᴠs"
__handlers__ = [
    SUDO_HANDLER,
    SUDOLIST_HANDLER,
    DEVLIST_HANDLER,
]
