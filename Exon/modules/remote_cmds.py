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

from telegram import ChatPermissions, Update
from telegram.error import BadRequest
from telegram.ext import CallbackContext, CommandHandler

from Exon import LOGGER, dispatcher
from Exon.modules.helper_funcs.chat_status import (
    bot_admin,
    is_bot_admin,
    is_user_ban_protected,
    is_user_in_chat,
)
from Exon.modules.helper_funcs.extraction import extract_user_and_text
from Exon.modules.helper_funcs.filters import CustomFilters

RBAN_ERRORS = {
    "ᴜsᴇʀ ɪs ᴀɴ ᴀᴅᴍɪɴɪsᴛʀᴀᴛᴏʀ ᴏғ ᴛʜᴇ ᴄʜᴀᴛ",
    "ᴄʜᴀᴛ not ғᴏᴜɴᴅ",
    "ɴᴏᴛ ᴇɴᴏᴜɢʜ ʀɪɢʜᴛs ᴛᴏ ʀᴇsᴛʀɪᴄᴛ/ᴜɴʀᴇsᴛʀɪᴄᴛ ᴄʜᴀᴛ ᴍᴇᴍʙᴇʀ",
    "User_not_participant",
    "Peer_id_invalid",
    "ɢʀᴏᴜᴘ ᴄʜᴀᴛ ᴡᴀs ᴅᴇᴀᴄᴛɪᴠᴀᴛᴇᴅ",
    "ɴᴇᴇᴅ ᴛᴏ ʙᴇ ɪɴᴠɪᴛᴇʀ ᴏғ ᴀ user ᴛᴏ ᴘᴜɴᴄʜ ɪᴛ ғʀᴏᴍ ᴀ ʙᴀsɪᴄ ɢʀᴏᴜᴘ",
    "Chat_admin_required",
    "ᴏɴʟʏ ᴛʜᴇ ᴄʀᴇᴀᴛᴏʀ ᴏғ ᴀ ʙᴀsɪᴄ ɢʀᴏᴜᴘ ᴄᴀɴ ᴘᴜɴᴄʜ ɢʀᴏᴜᴘ ᴀᴅᴍɪɴɪsᴛʀᴀᴛᴏʀs",
    "Channel_private",
    "ɴᴏᴛ ɪɴ ᴛʜᴇ ᴄʜᴀᴛ",
}

RUNBAN_ERRORS = {
    "User ɪs ᴀɴ ᴀᴅᴍɪɴɪsᴛʀᴀᴛᴏʀ ᴏғ ᴛʜᴇ ᴄʜᴀᴛ",
    "ᴄʜᴀᴛ ɴᴏᴛ ғᴏᴜɴᴅ",
    "ɴᴏᴛ ᴇɴᴏᴜɢʜ ʀɪɢʜᴛs ᴛᴏ ʀᴇsᴛʀɪᴄᴛ/ᴜɴʀᴇsᴛʀɪᴄᴛ ᴄʜᴀᴛ ᴍᴇᴍʙᴇʀ",
    "User_not_ᴘᴀʀᴛɪᴄɪᴘᴀɴᴛ",
    "Peer_id_invalid",
    "ɢʀᴏᴜᴘ ᴄʜᴀᴛ ᴡᴀs ᴅᴇᴀᴄᴛɪᴠᴀᴛᴇᴅ",
    "ɴᴇᴇᴅ ᴛᴏ ʙᴇ ɪɴᴠɪᴛᴇʀ ᴏғ ᴀ ᴜsᴇʀ ᴛᴏ ᴘᴜɴᴄʜ ɪᴛ ғʀᴏᴍ a ʙᴀsɪᴄ ɢʀᴏᴜᴘ",
    "Chat_admin_required",
    "ᴏɴʟʏ ᴛʜᴇ ᴄʀᴇᴀᴛᴏʀ ᴏғ ᴀ ʙᴀsɪᴄ ɢʀᴏᴜᴘ ᴄᴀɴ ᴘᴜɴᴄʜ ɢʀᴏᴜᴘ ᴀᴅᴍɪɴɪsᴛʀᴀᴛᴏʀs",
    "Channel_private",
    "ɴᴏᴛ ɪɴ ᴛʜᴇ ᴄʜᴀᴛ",
}

