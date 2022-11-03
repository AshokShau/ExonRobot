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

import logging
import time

from pyrogram import filters
from pyrogram.errors.exceptions.bad_request_400 import (
    ChatAdminRequired,
    PeerIdInvalid,
    UsernameNotOccupied,
    UserNotParticipant,
)
from pyrogram.types import ChatPermissions, InlineKeyboardButton, InlineKeyboardMarkup

from Exon import BOT_USERNAME as asau
from Exon import DRAGONS as SUDO_USERS
from Exon import pgram as pbot
from Exon.modules.sql import forceSubscribe_sql as sql

logging.basicConfig(level=logging.INFO)

static_data_filter = filters.create(
    lambda _, __, query: query.data == "onUnMuteRequest"
)


@pbot.on_callback_query(static_data_filter)
def _onUnMuteRequest(client, cb):
    user_id = cb.from_user.id
    chat_id = cb.message.chat.id
    if chat_db := sql.fs_settings(chat_id):
        channel = chat_db.channel
        chat_member = client.get_chat_member(chat_id, user_id)
        if chat_member.restricted_by:
            if chat_member.restricted_by.id == (client.get_me()).id:
                try:
                    client.get_chat_member(channel, user_id)
                    client.unban_chat_member(chat_id, user_id)
                    cb.message.delete()
                    # if cb.message.reply_to_message.from_user.id == user_id:
                    # cb.message.delete()
                except UserNotParticipant:
                    client.answer_callback_query(
                        cb.id,
                        text=f"❗ ᴊᴏɪɴ ᴏᴜʀ @{channel} ᴄʜᴀɴɴᴇʟ ᴀɴᴅ ᴘʀᴇss 'ᴜɴᴍᴜᴛᴇ ᴍᴇ ʙᴜᴛᴛᴏɴ.",
                        show_alert=True,
                    )
            else:
                client.answer_callback_query(
                    cb.id,
                    text="❗ ʏᴏᴜ ʜᴀᴠᴇ ʙᴇᴇɴ ᴍᴜᴛᴇᴅ ʙʏ ᴀᴅᴍɪɴs ᴅᴜᴇ ᴛᴏ sᴏᴍᴇ ᴏᴛʜᴇʀ ʀᴇᴀsᴏɴ.",
                    show_alert=True,
                )
        elif (
            client.get_chat_member(chat_id, (client.get_me()).id).status
            == "administrator"
        ):
            client.answer_callback_query(
                cb.id,
                text="❗ ᴡᴀʀɴɪɴɢ! ᴅᴏɴ'ᴛ ᴘʀᴇss ᴛʜᴇ ʙᴜᴛᴛᴏɴ ᴡʜᴇɴ ʏᴏᴜ ᴄᴀɴ ᴛᴀʟᴋ.",
                show_alert=True,
            )

        else:
            client.send_message(
                chat_id,
                f"❗ **{cb.from_user.mention} ɪs ᴛʀʏɪɴɢ ᴛᴏ ᴜɴᴍᴜᴛᴇ ʜɪᴍ/ʜᴇʀ-sᴇʟғ ʙᴜᴛ i ᴄᴀɴ'ᴛ ᴜɴᴍᴜᴛᴇ ʜɪᴍ/her ʙᴇᴄᴀᴜsᴇ ɪ ᴀᴍ ɴᴏᴛ ᴀɴ ᴀᴅᴍɪɴ ɪɴ ᴛʜɪs ᴄʜᴀᴛ ᴀᴅᴅ ᴍᴇ ᴀs ᴀᴅᴍɪɴ ᴀɢᴀɪɴ.\n",
            )


