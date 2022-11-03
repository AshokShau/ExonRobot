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
import json
import os
from typing import Optional

from telegram import ParseMode, TelegramError, Update
from telegram.ext import CallbackContext, CommandHandler
from telegram.utils.helpers import mention_html

from Exon import DEMONS, DEV_USERS, DRAGONS, OWNER_ID, TIGERS, WOLVES, dispatcher
from Exon.modules.helper_funcs.chat_status import dev_plus, sudo_plus, whitelist_plus
from Exon.modules.helper_funcs.extraction import extract_user
from Exon.modules.log_channel import gloggable

ELEVATED_USERS_FILE = os.path.join(os.getcwd(), "Exon/elevated_users.json")


def check_user_id(user_id: int, context: CallbackContext) -> Optional[str]:
    bot = context.bot
    if not user_id:
        return "ᴛʜᴀᴛ...ɪs a ᴄʜᴀᴛ! ʙᴀᴋᴀ ᴋᴀ ᴏᴍᴀᴇ?"

    return "ᴛʜɪs ᴅᴏᴇs ɴᴏᴛ ᴡᴏʀᴋ ᴛʜᴀᴛ ᴡᴀʏ." if user_id == bot.id else None


@dev_plus
@gloggable
def addsudo(update: Update, context: CallbackContext) -> str:
    message = update.effective_message
    user = update.effective_user
    chat = update.effective_chat
    bot, args = context.bot, context.args
    user_id = extract_user(message, args)
    user_member = bot.getChat(user_id)
    rt = ""

    if reply := check_user_id(user_id, bot):
        message.reply_text(reply)
        return ""

    with open(ELEVATED_USERS_FILE, "r") as infile:
        data = json.load(infile)

    if user_id in DRAGONS:
        message.reply_text("ᴀʟʀᴇᴀᴅʏ ᴏᴜʀ ʙᴇsᴛᴏ ғʀɪᴇɴᴅᴏ :3")
        return ""

    if user_id in DEMONS:
        rt += "."
        data["supports"].remove(user_id)
        DEMONS.remove(user_id)

    if user_id in WOLVES:
        rt += "ᴡᴇ ᴀʀᴇ ʙᴇsᴛ ғʀɪᴇɴᴅs ɴᴏᴡ 🌸"
        data["whitelists"].remove(user_id)
        WOLVES.remove(user_id)

    data["sudos"].append(user_id)
    DRAGONS.append(user_id)

    with open(ELEVATED_USERS_FILE, "w") as outfile:
        json.dump(data, outfile, indent=4)

    update.effective_message.reply_text(
        (rt + f"\nsᴜᴄᴄᴇssғᴜʟʟʏ ᴍᴀᴅᴇ ʙᴇsᴛ ғʀɪᴇɴᴅsʜɪᴘ ᴡɪᴛʜ {user_member.first_name} !")
    )

    log_message = (
        f"#sᴜᴅᴏ\n"
        f"<b>ᴀᴅᴍɪɴ:</b> {mention_html(user.id, html.escape(user.first_name))}\n"
        f"<b>ᴜsᴇʀ:</b> {mention_html(user_member.id, html.escape(user_member.first_name))}"
    )

    if chat.type != "private":
        log_message = f"<b>{html.escape(chat.title)}:</b>\n{log_message}"

    return log_message


