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
import asyncio
import html
import os
from typing import Optional

from pyrogram import enums, filters
from pyrogram.enums import ChatMemberStatus
from pyrogram.errors import FloodWait
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode, Update, User
from telegram.error import BadRequest
from telegram.ext import CallbackContext, CommandHandler, Filters
from telegram.utils.helpers import mention_html
from telethon import *
from telethon import events
from telethon.tl import *
from telethon.tl import functions, types

from Exon import Abishnoi, dispatcher
from Exon import telethn as bot
from Exon.modules.connection import connected
from Exon.modules.disable import DisableAbleCommandHandler
from Exon.modules.helper_funcs.alternate import typing_action
from Exon.modules.helper_funcs.chat_status import (
    ADMIN_CACHE,
    bot_admin,
    can_pin,
    can_promote,
    connection_status,
    user_admin,
    user_can_changeinfo,
    user_can_promote,
)
from Exon.modules.helper_funcs.extraction import extract_user, extract_user_and_text
from Exon.modules.log_channel import loggable


async def is_register_admin(chat, user):
    if isinstance(chat, (types.InputPeerChannel, types.InputChannel)):
        return isinstance(
            (
                await bot(functions.channels.GetParticipantRequest(chat, user))
            ).participant,
            (types.ChannelParticipantAdmin, types.ChannelParticipantCreator),
        )
    if isinstance(chat, types.InputPeerUser):
        return True


async def can_promote_users(message):
    result = await bot(
        functions.channels.GetParticipantRequest(
            channel=message.chat_id,
            user_id=message.sender_id,
        )
    )
    p = result.participant
    return isinstance(p, types.ChannelParticipantCreator) or (
        isinstance(p, types.ChannelParticipantAdmin) and p.admin_rights.ban_users
    )


async def can_ban_users(message):
    result = await bot(
        functions.channels.GetParticipantRequest(
            channel=message.chat_id,
            user_id=message.sender_id,
        )
    )
    p = result.participant
    return isinstance(p, types.ChannelParticipantCreator) or (
        isinstance(p, types.ChannelParticipantAdmin) and p.admin_rights.ban_users
    )


@bot.on(events.NewMessage(pattern="/users$"))
async def get_users(show):
    if not show.is_group:
        return
    if show.is_group and not await is_register_admin(show.input_chat, show.sender_id):
        return
    info = await bot.get_entity(show.chat_id)
    title = info.title if info.title else "this chat"
    mentions = "ᴜsᴇʀs ɪɴ {}: \n".format(title)
    async for user in bot.iter_participants(show.chat_id):
        if not user.deleted:
            mentions += f"\n[{user.first_name}](tg://user?id={user.id}) {user.id}"
        else:
            mentions += f"\nᴅᴇʟᴇᴛᴇᴅ ᴀᴄᴄᴏᴜɴᴛ {user.id}"
    file = open("userslist.txt", "w+")
    file.write(mentions)
    file.close()
    await bot.send_file(
        show.chat_id,
        "userslist.txt",
        caption="ᴜsᴇʀs ɪɴ {}".format(title),
        reply_to=show.id,
    )
    os.remove("userslist.txt")


@bot_admin
@user_admin
def set_sticker(update: Update, context: CallbackContext):
    msg = update.effective_message
    chat = update.effective_chat
    user = update.effective_user

    if user_can_changeinfo(chat, user, context.bot.id) is False:
        return msg.reply_text("ʏᴏᴜ'ʀᴇ ᴍɪssɪɴɢ ʀɪɢʜᴛs ᴛᴏ ᴄʜᴀɴɢᴇ ᴄʜᴀᴛ ɪɴғᴏ!")

    if msg.reply_to_message:
        if not msg.reply_to_message.sticker:
            return msg.reply_text(
                "ʏᴏᴜ ɴᴇᴇᴅ ᴛᴏ ʀᴇᴘʟʏ ᴛᴏ sᴏᴍᴇ sᴛɪᴄᴋᴇʀ ᴛᴏ sᴇᴛ ᴄʜᴀᴛ sᴛɪᴄᴋᴇʀ sᴇᴛ!"
            )
        stkr = msg.reply_to_message.sticker.set_name
        try:
            context.bot.set_chat_sticker_set(chat.id, stkr)
            msg.reply_text(f"sᴜᴄᴄᴇssғᴜʟʟʏ sᴇᴛ ɴᴇᴡ ɢʀᴏᴜᴘ sᴛɪᴄᴋᴇʀs ɪɴ {chat.title}!")
        except BadRequest as excp:
            if excp.message == "Participants_too_few":
                return msg.reply_text(
                    "sᴏʀʀʏ, ᴅᴜᴇ ᴛᴏ ᴛᴇʟᴇɢʀᴀᴍ ʀᴇsᴛʀɪᴄᴛɪᴏɴs ᴄʜᴀᴛ ɴᴇᴇᴅs ᴛᴏ ʜᴀᴠᴇ ᴍɪɴɪᴍᴜᴍ 100 ᴍᴇᴍʙᴇʀs ʙᴇғᴏʀᴇ ᴛʜᴇʏ ᴄᴀɴ ʜᴀᴠᴇ ɢʀᴏᴜᴘ sᴛɪᴄᴋᴇʀs!"
                )
            msg.reply_text(f"ᴇʀʀᴏʀ! {excp.message}.")
    else:
        msg.reply_text("ʏᴏᴜ ɴᴇᴇᴅ ᴛᴏ ʀᴇᴘʟʏ ᴛᴏ sᴏᴍᴇ sᴛɪᴄᴋᴇʀ ᴛᴏ sᴇᴛ ᴄʜᴀᴛ sᴛɪᴄᴋᴇʀ sᴇᴛ!")