@pbot.on_message(filters.text & ~filters.private, group=1)
def _check_member(client, message):
    chat_id = message.chat.id
    if chat_db := sql.fs_settings(chat_id):
        user_id = message.from_user.id
        if (
            client.get_chat_member(chat_id, user_id).status
            not in ("administrator", "creator")
            and user_id not in SUDO_USERS
        ):
            channel = chat_db.channel
            try:
                client.get_chat_member(channel, user_id)
            except UserNotParticipant:
                try:
                    sent_message = message.reply_text(
                        f"ᴡᴇʟᴄᴏᴍᴇ {message.from_user.mention} 🙏 \n **ʏᴏᴜ ʜᴀᴠᴇɴ'ᴛ ᴊᴏɪɴᴇᴅ ᴏᴜʀ @{channel} ᴄʜᴀɴɴᴇʟ ʏᴇᴛ**👷 \n \nᴘʟᴇᴀsᴇ ᴊᴏɪɴ [our channel](https://t.me/{channel}) ᴀɴᴅ ʜɪᴛ ᴛʜᴇ **ᴜɴᴍᴜᴛᴇ ᴍᴇ** ʙᴜᴛᴛᴏɴ. \n \n ",
                        disable_web_page_preview=True,
                        reply_markup=InlineKeyboardMarkup(
                            [
                                [
                                    InlineKeyboardButton(
                                        "ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ",
                                        url=f"https://t.me/{channel}",
                                    )
                                ],
                                [
                                    InlineKeyboardButton(
                                        "ᴜɴᴍᴜᴛᴇ ᴍᴇ",
                                        callback_data="onUnMuteRequest",
                                    )
                                ],
                            ]
                        ),
                    )

                    client.restrict_chat_member(
                        chat_id, user_id, ChatPermissions(can_send_messages=False)
                    )
                except ChatAdminRequired:
                    sent_message.edit(
                        "😕 **ɪ ᴀᴍ ɴᴏᴛ ᴀᴅᴍɪɴ ʜᴇʀᴇ..**\n__ɢɪᴠᴇ ᴍᴇ ʙᴀɴ ᴘᴇʀᴍɪssɪᴏɴs ᴀɴᴅ ʀᴇᴛʀʏ.. \n#ᴇɴᴅɪɴɢ ғsᴜʙ...."
                    )

            except ChatAdminRequired:
                client.send_message(
                    chat_id,
                    text=f"😕 **I ɴᴏᴛ ᴀɴ ᴀᴅᴍɪɴ ᴏғ @{channel} ᴄʜᴀɴɴᴇʟ.**\n__ɢɪᴠᴇ me ᴀᴅᴍɪɴ ᴏғ ᴛʜᴀᴛ ᴄʜᴀɴɴᴇʟ ᴀɴᴅ ʀᴇᴛʀʏ.\n#ᴇɴᴅɪɴɢ ғsᴜʙ....",
                )


