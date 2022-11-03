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
from typing import List, Optional

from telegram import Bot, Chat, Update, User
from telegram.error import BadRequest
from telegram.ext import CommandHandler, Filters, MessageHandler
from telegram.ext.dispatcher import run_async
from telegram.utils.helpers import mention_html

from Exon import dispatcher
from Exon.modules.helper_funcs.chat_status import bot_admin, can_pin, user_admin
from Exon.modules.log_channel import loggable
from Exon.modules.sql import pin_sql as sql

PMW_GROUP = 12


@run_async
@bot_admin
@can_pin
@user_admin
@loggable
def pin(bot: Bot, update: Update, args: List[str]) -> str:
    user = update.effective_user  # type: Optional[User]
    chat = update.effective_chat  # type: Optional[Chat]

    is_group = chat.type != "private" and chat.type != "channel"

    prev_message = update.effective_message.reply_to_message

    is_silent = True
    if len(args) >= 1:
        is_silent = not (
            args[0].lower() == "notify"
            or args[0].lower() == "loud"
            or args[0].lower() == "violent"
        )

    if prev_message and is_group:
        try:
            bot.pinChatMessage(
                chat.id, prev_message.message_id, disable_notification=is_silent
            )
        except BadRequest as excp:
            if excp.message == "Chat_not_modified":
                pass
            else:
                raise
        sql.add_mid(chat.id, prev_message.message_id)
        return (
            "<b>{}:</b>"
            "\n#ᴘɪɴɴᴇᴅ"
            "\n<b>ᴀᴅᴍɪɴ:</b> {}".format(
                html.escape(chat.title), mention_html(user.id, user.first_name)
            )
        )

    return ""


@run_async
@bot_admin
@can_pin
@user_admin
@loggable
def unpin(bot: Bot, update: Update) -> str:
    chat = update.effective_chat
    user = update.effective_user  # type: Optional[User]

    try:
        bot.unpinChatMessage(chat.id)
    except BadRequest as excp:
        if excp.message == "Chat_not_modified":
            pass
        else:
            raise
    sql.remove_mid(chat.id)
    return (
        "<b>{}:</b>"
        "\n#ᴜɴᴘɪɴɴᴇᴅ"
        "\n<b>ᴀᴅᴍɪɴ:</b> {}".format(
            html.escape(chat.title), mention_html(user.id, user.first_name)
        )
    )


@run_async
@bot_admin
@can_pin
@user_admin
@loggable
def anti_channel_pin(bot: Bot, update: Update, args: List[str]) -> str:
    chat = update.effective_chat  # type: Optional[Chat]
    user = update.effective_user  # type: Optional[User]

    if not args:
        update.effective_message.reply_text(
            "ɪ ᴜɴᴅᴇʀsᴛᴀɴᴅ ᴏɴʟʏ :'on/yes' ᴏʀ 'off/no' only!"
        )
        return ""

    if args[0].lower() in ("on", "yes"):
        sql.add_acp_o(str(chat.id), True)
        update.effective_message.reply_text(
            "I'll try to unpin Telegram Channel messages!"
        )
        return (
            "<b>{}:</b>"
            "\n#ᴀɴᴛɪ_ᴄʜᴀɴɴᴇʟ_ᴘɪɴ"
            "\n<b>ᴀᴅᴍɪɴ:</b> {}"
            "\nʜᴀs ᴛᴏɢɢʟᴇᴅ ᴀɴᴛɪ ᴄʜᴀɴɴᴇʟ ᴘɪɴ ᴛᴏ <code>ᴏɴ</code>.".format(
                html.escape(chat.title), mention_html(user.id, user.first_name)
            )
        )
    elif args[0].lower() in ("off", "no"):
        sql.add_acp_o(str(chat.id), False)
        update.effective_message.reply_text("I won't unpin Telegram Channel Messages!")
        return (
            "<b>{}:</b>"
            "\n#ᴀɴᴛɪ_ᴄʜᴀɴɴᴇʟ_ᴘɪɴ"
            "\n<b>ᴀᴅᴍɪɴ:</b> {}"
            "\nʜᴀs ᴛᴏɢɢʟᴇᴅ ᴀɴᴛɪ ᴄʜᴀɴɴᴇʟ ᴘɪɴ ᴛᴏ <code>ᴏғғ</code>.".format(
                html.escape(chat.title), mention_html(user.id, user.first_name)
            )
        )
    else:
        # idek what you're writing, say yes or no
        update.effective_message.reply_text(
            "ɪ ᴜɴᴅᴇʀsᴛᴀɴᴅ ᴏɴʟʏ  'on/yes' ᴏʀ 'off/no' only!"
        )
        return ""


