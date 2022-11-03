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

import collections
import importlib

from telegram import ParseMode, Update
from telegram.ext import CallbackContext, CommandHandler

from Exon import dispatcher, telethn
from Exon.__main__ import (
    CHAT_SETTINGS,
    DATA_EXPORT,
    DATA_IMPORT,
    HELPABLE,
    IMPORTED,
    MIGRATEABLE,
    STATS,
    USER_INFO,
    USER_SETTINGS,
)
from Exon.modules.helper_funcs.chat_status import dev_plus, sudo_plus


@dev_plus
def load(update: Update, context: CallbackContext):
    message = update.effective_message
    text = message.text.split(" ", 1)[1]
    load_messasge = message.reply_text(
        f"ᴀᴛᴛᴇᴍᴘᴛɪɴɢ ᴛᴏ ʟᴏᴀᴅ ᴍᴏᴅᴜʟᴇ : <b>{text}</b>",
        parse_mode=ParseMode.HTML,
    )

    try:
        imported_module = importlib.import_module(f"Exon.modules.{text}")
    except:
        load_messasge.edit_text("ᴅᴏᴇs ᴛʜᴀᴛ ᴍᴏᴅᴜʟᴇ ᴇᴠᴇɴ ᴇxɪsᴛ?")
        return

    if not hasattr(imported_module, "__mod_name__"):
        imported_module.__mod_name__ = imported_module.__name__

    if imported_module.__mod_name__.lower() not in IMPORTED:
        IMPORTED[imported_module.__mod_name__.lower()] = imported_module
    else:
        load_messasge.edit_text("ᴍᴏᴅᴜʟᴇ ᴀʟʀᴇᴀᴅʏ ʟᴏᴀᴅᴇᴅ.")
        return
    if "__handlers__" in dir(imported_module):
        handlers = imported_module.__handlers__
        for handler in handlers:
            if not isinstance(handler, tuple):
                dispatcher.add_handler(handler)
            elif isinstance(handler[0], collections.Callable):
                callback, telethon_event = handler
                telethn.add_event_handler(callback, telethon_event)
            else:
                handler_name, priority = handler
                dispatcher.add_handler(handler_name, priority)
    else:
        IMPORTED.pop(imported_module.__mod_name__.lower())
        load_messasge.edit_text("ᴛʜᴇ ᴍᴏᴅᴜʟᴇ ᴄᴀɴɴᴏᴛ ʙᴇ ʟᴏᴀᴅᴇᴅ.")
        return

    if hasattr(imported_module, "__help__") and imported_module.__help__:
        HELPABLE[imported_module.__mod_name__.lower()] = imported_module

    # Chats to migrate on chat_migrated events
    if hasattr(imported_module, "__migrate__"):
        MIGRATEABLE.append(imported_module)

    if hasattr(imported_module, "__stats__"):
        STATS.append(imported_module)

    if hasattr(imported_module, "__user_info__"):
        USER_INFO.append(imported_module)

    if hasattr(imported_module, "__import_data__"):
        DATA_IMPORT.append(imported_module)

    if hasattr(imported_module, "__export_data__"):
        DATA_EXPORT.append(imported_module)

    if hasattr(imported_module, "__chat_settings__"):
        CHAT_SETTINGS[imported_module.__mod_name__.lower()] = imported_module

    if hasattr(imported_module, "__user_settings__"):
        USER_SETTINGS[imported_module.__mod_name__.lower()] = imported_module

    load_messasge.edit_text(
        f"sᴜᴄᴄᴇssғᴜʟʟʏ ʟᴏᴀᴅᴇᴅ ᴍᴏᴅᴜʟᴇ : <b>{text}</b>",
        parse_mode=ParseMode.HTML,
    )