@sudo_plus
@gloggable
def addsupport(
    update: Update,
    context: CallbackContext,
) -> str:
    message = update.effective_message
    user = update.effective_user
    chat = update.effective_chat
    bot, args = context.bot, context.args
    user_id = extract_user(message, args)
    user_member = bot.getChat(user_id)
    rt = ""

    if reply := check_user_id(user_id, bot):
        message.reply_text(reply)
        return ""

    with open(ELEVATED_USERS_FILE, "r") as infile:
        data = json.load(infile)

    if user_id in DRAGONS:
        rt += "I ᴅᴏɴᴛ ᴡᴀɴᴛ ᴛᴏ ʙᴇ ʏᴏᴜʀ ʙᴇsᴛ ғʀɪᴇɴᴅ 🥲"
        data["sudos"].remove(user_id)
        DRAGONS.remove(user_id)

    if user_id in DEMONS:
        message.reply_text("ᴡᴇ ᴀʀᴇ ᴀʟʀᴇᴀᴅʏ ғʀɪᴇɴᴅs.")
        return ""

    if user_id in WOLVES:
        rt += "We are friends now :)"
        data["whitelists"].remove(user_id)
        WOLVES.remove(user_id)

    data["supports"].append(user_id)
    DEMONS.append(user_id)

    with open(ELEVATED_USERS_FILE, "w") as outfile:
        json.dump(data, outfile, indent=4)

    update.effective_message.reply_text(
        f"{rt}\n{user_member.first_name}, ᴡᴇ ᴄᴀɴ ʙᴇ ғʀɪᴇɴᴅs ;)"
    )

    log_message = (
        f"#sᴜᴘᴘᴏʀᴛ\n"
        f"<b>ᴀᴅᴍɪɴ:</b> {mention_html(user.id, html.escape(user.first_name))}\n"
        f"<b>ᴜsᴇʀ:</b> {mention_html(user_member.id, html.escape(user_member.first_name))}"
    )

    if chat.type != "private":
        log_message = f"<b>{html.escape(chat.title)}:</b>\n{log_message}"

    return log_message


@sudo_plus
@gloggable
def addwhitelist(update: Update, context: CallbackContext) -> str:
    message = update.effective_message
    user = update.effective_user
    chat = update.effective_chat
    bot, args = context.bot, context.args
    user_id = extract_user(message, args)
    user_member = bot.getChat(user_id)
    rt = ""

    if reply := check_user_id(user_id, bot):
        message.reply_text(reply)
        return ""

    with open(ELEVATED_USERS_FILE, "r") as infile:
        data = json.load(infile)

    if user_id in DRAGONS:
        rt += "ᴛʜɪs ᴍᴇᴍʙᴇʀ ɪs ᴏᴜʀ ʙᴇsᴛғʀɪᴇɴᴅ ʙᴜᴛ ɪ ᴡɪʟʟ ʟɪᴋᴇ ᴡʜᴇɴ ᴏᴜʀ ʙᴇsᴛғʀɪᴇɴᴅ ʙᴇᴄᴏᴍᴇs ᴀ ɪɢɴɪᴛᴇ "
        data["sudos"].remove(user_id)
        DRAGONS.remove(user_id)

    if user_id in DEMONS:
        rt += "ʏᴏᴜ ᴀʀᴇ ᴏᴜʀ ғʀɪᴇɴᴅ, ʙᴜᴛ it's ғᴏʀ ʏᴏᴜʀ ᴏᴡɴ ɢᴏᴏᴅ ɪғ ʏᴏᴜ ʙᴇᴄᴏᴍᴇ ᴀ ɪɢɴɪᴛᴇ ɪɴsᴛᴇᴀᴅ."
        data["supports"].remove(user_id)
        DEMONS.remove(user_id)

    if user_id in WOLVES:
        message.reply_text("ᴛʜɪs ᴜsᴇʀ ɪs ᴀʟʀᴇᴀᴅʏ ᴀ ᴛʀᴜᴇ ᴇxᴏɴ")
        return ""

    data["whitelists"].append(user_id)
    WOLVES.append(user_id)

    with open(ELEVATED_USERS_FILE, "w") as outfile:
        json.dump(data, outfile, indent=4)

    update.effective_message.reply_text(
        f"{rt}\nsᴜᴄᴄᴇssғᴜʟʟʏ ᴘʀᴏᴍᴏᴛᴇᴅ {user_member.first_name} ᴛᴏ ᴀ ʀᴀɴᴋᴇᴅ EXON!"
    )

    log_message = (
        f"#ᴡʜɪᴛᴇʟɪsᴛ\n"
        f"<b>ᴀᴅᴍɪɴ:</b> {mention_html(user.id, html.escape(user.first_name))} \n"
        f"<b>ᴜsᴇʀ:</b> {mention_html(user_member.id, html.escape(user_member.first_name))}"
    )

    if chat.type != "private":
        log_message = f"<b>{html.escape(chat.title)}:</b>\n{log_message}"

    return log_message