@run_async
@bot_admin
# @can_delete
@user_admin
@loggable
def clean_linked_channel(bot: Bot, update: Update, args: List[str]) -> str:
    chat = update.effective_chat  # type: Optional[Chat]
    user = update.effective_user  # type: Optional[User]

    if not args:
        update.effective_message.reply_text("ɪ ᴜɴᴅᴇʀsᴛᴀɴᴅ 'on/yes' ᴏʀ 'off/no' only!")
        return ""

    if args[0].lower() in ("on", "yes"):
        sql.add_ldp_m(str(chat.id), True)
        update.effective_message.reply_text(
            "I'll ᴛʀʏ ᴛᴏ ᴅᴇʟᴇᴛᴇ ᴛᴇʟᴇɢʀᴀᴍ ᴄʜᴀɴɴᴇʟ ᴍᴇssᴀɢᴇs!"
        )
        return (
            "<b>{}:</b>"
            "\n#ᴄʟᴇᴀɴ_ᴄʜᴀɴɴᴇʟ_ᴍᴇssᴀɢᴇs"
            "\n<b>ᴀᴅᴍɪɴ:</b> {}"
            "\nʜᴀs ᴛᴏɢɢʟᴇᴅ ᴅᴇʟᴇᴛᴇ ᴄʜᴀɴɴᴇʟ ᴍᴇssᴀɢᴇs ᴛᴏ <code>ᴏɴ</code>.".format(
                html.escape(chat.title), mention_html(user.id, user.first_name)
            )
        )
    elif args[0].lower() in ("off", "no"):
        sql.add_ldp_m(str(chat.id), False)
        update.effective_message.reply_text("I ᴡᴏɴ'ᴛ ᴅᴇʟᴇᴛᴇ ᴛᴇʟᴇɢʀᴀᴍ ᴄʜᴀɴɴᴇʟ ᴍᴇssᴀɢᴇs!")
        return (
            "<b>{}:</b>"
            "\n#ᴄʟᴇᴀɴ_ᴄʜᴀɴɴᴇʟ_ᴍᴇssᴀɢᴇs"
            "\n<b>ᴀᴅᴍɪɴ:</b> {}"
            "\nʜᴀs ᴛᴏɢɢʟᴇᴅ ᴅᴇʟᴇᴛᴇ ᴄʜᴀɴɴᴇʟ ᴍᴇssᴀɢᴇs ᴛᴏ <code>ᴏғғ</code>.".format(
                html.escape(chat.title), mention_html(user.id, user.first_name)
            )
        )
    else:
        # idek what you're writing, say yes or no
        update.effective_message.reply_text("ɪ ᴜɴᴅᴇʀsᴛᴀɴᴅ 'on/yes' ᴏʀ 'off/no' only!")
        return ""


@run_async
def amwltro_conreko(bot: Bot, update: Update):
    chat = update.effective_chat  # type: Optional[Chat]
    message = update.effective_message  # type: Optional[Message]
    sctg = sql.get_current_settings(chat.id)
    """we apparently do not receive any update for PINned messages
    """
    if sctg and sctg.message_id != 0 and message.from_user.id == 777000:
        if sctg.suacpmo:
            try:
                bot.unpin_chat_message(chat.id)
            except:
                pass
            pin_chat_message(bot, chat.id, sctg.message_id, True)
        if sctg.scldpmo:
            try:
                message.delete()
            except:
                pass
            pin_chat_message(bot, chat.id, sctg.message_id, True)