RKICK_ERRORS = {
    "ᴜsᴇʀ ɪs ᴀɴ ᴀᴅᴍɪɴɪsᴛʀᴀᴛᴏʀ ᴏғ ᴛʜᴇ ᴄʜᴀᴛ",
    "ᴄʜᴀᴛ ɴᴏᴛ ғᴏᴜɴᴅ",
    "ɴᴏᴛ ᴇɴᴏᴜɢʜ ʀɪɢʜᴛs ᴛᴏ ʀᴇsᴛʀɪᴄᴛ/ᴜɴʀᴇsᴛʀɪᴄᴛ ᴄʜᴀᴛ ᴍᴇᴍʙᴇʀ",
    "ᴜsᴇʀ_ɴᴏᴛ_ᴘᴀʀᴛɪᴄɪᴘᴀɴᴛ",
    "ᴘᴇᴇʀ_ɪᴅ_ɪɴᴠᴀʟɪᴅ",
    "ɢʀᴏᴜᴘ ᴄʜᴀᴛ ᴡᴀs ᴅᴇᴀᴄᴛɪᴠᴀᴛᴇᴅ",
    "ɴᴇᴇᴅ ᴛᴏ ʙᴇ ɪɴᴠɪᴛᴇʀ ᴏғ ᴀ ᴜsᴇʀ ᴛᴏ ᴘᴜɴᴄʜ ɪᴛ ғʀᴏᴍ ᴀ ʙᴀsɪᴄ ɢʀᴏᴜᴘ",
    "ᴄʜᴀᴛ_ᴀᴅᴍɪɴ_ʀᴇǫᴜɪʀᴇᴅ",
    "ᴏɴʟʏ ᴛʜᴇ ᴄʀᴇᴀᴛᴏʀ ᴏғ ᴀ ʙᴀsɪᴄ ɢʀᴏᴜᴘ ᴄᴀɴ ᴘᴜɴᴄʜ ɢʀᴏᴜᴘ ᴀᴅᴍɪɴɪsᴛʀᴀᴛᴏʀs",
    "Channel_ᴘʀɪᴠᴀᴛᴇ",
    "ɴᴏᴛ ɪɴ ᴛʜᴇ ᴄʜᴀᴛ",
}

RMUTE_ERRORS = {
    "ᴜsᴇʀ ɪs ᴀɴ ᴀᴅᴍɪɴɪsᴛʀᴀᴛᴏʀ ᴏғ ᴛʜᴇ ᴄʜᴀᴛ",
    "ᴄʜᴀᴛ ɴᴏᴛ ғᴏᴜɴᴅ",
    "ɴᴏᴛ ᴇɴᴏᴜɢʜ ʀɪɢʜᴛs ᴛᴏ ʀᴇsᴛʀɪᴄᴛ/ᴜɴʀᴇsᴛʀɪᴄᴛ ᴄʜᴀᴛ ᴍᴇᴍʙᴇʀ",
    "ᴜsᴇʀ_ɴᴏᴛ_ᴘᴀʀᴛɪᴄɪᴘᴀɴᴛ",
    "ᴘᴇᴇʀ_ɪᴅ_ɪɴᴠᴀʟɪᴅ",
    "ɢʀᴏᴜᴘ ᴄʜᴀᴛ ᴡᴀs ᴅᴇᴀᴄᴛɪᴠᴀᴛᴇᴅ",
    "ɴᴇᴇᴅ ᴛᴏ ʙᴇ ɪɴᴠɪᴛᴇʀ ᴏғ ᴀ ᴜsᴇʀ ᴛᴏ ᴘᴜɴᴄʜ ɪᴛ ғʀᴏᴍ ᴀ ʙᴀsɪᴄ ɢʀᴏᴜᴘ",
    "ᴄʜᴀᴛ_ᴀᴅᴍɪɴ_ʀᴇǫᴜɪʀᴇᴅ",
    "ᴏɴʟʏ ᴛʜᴇ ᴄʀᴇᴀᴛᴏʀ ᴏғ ᴀ ʙᴀsɪᴄ ɢʀᴏᴜᴘ ᴄᴀɴ ᴘᴜɴᴄʜ ɢʀᴏᴜᴘ ᴀᴅᴍɪɴɪsᴛʀᴀᴛᴏʀs",
    "ᴄʜᴀɴɴᴇʟ_ᴘʀɪᴠᴀᴛᴇ",
    "ɴᴏᴛ ɪɴ ᴛʜᴇ ᴄʜᴀᴛ",
}