@bot_admin
@user_admin
def setchatpic(update: Update, context: CallbackContext):
    chat = update.effective_chat
    msg = update.effective_message
    user = update.effective_user

    if user_can_changeinfo(chat, user, context.bot.id) is False:
        msg.reply_text("ʏᴏᴜ ᴀʀᴇ ᴍɪssɪɴɢ ʀɪɢʜᴛ ᴛᴏ ᴄʜᴀɴɢᴇ ɢʀᴏᴜᴘ ɪɴғᴏ!")
        ʀᴇᴛᴜʀɴ

    if msg.reply_to_message:
        if msg.reply_to_message.photo:
            pic_id = msg.reply_to_message.photo[-1].file_id
        elif msg.reply_to_message.document:
            pic_id = msg.reply_to_message.document.file_id
        else:
            msg.reply_text("ʏᴏᴜ ᴄᴀɴ ᴏɴʟʏ sᴇᴛ sᴏᴍᴇ ᴘʜᴏᴛᴏ ᴀs ᴄʜᴀᴛ ᴘɪᴄ!")
            return
        dlmsg = msg.reply_text("ᴊᴜsᴛ ᴀ sᴇᴄ......")
        tpic = context.bot.get_file(pic_id)
        tpic.download("gpic.png")
        try:
            with open("gpic.png", "rb") as chatp:
                context.bot.set_chat_photo(int(chat.id), photo=chatp)
                msg.reply_text("sᴜᴄᴄᴇssғᴜʟʟʏ sᴇᴛ ɴᴇᴡ ᴄʜᴀᴛᴘɪᴄ!")
        except BadRequest as excp:
            msg.reply_text(f"ᴇʀʀᴏʀ! {excp.message}")
        finally:
            dlmsg.delete()
            if os.path.isfile("gpic.png"):
                os.remove("gpic.png")
    else:
        msg.reply_text("ʀᴇᴘʟʏ ᴛᴏ sᴏᴍᴇ ᴘʜᴏᴛᴏ ᴏʀ ғɪʟᴇ ᴛᴏ sᴇᴛ ɴᴇᴡ ᴄʜᴀᴛ ᴘɪᴄ!")


@bot_admin
@user_admin
def rmchatpic(update: Update, context: CallbackContext):
    chat = update.effective_chat
    msg = update.effective_message
    user = update.effective_user

    if user_can_changeinfo(chat, user, context.bot.id) is False:
        msg.reply_text("ʏᴏᴜ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ ᴇɴᴏᴜɢʜ ʀɪɢʜᴛs ᴛᴏ ᴅᴇʟᴇᴛᴇ ɢʀᴏᴜᴘ ᴘʜᴏᴛᴏ")
        return
    try:
        context.bot.delete_chat_photo(int(chat.id))
        msg.reply_text("sᴜᴄᴄᴇssғᴜʟʟʏ ᴅᴇʟᴇᴛᴇᴅ ᴄʜᴀᴛ's ᴘʀᴏғɪʟᴇ ᴘʜᴏᴛᴏ!")
    except BadRequest as excp:
        msg.reply_text(f"ᴇʀʀᴏʀ! {excp.message}.")
        return


@bot_admin
@user_admin
def set_desc(update: Update, context: CallbackContext):
    msg = update.effective_message
    chat = update.effective_chat
    user = update.effective_user

    if user_can_changeinfo(chat, user, context.bot.id) is False:
        return msg.reply_text("ʏᴏᴜ'ʀᴇ ᴍɪssɪɴɢ ʀɪɢʜᴛs ᴛᴏ ᴄʜᴀɴɢᴇ ᴄʜᴀᴛ ɪɴғᴏ!")

    tesc = msg.text.split(None, 1)
    if len(tesc) >= 2:
        desc = tesc[1]
    else:
        return msg.reply_text("sᴇᴛᴛɪɴɢ ᴇᴍᴘᴛʏ ᴅᴇsᴄʀɪᴘᴛɪᴏɴ ᴡᴏɴ'ᴛ ᴅᴏ ᴀɴʏᴛʜɪɴɢ!")
    try:
        if len(desc) > 255:
            return msg.reply_text("ᴅᴇsᴄʀɪᴘᴛɪᴏɴ ᴍᴜsᴛ ɴᴇᴇᴅs ᴛᴏ ʙᴇ ᴜɴᴅᴇʀ 255 ᴄʜᴀʀᴀᴄᴛᴇʀs!")
        context.bot.set_chat_description(chat.id, desc)
        msg.reply_text(f"sᴜᴄᴄᴇssғᴜʟʟʏ ᴜᴘᴅᴀᴛᴇᴅ ᴄʜᴀᴛ ᴅᴇsᴄʀɪᴘᴛɪᴏɴ ɪɴ {chat.title}!")
    except BadRequest as excp:
        msg.reply_text(f"ᴇʀʀᴏʀ! {excp.message}.")


@bot_admin
@user_admin
def setchat_title(update: Update, context: CallbackContext):
    chat = update.effective_chat
    msg = update.effective_message
    user = update.effective_user
    args = context.args

    if user_can_changeinfo(chat, user, context.bot.id) is False:
        msg.reply_text("ʏᴏᴜ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ ᴇɴᴏᴜɢʜ ʀɪɢʜᴛs ᴛᴏ ᴄʜᴀɴɢᴇ ᴄʜᴀᴛ ɪɴғᴏ!")
        ʀᴇᴛᴜʀɴ

    title = " ".join(args)
    if not title:
        msg.reply_text("ᴇɴᴛᴇʀ sᴏᴍᴇ ᴛᴇxᴛ ᴛᴏ sᴇᴛ ɴᴇᴡ ᴛɪᴛʟᴇ ɪɴ ʏᴏᴜʀ ᴄʜᴀᴛ!")
        return

    try:
        context.bot.set_chat_title(int(chat.id), str(title))
        msg.reply_text(
            f"sᴜᴄᴄᴇssғᴜʟʟʏ sᴇᴛ <b>{title}</b> ᴀs ɴᴇᴡ ᴄʜᴀᴛ ᴛɪᴛʟᴇ!",
            parse_mode=ParseMode.HTML,
        )
    except BadRequest as excp:
        msg.reply_text(f"ᴇʀʀᴏʀ! {excp.message}.")
        return