def pin_chat_message(bot, chat_id, message_id, is_silent):
    try:
        bot.pinChatMessage(chat_id, message_id, disable_notification=is_silent)
    except BadRequest as excp:
        if excp.message == "Chat_not_modified":
            pass
        """else:
            raise"""


__help__ = """

*ᴀᴅᴍɪɴ ᴏɴʟʏ:*
 ⍟ /pin: `sɪʟᴇɴᴛʟʏ ᴘɪɴs ᴛʜᴇ ᴍᴇssᴀɢᴇ ʀᴇᴘʟɪᴇᴅ ᴛᴏ`
       : ᴀᴅᴅ 'loud' ᴏʀ 'notify' ᴛᴏ ɢɪᴠᴇ ɴᴏᴛɪғs ᴛᴏ ᴜsᴇʀs
       
 ⍟ /unpin: `ᴜɴᴘɪɴs ᴛʜᴇ ᴄᴜʀʀᴇɴᴛʟʏ ᴘɪɴɴᴇᴅ ᴍᴇssᴀɢᴇ `
 
 ⍟ /antichannelpin <yes/no/on/off>: `ᴅᴏɴ'ᴛ ʟᴇᴛ ᴛᴇʟᴇɢʀᴀᴍ ᴀᴜᴛᴏ-ᴘɪɴ  ʟɪɴᴋᴇᴅ ᴄʜᴀɴɴᴇʟs `
 
 ⍟ /cleanlinked <yes/no/on/off>: `ᴅᴇʟᴇᴛᴇ ᴍᴇssᴀɢᴇs sᴇɴᴛ ʙʏ ᴛʜᴇ ʟɪɴᴋᴇᴅ ᴄʜᴀɴɴᴇʟ `.

Note:
ᴡʜᴇɴ using ᴀɴᴛɪᴄʜᴀɴɴᴇʟ pins, ᴍᴀᴋᴇ sᴜʀᴇ ᴛᴏ ᴜsᴇ ᴛʜᴇ /unpin ᴄᴏᴍᴍᴀɴᴅ,
ɪɴsᴛᴇᴀᴅ ᴏғ ᴅᴏɪɴɢ ɪᴛ ᴍᴀɴᴜᴀʟʟʏ.

ᴏᴛʜᴇʀᴡɪsᴇ, the ᴏʟᴅ message ᴡɪʟʟ ɢᴇᴛ ʀᴇ-ᴘɪɴɴᴇᴅ ᴡʜᴇɴ ᴛʜᴇ ᴄʜᴀɴɴᴇʟ sᴇɴᴅs ᴀɴʏ ᴍᴇssᴀɢᴇs.
"""

__mod_name__ = "𝙿ɪɴs"


PIN_HANDLER = CommandHandler(
    "pin", pin, pass_args=True, filters=Filters.chat_type.groups
)
UNPIN_HANDLER = CommandHandler("unpin", unpin, filters=Filters.chat_type.groups)
ATCPIN_HANDLER = CommandHandler(
    "antichannelpin", anti_channel_pin, pass_args=True, filters=Filters.chat_type.groups
)
CLCLDC_HANDLER = CommandHandler(
    "cleanlinked",
    clean_linked_channel,
    pass_args=True,
    filters=Filters.chat_type.groups,
)
AMWLTRO_HANDLER = MessageHandler(
    Filters.forwarded & Filters.chat_type.groups, amwltro_conreko, edited_updates=False
)

dispatcher.add_handler(PIN_HANDLER)
dispatcher.add_handler(UNPIN_HANDLER)
dispatcher.add_handler(ATCPIN_HANDLER)
dispatcher.add_handler(CLCLDC_HANDLER)
dispatcher.add_handler(AMWLTRO_HANDLER, PMW_GROUP)
