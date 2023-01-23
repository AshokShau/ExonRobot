import re
from typing import Dict, List, Optional, Tuple, Union

from pyrate_limiter import (
    BucketFullException,
    Duration,
    Limiter,
    MemoryListBucket,
    RequestRate,
)
from telegram import Update
from telegram.ext import CommandHandler, MessageHandler
from telegram.ext import filters as filters_module

import Exon.modules.sql.blacklistusers_sql as sql
from Exon import DEV_USERS, DRAGONS

ALLOW_EXCL = True

if ALLOW_EXCL:
    CMD_STARTERS = (
        "/",
        "!",
        ".",
        "-",
        "$",
        "*",
        "+",
    )
else:
    CMD_STARTERS = ("/",)


class AntiSpam:
    def __init__(self):
        self.whitelist = (DEV_USERS or []) + (DRAGONS or [])
        # Values are HIGHLY experimental, its recommended you pay attention to our commits as we will be adjusting the values over time with what suits best.
        Duration.CUSTOM = 15  # Custom duration, 15 seconds
        self.sec_limit = RequestRate(6, Duration.CUSTOM)  # 6 / Per 15 Seconds
        self.min_limit = RequestRate(20, Duration.MINUTE)  # 20 / Per minute
        self.hour_limit = RequestRate(100, Duration.HOUR)  # 100 / Per hour
        self.daily_limit = RequestRate(1000, Duration.DAY)  # 1000 / Per day
        self.limiter = Limiter(
            self.sec_limit,
            self.min_limit,
            self.hour_limit,
            self.daily_limit,
            bucket_class=MemoryListBucket,
        )

    def check_user(self, user):
        """
        Return True if user is to be ignored else False
        """
        if user in self.whitelist:
            return False
        try:
            self.limiter.try_acquire(user)
            return False
        except BucketFullException:
            return True


SpamChecker = AntiSpam()
MessageHandlerChecker = AntiSpam()


class CustomCommandHandler(CommandHandler):
    def __init__(self, command, callback, **kwargs):
        super().__init__(command, callback, **kwargs)

        if isinstance(command, str):
            commands = frozenset({command.lower()})
        else:
            commands = frozenset(x.lower() for x in command)
        for comm in commands:
            if not re.match(r"^[\da-z_]{1,32}$", comm):
                raise ValueError(f"ᴄᴏᴍᴍᴀɴᴅ `{comm}` ɪs ɴᴏᴛ ᴀ ᴠᴀʟɪᴅ ʙᴏᴛ ᴄᴏᴍᴍᴀɴᴅ")
        self.commands = commands

    def check_update(
        self, update
    ) -> Optional[Union[bool, Tuple[List[str], Optional[Union[bool, Dict]]]]]:
        if isinstance(update, Update) and update.effective_message:
            message = update.effective_message

            try:
                user_id = update.effective_user.id
            except:
                user_id = None

            if user_id:
                if sql.is_user_blacklisted(user_id):
                    return False

            if message.text and len(message.text) > 1:
                fst_word = message.text.split(None, 1)[0]
                if len(fst_word) > 1 and any(
                    fst_word.startswith(start) for start in CMD_STARTERS
                ):

                    args = message.text.split()[1:]
                    command_parts = fst_word[1:].split("@")
                    command_parts.append(message.get_bot().username)
                    if user_id == 1087968824:
                        user_id = update.effective_chat.id
                    if not (
                        command_parts[0].lower() in self.commands
                        and command_parts[1].lower()
                        == message.get_bot().username.lower()
                    ):
                        return None
                    if SpamChecker.check_user(user_id):
                        return None
                    filter_result = self.filters.check_update(update)
                    if filter_result:
                        return args, filter_result
                    return False
        return None

    def handle_update(self, update, exon, check_result, context=None):
        if context:
            self.collect_additional_context(context, update, exon, check_result)
            return self.callback(update, context)
        else:
            optional_args = self.collect_optional_args(exon, update, check_result)
            return self.callback(exon.bot, update, **optional_args)

    def collect_additional_context(
        self,
        context,
        update,
        exon,
        check_result: Optional[Union[bool, Tuple[List[str], Optional[bool]]]],
    ) -> None:
        if isinstance(check_result, tuple):
            context.args = check_result[0]
            if isinstance(check_result[1], dict):
                context.update(check_result[1])
                if isinstance(check_result[1], dict):
                    context.update(check_result[1])


class CustomMessageHandler(MessageHandler):
    def __init__(self, filters, callback, friendly="", allow_edit=False, **kwargs):
        super().__init__(filters, callback, **kwargs)
        if allow_edit is False:
            self.filters &= ~(
                filters_module.UpdateType.EDITED_MESSAGE
                | filters_module.UpdateType.EDITED_CHANNEL_POST
            )

        def check_update(self, update):
            if isinstance(update, Update) and update.effective_message:
                return self.filters(update)