@bot_admin
@can_promote
@user_admin
@loggable
@typing_action
def promote(update: Update, context: CallbackContext) -> Optional[str]:
    chat_id = update.effective_chat.id
    message = update.effective_message
    chat = update.effective_chat
    user = update.effective_user
    bot, args = context.bot, context.args

    if user_can_promote(chat, user, bot.id) is False:
        message.reply_text("ʏᴏᴜ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ ᴇɴᴏᴜɢʜ ʀɪɢʜᴛs ᴛᴏ ᴘʀᴏᴍᴏᴛᴇ sᴏᴍᴇᴏɴᴇ!")
        return ""

    user_id = extract_user(message, args)
    if not user_id:
        message.reply_text("ᴍᴇɴᴛɪᴏɴ ᴏɴᴇ.... 🤷🏻‍♂.")
        return ""

    user_member = chat.get_member(user_id)
    if user_member.status in ["administrator", "creator"]:
        message.reply_text("ᴛʜɪs ᴘᴇʀsᴏɴ ɪs ᴀʟʀᴇᴀᴅʏ ᴀɴ ᴀᴅᴍɪɴ...!")
        return ""

    if user_id == bot.id:
        message.reply_text("I ʜᴏᴘᴇ, ɪғ ɪ ᴄᴏᴜʟᴅ ᴘʀᴏᴍᴏᴛᴇ ᴍʏsᴇʟғ!")
        return ""

    # set same perms as bot - bot can't assign higher perms than itself!
    bot_member = chat.get_member(bot.id)

    bot.promoteChatMember(
        chat_id,
        user_id,
        can_change_info=bot_member.can_change_info,
        can_post_messages=bot_member.can_post_messages,
        can_edit_messages=bot_member.can_edit_messages,
        can_delete_messages=bot_member.can_delete_messages,
        can_invite_users=bot_member.can_invite_users,
        can_restrict_members=bot_member.can_restrict_members,
        can_pin_messages=bot_member.can_pin_messages,
    )

    title = "admin"
    if " " in message.text:
        title = message.text.split(" ", 1)[1]
        if len(title) > 16:
            message.reply_text(
                "ᴛʜᴇ ᴛɪᴛʟᴇ ʟᴇɴɢᴛʜ ɪs ʟᴏɴɢᴇʀ ᴛʜᴀɴ 16 ᴄʜᴀʀᴀᴄᴛᴇʀs.\nᴛʀᴜɴᴄᴀᴛɪɴɢ it ᴛᴏ 16 ᴄʜᴀʀᴀᴄᴛᴇʀs."
            )

        try:
            bot.setChatAdministratorCustomTitle(chat.id, user_id, title)

        except BadRequest:
            message.reply_text(
                "I ᴄᴀɴ'ᴛ sᴇᴛ ᴄᴜsᴛᴏᴍ ᴛɪᴛʟᴇ ғᴏʀ ᴀᴅᴍɪɴs ᴛʜᴀᴛ I ᴅɪᴅɴ'ᴛ ᴘʀᴏᴍᴏᴛᴇ!"
            )

    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    text="⏬ ᴅᴇᴍᴏᴛᴇ",
                    callback_data="demote_({})".format(user_member.user.id),
                ),
                InlineKeyboardButton(text="ᴄʟᴏsᴇ ⛔", callback_data="close2"),
            ]
        ]
    )
    message.reply_text(
        f"♔ {chat.title} ᴇᴠᴇɴᴛ!\n"
        f"• ᴀ ɴᴇᴡ ᴀᴅᴍɪɴ ʜᴀs ʙᴇᴇɴ ᴀᴘᴘᴏɪɴᴛᴇᴅ!\n"
        f"• ʟᴇᴛ's ᴀʟʟ ᴡᴇʟᴄᴏᴍᴇ {mention_html(user_member.user.id, user_member.user.first_name)}",
        reply_markup=keyboard,
        parse_mode=ParseMode.HTML,
    )
    # ʀᴇғʀᴇsʜ ᴀᴅᴍɪɴ ᴄᴀᴄʜᴇ
    try:
        ADMIN_CACHE.pop(update.effective_chat.id)
    except KeyError:
        pass
    return (
        "<b>{}:</b>"
        "\n#ᴘʀᴏᴍᴏᴛᴇᴅ"
        "\n<b>ᴀᴅᴍɪɴ:</b> {}"
        "\n<b>ᴜsᴇʀ:</b> {}".format(
            html.escape(chat.title),
            mention_html(user.id, user.first_name),
            mention_html(user_member.user.id, user_member.user.first_name),
        )
    )


close_keyboard = InlineKeyboardMarkup(
    [[InlineKeyboardButton("🔄 ᴄᴀᴄʜᴇ", callback_data="close2")]]
)