@sudo_plus
@gloggable
def addtiger(update: Update, context: CallbackContext) -> str:
    message = update.effective_message
    user = update.effective_user
    chat = update.effective_chat
    bot, args = context.bot, context.args
    user_id = extract_user(message, args)
    user_member = bot.getChat(user_id)
    rt = ""

    if reply := check_user_id(user_id, bot):
        message.reply_text(reply)
        return ""

    with open(ELEVATED_USERS_FILE, "r") as infile:
        data = json.load(infile)

    if user_id in DRAGONS:
        rt += "ʏᴏᴜ ᴡᴇʀᴇ ᴏᴜʀ ʙᴇsᴛᴏ ғʀɪᴇɴᴅᴏ, ʙᴜᴛ ɴᴏᴡ ʏᴏᴜ ᴀʀᴇ ᴊᴜsᴛ ᴀ ᴄʟᴀssᴍᴀᴛᴇ ᴛᴏ ᴜs ;("
        data["sudos"].remove(user_id)
        DRAGONS.remove(user_id)

    if user_id in DEMONS:
        rt += "Let's become classmates instead."
        data["supports"].remove(user_id)
        DEMONS.remove(user_id)

    if user_id in WOLVES:
        rt += "ᴛʜɪs ᴜsᴇʀ ɪs ᴀʟʀᴇᴀᴅʏ a ᴇxᴏɴ, ᴡᴇ ᴄᴀɴ ʙᴇ ᴄʟᴀssᴍᴀᴛᴇs ᴀs ᴡᴇʟʟ.."
        data["whitelists"].remove(user_id)
        WOLVES.remove(user_id)

    if user_id in TIGERS:
        message.reply_text("ᴛʜɪs ᴜsᴇʀ ɪs ᴀʟʀᴇᴀᴅʏ ᴏᴜʀ ᴄʟᴀssᴍᴀᴛᴇ.")
        return ""

    data["tigers"].append(user_id)
    TIGERS.append(user_id)

    with open(ELEVATED_USERS_FILE, "w") as outfile:
        json.dump(data, outfile, indent=4)

    update.effective_message.reply_text(
        f"{rt}\nʟᴇᴛ's ᴡᴇʟᴄᴏᴍᴇ ᴏᴜʀ ɴᴇᴡ ᴄʟᴀssᴍᴀᴛᴇ, {user_member.first_name}!"
    )

    log_message = (
        f"#sᴄᴏᴜᴛ\n"
        f"<b>ᴀᴅᴍɪɴ:</b> {mention_html(user.id, html.escape(user.first_name))} \n"
        f"<b>ᴜsᴇʀ:</b> {mention_html(user_member.id, html.escape(user_member.first_name))}"
    )

    if chat.type != "private":
        log_message = f"<b>{html.escape(chat.title)}:</b>\n{log_message}"

    return log_message


@dev_plus
@gloggable
def removesudo(update: Update, context: CallbackContext) -> str:
    message = update.effective_message
    user = update.effective_user
    chat = update.effective_chat
    bot, args = context.bot, context.args
    user_id = extract_user(message, args)
    user_member = bot.getChat(user_id)

    if reply := check_user_id(user_id, bot):
        message.reply_text(reply)
        return ""

    with open(ELEVATED_USERS_FILE, "r") as infile:
        data = json.load(infile)

    if user_id in DRAGONS:
        message.reply_text("ᴡᴇ ᴀʀᴇ ɴᴏ ᴍᴏʀᴇ ʙᴇsᴛ ғʀɪᴇɴᴅs ʜᴍᴘʜ!")
        DRAGONS.remove(user_id)
        data["sudos"].remove(user_id)

        with open(ELEVATED_USERS_FILE, "w") as outfile:
            json.dump(data, outfile, indent=4)

        log_message = (
            f"#ᴜɴsᴜᴅᴏ\n"
            f"<b>ᴀᴅᴍɪɴ:</b> {mention_html(user.id, html.escape(user.first_name))}\n"
            f"<b>ᴜsᴇʀ:</b> {mention_html(user_member.id, html.escape(user_member.first_name))}"
        )

        if chat.type != "private":
            log_message = f"<b>{html.escape(chat.title)}:</b>\n" + log_message

        return log_message
    message.reply_text(
        "ᴛʜɪs ᴜsᴇʀ ɪs ɴᴏᴛ ᴀ ᴏᴜʀ ʙᴇsᴛᴏ ғʀɪᴇɴᴅᴏ, ʏᴏᴜ ᴍᴜsᴛ ʜᴀᴠᴇ ᴍɪsᴜɴᴅᴇʀsᴛᴏᴏᴅ sᴇɴᴘᴀɪ!"
    )
    return ""


