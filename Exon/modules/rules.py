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

from typing import Optional

from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
    ParseMode,
    Update,
    User,
)
from telegram.error import BadRequest
from telegram.ext import CallbackContext, CommandHandler, Filters
from telegram.utils.helpers import escape_markdown

import Exon.modules.sql.rules_sql as sql
from Exon import dispatcher
from Exon.modules.helper_funcs.chat_status import user_admin
from Exon.modules.helper_funcs.string_handling import markdown_parser


def get_rules(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    send_rules(update, chat_id)


# Do not async - not from a handler
def send_rules(update, chat_id, from_pm=False):
    bot = dispatcher.bot
    user = update.effective_user  # type: Optional[User]
    reply_msg = update.message.reply_to_message
    try:
        chat = bot.get_chat(chat_id)
    except BadRequest as excp:
        if excp.message == "ᴄʜᴀᴛ ɴᴏᴛ ғᴏᴜɴᴅ" and from_pm:
            bot.send_message(
                user.id,
                "The ʀᴜʟᴇs sʜᴏʀᴛᴄᴜᴛ ғᴏʀ ᴛʜɪs ᴄʜᴀᴛ ʜᴀsɴ'ᴛ ʙᴇᴇɴ sᴇᴛ ᴘʀᴏᴘᴇʀʟʏ! ᴀsᴋ ᴀᴅᴍɪɴs to "
                "ғɪx ᴛʜɪs.\nMaybe ᴛʜᴇʏ ғᴏʀɢᴏᴛ ᴛʜᴇ ʜʏᴘʜᴇɴ ɪɴ ɪᴅ",
            )
            return
        raise

    rules = sql.get_rules(chat_id)
    text = f"ᴛʜᴇ ʀᴜʟᴇs ғᴏʀ *{escape_markdown(chat.title)}* ᴀʀᴇ:\n\n{rules}"

    if from_pm and rules:
        bot.send_message(
            user.id,
            text,
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
        )
    elif from_pm:
        bot.send_message(
            user.id,
            "ᴛʜᴇ ɢʀᴏᴜᴘ ᴀᴅᴍɪɴs ʜᴀᴠᴇɴ'ᴛ sᴇᴛ ᴀɴʏ ʀᴜʟᴇs ғᴏʀ ᴛʜɪs ᴄʜᴀᴛ ʏᴇᴛ. "
            "ᴛʜɪs ᴘʀᴏʙᴀʙʟʏ ᴅᴏᴇsɴ'ᴛ ᴍᴇᴀɴ ɪᴛ's ʟᴀᴡʟᴇss ᴛʜᴏᴜɢʜ...!",
        )
    elif rules and reply_msg:
        reply_msg.reply_text(
            "ᴘʟᴇᴀsᴇ ᴄʟɪᴄᴋ ᴛʜᴇ ʙᴜᴛᴛᴏɴ ʙᴇʟᴏᴡ ᴛᴏ sᴇᴇ ᴛʜᴇ ʀᴜʟᴇs.",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text="ʀᴜʟᴇs",
                            url=f"t.me/{bot.username}?start={chat_id}",
                        ),
                    ],
                ],
            ),
        )
    elif rules:
        update.effective_message.reply_text(
            "ᴘʟᴇᴀsᴇ ᴄʟɪᴄᴋ ᴛʜᴇ ʙᴜᴛᴛᴏɴ ʙᴇʟᴏᴡ ᴛᴏ sᴇᴇ ᴛʜᴇ ʀᴜʟᴇs.",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text="ʀᴜʟᴇs",
                            url=f"t.me/{bot.username}?start={chat_id}",
                        ),
                    ],
                ],
            ),
        )
    else:
        update.effective_message.reply_text(
            "ᴛʜᴇ ɢʀᴏᴜᴘ ᴀᴅᴍɪɴs ʜᴀᴠᴇɴ sᴇᴛ ᴀɴʏ ʀᴜʟᴇs ғᴏʀ ᴛʜɪs ᴄʜᴀᴛ ʏᴇᴛ. "
            "ᴛʜɪs ᴘʀᴏʙᴀʙʟʏ ᴅᴏᴇsɴ'ᴛ ᴍᴇᴀɴ ɪᴛ's ʟᴀᴡʟᴇss ᴛʜᴏᴜɢʜ \nᴇɴᴊᴏʏ...!",
        )


@user_admin
def set_rules(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    msg = update.effective_message  # type: Optional[Message]
    raw_text = msg.text
    args = raw_text.split(None, 1)  # use python's maxsplit to separate cmd and args
    if len(args) == 2:
        txt = args[1]
        offset = len(txt) - len(raw_text)  # set correct offset relative to command
        markdown_rules = markdown_parser(
            txt,
            entities=msg.parse_entities(),
            offset=offset,
        )

        sql.set_rules(chat_id, markdown_rules)
        update.effective_message.reply_text("sᴜᴄᴄᴇssғᴜʟʟʏ sᴇᴛ ʀᴜʟᴇs ғᴏʀ ᴛʜɪs ɢʀᴏᴜᴘ.")


@user_admin
def clear_rules(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    sql.set_rules(chat_id, "")
    update.effective_message.reply_text("sᴜᴄᴄᴇssғᴜʟʟʏ ᴄʟᴇᴀʀᴇᴅ ʀᴜʟᴇs!")


def __stats__():
    return f"•➥ {sql.num_chats()} ᴄʜᴀᴛs ʜᴀᴠᴇ ʀᴜʟᴇs sᴇᴛ."


def __import_data__(chat_id, data):
    # set chat rules
    rules = data.get("info", {}).get("rules", "")
    sql.set_rules(chat_id, rules)


def __migrate__(old_chat_id, new_chat_id):
    sql.migrate_chat(old_chat_id, new_chat_id)


def __chat_settings__(chat_id, user_id):
    return f"ᴛʜɪs ᴄʜᴀᴛ ʜᴀs ʜᴀᴅ ɪᴛ's  ʀᴜʟᴇs sᴇᴛ: `{bool(sql.get_rules(chat_id))}`"


__mod_name__ = "𝚁ᴜʟᴇs"

GET_RULES_HANDLER = CommandHandler(
    "rules", get_rules, filters=Filters.chat_type.groups, run_async=True
)
SET_RULES_HANDLER = CommandHandler(
    "setrules", set_rules, filters=Filters.chat_type.groups, run_async=True
)
RESET_RULES_HANDLER = CommandHandler(
    "clearrules", clear_rules, filters=Filters.chat_type.groups, run_async=True
)

dispatcher.add_handler(GET_RULES_HANDLER)
dispatcher.add_handler(SET_RULES_HANDLER)
dispatcher.add_handler(RESET_RULES_HANDLER)
