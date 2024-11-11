import importlib

from ptbmod import verifyAnonymousAdmin
from telegram import Update
from telegram.ext import CallbackQueryHandler

from Telegram import HELP_COMMANDS, LOGGER, application
from Telegram.modules import ALL_MODULES
from Telegram.modules.errorHandler import error_handler


def setup() -> None:
    """
    Initialize the application and load all modules.

    This function imports all the modules in the modules directory, adds them to
    HELP_COMMANDS and starts the application with polling.

    Raises:
        SystemExit: If duplicate modules are found.
    """
    for single in ALL_MODULES:
        imported_module = importlib.import_module(f"Telegram.modules.{single}")
        plugin_name = getattr(imported_module, "__mod_name__", single).lower()
        plugin_dict_name = f"modules.{plugin_name}"

        plugin_help = getattr(imported_module, "__help__", None)
        if not plugin_help:
            continue

        if plugin_dict_name in HELP_COMMANDS:
            raise SystemExit(f"Duplicate modules found: {plugin_dict_name}.")

        HELP_COMMANDS[plugin_dict_name] = {
            "buttons": getattr(imported_module, "__buttons__", []),
            "alt_cmd": getattr(imported_module, "__alt_name__", []) + [plugin_name],
            "help_msg": plugin_help,
        }

    LOGGER.info(
        "Total Modules: %s, Loaded Help Modules: %s",
        len(ALL_MODULES),
        len(HELP_COMMANDS),
    )

    application.add_handler(
        CallbackQueryHandler(verifyAnonymousAdmin, pattern=r"^anon.")
    )
    application.add_error_handler(error_handler)

    application.run_polling(
        drop_pending_updates=True,
        allowed_updates=Update.ALL_TYPES,
    )


if __name__ == "__main__":
    setup()
