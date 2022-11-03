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

from typing import List, Optional, Union

from telegram.ext import (
    CallbackQueryHandler,
    CommandHandler,
    InlineQueryHandler,
    MessageHandler,
)
from telegram.ext.filters import MessageFilter

from Exon import LOGGER
from Exon import dispatcher as d
from Exon.modules.disable import DisableAbleCommandHandler, DisableAbleMessageHandler


class ExonHandler:
    def __init__(self, d):
        self._dispatcher = d

    def command(
        self,
        command: str,
        filters: Optional[MessageFilter] = None,
        admin_ok: bool = False,
        pass_args: bool = False,
        pass_chat_data: bool = False,
        run_async: bool = True,
        can_disable: bool = True,
        group: Optional[Union[int, str]] = 40,
    ):
        def _command(func):
            try:
                if can_disable:
                    self._dispatcher.add_handler(
                        DisableAbleCommandHandler(
                            command,
                            func,
                            filters=filters,
                            run_async=run_async,
                            pass_args=pass_args,
                            admin_ok=admin_ok,
                        ),
                        group,
                    )
                else:
                    self._dispatcher.add_handler(
                        CommandHandler(
                            command,
                            func,
                            filters=filters,
                            run_async=run_async,
                            pass_args=pass_args,
                        ),
                        group,
                    )
                LOGGER.debug(
                    f"[ᴇxᴏɴᴄᴍᴅ] ʟᴏᴀᴅᴇᴅ ʜᴀɴᴅʟᴇʀ {command} ғᴏʀ ғᴜɴᴄᴛɪᴏɴ {func.__name__} ɪɴ ɢʀᴏᴜᴘ {group}"
                )
            except TypeError:
                if can_disable:
                    self._dispatcher.add_handler(
                        DisableAbleCommandHandler(
                            command,
                            func,
                            filters=filters,
                            run_async=run_async,
                            pass_args=pass_args,
                            admin_ok=admin_ok,
                            pass_chat_data=pass_chat_data,
                        )
                    )
                else:
                    self._dispatcher.add_handler(
                        CommandHandler(
                            command,
                            func,
                            filters=filters,
                            run_async=run_async,
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
        run_async: bool = True,
        group: Optional[Union[int, str]] = 60,
        friendly=None,
    ):
        def _message(func):
            try:
                if can_disable:
                    self._dispatcher.add_handler(
                        DisableAbleMessageHandler(
                            pattern, func, friendly=friendly, run_async=run_async
                        ),
                        group,
                    )
                else:
                    self._dispatcher.add_handler(
                        MessageHandler(pattern, func, run_async=run_async), group
                    )
                LOGGER.debug(
                    f"[ᴇxᴏɴᴍsɢ] Loaded filter pattern {pattern} for function {func.__name__} in group {group}"
                )
            except TypeError:
                if can_disable:
                    self._dispatcher.add_handler(
                        DisableAbleMessageHandler(
                            pattern, func, friendly=friendly, run_async=run_async
                        )
                    )
                else:
                    self._dispatcher.add_handler(
                        MessageHandler(pattern, func, run_async=run_async)
                    )
                LOGGER.debug(
                    f"[ᴇxᴏɴᴍsɢ] ʟᴏᴀᴅᴇᴅ ғɪʟᴛᴇʀ ᴘᴀᴛᴛᴇʀɴ {pattern} ғᴏʀ ғᴜɴᴄᴛɪᴏɴ {func.__name__}"
                )

            return func

        return _message

    def callbackquery(self, pattern: str = None, run_async: bool = True):
        def _callbackquery(func):
            self._dispatcher.add_handler(
                CallbackQueryHandler(
                    pattern=pattern, callback=func, run_async=run_async
                )
            )
            LOGGER.debug(
                f"[ᴇxᴏɴᴄᴀʟʟʙᴀᴄᴋ] ʟᴏᴀᴅᴇᴅ ᴄᴀʟʟʙᴀᴄᴋǫᴜᴇʀʏ ʜᴀɴᴅʟᴇʀ ᴡɪᴛʜ ᴘᴀᴛᴛᴇʀɴ {pattern} ғᴏʀ ғᴜɴᴄᴛɪᴏɴ {func.__name__}"
            )
            return func

        return _callbackquery

    def inlinequery(
        self,
        pattern: Optional[str] = None,
        run_async: bool = True,
        pass_user_data: bool = True,
        pass_chat_data: bool = True,
        chat_types: List[str] = None,
    ):
        def _inlinequery(func):
            self._dispatcher.add_handler(
                InlineQueryHandler(
                    pattern=pattern,
                    callback=func,
                    run_async=run_async,
                    pass_user_data=pass_user_data,
                    pass_chat_data=pass_chat_data,
                    chat_types=chat_types,
                )
            )
            LOGGER.debug(
                f"[ᴇxᴏɴɪɴʟɪɴᴇ] ʟᴏᴀᴅᴇᴅ ɪɴʟɪɴᴇǫᴜᴇʀʏ ʜᴀɴᴅʟᴇʀ ᴡɪᴛʜ ᴘᴀᴛᴛᴇʀɴ {pattern} ғᴏʀ ғᴜɴᴄᴛɪᴏɴ {func.__name__} | ᴘᴀssᴇs ᴜsᴇʀ ᴅᴀᴛᴀ: {pass_user_data} | ᴘᴀssᴇs ᴄʜᴀᴛ ᴅᴀᴛᴀ: {pass_chat_data} | ᴄʜᴀᴛ ᴛʏᴘᴇs: {chat_types}"
            )
            return func

        return _inlinequery


Exoncmd = ExonHandler(d).command
Exonmsg = ExonHandler(d).message
Exoncallback = ExonHandler(d).callbackquery
Exoninline = ExonHandler(d).inlinequery