@bot_admin
@can_promote
@user_admin
@loggable
@typing_action
def fullpromote(update, context):
    message = update.effective_message
    chat = update.effective_chat
    user = update.effective_user
    bot, args = context.bot, context.args

    if user_can_promote(chat, user, bot.id) is False:
        message.reply_text("ʏᴏᴜ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ ᴇɴᴏᴜɢʜ ʀɪɢʜᴛs ᴛᴏ ᴘʀᴏᴍᴏᴛᴇ sᴏᴍᴇᴏɴᴇ!")
        return ""

    user_id = extract_user(message, args)
    if not user_id:
        message.reply_text("ᴍᴇɴᴛɪᴏɴ ᴏɴᴇ.... 🤷🏻‍♂.")
        return ""

    user_member = chat.get_member(user_id)
    if user_member.status in ["administrator", "creator"]:
        message.reply_text("ᴛʜɪs ᴘᴇʀsᴏɴ ɪs ᴀʟʀᴇᴀᴅʏ ᴀɴ ᴀᴅᴍɪɴ...!")
        return ""

    if user_id == bot.id:
        message.reply_text("I ʜᴏᴘᴇ, ɪғ ɪ ᴄᴏᴜʟᴅ ᴘʀᴏᴍᴏᴛᴇ ᴍʏsᴇʟғ!")
        return ""

    # set same perms as bot - bot can't assign higher perms than itself!
    bot_member = chat.get_member(bot.id)

    bot.promoteChatMember(
        chat.id,
        user_id,
        can_change_info=bot_member.can_change_info,
        can_post_messages=bot_member.can_post_messages,
        can_edit_messages=bot_member.can_edit_messages,
        can_delete_messages=bot_member.can_delete_messages,
        can_invite_users=bot_member.can_invite_users,
        can_promote_members=bot_member.can_promote_members,
        can_restrict_members=bot_member.can_restrict_members,
        can_pin_messages=bot_member.can_pin_messages,
        can_manage_voice_chats=bot_member.can_manage_voice_chats,
    )

    title = "admin"
    if " " in message.text:
        title = message.text.split(" ", 1)[1]
        if len(title) > 16:
            message.reply_text(
                "ᴛʜᴇ ᴛɪᴛʟᴇ ʟᴇɴɢᴛʜ ɪs ʟᴏɴɢᴇʀ ᴛʜᴀɴ 16 ᴄʜᴀʀᴀᴄᴛᴇʀs.\nᴛʀᴜɴᴄᴀᴛɪɴɢ ɪᴛ ᴛᴏ 16 ᴄʜᴀʀᴀᴄᴛᴇʀs."
            )

        try:
            bot.setChatAdministratorCustomTitle(chat.id, user_id, title)

        except BadRequest:
            message.reply_text(
                "I ᴄᴀɴ'ᴛ sᴇᴛ ᴄᴜsᴛᴏᴍ ᴛɪᴛʟᴇ ғᴏʀ ᴀᴅᴍɪɴs ᴛʜᴀᴛ I ᴅɪᴅɴ'ᴛ ᴘʀᴏᴍᴏᴛᴇ!"
            )

    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    text="⏬ ᴅᴇᴍᴏᴛᴇ",
                    callback_data="demote_({})".format(user_member.user.id),
                ),
                InlineKeyboardButton(text="🔄 ᴄʟᴏsᴇ", callback_data="close2"),
            ]
        ]
    )
    message.reply_text(
        f"♔ {chat.title} ᴇᴠᴇɴᴛ!\n"
        f"• ᴀ ɴᴇᴡ ᴀᴅᴍɪɴ ʜᴀs ʙᴇᴇɴ ᴀᴘᴘᴏɪɴᴛᴇᴅ ᴀs ғᴜʟʟʏ ᴘʀᴏᴍᴏᴛᴇᴅ!\n"
        f"• ʟᴇᴛ's ᴀʟʟ ᴡᴇʟᴄᴏᴍᴇ {mention_html(user_member.user.id, user_member.user.first_name)}",
        reply_markup=keyboard,
        parse_mode=ParseMode.HTML,
    )

    log_message = (
        f"<b>{html.escape(chat.title)}:</b>\n"
        f"#ғᴜʟʟᴘʀᴏᴍᴏᴛᴇᴅ\n"
        f"<b>ᴀᴅᴍɪɴ:</b> {mention_html(user.id, user.first_name)}\n"
        f"<b>ᴜsᴇʀ:</b> {mention_html(user_member.user.id, user_member.user.first_name)}"
    )


close_keyboard = InlineKeyboardMarkup(
    [[InlineKeyboardButton("🔄 ᴄᴀᴄʜᴇ", callback_data="close2")]]
)


@bot_admin
@can_promote
@user_admin
@loggable
@typing_action
def demote(update: Update, context: CallbackContext) -> Optional[str]:
    chat = update.effective_chat
    message = update.effective_message
    user = update.effective_user
    bot, args = context.bot, context.args

    if user_can_promote(chat, user, bot.id) is False:
        message.reply_text("ʏᴏᴜ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ ᴇɴᴏᴜɢʜ ʀɪɢʜᴛs ᴛᴏ ᴅᴇᴍᴏᴛᴇ sᴏᴍᴇᴏɴᴇ!")
        return ""

    user_id = extract_user(message, args)
    if not user_id:
        message.reply_text(
            "ʏᴏᴜ ᴅᴏɴ'ᴛ sᴇᴇᴍ ᴛᴏ ʙᴇ ʀᴇғᴇʀʀɪɴɢ ᴛᴏ ᴀ ᴜsᴇʀ ᴏʀ ᴛʜᴇ ɪᴅ sᴘᴇᴄɪғɪᴇᴅ ɪs ɪɴᴄᴏʀʀᴇᴄᴛ.."
        )
        return ""

    user_member = chat.get_member(user_id)
    if user_member.status == "creator":
        message.reply_text("ᴛʜɪs ᴘᴇʀsᴏɴ CREATED ᴛʜᴇ ᴄʜᴀᴛ, ʜᴏᴡ ᴡᴏᴜʟᴅ I ᴅᴇᴍᴏᴛᴇ ᴛʜᴇᴍ?")
        return ""

    if user_member.status != "administrator":
        message.reply_text(
            "ʜᴏᴡ I'ᴍ sᴜᴘᴘᴏsᴇᴅ ᴛᴏ ᴅᴇᴍᴏᴛᴇ sᴏᴍᴇᴏɴᴇ ᴡʜᴏ ɪs ɴᴏᴛ ᴇᴠᴇɴ ᴀɴ ᴀᴅᴍɪɴ!"
        )
        return ""

    if user_id == bot.id:
        message.reply_text("ʏᴇᴀʜʜʜ... I'ᴍ ɴᴏᴛ ɢᴏɴɴᴀ ᴅᴇᴍᴏᴛᴇ ᴍʏsᴇʟғ!")
        return ""

    try:
        bot.promoteChatMember(
            int(chat.id),
            int(user_id),
            can_change_info=False,
            can_post_messages=False,
            can_edit_messages=False,
            can_delete_messages=False,
            can_invite_users=False,
            can_restrict_members=False,
            can_pin_messages=False,
            can_manage_voice_chats=False,
        )
        message.reply_text(
            f"sᴜᴄᴄᴇssғᴜʟʟʏ ᴅᴇᴍᴏᴛᴇᴅ <b>{user_member.user.first_name or user_id}</b>!",
            parse_mode=ParseMode.HTML,
        )
        return (
            "<b>{}:</b>"
            "\n#ᴅᴇᴍᴏᴛᴇᴅ"
            "\n<b>ᴀᴅᴍɪɴ:</b> {}"
            "\n<b>ᴜsᴇʀ:</b> {}".format(
                html.escape(chat.title),
                mention_html(user.id, user.first_name),
                mention_html(user_member.user.id, user_member.user.first_name),
            )
        )

    except BadRequest:
        message.reply_text(
            "ғᴀɪʟᴇᴅ ᴛᴏ ᴅᴇᴍᴏᴛᴇ. ɪ ᴍɪɢʜᴛ ɴᴏᴛ ʙᴇ ᴀᴅᴍɪɴ, ᴏʀ ᴛʜᴇ ᴀᴅᴍɪɴ sᴛᴀᴛᴜs ᴡᴀs ᴀᴘᴘᴏɪɴᴛᴇᴅ ʙʏ ᴀɴᴏᴛʜᴇʀ "
            "ᴜsᴇʀ, sᴏ I ᴄᴀɴ'ᴛ act upon them!"
        )
        return ""