@dev_plus
def unload(update: Update, context: CallbackContext):
    message = update.effective_message
    text = message.text.split(" ", 1)[1]
    unload_messasge = message.reply_text(
        f"ᴀᴛᴛᴇᴍᴘᴛɪɴɢ ᴛᴏ ᴜɴʟᴏᴀᴅ ᴍᴏᴅᴜʟᴇ : <b>{text}</b>",
        parse_mode=ParseMode.HTML,
    )

    try:
        imported_module = importlib.import_module(f"Exon.modules.{text}")
    except:
        unload_messasge.edit_text("ᴅᴏᴇs ᴛʜᴀᴛ ᴍᴏᴅᴜʟᴇ ᴇᴠᴇɴ ᴇxɪsᴛ?")
        return

    if not hasattr(imported_module, "__mod_name__"):
        imported_module.__mod_name__ = imported_module.__name__
    if imported_module.__mod_name__.lower() in IMPORTED:
        IMPORTED.pop(imported_module.__mod_name__.lower())
    else:
        unload_messasge.edit_text("ᴄᴀɴ'ᴛ ᴜɴʟᴏᴀᴅ sᴏᴍᴇᴛʜɪɴɢ that isn't loaded.")
        return
    if "__handlers__" in dir(imported_module):
        handlers = imported_module.__handlers__
        for handler in handlers:
            if isinstance(handler, bool):
                unload_messasge.edit_text("ᴛʜɪs ᴍᴏᴅᴜʟᴇ ᴄᴀɴ'ᴛ ʙᴇ ᴜɴʟᴏᴀᴅᴇᴅ!")
                return
            if not isinstance(handler, tuple):
                dispatcher.remove_handler(handler)
            elif isinstance(handler[0], collections.Callable):
                callback, telethon_event = handler
                telethn.remove_event_handler(callback, telethon_event)
            else:
                handler_name, priority = handler
                dispatcher.remove_handler(handler_name, priority)
    else:
        unload_messasge.edit_text("ᴛʜᴇ ᴍᴏᴅᴜʟᴇ ᴄᴀɴɴᴏᴛ ʙᴇ ᴜɴʟᴏᴀᴅᴇᴅ.")
        return

    if hasattr(imported_module, "__help__") and imported_module.__help__:
        HELPABLE.pop(imported_module.__mod_name__.lower())

    # Chats to migrate on chat_migrated events
    if hasattr(imported_module, "__migrate__"):
        MIGRATEABLE.remove(imported_module)

    if hasattr(imported_module, "__stats__"):
        STATS.remove(imported_module)

    if hasattr(imported_module, "__user_info__"):
        USER_INFO.remove(imported_module)

    if hasattr(imported_module, "__import_data__"):
        DATA_IMPORT.remove(imported_module)

    if hasattr(imported_module, "__export_data__"):
        DATA_EXPORT.remove(imported_module)

    if hasattr(imported_module, "__chat_settings__"):
        CHAT_SETTINGS.pop(imported_module.__mod_name__.lower())

    if hasattr(imported_module, "__user_settings__"):
        USER_SETTINGS.pop(imported_module.__mod_name__.lower())

    unload_messasge.edit_text(
        f"sᴜᴄᴄᴇssғᴜʟʟʏ ᴜɴʟᴏᴀᴅᴇᴅ ᴍᴏᴅᴜʟᴇ : <b>{text}</b>",
        parse_mode=ParseMode.HTML,
    )


@sudo_plus
def listmodules(update: Update, context: CallbackContext):
    message = update.effective_message
    module_list = []

    for helpable_module in HELPABLE:
        helpable_module_info = IMPORTED[helpable_module]
        file_info = IMPORTED[helpable_module_info.__mod_name__.lower()]
        file_name = file_info.__name__.rsplit("Exon.modules.", 1)[1]
        mod_name = file_info.__mod_name__
        module_list.append(f"- <code>{mod_name} ({file_name})</code>\n")
    module_list = "ғᴏʟʟᴏᴡɪɴɢ ᴍᴏᴅᴜʟᴇs ᴀʀᴇ ʟᴏᴀᴅᴇᴅ : \n\n" + "".join(module_list)
    message.reply_text(module_list, parse_mode=ParseMode.HTML)


LOAD_HANDLER = CommandHandler("load", load, run_async=True)
UNLOAD_HANDLER = CommandHandler("unload", unload, run_async=True)
LISTMODULES_HANDLER = CommandHandler("listmodules", listmodules, run_async=True)

dispatcher.add_handler(LOAD_HANDLER)
dispatcher.add_handler(UNLOAD_HANDLER)
dispatcher.add_handler(LISTMODULES_HANDLER)

__mod_name__ = "ᴍᴏᴅᴜʟᴇs"
