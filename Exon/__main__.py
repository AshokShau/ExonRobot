import importlib

from telegram import Update
from telegram.ext import ApplicationHandlerStop, ContextTypes, MessageHandler, filters

from Exon import LOGGER as log
from Exon import exon
from Exon.modules import ALL_MODULES

IMPORTED = {}
MIGRATEABLE = []
HELPABLE = {}
STATS = []
DATA_IMPORT = []
DATA_EXPORT = []

for module_name in ALL_MODULES:
    imported_module = importlib.import_module("Exon.modules." + module_name)
    if not hasattr(imported_module, "__mod_name__"):
        imported_module.__mod_name__ = imported_module.__name__

    if imported_module.__mod_name__.lower() not in IMPORTED:
        IMPORTED[imported_module.__mod_name__.lower()] = imported_module
    else:
        raise Exception("ᴄᴀɴ'ᴛ ʜᴀᴠᴇ ᴛᴡᴏ ᴍᴏᴅᴜʟᴇs ᴡɪᴛʜ ᴛʜᴇ sᴀᴍᴇ ɴᴀᴍᴇ! ᴘʟᴇᴀsᴇ ᴄʜᴀɴɢᴇ ᴏɴᴇ")

    if hasattr(imported_module, "get_help") and imported_module.get_help:
        HELPABLE[imported_module.__mod_name__.lower()] = imported_module

    if hasattr(imported_module, "__migrate__"):
        MIGRATEABLE.append(imported_module)

    if hasattr(imported_module, "__stats__"):
        STATS.append(imported_module)

    if hasattr(imported_module, "__import_data__"):
        DATA_IMPORT.append(imported_module)

    if hasattr(imported_module, "__export_data__"):
        DATA_EXPORT.append(imported_module)


async def migrate_chats(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    msg = update.effective_message
    if msg.migrate_to_chat_id:
        old_chat = update.effective_chat.id
        new_chat = msg.migrate_to_chat_id
    elif msg.migrate_from_chat_id:
        old_chat = msg.migrate_from_chat_id
        new_chat = update.effective_chat.id
    else:
        return

    log("ᴍɪɢʀᴀᴛɪɴɢ ғʀᴏᴍ %s, ᴛᴏ %s", str(old_chat), str(new_chat))
    for mod in MIGRATEABLE:
        mod.__migrate__(old_chat, new_chat)

    log.info("sᴜᴄᴄᴇssғᴜʟʟʏ ᴍɪɢʀᴀᴛᴇᴅ!")
    raise ApplicationHandlerStop


def main() -> None:
    exon.add_handler(MessageHandler(filters.StatusUpdate.MIGRATE, migrate_chats))

    log.info(f"ʙᴏᴛ sᴛᴀʀᴛᴇᴅ.")
    exon.run_polling(
        drop_pending_updates=True, allowed_updates=Update.ALL_TYPES, close_loop=False
    )


if __name__ == "__main__":
    log.info("sᴜᴄᴄᴇssғᴜʟʟʏ ʟᴏᴀᴅᴇᴅ ᴍᴏᴅᴜʟᴇs: ")
    main()