@user_admin
def refresh_admin(update, _):
    try:
        ADMIN_CACHE.pop(update.effective_chat.id)
    except KeyError:
        pass

    update.effective_message.reply_text("ᴀᴅᴍɪɴs ᴄᴀᴄʜᴇ ʀᴇғʀᴇsʜᴇᴅ!")


@connection_status
@bot_admin
@can_promote
@user_admin
def set_title(update: Update, context: CallbackContext):
    bot = context.bot
    args = context.args

    chat = update.effective_chat
    message = update.effective_message

    user_id, title = extract_user_and_text(message, args)
    try:
        user_member = chat.get_member(user_id)
    except:
        return

    if not user_id:
        message.reply_text(
            "ʏᴏᴜ ᴅᴏɴ'ᴛ sᴇᴇᴍ ᴛᴏ ʙᴇ ʀᴇғᴇʀʀɪɴɢ ᴛᴏ ᴀ ᴜsᴇʀ ᴏʀ ᴛʜᴇ ɪᴅ sᴘᴇᴄɪғɪᴇᴅ ɪs ɪɴᴄᴏʀʀᴇᴄᴛ..",
        )
        return

    if user_member.status == "creator":
        message.reply_text(
            "ᴛʜɪs ᴘᴇʀsᴏɴ CREATED ᴛʜᴇ ᴄʜᴀᴛ, ʜᴏᴡ ᴄᴀɴ ɪ sᴇᴛ ᴄᴜsᴛᴏᴍ ᴛɪᴛʟᴇ ғᴏʀ ʜɪᴍ?",
        )
        return

    if user_member.status != "administrator":
        message.reply_text(
            "ᴄᴀɴ'ᴛ sᴇᴛ title for ɴᴏɴ-ᴀᴅᴍɪɴs!\nᴘʀᴏᴍᴏᴛᴇ ᴛʜᴇᴍ ғɪʀsᴛ ᴛᴏ sᴇᴛ ᴄᴜsᴛᴏᴍ ᴛɪᴛʟᴇ!",
        )
        return

    if user_id == bot.id:
        message.reply_text(
            "I ᴄᴀɴ'ᴛ sᴇᴛ ᴍʏ ᴏᴡɴ ᴛɪᴛʟᴇ ᴍʏsᴇʟғ! ɢᴇᴛ ᴛʜᴇ ᴏɴᴇ ᴡʜᴏ ᴍᴀᴅᴇ ᴍᴇ ᴀᴅᴍɪɴ ᴛᴏ ᴅᴏ ɪᴛ ғᴏʀ ᴍᴇ.",
        )
        return

    if not title:
        message.reply_text("sᴇᴛᴛɪɴɢ ʙʟᴀɴᴋ ᴛɪᴛʟᴇ ᴅᴏᴇsɴ'ᴛ ᴅᴏ ᴀɴʏᴛʜɪɴɢ!")
        return

    if len(title) > 16:
        message.reply_text(
            "ᴛʜᴇ ᴛɪᴛʟᴇ ʟᴇɴɢᴛʜ ɪs ʟᴏɴɢᴇʀ ᴛʜᴀɴ 16 ᴄʜᴀʀᴀᴄᴛᴇʀs.\nᴛʀᴜɴᴄᴀᴛɪɴɢ it ᴛᴏ 16 ᴄʜᴀʀᴀᴄᴛᴇʀs.",
        )

    try:
        bot.setChatAdministratorCustomTitle(chat.id, user_id, title)
    except BadRequest:
        message.reply_text(
            "ᴇɪᴛʜᴇʀ ᴛʜᴇʏ ᴀʀᴇɴ'ᴛ ᴘʀᴏᴍᴏᴛᴇᴅ ʙʏ ᴍᴇ ᴏʀ ʏᴏᴜ sᴇᴛ ᴀ ᴛɪᴛʟᴇ ᴛᴇxᴛ ᴛʜᴀᴛ ɪs ɪᴍᴘᴏssɪʙʟᴇ ᴛᴏ sᴇᴛ."
        )
        return

    bot.sendMessage(
        chat.id,
        f"sᴜᴄᴇssғᴜʟʟʏ sᴇᴛ ᴛɪᴛʟᴇ ғᴏʀ <code>{user_member.user.first_name or user_id}</code> "
        f"ᴛᴏ <code>{html.escape(title[:16])}</code>!",
        parse_mode=ParseMode.HTML,
    )