RUNMUTE_ERRORS = {
    "User is an administrator of the chat",
    "Chat not found",
    "Not enough rights to restrict/unrestrict chat member",
    "User_not_participant",
    "Peer_id_invalid",
    "Group chat was deactivated",
    "Need to be inviter of a user to punch it from a basic group",
    "Chat_admin_required",
    "Only the creator of a basic group can punch group administrators",
    "Channel_private",
    "Not in the chat",
}


@bot_admin
def rban(update: Update, context: CallbackContext):
    bot, args = context.bot, context.args
    message = update.effective_message

    if not args:
        message.reply_text("ʏᴏᴜ ᴅᴏɴ'ᴛ sᴇᴇᴍ ᴛᴏ ʙᴇ ʀᴇғᴇʀʀɪɴɢ ᴛᴏ a ᴄʜᴀᴛ/ᴜsᴇʀ.")
        return

    user_id, chat_id = extract_user_and_text(message, args)

    if not user_id:
        message.reply_text(
            "ʏᴏᴜ ᴅᴏɴ'ᴛ sᴇᴇᴍ ᴛᴏ ʙᴇ ʀᴇғᴇʀʀɪɴɢ ᴛᴏ ᴀ ᴜsᴇʀ ᴏʀ ᴛʜᴇ ɪᴅ sᴘᴇᴄɪғɪᴇᴅ ɪs ɪɴᴄᴏʀʀᴇᴄᴛ..",
        )
        return
    if not chat_id:
        message.reply_text("ʏᴏᴜ ᴅᴏɴ'ᴛ sᴇᴇᴍ ᴛᴏ ʙᴇ ʀᴇғᴇʀʀɪɴɢ ᴛᴏ ᴀ ᴄʜᴀᴛ.")
        return

    try:
        chat = bot.get_chat(chat_id.split()[0])
    except BadRequest as excp:
        if excp.message == "ᴄʜᴀᴛ ɴᴏᴛ ғᴏᴜɴᴅ":
            message.reply_text(
                "ᴄʜᴀᴛ ɴᴏᴛ ғᴏᴜɴᴅ! ᴍᴀᴋᴇ sᴜʀᴇ ʏᴏᴜ ᴇɴᴛᴇʀᴇᴅ ᴀ ᴠᴀʟɪᴅ ᴄʜᴀᴛ ID ᴀɴᴅ I'm ᴘᴀʀᴛ ᴏғ ᴛʜᴀᴛ ᴄʜᴀᴛ.",
            )
            return
        raise

    if chat.type == "private":
        message.reply_text("I'ᴍ sᴏʀʀʏ, ʙᴜᴛ ᴛʜᴀᴛ ᴀ ᴘʀɪᴠᴀᴛᴇ ᴄʜᴀᴛ!")
        return

    if (
        not is_bot_admin(chat, bot.id)
        or not chat.get_member(bot.id).can_restrict_members
    ):
        message.reply_text(
            "I ᴄᴀɴ'ᴛ ʀᴇsᴛʀɪᴄᴛ ᴘᴇᴏᴘʟᴇ ᴛʜᴇʀᴇ! ᴍᴀᴋᴇ sᴜʀᴇ I'ᴍ ᴀᴅᴍɪɴ ᴀɴᴅ ᴄᴀɴ ʙᴀɴ ᴜsᴇʀs.",
        )
        return

    try:
        member = chat.get_member(user_id)
    except BadRequest as excp:
        if excp.message == "ᴜsᴇʀ ɴᴏᴛ ғᴏᴜɴᴅ":
            message.reply_text("ɪ ᴄᴀɴ'ᴛ sᴇᴇᴍ ᴛᴏ ғɪɴᴅ ᴛʜɪs ᴜsᴇʀ")
            return
        raise

    if is_user_ban_protected(chat, user_id, member):
        message.reply_text("I ʀᴇᴀʟʟʏ ᴡɪsʜ I ᴄᴏᴜʟᴅ ʙᴀɴ ᴀᴅᴍɪɴs...")
        return

    if user_id == bot.id:
        message.reply_text("I'm ɴᴏᴛ ɢᴏɴɴᴀ ʙᴀɴ ᴍʏsᴇʟғ, ᴀʀᴇ ʏᴏᴜ ᴄʀᴀᴢʏ?")
        return

    try:
        chat.ban_member(user_id)
        message.reply_text("ʙᴀɴɴᴇᴅ ғʀᴏᴍ chat!")
    except BadRequest as excp:
        if excp.message == "ʀᴇᴘʟʏ ᴍᴇssᴀɢᴇ ɴᴏᴛ ғᴏᴜɴᴅ":
            # Do not reply
            message.reply_text("Banned!", quote=False)
        elif excp.message in RBAN_ERRORS:
            message.reply_text(excp.message)
        else:
            LOGGER.warning(update)
            LOGGER.exception(
                "ᴇʀʀᴏʀ ʙᴀɴɴɪɴɢ ᴜsᴇʀ %s ɪɴ ᴄʜᴀᴛ %s (%s) ᴅᴜᴇ ᴛᴏ %s",
                user_id,
                chat.title,
                chat.id,
                excp.message,
            )
            message.reply_text("ᴡᴇʟʟ ᴅᴀᴍɴ, I ᴄᴀɴ'ᴛ ʙᴀɴ ᴛʜᴀᴛ ᴜsᴇʀ.")


