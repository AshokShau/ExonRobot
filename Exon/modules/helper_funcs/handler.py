from typing import List, Optional, Union

from telegram.ext import (
    CallbackQueryHandler,
    CommandHandler,
    InlineQueryHandler,
    MessageHandler,
)
from telegram.ext.filters import MessageFilter

from Exon import LOGGER
from Exon import application as n
try:
    from Exon.modules.disable import DisableAbleCommandHandler, DisableAbleMessageHandler
except ImportError as e:
    print(e)

class ExonTelegramHandler:
    def __init__(self, n):
        self._Application = n

    def command(
        self,
        command: str,
        filters: Optional[MessageFilter] = None,
        admin_ok: bool = True,
        pass_args: bool = False,
        pass_chat_data: bool = False,
        block: bool = False,
        can_disable: bool = True,
        group: Optional[Union[int, str]] = 40,
    ):
        def _command(func):
            try:
                if can_disable:
                    self._Application.add_handler(
                        DisableAbleCommandHandler(
                            command,
                            func,
                            filters=filters,
                            block=block,
                            pass_args=pass_args,
                            admin_ok=admin_ok,
                        ),
                        group,
                    )
                else:
                    self._Application.add_handler(
                        CommandHandler(
                            command,
                            func,
                            filters=filters,
                            block=block,
                            pass_args=pass_args,
                        ),
                        group,
                    )
                LOGGER.debug(
                    f"[ExonCMD] Loaded handler {command} for function {func.__name__} in group {group}"
                )
            except TypeError:
                if can_disable:
                    self._Application.add_handler(
                        DisableAbleCommandHandler(
                            command,
                            func,
                            filters=filters,
                            block=block,
                            pass_args=pass_args,
                            admin_ok=admin_ok,
                            pass_chat_data=pass_chat_data,
                        )
                    )
                else:
                    self._Application.add_handler(
                        CommandHandler(
                            command,
                            func,
                            filters=filters,
                            block=block,
                            pass_args=pass_args,
                            pass_chat_data=pass_chat_data,
                        )
                    )
                LOGGER.debug(
                    f"[ExonCMD] Loaded handler {command} for function {func.__name__}"
                )

            return func

        return _command

    def message(
        self,
        pattern: Optional[str] = None,
        can_disable: bool = True,
        block: bool = False,
        group: Optional[Union[int, str]] = 60,
        friendly=None,
    ):
        def _message(func):
            try:
                if can_disable:
                    self._Application.add_handler(
                        DisableAbleMessageHandler(
                            pattern, func, friendly=friendly, block=block
                        ),
                        group,
                    )
                else:
                    self._Application.add_handler(
                        MessageHandler(pattern, func, block=block), group
                    )
                LOGGER.debug(
                    f"[ExonMSG] Loaded filter pattern {pattern} for function {func.__name__} in group {group}"
                )
            except TypeError:
                if can_disable:
                    self._Application.add_handler(
                        DisableAbleMessageHandler(
                            pattern, func, friendly=friendly, block=block
                        )
                    )
                else:
                    self._Application.add_handler(
                        MessageHandler(pattern, func, block=block)
                    )
                LOGGER.debug(
                    f"[ExonMSG] Loaded filter pattern {pattern} for function {func.__name__}"
                )

            return func

        return _message

    def callbackquery(self, pattern: str = None, block: bool = True):
        def _callbackquery(func):
            self._Application.add_handler(
                CallbackQueryHandler(pattern=pattern, callback=func, block=block)
            )
            LOGGER.debug(
                f"[ExonCALLBACK] Loaded callbackquery handler with pattern {pattern} for function {func.__name__}"
            )
            return func

        return _callbackquery

    def inlinequery(
        self,
        pattern: Optional[str] = None,
        block: bool = False,
        pass_user_data: bool = True,
        pass_chat_data: bool = True,
        chat_types: List[str] = None,
    ):
        def _inlinequery(func):
            self._Application.add_handler(
                InlineQueryHandler(
                    pattern=pattern,
                    callback=func,
                    block=block,
                    pass_user_data=pass_user_data,
                    pass_chat_data=pass_chat_data,
                    chat_types=chat_types,
                )
            )
            LOGGER.debug(
                f"[ExonINLINE] Loaded inlinequery handler with pattern {pattern} for function {func.__name__} | PASSES "
                f"USER DATA: {pass_user_data} | PASSES CHAT DATA: {pass_chat_data} | CHAT TYPES: {chat_types}"
            )
            return func

        return _inlinequery


Exoncmd = ExonTelegramHandler(n).command
Exonmsg = ExonTelegramHandler(n).message
Exoncallback = ExonTelegramHandler(n).callbackquery
Exoninline = ExonTelegramHandler(n).inlinequery
