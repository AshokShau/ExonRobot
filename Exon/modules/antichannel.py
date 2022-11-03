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

from telegram import Update
from telegram.ext import CallbackContext
from telegram.ext.filters import Filters

from Exon.modules.helper_funcs.anonymous import AdminPerms, user_admin
from Exon.modules.helper_funcs.decorators import Exoncmd, Exonmsg
from Exon.modules.sql.antichannel_sql import (
    antichannel_status,
    disable_antichannel,
    enable_antichannel,
)


@Exoncmd(command="antichannelmode", group=100)
@user_admin(AdminPerms.CAN_RESTRICT_MEMBERS)
def set_antichannel(update: Update, context: CallbackContext):
    message = update.effective_message
    chat = update.effective_chat
    args = context.args
    if len(args) > 0:
        s = args[0].lower()
        if s in ["yes", "on"]:
            enable_antichannel(chat.id)
            message.reply_html(f"ᴇɴᴀʙʟᴇᴅ 𝗔𝗻𝘁𝗶𝗰𝗵𝗮𝗻𝗻𝗲𝗹 ɪɴ {html.escape(chat.title)}")
        elif s in ["off", "no"]:
            disable_antichannel(chat.id)
            message.reply_html(f"ᴅɪsᴀʙʟᴇᴅ 𝗔𝗻𝘁𝗶𝗰𝗵𝗮𝗻𝗻𝗲𝗹 ɪɴ {html.escape(chat.title)}")
        else:
            message.reply_text(f"ᴜɴʀᴇᴄᴏɢɴɪᴢᴇᴅ ᴀʀɢᴜᴍᴇɴᴛs {s}")
        return
    message.reply_html(
        f"ᴀɴᴛɪᴄʜᴀɴɴᴇʟ sᴇᴛᴛɪɴɢ ɪs ᴄᴜʀʀᴇɴᴛʟʏ {antichannel_status(chat.id)} ɪɴ {html.escape(chat.title)}"
    )


@Exonmsg(Filters.chat_type.groups, group=110)
def eliminate_channel(update: Update, context: CallbackContext):
    message = update.effective_message
    chat = update.effective_chat
    bot = context.bot
    if not antichannel_status(chat.id):
        return
    if (
        message.sender_chat
        and message.sender_chat.type == "channel"
        and not message.is_automatic_forward
    ):
        message.delete()
        sender_chat = message.sender_chat
        bot.ban_chat_sender_chat(sender_chat_id=sender_chat.id, chat_id=chat.id)


__mod_name__ = "𝙰ɴᴛɪ-ᴄʜᴀɴɴᴇʟ"

__help__ = """
 
        ⚠️ ᴡᴀʀɴɪɴɢ ⚠️
 
ɪғ ʏᴏᴜ ᴜsᴇ ᴛʜɪs ᴍᴏᴅᴇ, ᴛʜᴇ ʀᴇsᴜʟᴛ ɪs, ɪɴ ᴛʜᴇ ɢʀᴏᴜᴘ, ʏᴏᴜ ᴄᴀɴ'ᴛ ᴄʜᴀᴛ ᴜsɪɴɢ ᴛʜᴇ ᴄʜᴀɴɴᴇʟ ғᴏʀ ғᴏʀᴇᴠᴇʀ ɪғ ʏᴏᴜ ɢᴇᴛ ʙᴀɴɴᴇᴅ ᴏɴᴄᴇ,
ᴀɴᴛɪ ᴄʜᴀɴɴᴇʟ ᴍᴏᴅᴇ ɪs ᴀ ᴍᴏᴅᴇ ᴛᴏ ᴀᴜᴛᴏᴍᴀᴛɪᴄᴀʟʟʏ ʙᴀɴ ᴜsᴇʀs ᴡʜᴏ ᴄʜᴀᴛ ᴜsɪɴɢ ᴄʜᴀɴɴᴇʟs. 
ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ ᴄᴀɴ ᴏɴʟʏ ʙᴇ ᴜsᴇᴅ ʙʏ ᴀᴅᴍɪɴs.

/antichannelmode <'ᴏɴ/'ʏᴇs> : `ᴇɴᴀʙʟᴇs ᴀɴᴛɪ-ᴄʜᴀɴɴᴇʟ ᴍᴏᴅᴇ ʙᴀɴ`

/antichannelmode <'ᴏғғ/'ɴᴏ> : `ᴅɪsᴀʙʟᴇᴅ ᴀɴᴛɪ-ᴄʜᴀɴɴᴇʟ ᴍᴏᴅᴇ ʙᴀɴ`

/cleanlinked on  :  `ᴇɴᴀʙʟᴇs ᴄʜᴀɴɴᴇʟ ʟɪɴᴋ`
 
/antichannelpin on  : `ᴀɴᴛɪ-ᴄʜᴀɴɴᴇʟ ᴘɪɴ ᴍᴏᴅᴇ`

/antiservice <'ᴏɴ/'ᴏғғ> : `ᴅᴇʟᴇᴛᴇ sᴇʀᴠɪᴄᴇ ᴍsɢ. `
"""