@bot_admin
def runban(update: Update, context: CallbackContext):
    bot, args = context.bot, context.args
    message = update.effective_message

    if not args:
        message.reply_text("ʏᴏᴜ ᴅᴏɴ'ᴛ sᴇᴇᴍ ᴛᴏ ʙᴇ ʀᴇғᴇʀʀɪɴɢ ᴛᴏ a ᴄʜᴀᴛ/ᴜsᴇʀ.")
        return

    user_id, chat_id = extract_user_and_text(message, args)

    if not user_id:
        message.reply_text(
            "ʏᴏᴜ ᴅᴏɴ'ᴛ sᴇᴇᴍ ᴛᴏ ʙᴇ ʀᴇғᴇʀʀɪɴɢ ᴛᴏ ᴀ ᴜsᴇʀ ᴏʀ ᴛʜᴇ ɪᴅ sᴘᴇᴄɪғɪᴇᴅ ɪs ɪɴᴄᴏʀʀᴇᴄᴛ..",
        )
        return
    if not chat_id:
        message.reply_text("ʏᴏᴜ ᴅᴏɴ'ᴛ sᴇᴇᴍ ᴛᴏ ʙᴇ ʀᴇғᴇʀʀɪɴɢ ᴛᴏ ᴀ ᴄʜᴀᴛ.")
        return

    try:
        chat = bot.get_chat(chat_id.split()[0])
    except BadRequest as excp:
        if excp.message == "Chat not found":
            message.reply_text(
                "ᴄʜᴀᴛ ɴᴏᴛ ғᴏᴜɴᴅ! ᴍᴀᴋᴇ sᴜʀᴇ ʏᴏᴜ ᴇɴᴛᴇʀᴇᴅ ᴀ ᴠᴀʟɪᴅ ᴄʜᴀᴛ ɪᴅ ᴀɴᴅ I'ᴍ ᴘᴀʀᴛ ᴏғ ᴛʜᴀᴛ ᴄʜᴀᴛ.",
            )
            return
        raise

    if chat.type == "private":
        message.reply_text("I'ᴍ sᴏʀʀʏ, ʙᴜᴛ ᴛʜᴀᴛ's ᴀ ᴘʀɪᴠᴀᴛᴇ ᴄʜᴀᴛ!")
        return

    if (
        not is_bot_admin(chat, bot.id)
        or not chat.get_member(bot.id).can_restrict_members
    ):
        message.reply_text(
            "I ᴄᴀɴ'ᴛ ᴜɴʀᴇsᴛʀɪᴄᴛ ᴘᴇᴏᴘʟᴇ ᴛʜᴇʀᴇ! ᴍᴀᴋᴇ sᴜʀᴇ I'm ᴀᴅᴍɪɴ ᴀɴᴅ ᴄᴀɴ ᴜɴʙᴀɴ ᴜsᴇʀs.",
        )
        return

    try:
        chat.get_member(user_id)
    except BadRequest as excp:
        if excp.message == "ᴜsᴇʀ ɴᴏᴛ ғᴏᴜɴᴅ":
            message.reply_text("I ᴄᴀɴ'ᴛ sᴇᴇᴍ ᴛᴏ ғɪɴᴅ ᴛʜɪs ᴜsᴇʀ ᴛʜᴇʀᴇ")
            return
        raise

    if is_user_in_chat(chat, user_id):
        message.reply_text(
            "ᴡʜʏ ᴀʀᴇ ʏᴏᴜ ᴛʀʏɪɴɢ ᴛᴏ ʀᴇᴍᴏᴛᴇʟʏ ᴜɴʙᴀɴ sᴏᴍᴇᴏɴᴇ ᴛʜᴀᴛ's ᴀʟʀᴇᴀᴅʏ ɪɴ thʏat ᴄʜᴀᴛ?",
        )
        return

    if user_id == bot.id:
        message.reply_text("I'm not ɢᴏɴɴᴀ UNBAN ᴍʏsᴇʟғ, I'm ᴀɴ ᴀᴅᴍɪɴ ᴛʜᴇʀᴇ!")
        return

    try:
        chat.unban_member(user_id)
        message.reply_text("ʏᴇᴘ, ᴛʜɪs ᴜsᴇʀ ᴄᴀɴ ᴊᴏɪɴ ᴛʜᴀᴛ ᴄʜᴀᴛ!")
    except BadRequest as excp:
        if excp.message == "ʀᴇᴘʟʏ ᴍᴇssᴀɢᴇ ɴᴏᴛ ғᴏᴜɴᴅ":
            # Do not reply
            message.reply_text("Unbanned!", quote=False)
        elif excp.message in RUNBAN_ERRORS:
            message.reply_text(excp.message)
        else:
            LOGGER.warning(update)
            LOGGER.exception(
                "ERROR ᴜɴʙᴀɴɴɪɴɢ ᴜsᴇʀ %s ɪɴ ᴄʜᴀᴛ %s (%s) ᴅᴜᴇ ᴛᴏ %s",
                user_id,
                chat.title,
                chat.id,
                excp.message,
            )
            message.reply_text("ᴡᴇʟʟ ᴅᴀᴍɴ, I ᴄᴀɴ'ᴛ ᴜɴʙᴀɴ ᴛʜᴀᴛ ᴜsᴇʀ.")