@pbot.on_message(filters.command(["forcesubscribe", "fsub"]) & ~filters.private)
def config(client, message):
    user = client.get_chat_member(message.chat.id, message.from_user.id)
    if user.status == "creator" or user.user.id in SUDO_USERS:
        chat_id = message.chat.id
        if len(message.command) > 1:
            input_str = message.command[1]
            input_str = input_str.replace("@", "")
            if input_str.lower() in ("off", "no", "disable"):
                sql.disapprove(chat_id)
                message.reply_text("❌ **ғᴏʀᴄᴇ sᴜʙsᴄʀɪʙᴇ ɪs ᴅɪsᴀʙʟᴇᴅ sᴜᴄᴄᴇssғᴜʟʟʏ.**")
            elif input_str.lower() in ("clear"):
                sent_message = message.reply_text(
                    "**ᴜɴᴍᴜᴛɪɴɢ ᴀʟʟ ᴍᴇᴍʙᴇʀs ᴡʜᴏ ᴀʀᴇ ᴍᴜᴛᴇᴅ ʙʏ ᴍᴇ ...**"
                )
                try:
                    for chat_member in client.get_chat_members(
                        message.chat.id, filter="restricted"
                    ):
                        if chat_member.restricted_by.id == (client.get_me()).id:
                            client.unban_chat_member(chat_id, chat_member.user.id)
                            time.sleep(1)
                    sent_message.edit("✅ **ᴜɴᴍᴜᴛᴇᴅ ᴀʟʟ ᴍᴇᴍʙᴇʀs ᴡʜᴏ ᴀʀᴇ ᴍᴜᴛᴇᴅ ʙʏ ᴍᴇ.**")
                except ChatAdminRequired:
                    sent_message.edit(
                        "😕 **I ᴀᴍ ɴᴏᴛ ᴀɴ ᴀᴅᴍɪɴ ɪɴ ᴛʜɪs ᴄʜᴀᴛ.**\n__I ᴄᴀɴ'ᴛ ᴜɴᴍᴜᴛᴇ ᴍᴇᴍʙᴇʀs ʙᴇᴄᴀᴜsᴇ i ᴀᴍ ɴᴏᴛ ᴀɴ ᴀᴅᴍɪɴ ɪɴ ᴛʜɪs ᴄʜᴀᴛ ᴍᴀᴋᴇ ᴍᴇ ᴀᴅᴍɪɴ ᴡɪᴛʜ ʙᴀɴ ᴜsᴇʀ ᴘᴇʀᴍɪssɪᴏɴ.__"
                    )
            else:
                try:
                    client.get_chat_member(input_str, "me")
                    sql.add_channel(chat_id, input_str)
                    message.reply_text(
                        f"✅ **ғᴏʀᴄᴇ sᴜʙsᴄʀɪʙᴇ ɪs ᴇɴᴀʙʟᴇᴅ**\n__ғᴏʀᴄᴇ sᴜʙsᴄʀɪʙᴇ ɪs ᴇɴᴀʙʟᴇᴅ, ᴀʟʟ ᴛʜᴇ ɢʀᴏᴜᴘ ᴍᴇᴍʙᴇʀs ʜᴀᴠᴇ ᴛᴏ sᴜʙsᴄʀɪʙᴇ ᴛʜɪs [ᴄʜᴀɴɴᴇʟ](https://t.me/{input_str}) ɪɴ ᴏʀᴅᴇʀ ᴛᴏ sᴇɴᴅ ᴍᴇssᴀɢᴇs ɪɴ ᴛʜɪs group.",
                        disable_web_page_preview=True,
                    )
                except UserNotParticipant:
                    message.reply_text(
                        f"😕 **ɴᴏᴛ ᴀɴ ᴀᴅᴍɪɴ ɪɴ ᴛʜᴇ ᴄʜᴀɴɴᴇʟ**\n__I ᴀᴍ ɴᴏᴛ ᴀɴ ᴀᴅᴍɪɴ ɪɴ ᴛʜᴇ [ᴄʜᴀɴɴᴇʟ](https://t.me/{input_str}). ᴀᴅᴅ ᴍᴇ ᴀs ᴀ ᴀᴅᴍɪɴ ɪɴ ᴏʀᴅᴇʀ ᴛᴏ ᴇɴᴀʙʟᴇ ғᴏʀᴄᴇsᴜʙsᴄʀɪʙᴇ.",
                        disable_web_page_preview=True,
                    )
                except (UsernameNotOccupied, PeerIdInvalid):
                    message.reply_text("❗ **ɪɴᴠᴀʟɪᴅ ᴄʜᴀɴɴᴇʟ ᴜsᴇʀɴᴀᴍᴇ.**")
                except Exception as err:
                    message.reply_text(f"❗ **ᴇʀʀᴏʀ:** ```{err}```")
        elif sql.fs_settings(chat_id):
            message.reply_text(
                f"✅ **ғᴏʀᴄᴇ sᴜʙsᴄʀɪʙᴇ ɪs ᴇɴᴀʙʟᴇᴅ ɪɴ ᴛʜɪs ᴄʜᴀᴛ.**\n__ғᴏʀ ᴛʜɪs [ᴄʜᴀɴɴᴇʟ](https://t.me/{sql.fs_settings(chat_id).channel})__",
                disable_web_page_preview=True,
            )
        else:
            message.reply_text("❌ **ғᴏʀᴄᴇ sᴜʙsᴄʀɪʙᴇ ɪs ᴅɪsᴀʙʟᴇᴅ ɪɴ ᴛʜɪs ᴄʜᴀᴛ.**")
    else:
        message.reply_text(
            "❗ **ɢʀᴏᴜᴘ ᴄʀᴇᴀᴛᴏʀ ʀᴇǫᴜɪʀᴇᴅ**\n__ʏᴏᴜ ʜᴀᴠᴇ ᴛᴏ ʙᴇ ᴛʜᴇ ɢʀᴏᴜᴘ ᴄʀᴇᴀᴛᴏʀ ᴛᴏ ᴅᴏ ᴛʜᴀᴛ.__"
        )


