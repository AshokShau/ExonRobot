import collections
import importlib

from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import CommandHandler, ContextTypes

from Exon import application, telethn
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
from Exon.modules.helper_funcs.chat_status import check_admin


@check_admin(only_dev=True)
async def load(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.effective_message
    text = message.text.split(" ", 1)[1]
    load_messasge = await message.reply_text(
        f"ᴀᴛᴛᴇᴍᴘᴛɪɴɢ ᴛᴏ ʟᴏᴀᴅ ᴍᴏᴅᴜʟᴇ : <b>{text}</b>",
        parse_mode=ParseMode.HTML,
    )

    try:
        imported_module = importlib.import_module("Exon.modules." + text)
    except:
        await load_messasge.edit_text("ᴅᴏᴇs ᴛʜᴀᴛ ᴍᴏᴅᴜʟᴇ ᴇᴠᴇɴ ᴇxɪsᴛ?")
        ʀᴇᴛᴜʀɴ

    if not hasattr(imported_module, "__mod_name__"):
        imported_module.__mod_name__ = imported_module.__name__

    if imported_module.__mod_name__.lower() not in IMPORTED:
        IMPORTED[imported_module.__mod_name__.lower()] = imported_module
    else:
        await load_messasge.edit_text("ᴍᴏᴅᴜʟᴇ ᴀʟʀᴇᴀᴅʏ ʟᴏᴀᴅᴇᴅ.")
        return
    if "__handlers__" in dir(imported_module):
        handlers = imported_module.__handlers__
        for handler in handlers:
            if not isinstance(handler, tuple):
                application.add_handler(handler)
            else:
                if isinstance(handler[0], collections.Callable):
                    callback, telethon_event = handler
                    telethn.add_event_handler(callback, telethon_event)
                else:
                    handler_name, priority = handler
                    application.add_handler(handler_name, priority)
    else:
        IMPORTED.pop(imported_module.__mod_name__.lower())
        await load_messasge.edit_text("ᴛʜᴇ ᴍᴏᴅᴜʟᴇ ᴄᴀɴɴᴏᴛ ʙᴇ ʟᴏᴀᴅᴇᴅ.")
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

    await load_messasge.edit_text(
        "sᴜᴄᴄᴇssғᴜʟʟʏ ʟᴏᴀᴅᴇᴅ ᴍᴏᴅᴜʟᴇ : <b>{}</b>".format(text),
        parse_mode=ParseMode.HTML,
    )


@check_admin(only_dev=True)
async def unload(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.effective_message
    text = message.text.split(" ", 1)[1]
    unload_messasge = await message.reply_text(
        f"ᴀᴛᴛᴇᴍᴘᴛɪɴɢ ᴛᴏ ᴜɴʟᴏᴀᴅ ᴍᴏᴅᴜʟᴇ : <b>{text}</b>",
        parse_mode=ParseMode.HTML,
    )

    try:
        imported_module = importlib.import_module("Exon.modules." + text)
    except:
        await unload_messasge.edit_text("ᴅᴏᴇs ᴛʜᴀᴛ ᴍᴏᴅᴜʟᴇ ᴇᴠᴇɴ ᴇxɪsᴛ?")
        return

    if not hasattr(imported_module, "__mod_name__"):
        imported_module.__mod_name__ = imported_module.__name__
    if imported_module.__mod_name__.lower() in IMPORTED:
        IMPORTED.pop(imported_module.__mod_name__.lower())
    else:
        await unload_messasge.edit_text("ᴄᴀɴ'ᴛ ᴜɴʟᴏᴀᴅ sᴏᴍᴇᴛʜɪɴɢ ᴛʜᴀᴛ ɪsɴ'ᴛ ʟᴏᴀᴅᴇᴅ.")
        return
    if "__handlers__" in dir(imported_module):
        handlers = imported_module.__handlers__
        for handler in handlers:
            if isinstance(handler, bool):
                await unload_messasge.edit_text("ᴛʜɪs ᴍᴏᴅᴜʟᴇ ᴄᴀɴ'ᴛ ʙᴇ ᴜɴʟᴏᴀᴅᴇᴅ!")
                return
            elif not isinstance(handler, tuple):
                application.remove_handler(handler)
            else:
                if isinstance(handler[0], collections.Callable):
                    callback, telethon_event = handler
                    telethn.remove_event_handler(callback, telethon_event)
                else:
                    handler_name, priority = handler
                    application.remove_handler(handler_name, priority)
    else:
        await unload_messasge.edit_text("ᴛʜᴇ ᴍᴏᴅᴜʟᴇ ᴄᴀɴɴᴏᴛ ʙᴇ ᴜɴʟᴏᴀᴅᴇᴅ.")
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

    await unload_messasge.edit_text(
        f"sᴜᴄᴄᴇssғᴜʟʟʏ ᴜɴʟᴏᴀᴅᴇᴅ ᴍᴏᴅᴜʟᴇ : <b>{text}</b>",
        parse_mode=ParseMode.HTML,
    )


@check_admin(only_sudo=True)
async def listmodules(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.effective_message
    module_list = []

    for helpable_module in HELPABLE:
        helpable_module_info = IMPORTED[helpable_module]
        file_info = IMPORTED[helpable_module_info.__mod_name__.lower()]
        file_name = file_info.__name__.rsplit("Exon.modules.", 1)[1]
        mod_name = file_info.__mod_name__
        module_list.append(f"- <code>{mod_name} ({file_name})</code>\n")
    module_list = "ғᴏʟʟᴏᴡɪɴɢ ᴍᴏᴅᴜʟᴇs ᴀʀᴇ ʟᴏᴀᴅᴇᴅ : \n\n" + "".join(module_list)
    await message.reply_text(module_list, parse_mode=ParseMode.HTML)


LOAD_HANDLER = CommandHandler("load", load, block=False)
UNLOAD_HANDLER = CommandHandler("unload", unload, block=False)
LISTMODULES_HANDLER = CommandHandler("listmodules", listmodules, block=False)

application.add_handler(LOAD_HANDLER)
application.add_handler(UNLOAD_HANDLER)
application.add_handler(LISTMODULES_HANDLER)

__mod_name__ = "𝐌ᴏᴅᴜʟᴇs"