@bot_admin
def rkick(update: Update, context: CallbackContext):
    bot, args = context.bot, context.args
    message = update.effective_message

    if not args:
        message.reply_text("ʏᴏᴜ ᴅᴏɴ'ᴛ sᴇᴇᴍ ᴛᴏ ʙᴇ ʀᴇғᴇʀʀɪɴɢ ᴛᴏ ᴀ ᴄʜᴀᴛ/ᴜsᴇʀ.")
        return

    user_id, chat_id = extract_user_and_text(message, args)

    if not user_id:
        message.reply_text(
            "ʏᴏᴜ ᴅᴏɴ'ᴛ sᴇᴇᴍ ᴛᴏ ʙᴇ ʀᴇғᴇʀʀɪɴɢ ᴛᴏ ᴀ ᴜsᴇʀ ᴏʀ ᴛʜᴇ ɪᴅ sᴘᴇᴄɪғɪᴇᴅ ɪs ɪɴᴄᴏʀʀᴇᴄᴛ..",
        )
        return
    if not chat_id:
        message.reply_text("ʏᴏᴜ ᴅᴏɴ'ᴛ sᴇᴇᴍ ᴛᴏ ʙᴇ ʀᴇғᴇʀʀɪɴɢ ᴛᴏ a ᴄʜᴀᴛ.")
        return

    try:
        chat = bot.get_chat(chat_id.split()[0])
    except BadRequest as excp:
        if excp.message == "ᴄʜᴀᴛ ɴᴏᴛ ғᴏᴜɴᴅ":
            message.reply_text(
                "ᴄʜᴀᴛ ɴᴏᴛ ғᴏᴜɴᴅ! ᴍᴀᴋᴇ sᴜʀᴇ ʏᴏᴜ ᴇɴᴛᴇʀᴇᴅ ᴀ ᴠᴀʟɪᴅ ᴄʜᴀᴛ ɪᴅ ᴀɴᴅ I'ᴍ ᴘᴀʀᴛ ᴏғ ᴛʜᴀᴛ ᴄʜᴀᴛ.",
            )
            return
        raise

    if chat.type == "private":
        message.reply_text("I'ᴍ sᴏʀʀʏ, ʙᴜᴛ ᴛʜᴀᴛ's a ᴘʀɪᴠᴀᴛᴇ ᴄʜᴀᴛ!")
        return

    if (
        not is_bot_admin(chat, bot.id)
        or not chat.get_member(bot.id).can_restrict_members
    ):
        message.reply_text(
            "I ᴄᴀɴ'ᴛ ʀᴇsᴛʀɪᴄᴛ ᴘᴇᴏᴘʟᴇ ᴛʜᴇʀᴇ! ᴍᴀᴋᴇ sᴜʀᴇ I'ᴍ ᴀᴅᴍɪɴ ᴀɴᴅ ᴄᴀɴ ᴘᴜɴᴄʜ ᴜsᴇʀs.",
        )
        return

    try:
        member = chat.get_member(user_id)
    except BadRequest as excp:
        if excp.message == "ᴜsᴇʀ ɴᴏᴛ ғᴏᴜɴᴅ":
            message.reply_text("I ᴄᴀɴ'ᴛ sᴇᴇᴍ ᴛᴏ ғɪɴᴅ ᴛʜɪs ᴜsᴇʀ")
            return
        raise

    if is_user_ban_protected(chat, user_id, member):
        message.reply_text("I really wish I could punch admins...")
        return

    if user_id == bot.id:
        message.reply_text("I'ᴍ ɴᴏᴛ ɢᴏɴɴᴀ ᴘᴜɴᴄʜ ᴍʏsᴇʟғ, ᴀʀᴇ ʏᴏᴜ ᴄʀᴀᴢʏ?")
        return

    try:
        chat.unban_member(user_id)
        message.reply_text("ᴘᴜɴᴄʜᴇᴅ ғʀᴏᴍ ᴄʜᴀᴛ!")
    except BadRequest as excp:
        if excp.message == "ʀᴇᴘʟʏ ᴍᴇssᴀɢᴇ ɴᴏᴛ ғᴏᴜɴᴅ":
            # Do not reply
            message.reply_text("ᴘᴜɴᴄʜᴇᴅ !", quote=False)
        elif excp.message in RKICK_ERRORS:
            message.reply_text(excp.message)
        else:
            LOGGER.warning(update)
            LOGGER.exception(
                "ERROR ᴘᴜɴᴄʜɪɴɢ ᴜsᴇʀ %s ɪɴ ᴄʜᴀᴛ %s (%s) ᴅᴜᴇ ᴛᴏ %s",
                user_id,
                chat.title,
                chat.id,
                excp.message,
            )
            message.reply_text("ᴡᴇʟʟ ᴅᴀᴍɴ, I ᴄᴀɴ'ᴛ ᴘᴜɴᴄʜ ᴛʜᴀᴛ ᴜsᴇʀ.")