@sudo_plus
@gloggable
def removesupport(update: Update, context: CallbackContext) -> str:
    message = update.effective_message
    user = update.effective_user
    chat = update.effective_chat
    bot, args = context.bot, context.args
    user_id = extract_user(message, args)
    user_member = bot.getChat(user_id)

    if reply := check_user_id(user_id, bot):
        message.reply_text(reply)
        return ""

    with open(ELEVATED_USERS_FILE, "r") as infile:
        data = json.load(infile)

    if user_id in DEMONS:
        message.reply_text("ᴏᴜʀ ғʀɪᴇɴᴅsʜɪᴘ ʜᴀs ʙᴇᴇɴ ʙʀᴏᴋᴇɴ 💔")
        DEMONS.remove(user_id)
        data["supports"].remove(user_id)

        with open(ELEVATED_USERS_FILE, "w") as outfile:
            json.dump(data, outfile, indent=4)

        log_message = (
            f"#ᴜɴsᴜᴘᴘᴏʀᴛ\n"
            f"<b>ᴀᴅᴍɪɴ:</b> {mention_html(user.id, html.escape(user.first_name))}\n"
            f"<b>ᴜsᴇʀ:</b> {mention_html(user_member.id, html.escape(user_member.first_name))}"
        )

        if chat.type != "private":
            log_message = f"<b>{html.escape(chat.title)}:</b>\n{log_message}"

        return log_message
    message.reply_text("ᴛʜɪs ᴜsᴇʀ ɪs ɴᴏᴛ ᴏᴜʀ ғʀɪᴇɴᴅ, ʙᴀᴋᴀ ᴏɴɪᴄʜᴀɴ!")
    return ""


@sudo_plus
@gloggable
def removewhitelist(update: Update, context: CallbackContext) -> str:
    message = update.effective_message
    user = update.effective_user
    chat = update.effective_chat
    bot, args = context.bot, context.args
    user_id = extract_user(message, args)
    user_member = bot.getChat(user_id)

    if reply := check_user_id(user_id, bot):
        message.reply_text(reply)
        return ""

    with open(ELEVATED_USERS_FILE, "r") as infile:
        data = json.load(infile)

    if user_id in WOLVES:
        message.reply_text("ᴅᴇᴍᴏᴛɪɴɢ ᴛᴏ ɴᴏʀᴍᴀʟ ᴄɪᴛɪᴢᴇɴ")
        WOLVES.remove(user_id)
        data["whitelists"].remove(user_id)

        with open(ELEVATED_USERS_FILE, "w") as outfile:
            json.dump(data, outfile, indent=4)

        log_message = (
            f"#ᴜɴᴡʜɪᴛᴇʟɪsᴛ\n"
            f"<b>ᴀᴅᴍɪɴ:</b> {mention_html(user.id, html.escape(user.first_name))}\n"
            f"<b>ᴜsᴇʀ:</b> {mention_html(user_member.id, html.escape(user_member.first_name))}"
        )

        if chat.type != "private":
            log_message = f"<b>{html.escape(chat.title)}:</b>\n{log_message}"

        return log_message
    message.reply_text("ᴛʜɪs ᴜsᴇʀ ɪs ɴᴏᴛ ᴀ ᴇxᴏɴ!")
    return ""