@bot_admin
@can_pin
@user_admin
@loggable
def pin(update: Update, context: CallbackContext) -> str:
    bot, args = context.bot, context.args
    user = update.effective_user
    chat = update.effective_chat
    msg = update.effective_message
    msg_id = msg.reply_to_message.message_id if msg.reply_to_message else msg.message_id

    if msg.chat.username:
        # If chat has a username, use this format
        link_chat_id = msg.chat.username
        message_link = f"https://t.me/{link_chat_id}/{msg_id}"
    elif (str(msg.chat.id)).startswith("-100"):
        # If chat does not have a username, use this
        link_chat_id = (str(msg.chat.id)).replace("-100", "")
        message_link = f"https://t.me/c/{link_chat_id}/{msg_id}"

    is_group = chat.type not in ("private", "channel")
    prev_message = update.effective_message.reply_to_message

    if prev_message is None:
        msg.reply_text("ʀᴇᴘʟʏ ᴀ ᴍᴇssᴀɢᴇ ᴛᴏ ᴘɪɴ ɪᴛ!")
        return

    is_silent = True
    if len(args) >= 1:
        is_silent = (
            args[0].lower() != "notify"
            or args[0].lower() == "loud"
            or args[0].lower() == "violent"
        )

    if prev_message and is_group:
        try:
            bot.pinChatMessage(
                chat.id, prev_message.message_id, disable_notification=is_silent
            )
            msg.reply_text(
                "sᴜᴄᴄᴇss! ᴘɪɴɴᴇᴅ ᴛʜɪs ᴍᴇssᴀɢᴇ ᴏɴ ᴛʜɪs ɢʀᴏᴜᴘ",
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                text="📝 ᴠɪᴇᴡ ᴍᴇssᴀɢᴇs", url=f"{message_link}"
                            ),
                            InlineKeyboardButton(
                                text="❌ ᴅᴇʟᴇᴛᴇ", callback_data="close2"
                            ),
                        ]
                    ]
                ),
                parse_mode=ParseMode.HTML,
                disable_web_page_preview=True,
            )
        except BadRequest as excp:
            if excp.message != "Chat_not_modified":
                raise

        log_message = (
            f"<b>{html.escape(chat.title)}:</b>\n"
            f"ᴘɪɴɴᴇᴅ\n"
            f"<b>ᴀᴅᴍɪɴ:</b> {mention_html(user.id, html.escape(user.first_name))}"
        )

        return log_message


close_keyboard = InlineKeyboardMarkup(
    [[InlineKeyboardButton("❌ ᴅᴇʟᴇᴛᴇ", callback_data="close2")]]
)


@bot_admin
@can_pin
@user_admin
@loggable
def unpin(update: Update, context: CallbackContext):
    chat = update.effective_chat
    user = update.effective_user
    msg = update.effective_message
    msg_id = msg.reply_to_message.message_id if msg.reply_to_message else msg.message_id
    unpinner = chat.get_member(user.id)

    if (
        not (unpinner.can_pin_messages or unpinner.status == "creator")
        and user.id not in DRAGONS
    ):
        message.reply_text("ʏᴏᴜ ᴅᴏɴ ʜᴀᴠᴇ ᴛʜᴇ ɴᴇᴄᴇssᴀʀʏ ʀɪɢʜᴛs ᴛᴏ ᴅᴏ ᴛʜᴀᴛ!")
        return

    if msg.chat.username:
        # If chat has a username, use this format
        link_chat_id = msg.chat.username
        message_link = f"https://t.me/{link_chat_id}/{msg_id}"
    elif (str(msg.chat.id)).startswith("-100"):
        # If chat does not have a username, use this
        link_chat_id = (str(msg.chat.id)).replace("-100", "")
        message_link = f"https://t.me/c/{link_chat_id}/{msg_id}"

    is_group = chat.type not in ("private", "channel")
    prev_message = update.effective_message.reply_to_message

    if prev_message and is_group:
        try:
            context.bot.unpinChatMessage(chat.id, prev_message.message_id)
            msg.reply_text(
                f"ᴜɴᴘɪɴɴᴇᴅ <a href='{message_link}'>this message</a>.",
                parse_mode=ParseMode.HTML,
                disable_web_page_preview=True,
            )
        except BadRequest as excp:
            if excp.message != "Chat_not_modified":
                raise

    if not prev_message and is_group:
        try:
            context.bot.unpinChatMessage(chat.id)
            msg.reply_text("🔽 ᴜɴᴘɪɴɴᴇᴅ ᴛʜᴇ ʟᴀsᴛ ᴍᴇssᴀɢᴇ ᴏɴ ᴛʜɪs ɢʀᴏᴜᴘ.")
        except BadRequest as excp:
            if excp.message == "ᴍᴇssᴀɢᴇ ᴛᴏ ᴜɴᴘɪɴ ɴᴏᴛ ғᴏᴜɴᴅ":
                msg.reply_text(
                    "I ᴄᴀɴ'ᴛ sᴇᴇ ᴘɪɴɴᴇᴅ ᴍᴇssᴀɢᴇ, ᴍᴀʏʙᴇ ᴀʟʀᴇᴀᴅʏ ᴜɴᴘɪɴᴇᴅ, ᴏʀ ᴘɪɴ ᴍᴇssᴀɢᴇ ᴛᴏ ᴏʟᴅ 🙂"
                )
            else:
                raise

    log_message = (
        f"<b>{html.escape(chat.title)}:</b>\n"
        f"ᴍᴇssᴀɢᴇ-ᴜɴᴘɪɴɴᴇᴅ-sᴜᴄᴄᴇssғᴜʟʟʏ\n"
        f"<b>ᴀᴅᴍɪɴ:</b> {mention_html(user.id, html.escape(user.first_name))}"
    )

    return log_message


@bot_admin
def pinned(update: Update, context: CallbackContext) -> str:
    bot = context.bot
    msg = update.effective_message
    msg_id = (
        update.effective_message.reply_to_message.message_id
        if update.effective_message.reply_to_message
        else update.effective_message.message_id
    )

    chat = bot.getChat(chat_id=msg.chat.id)
    if chat.pinned_message:
        pinned_id = chat.pinned_message.message_id
        if msg.chat.username:
            link_chat_id = msg.chat.username
            message_link = f"https://t.me/{link_chat_id}/{pinned_id}"
        elif (str(msg.chat.id)).startswith("-100"):
            link_chat_id = (str(msg.chat.id)).replace("-100", "")
            message_link = f"https://t.me/c/{link_chat_id}/{pinned_id}"

        msg.reply_text(
            f"📌 ᴘɪɴɴᴇᴅ ᴛʜᴇ ᴍᴇssᴀɢᴇ ᴏɴ {html.escape(chat.title)}.",
            reply_to_message_id=msg_id,
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text="ᴘɪɴɴᴇᴅ ᴍᴇssᴀɢᴇs",
                            url=f"https://t.me/{link_chat_id}/{pinned_id}",
                        )
                    ]
                ]
            ),
        )

    else:
        msg.reply_text(
            f"ᴛʜᴇʀᴇ ɪs ɴᴏ ᴘɪɴɴᴇᴅ ᴍᴇssᴀɢᴇ ᴏɴ <b>{html.escape(chat.title)}!</b>",
            parse_mode=ParseMode.HTML,
        )