@bot_admin
def rmute(update: Update, context: CallbackContext):
    bot, args = context.bot, context.args
    message = update.effective_message

    if not args:
        message.reply_text("ʏᴏᴜ ᴅᴏɴ'ᴛ sᴇᴇᴍ ᴛᴏ ʙᴇ ʀᴇғᴇʀʀɪɴɢ ᴛᴏ ᴀ ᴄʜᴀᴛ/ᴜsᴇʀ.")
        return

    user_id, chat_id = extract_user_and_text(message, args)

    if not user_id:
        message.reply_text(
            "You don't sᴇᴇᴍ to ʙᴇ ʀᴇғᴇʀʀɪɴɢ to ᴀ ᴜsᴇʀ ᴏʀ ᴛʜᴇ ɪᴅ sᴘᴇᴄɪғɪᴇᴅ is ɪɴᴄᴏʀʀᴇᴄᴛ..",
        )
        return
    if not chat_id:
        message.reply_text("You don't seem to be referring to a chat.")
        return

    try:
        chat = bot.get_chat(chat_id.split()[0])
    except BadRequest as excp:
        if excp.message == "Chat not found":
            message.reply_text(
                "Chat not found! Make sure you entered a valid chat ID and I'm part of that chat.",
            )
            return
        raise

    if chat.type == "private":
        message.reply_text("I'm sorry, but that's a private chat!")
        return

    if (
        not is_bot_admin(chat, bot.id)
        or not chat.get_member(bot.id).can_restrict_members
    ):
        message.reply_text(
            "I can't restrict people there! Make sure I'm admin and can mute users.",
        )
        return

    try:
        member = chat.get_member(user_id)
    except BadRequest as excp:
        if excp.message == "User not found":
            message.reply_text("I can't seem to find this user")
            return
        raise

    if is_user_ban_protected(chat, user_id, member):
        message.reply_text("I really wish I could mute admins...")
        return

    if user_id == bot.id:
        message.reply_text("I'm not gonna MUTE myself, are you crazy?")
        return

    try:
        bot.restrict_chat_member(
            chat.id,
            user_id,
            permissions=ChatPermissions(can_send_messages=False),
        )
        message.reply_text("Muted from the chat!")
    except BadRequest as excp:
        if excp.message == "Reply message not found":
            # Do not reply
            message.reply_text("Muted!", quote=False)
        elif excp.message in RMUTE_ERRORS:
            message.reply_text(excp.message)
        else:
            LOGGER.warning(update)
            LOGGER.exception(
                "ERROR mute user %s in chat %s (%s) due to %s",
                user_id,
                chat.title,
                chat.id,
                excp.message,
            )
            message.reply_text("Well damn, I can't mute that user.")