@sudo_plus
@gloggable
def removetiger(update: Update, context: CallbackContext) -> str:
    message = update.effective_message
    user = update.effective_user
    chat = update.effective_chat
    bot, args = context.bot, context.args
    user_id = extract_user(message, args)
    user_member = bot.getChat(user_id)

    if reply := check_user_id(user_id, bot):
        message.reply_text(reply)
        return ""

    with open(ELEVATED_USERS_FILE, "r") as infile:
        data = json.load(infile)

    if user_id in TIGERS:
        message.reply_text("ᴅᴇᴍᴏᴛɪɴɢ ᴛᴏ ɴᴏʀᴍᴀʟ ᴄɪᴛɪᴢᴇɴ")
        TIGERS.remove(user_id)
        data["Tigers"].remove(user_id)

        with open(ELEVATED_USERS_FILE, "w") as outfile:
            json.dump(data, outfile, indent=4)

        log_message = (
            f"#ᴜɴsᴄᴏᴜᴛ\n"
            f"<b>ᴀᴅᴍɪɴ:</b> {mention_html(user.id, html.escape(user.first_name))}\n"
            f"<b>ᴜsᴇʀ:</b> {mention_html(user_member.id, html.escape(user_member.first_name))}"
        )

        if chat.type != "private":
            log_message = f"<b>{html.escape(chat.title)}:</b>\n{log_message}"

        return log_message
    message.reply_text("ᴛʜɪs ᴜsᴇʀ ɪs ɴᴏᴛ ᴏᴜʀ ᴄʟᴀssᴍᴀᴛᴇ!")
    return ""


@whitelist_plus
def whitelistlist(update: Update, context: CallbackContext):
    reply = "<b>ᴇxᴏɴ:</b>\n\n"
    m = update.effective_message.reply_text(
        "<code>ɢᴀᴛʜᴇʀɪɴɢ ɪɴᴛᴇʟ ғʀᴏᴍ ᴇxᴏɴ..</code>",
        parse_mode=ParseMode.HTML,
    )
    bot = context.bot
    for each_user in WOLVES:
        user_id = int(each_user)
        try:
            user = bot.get_chat(user_id)

            reply += f"• {mention_html(user_id, html.escape(user.first_name))}\n"
        except TelegramError:
            pass
    m.edit_text(reply, parse_mode=ParseMode.HTML)


@whitelist_plus
def tigerlist(update: Update, context: CallbackContext):
    reply = "<b>Classmates:</b>\n\n"
    m = update.effective_message.reply_text(
        "<code>ɢᴀᴛʜᴇʀɪɴɢ ɪɴᴛᴇʟ ғʀᴏᴍ ᴇxᴏɴ ɪǫ.</code>",
        parse_mode=ParseMode.HTML,
    )
    bot = context.bot
    for each_user in TIGERS:
        user_id = int(each_user)
        try:
            user = bot.get_chat(user_id)
            reply += f"• {mention_html(user_id, html.escape(user.first_name))}\n"
        except TelegramError:
            pass
    m.edit_text(reply, parse_mode=ParseMode.HTML)


@whitelist_plus
def supportlist(update: Update, context: CallbackContext):
    bot = context.bot
    m = update.effective_message.reply_text(
        "<code>ɢᴀᴛʜᴇʀɪɴɢ ɪɴᴛᴇʟ ғʀᴏᴍ .</code>",
        parse_mode=ParseMode.HTML,
    )
    reply = "<b>ғʀɪᴇɴᴅs:</b>\n\n"
    for each_user in DEMONS:
        user_id = int(each_user)
        try:
            user = bot.get_chat(user_id)
            reply += f"• {mention_html(user_id, html.escape(user.first_name))}\n"
        except TelegramError:
            pass
    m.edit_text(reply, parse_mode=ParseMode.HTML)


@whitelist_plus
def sudolist(update: Update, context: CallbackContext):
    bot = context.bot
    m = update.effective_message.reply_text(
        "<code>ɢᴀᴛʜᴇʀɪɴɢ ɪɴᴛᴇʟ ғʀᴏᴍ ᴇxᴏɴ ʜǫ.</code>",
        parse_mode=ParseMode.HTML,
    )
    true_sudo = list(set(DRAGONS) - set(DEV_USERS))
    reply = "<b>ʙᴇsᴛᴏ ғʀɪᴇɴᴅᴏs:</b>\n\n"
    for each_user in true_sudo:
        user_id = int(each_user)
        try:
            user = bot.get_chat(user_id)
            reply += f"• {mention_html(user_id, html.escape(user.first_name))}\n"
        except TelegramError:
            pass
    m.edit_text(reply, parse_mode=ParseMode.HTML)