@bot_admin
@user_admin
@typing_action
def invite(update, context):
    bot = context.bot
    user = update.effective_user
    msg = update.effective_message
    chat = update.effective_chat

    conn = connected(bot, update, chat, user.id, need_admin=True)
    if conn:
        chat = dispatcher.bot.getChat(conn)
    else:
        if msg.chat.type == "private":
            msg.reply_text("ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ ɪs ᴍᴇᴀɴᴛ ᴛᴏ ᴜsᴇ ɪɴ ᴄʜᴀᴛ ɴᴏᴛ ɪɴ PM")
            return ""
        chat = update.effective_chat

    if chat.username:
        msg.reply_text(chat.username)
    elif chat.type in [chat.SUPERGROUP, chat.CHANNEL]:
        bot_member = chat.get_member(bot.id)
        if bot_member.can_invite_users:
            invitelink = context.bot.exportChatInviteLink(chat.id)
            msg.reply_text(invitelink)
        else:
            msg.reply_text(
                "I ᴅᴏɴ'ᴛ ʜᴀᴠᴇ ᴀᴄᴄᴇss ᴛᴏ ᴛʜᴇ ɪɴᴠɪᴛᴇ ʟɪɴᴋ, ᴛʀʏ ᴄʜᴀɴɢɪɴɢ ᴍʏ ᴘᴇʀᴍɪssɪᴏɴs!"
            )
    else:
        msg.reply_text(
            "I ᴄᴀɴ ᴏɴʟʏ ɢɪᴠᴇ ʏᴏᴜ ɪɴᴠɪᴛᴇ ʟɪɴᴋs ғᴏʀ sᴜᴘᴇʀɢʀᴏᴜᴘs ᴀɴᴅ ᴄʜᴀɴɴᴇʟs, sᴏʀʀʏ!"
        )


"""        
@Abishnoi.on_message(filters.command(["staff", "admins", "adminlist"]) & filters.group)
    uname = f"ᴀᴅᴍɪɴs ɪɴ {message.chat.title} :\n\n"
    async for gey in app.iter_chat_members(message.chat.id, filter="administrators"):
        try:
            uname += f"@{(await app.get_users(int(gey.user.id))).username}\n"
        except:
            uname += ""
    await message.reply_text(uname)
"""


@Abishnoi.on_message(filters.command(["adminlist", "staff", "admins"]))
async def admins(client, message):
    try:
        adminList = []
        ownerList = []
        async for admin in Abishnoi.get_chat_members(
            message.chat.id, filter=enums.ChatMembersFilter.ADMINISTRATORS
        ):
            if admin.privileges.is_anonymous == False:
                if admin.user.is_bot == True:
                    pass
                elif admin.status == ChatMemberStatus.OWNER:
                    ownerList.append(admin.user)
                else:
                    adminList.append(admin.user)
            else:
                pass
        lenAdminList = len(ownerList) + len(adminList)
        text2 = f"**ɢʀᴏᴜᴘ sᴛᴀғғ - {message.chat.title}**\n\n"
        try:
            owner = ownerList[0]
            if owner.username == None:
                text2 += f"👑 ᴏᴡɴᴇʀ\n└ {owner.mention}\n\n👮🏻 ᴀᴅᴍɪɴs\n"
            else:
                text2 += f"👑 ᴏᴡɴᴇʀ\n└ @{owner.username}\n\n👮🏻 ᴀᴅᴍɪɴs\n"
        except:
            text2 += f"👑 ᴏᴡɴᴇʀ\n└ <i>Hidden</i>\n\n👮🏻 ᴀᴅᴍɪɴs\n"
        if len(adminList) == 0:
            text2 += "└ <i>ᴀᴅᴍɪɴs ᴀʀᴇ ʜɪᴅᴅᴇɴ</i>"
            await Abishnoi.send_message(message.chat.id, text2)
        else:
            while len(adminList) > 1:
                admin = adminList.pop(0)
                if admin.username == None:
                    text2 += f"├ {admin.mention}\n"
                else:
                    text2 += f"├ @{admin.username}\n"
            else:
                admin = adminList.pop(0)
                if admin.username == None:
                    text2 += f"└ {admin.mention}\n\n"
                else:
                    text2 += f"└ @{admin.username}\n\n"
            text2 += f"✅ | **ᴛᴏᴛᴀʟ ɴᴜᴍʙᴇʀ ᴏғ ᴀᴅᴍɪɴs**: {lenAdminList}\n❌ | ʙᴏᴛs ᴀɴᴅ ᴀɴᴏɴʏᴍᴏᴜs ᴀᴅᴍɪɴs ᴡᴇʀᴇ ʀᴇᴊᴇᴄᴛᴇᴅ."
            await Abishnoi.send_message(message.chat.id, text2)
    except FloodWait as e:
        await asyncio.sleep(e.value)


@Abishnoi.on_message(filters.command("bots"))
async def bots(client, message):
    try:
        botList = []
        async for bot in Abishnoi.get_chat_members(
            message.chat.id, filter=enums.ChatMembersFilter.BOTS
        ):
            botList.append(bot.user)
        lenBotList = len(botList)
        text3 = f"**ʙᴏᴛ ʟɪsᴛ - {message.chat.title}**\n\n🤖 Bots\n"
        while len(botList) > 1:
            bot = botList.pop(0)
            text3 += f"├ @{bot.username}\n"
        else:
            bot = botList.pop(0)
            text3 += f"└ @{bot.username}\n\n"
            text3 += f"✅ | **ᴛᴏᴛᴀʟ ɴᴜᴍʙᴇʀ ᴏғ ʙᴏᴛs**: {lenBotList}"
            await Abishnoi.send_message(message.chat.id, text3)
    except FloodWait as e:
        await asyncio.sleep(e.value)