__help__ = f"""
*ғᴏʀᴄᴇ ꜱᴜʙꜱᴄʀɪʙᴇ:*

❂ *Aʙɢ ᴄᴀɴ ᴍᴜᴛᴇ ᴍᴇᴍʙᴇʀꜱ ᴡʜᴏ ᴀʀᴇ ɴᴏᴛ ꜱᴜʙꜱᴄʀɪʙᴇᴅ ʏᴏᴜʀ ᴄʜᴀɴɴᴇʟ ᴜɴᴛɪʟ ᴛʜᴇʏ ꜱᴜʙꜱᴄʀɪʙᴇ*

❂ `ᴡʜᴇɴ ᴇɴᴀʙʟᴇᴅ ɪ ᴡɪʟʟ ᴍᴜᴛᴇ ᴜɴꜱᴜʙꜱᴄʀɪʙᴇᴅ ᴍᴇᴍʙᴇʀꜱ ᴀɴᴅ ꜱʜᴏᴡ ᴛʜᴇᴍ ᴀ ᴜɴᴍᴜᴛᴇ ʙᴜᴛᴛᴏɴ. ᴡʜᴇɴ ᴛʜᴇʏ ᴘʀᴇꜱꜱᴇᴅ ᴛʜᴇ ʙᴜᴛᴛᴏɴ ɪ ᴡɪʟʟ ᴜɴᴍᴜᴛᴇ ᴛʜᴇᴍ`

❂ *ꜱᴇᴛᴜᴘ*
*ᴏɴʟʏ ᴄʀᴇᴀᴛᴏʀ*
❂ [ᴀᴅᴅ ᴍᴇ ɪɴ ʏᴏᴜʀ ɢʀᴏᴜᴘ ᴀꜱ ᴀᴅᴍɪɴ](https://t.me/{asau}?startgroup=new)
❂ [ᴀᴅᴅ ᴍᴇ ɪɴ your ᴄʜᴀɴɴᴇʟ ᴀꜱ ᴀᴅᴍɪɴ](https://t.me/{asau}?startgroup=new)
 
*ᴄᴏᴍᴍᴍᴀɴᴅꜱ*
❂ /fsub channel username - `ᴛᴏ ᴛᴜʀɴ ᴏɴ ᴀɴᴅ 𝚜𝚎𝚝𝚞𝚙 ᴛʜᴇ ᴄʜᴀɴɴᴇʟ.`

  💡*ᴅᴏ ᴛʜɪꜱ ғɪʀꜱᴛ...*
❂ /fsub - `ᴛᴏ ɢᴇᴛ ᴛʜᴇ ᴄᴜʀʀᴇɴᴛ ꜱᴇᴛᴛɪɴɢꜱ.`

❂ /fsub disable - `ᴛᴏ ᴛᴜʀɴ ᴏғ ғᴏʀᴄᴇꜱᴜʙꜱᴄʀɪʙᴇ..`

  💡`ɪғ ʏᴏᴜ ᴅɪꜱᴀʙʟᴇ ғꜱᴜʙ`, `ʏᴏᴜ ɴᴇᴇᴅ ᴛᴏ ꜱᴇᴛ ᴀɢᴀɪɴ ғᴏʀ ᴡᴏʀᴋɪɴɢ` /fsub channel username
  
❂ /fsub clear - `ᴛᴏ ᴜɴᴍᴜᴛᴇ ᴀʟʟ ᴍᴇᴍʙᴇʀꜱ ᴡʜᴏ ᴍᴜᴛᴇᴅ ʙʏ ᴍᴇ.`
"""
__mod_name__ = "𝙵-sᴜʙ"