@whitelist_plus
def devlist(update: Update, context: CallbackContext):
    bot = context.bot
    m = update.effective_message.reply_text(
        "<code>ɢᴀᴛʜᴇʀɪɴɢ ɪɴᴛᴇʟ ғʀᴏᴍ ᴀʙɪsʜɴᴏɪ HQ..</code>",
        parse_mode=ParseMode.HTML,
    )
    true_dev = list(set(DEV_USERS) - {OWNER_ID})
    reply = "<b>ғᴀᴍɪʟʏ ᴍᴇᴍʙᴇʀs:</b>\n\n"
    for each_user in true_dev:
        user_id = int(each_user)
        try:
            user = bot.get_chat(user_id)
            reply += f"• {mention_html(user_id, html.escape(user.first_name))}\n"
        except TelegramError:
            pass
    m.edit_text(reply, parse_mode=ParseMode.HTML)


SUDO_HANDLER = CommandHandler(("addsudo", "addbestfriend"), addsudo, run_async=True)
SUPPORT_HANDLER = CommandHandler(
    ("addsupport", "addfriend"), addsupport, run_async=True
)
TIGER_HANDLER = CommandHandler(("addclassmate"), addtiger)
WHITELIST_HANDLER = CommandHandler(
    ("EXON", "addwhitelist"), addwhitelist, run_async=True
)
UNSUDO_HANDLER = CommandHandler(
    ("removesudo", "rmbestfriend"), removesudo, run_async=True
)
UNSUPPORT_HANDLER = CommandHandler(
    ("removesupport", "rmfriend"), removesupport, run_async=True
)
UNTIGER_HANDLER = CommandHandler(("rmclassmate"), removetiger)
UNWHITELIST_HANDLER = CommandHandler(
    ("removewhitelist", "rmIGNITE"), removewhitelist, run_async=True
)
WHITELISTLIST_HANDLER = CommandHandler(
    ["whitelistlist", "EXONS"], whitelistlist, run_async=True
)
TIGERLIST_HANDLER = CommandHandler(["classmates"], tigerlist, run_async=True)
SUPPORTLIST_HANDLER = CommandHandler(
    ["supportlist", "friends"], supportlist, run_async=True
)
SUDOLIST_HANDLER = CommandHandler(["sudolist", "bestfriends"], sudolist, run_async=True)
DEVLIST_HANDLER = CommandHandler(["devlist", "devs"], devlist, run_async=True)


dispatcher.add_handler(SUDO_HANDLER)
dispatcher.add_handler(SUPPORT_HANDLER)
dispatcher.add_handler(TIGER_HANDLER)
dispatcher.add_handler(WHITELIST_HANDLER)
dispatcher.add_handler(UNSUDO_HANDLER)
dispatcher.add_handler(UNSUPPORT_HANDLER)
dispatcher.add_handler(UNTIGER_HANDLER)
dispatcher.add_handler(UNWHITELIST_HANDLER)
dispatcher.add_handler(WHITELISTLIST_HANDLER)
dispatcher.add_handler(TIGERLIST_HANDLER)
dispatcher.add_handler(SUPPORTLIST_HANDLER)
dispatcher.add_handler(SUDOLIST_HANDLER)
dispatcher.add_handler(DEVLIST_HANDLER)


__mod_name__ = "Bot Owner"

__handlers__ = [
    SUDO_HANDLER,
    SUPPORT_HANDLER,
    TIGER_HANDLER,
    WHITELIST_HANDLER,
    UNSUDO_HANDLER,
    UNSUPPORT_HANDLER,
    UNTIGER_HANDLER,
    UNWHITELIST_HANDLER,
    WHITELISTLIST_HANDLER,
    TIGERLIST_HANDLER,
    SUPPORTLIST_HANDLER,
    SUDOLIST_HANDLER,
    DEVLIST_HANDLER,
]