@bot_admin
@can_promote
@user_admin
@loggable
def button(update: Update, context: CallbackContext) -> str:
    query: Optional[CallbackQuery] = update.callback_query
    user: Optional[User] = update.effective_user
    bot: Optional[Bot] = context.bot
    match = re.match(r"demote_\((.+?)\)", query.data)
    if match:
        user_id = match.group(1)
        chat: Optional[Chat] = update.effective_chat
        member = chat.get_member(user_id)
        bot_member = chat.get_member(bot.id)
        bot_permissions = promoteChatMember(
            chat.id,
            user_id,
            can_change_info=bot_member.can_change_info,
            can_post_messages=bot_member.can_post_messages,
            can_edit_messages=bot_member.can_edit_messages,
            can_delete_messages=bot_member.can_delete_messages,
            can_invite_users=bot_member.can_invite_users,
            can_promote_members=bot_member.can_promote_members,
            can_restrict_members=bot_member.can_restrict_members,
            can_pin_messages=bot_member.can_pin_messages,
            can_manage_voice_chats=bot_member.can_manage_voice_chats,
        )
        demoted = bot.promoteChatMember(
            chat.id,
            user_id,
            can_change_info=False,
            can_post_messages=False,
            can_edit_messages=False,
            can_delete_messages=False,
            can_invite_users=False,
            can_restrict_members=False,
            can_pin_messages=False,
            can_promote_members=False,
            can_manage_voice_chats=False,
        )
        if demoted:
            update.effective_message.edit_text(
                f"ʏᴇᴘ! {mention_html(user_member.user.id, user_member.user.first_name)} has been demoted in {chat.title}!"
                f"ʙʏ {mention_html(user.id, user.first_name)}",
                parse_mode=ParseMode.HTML,
            )
            query.answer("ᴅᴇᴍᴏᴛᴇᴅ!")
            return (
                f"<b>{html.escape(chat.title)}:</b>\n"
                f"#ᴅᴇᴍᴏᴛᴇ\n"
                f"<b>ᴀᴅᴍɪɴ:</b> {mention_html(user.id, user.first_name)}\n"
                f"<b>ᴜsᴇʀ:</b> {mention_html(member.user.id, member.user.first_name)}"
            )
    else:
        update.effective_message.edit_text(
            "ᴛʜɪs ᴜsᴇʀ ɪs ɴᴏᴛ ᴘʀᴏᴍᴏᴛᴇᴅ ᴏʀ ʜᴀs ʟᴇғᴛ ᴛʜᴇ ɢʀᴏᴜᴘ!"
        )
        return ""


SET_DESC_HANDLER = CommandHandler(
    "setdesc", set_desc, filters=Filters.chat_type.groups, run_async=True
)
SET_STICKER_HANDLER = CommandHandler(
    "setsticker", set_sticker, filters=Filters.chat_type.groups, run_async=True
)
SETCHATPIC_HANDLER = CommandHandler(
    "setgpic", setchatpic, filters=Filters.chat_type.groups, run_async=True
)
RMCHATPIC_HANDLER = CommandHandler(
    "delgpic", rmchatpic, filters=Filters.chat_type.groups, run_async=True
)
SETCHAT_TITLE_HANDLER = CommandHandler(
    "setgtitle", setchat_title, filters=Filters.chat_type.groups, run_async=True
)

PIN_HANDLER = CommandHandler(
    "pin", pin, filters=Filters.chat_type.groups, run_async=True
)
UNPIN_HANDLER = CommandHandler(
    "unpin", unpin, filters=Filters.chat_type.groups, run_async=True
)
PINNED_HANDLER = CommandHandler(
    "pinned", pinned, filters=Filters.chat_type.groups, run_async=True
)

INVITE_HANDLER = DisableAbleCommandHandler("invitelink", invite, run_async=True)

PROMOTE_HANDLER = DisableAbleCommandHandler("promote", promote, run_async=True)
FULLPROMOTE_HANDLER = DisableAbleCommandHandler(
    "fullpromote", fullpromote, run_async=True
)
DEMOTE_HANDLER = DisableAbleCommandHandler("demote", demote, run_async=True)

SET_TITLE_HANDLER = CommandHandler("title", set_title, run_async=True)
ADMIN_REFRESH_HANDLER = CommandHandler(
    "admincache", refresh_admin, filters=Filters.chat_type.groups, run_async=True
)

dispatcher.add_handler(SET_DESC_HANDLER)
dispatcher.add_handler(SET_STICKER_HANDLER)
dispatcher.add_handler(SETCHATPIC_HANDLER)
dispatcher.add_handler(RMCHATPIC_HANDLER)
dispatcher.add_handler(SETCHAT_TITLE_HANDLER)
dispatcher.add_handler(PIN_HANDLER)
dispatcher.add_handler(UNPIN_HANDLER)
dispatcher.add_handler(PINNED_HANDLER)
dispatcher.add_handler(INVITE_HANDLER)
dispatcher.add_handler(PROMOTE_HANDLER)
dispatcher.add_handler(FULLPROMOTE_HANDLER)
dispatcher.add_handler(DEMOTE_HANDLER)
dispatcher.add_handler(SET_TITLE_HANDLER)
dispatcher.add_handler(ADMIN_REFRESH_HANDLER)

__mod_name__ = "𝐀ᴅᴍɪɴ"
__command_list__ = [
    "setdesc" "setsticker" "setgpic" "delgpic" "setgtitle",
    "admins",
    "invitelink",
    "promote",
    "fullpromote",
    "demote",
    "admincache",
]
__handlers__ = [
    SET_DESC_HANDLER,
    SET_STICKER_HANDLER,
    SETCHATPIC_HANDLER,
    RMCHATPIC_HANDLER,
    SETCHAT_TITLE_HANDLER,
    PIN_HANDLER,
    UNPIN_HANDLER,
    PINNED_HANDLER,
    INVITE_HANDLER,
    PROMOTE_HANDLER,
    FULLPROMOTE_HANDLER,
    DEMOTE_HANDLER,
    SET_TITLE_HANDLER,
    ADMIN_REFRESH_HANDLER,
]


# ғᴏʀ ʜᴇʟᴘ ᴍᴇɴᴜ

# """
from Exon.modules.language import gs


def get_help(chat):
    return gs(chat, "admin_help")


# """