@bot_admin
def runmute(update: Update, context: CallbackContext):
    bot, args = context.bot, context.args
    message = update.effective_message

    if not args:
        message.reply_text("You don't seem to be referring to a chat/user.")
        return

    user_id, chat_id = extract_user_and_text(message, args)

    if not user_id:
        message.reply_text(
            "You don't seem to be referring to a user or the ID specified is incorrect..",
        )
        return
    if not chat_id:
        message.reply_text("You don't seem to be referring to a chat.")
        return

    try:
        chat = bot.get_chat(chat_id.split()[0])
    except BadRequest as excp:
        if excp.message == "Chat not found":
            message.reply_text(
                "Chat not found! Make sure you entered a valid chat ID and I'm part of that chat.",
            )
            return
        raise

    if chat.type == "private":
        message.reply_text("I'm sorry, but that's a private chat!")
        return

    if (
        not is_bot_admin(chat, bot.id)
        or not chat.get_member(bot.id).can_restrict_members
    ):
        message.reply_text(
            "I can't unrestrict people there! Make sure I'm admin and can unban users.",
        )
        return

    try:
        member = chat.get_member(user_id)
    except BadRequest as excp:
        if excp.message == "User not found":
            message.reply_text("I can't seem to find this user there")
            return
        raise

    if is_user_in_chat(chat, user_id) and (
        member.can_send_messages
        and member.can_send_media_messages
        and member.can_send_other_messages
        and member.can_add_web_page_previews
    ):
        message.reply_text("This user already has the right to speak in that chat.")
        return

    if user_id == bot.id:
        message.reply_text("I'm not gonna UNMUTE myself, I'm an admin there!")
        return

    try:
        bot.restrict_chat_member(
            chat.id,
            int(user_id),
            permissions=ChatPermissions(
                can_send_messages=True,
                can_send_media_messages=True,
                can_send_other_messages=True,
                can_add_web_page_previews=True,
            ),
        )
        message.reply_text("ʏᴇᴘ, ᴛʜɪs ᴜsᴇʀ ᴄᴀɴ ᴛᴀʟᴋ ɪɴ ᴛʜᴀᴛ ᴄʜᴀᴛ!")
    except BadRequest as excp:
        if excp.message == "ʀᴇᴘʟʏ ᴍᴇssᴀɢᴇ ɴᴏᴛ ғᴏᴜɴᴅ":
            # Do not reply
            message.reply_text("Unmuted!", quote=False)
        elif excp.message in RUNMUTE_ERRORS:
            message.reply_text(excp.message)
        else:
            LOGGER.warning(update)
            LOGGER.exception(
                "ERROR ᴜɴᴍɴᴜᴛɪɴɢ ᴜsᴇʀ %s ɪɴ ᴄʜᴀᴛ %s (%s) ᴅᴜᴇ ᴛᴏ %s",
                user_id,
                chat.title,
                chat.id,
                excp.message,
            )
            message.reply_text("ᴡᴇʟʟ ᴅᴀᴍɴ, I ᴄᴀɴ'ᴛ ᴜɴᴍᴜᴛᴇ ᴛʜᴀᴛ ᴜsᴇʀ.")


RBAN_HANDLER = CommandHandler(
    "rban", rban, filters=CustomFilters.sudo_filter, run_async=True
)
RUNBAN_HANDLER = CommandHandler(
    "runban", runban, filters=CustomFilters.sudo_filter, run_async=True
)
RKICK_HANDLER = CommandHandler(
    "rpunch", rkick, filters=CustomFilters.sudo_filter, run_async=True
)
RMUTE_HANDLER = CommandHandler(
    "rmute", rmute, filters=CustomFilters.sudo_filter, run_async=True
)
RUNMUTE_HANDLER = CommandHandler(
    "runmute", runmute, filters=CustomFilters.sudo_filter, run_async=True
)

dispatcher.add_handler(RBAN_HANDLER)
dispatcher.add_handler(RUNBAN_HANDLER)
dispatcher.add_handler(RKICK_HANDLER)
dispatcher.add_handler(RMUTE_HANDLER)
dispatcher.add_handler(RUNMUTE_HANDLER)
