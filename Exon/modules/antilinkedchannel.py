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

from telegram import TelegramError, Update
from telegram.ext import CallbackContext
from telegram.ext.filters import Filters

import Exon.modules.sql.antilinkedchannel_sql as sql
from Exon.modules.helper_funcs.anonymous import AdminPerms, user_admin
from Exon.modules.helper_funcs.chat_status import bot_admin, bot_can_delete
from Exon.modules.helper_funcs.decorators import Exoncmd, Exonmsg


@Exoncmd(command="cleanlinked", group=112)
@bot_can_delete
@user_admin(AdminPerms.CAN_RESTRICT_MEMBERS)
def set_antilinkedchannel(update: Update, context: CallbackContext):
    message = update.effective_message
    chat = update.effective_chat
    args = context.args
    if len(args) > 0:
        s = args[0].lower()
        if s in ["yes", "on"]:
            if sql.status_pin(chat.id):
                sql.disable_pin(chat.id)
                sql.enable_pin(chat.id)
                message.reply_html(
                    f"ᴇɴᴀʙʟᴇᴅ ʟɪɴᴋᴇᴅ channel ᴘᴏsᴛ ᴅᴇʟᴇᴛɪᴏɴ ᴀɴᴅ ᴅɪsᴀʙʟᴇᴅ ᴀɴᴛɪ ᴄʜᴀɴɴᴇʟ ᴘɪɴ ɪɴ {html.escape(chat.title)}"
                )

            else:
                sql.enable_linked(chat.id)
                message.reply_html(
                    f"ᴇɴᴀʙʟᴇᴅ ʟɪɴᴋᴇᴅ ᴄʜᴀɴɴᴇʟ ᴘᴏsᴛ ᴅᴇʟᴇᴛɪᴏɴ ɪɴ {html.escape(chat.title)}. ᴍᴇssᴀɢᴇs sᴇɴᴛ ғʀᴏᴍ ᴛʜᴇ ʟɪɴᴋᴇᴅ ᴄʜᴀɴɴᴇʟ ᴡɪʟʟ ʙᴇ ᴅᴇʟᴇᴛᴇᴅ."
                )

        elif s in ["off", "no"]:
            sql.disable_linked(chat.id)
            message.reply_html(
                f"ᴅɪsᴀʙʟᴇᴅ ʟɪɴᴋᴇᴅ ᴄʜᴀɴɴᴇʟ ᴘᴏsᴛ ᴅᴇʟᴇᴛɪᴏɴ ɪɴ {html.escape(chat.title)}"
            )

        else:
            message.reply_text(f"ᴜɴʀᴇᴄᴏɢɴɪᴢᴇᴅ arguments {s}")
        return
    message.reply_html(
        f"ʟɪɴᴋᴇᴅ ᴄʜᴀɴɴᴇʟ ᴘᴏsᴛ ᴅᴇʟᴇᴛɪᴏɴ ɪs ᴄᴜʀʀᴇɴᴛʟʏ {sql.status_linked(chat.id)} ɪɴ {html.escape(chat.title)}"
    )


@Exonmsg(Filters.is_automatic_forward, group=111)
def eliminate_linked_channel_msg(update: Update, _: CallbackContext):
    message = update.effective_message
    chat = update.effective_chat
    if not sql.status_linked(chat.id):
        return
    try:
        message.delete()
    except TelegramError:
        return


@Exoncmd(command="antichannelpin", group=114)
@bot_admin
@user_admin(AdminPerms.CAN_RESTRICT_MEMBERS)
def set_antipinchannel(update: Update, context: CallbackContext):
    message = update.effective_message
    chat = update.effective_chat
    args = context.args
    if len(args) > 0:
        s = args[0].lower()
        if s in ["yes", "on"]:
            if sql.status_linked(chat.id):
                sql.disable_linked(chat.id)
                sql.enable_pin(chat.id)
                message.reply_html(
                    f"ᴅɪsᴀʙʟᴇᴅ ʟɪɴᴋᴇᴅ ᴄʜᴀɴɴᴇʟ ᴅᴇʟᴇᴛɪᴏɴ ᴀɴᴅ ᴇɴᴀʙʟᴇᴅ ᴀɴᴛɪ ᴄʜᴀɴɴᴇʟ ᴘɪɴ ɪɴ {html.escape(chat.title)}"
                )

            else:
                sql.enable_pin(chat.id)
                message.reply_html(
                    f"ᴇɴᴀʙʟᴇᴅ ᴀɴᴛɪ ᴄʜᴀɴɴᴇʟ ᴘɪɴ ɪɴ {html.escape(chat.title)}"
                )
        elif s in ["off", "no"]:
            sql.disable_pin(chat.id)
            message.reply_html(
                f"ᴅɪsᴀʙʟᴇᴅ ᴀɴᴛɪ ᴄʜᴀɴɴᴇʟ ᴘɪɴ ɪɴ {html.escape(chat.title)}"
            )
        else:
            message.reply_text(f"ᴜɴʀᴇᴄᴏɢɴɪᴢᴇᴅ ᴀʀɢᴜᴍᴇɴᴛs {s}")
        return
    message.reply_html(
        f"ʟɪɴᴋᴇᴅ ᴄʜᴀɴɴᴇʟ message ᴜɴᴘɪɴ ɪs ᴄᴜʀʀᴇɴᴛʟʏ {sql.status_pin(chat.id)} ɪɴ {html.escape(chat.title)}"
    )


@Exonmsg(Filters.is_automatic_forward | Filters.status_update.pinned_message, group=113)
def eliminate_linked_channel_msg(update: Update, _: CallbackContext):
    message = update.effective_message
    chat = update.effective_chat
    if not sql.status_pin(chat.id):
        return
    try:
        message.unpin()
    except TelegramError:
        return
