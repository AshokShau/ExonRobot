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

import sre_constants

import regex
import telegram
from telegram import Update
from telegram.ext import CallbackContext, Filters

from Exon import LOGGER, dispatcher
from Exon.modules.disable import DisableAbleMessageHandler
from Exon.modules.helper_funcs.regex_helper import infinite_loop_check

DELIMITERS = ("/", ":", "|", "_")


def separate_sed(sed_string):
    if (
        len(sed_string) < 3
        or sed_string[1] not in DELIMITERS
        or sed_string.count(sed_string[1]) < 2
    ):
        return

    delim = sed_string[1]
    start = counter = 2
    while counter < len(sed_string):
        if sed_string[counter] == "\\":
            counter += 1

        elif sed_string[counter] == delim:
            replace = sed_string[start:counter]
            counter += 1
            start = counter
            break

        counter += 1

    else:
        return None

    while counter < len(sed_string):
        if (
            sed_string[counter] == "\\"
            and counter + 1 < len(sed_string)
            and sed_string[counter + 1] == delim
        ):
            sed_string = sed_string[:counter] + sed_string[counter + 1 :]

        elif sed_string[counter] == delim:
            replace_with = sed_string[start:counter]
            counter += 1
            break

        counter += 1
    else:
        return replace, sed_string[start:], ""

    flags = sed_string[counter:] if counter < len(sed_string) else ""
    return replace, replace_with, flags.lower()


def sed(update: Update, context: CallbackContext):
    sed_result = separate_sed(update.effective_message.text)
    if sed_result and update.effective_message.reply_to_message:
        if update.effective_message.reply_to_message.text:
            to_fix = update.effective_message.reply_to_message.text
        elif update.effective_message.reply_to_message.caption:
            to_fix = update.effective_message.reply_to_message.caption
        else:
            return

        repl, repl_with, flags = sed_result
        if not repl:
            update.effective_message.reply_to_message.reply_text(
                "You're trying to replace... " "nothing with something?",
            )
            return

        try:
            try:
                check = regex.match(repl, to_fix, flags=regex.IGNORECASE, timeout=5)
            except TimeoutError:
                return
            if check and check.group(0).lower() == to_fix.lower():
                update.effective_message.reply_to_message.reply_text(
                    "ʜᴇʏ ᴇᴠᴇʀʏᴏɴᴇ, {} ɪs ᴛʀʏɪɴɢ ᴛᴏ ᴍᴀᴋᴇ "
                    "ᴍᴇ sᴀʏ sᴛᴜғғ I ᴅᴏɴ'ᴛ ᴡᴀɴɴᴀ "
                    "sᴀʏ!".format(update.effective_user.first_name),
                )
                return
            if infinite_loop_check(repl):
                update.effective_message.reply_text(
                    "I'ᴍ ᴀғʀᴀɪᴅ I ᴄᴀɴ'ᴛ ʀᴜɴ ᴛʜᴀᴛ ʀᴇɢᴇx.",
                )
                return
            if "i" in flags and "g" in flags:
                text = regex.sub(
                    repl,
                    repl_with,
                    to_fix,
                    flags=regex.I,
                    timeout=3,
                ).strip()
            elif "i" in flags:
                text = regex.sub(
                    repl,
                    repl_with,
                    to_fix,
                    count=1,
                    flags=regex.I,
                    timeout=3,
                ).strip()
            elif "g" in flags:
                text = regex.sub(repl, repl_with, to_fix, timeout=3).strip()
            else:
                text = regex.sub(repl, repl_with, to_fix, count=1, timeout=3).strip()
        except TimeoutError:
            update.effective_message.reply_text("ᴛɪᴍᴇᴏᴜᴛ")
            return
        except sre_constants.error:
            LOGGER.warning(update.effective_message.text)
            LOGGER.exception("sʀᴇ ᴄᴏɴsᴛᴀɴᴛ ᴇʀʀᴏʀ")
            update.effective_message.reply_text("ᴅᴏ ʏᴏᴜ ᴇᴠᴇɴ sᴇᴅ? ᴀᴘᴘᴀʀᴇɴᴛʟʏ ɴᴏᴛ.")
            return

        # empty string errors -_-
        if len(text) >= telegram.MAX_MESSAGE_LENGTH:
            update.effective_message.reply_text(
                "ᴛʜᴇ ʀᴇsᴜʟᴛ ᴏғ ᴛʜᴇ sed ᴄᴏᴍᴍᴀɴᴅ ᴡᴀs ᴛᴏᴏ ʟᴏɴɢ ғᴏʀ \
                                                 ᴛᴇʟᴇɢʀᴀᴍ!",
            )
        elif text:
            update.effective_message.reply_to_message.reply_text(text)


__help__ = """
 ➩ `s/<text1>/<text2>(/<flag>)`*:* ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴍᴇssᴀɢᴇ ᴡɪᴛʜ ᴛʜɪs ᴛᴏ ᴘᴇʀғᴏʀᴍ ᴀ sᴇᴅ ᴏᴘᴇʀᴀᴛɪᴏɴ ᴏɴ ᴛʜᴀᴛ ᴍᴇssᴀɢᴇ, ʀᴇᴘʟᴀᴄɪɴɢ ᴀʟʟ \
ᴏᴄᴄᴜʀʀᴇɴᴄᴇs ᴏғ 'text1' ᴡɪᴛʜ 'text2'. ғʟᴀɢs ᴀʀᴇ ᴏᴘᴛɪᴏɴᴀʟ, ᴀɴᴅ ᴄᴜʀʀᴇɴᴛʟʏ ɪɴᴄʟᴜᴅᴇ 'i' ғᴏʀ ɪɢɴᴏʀᴇ ᴄᴀsᴇ, 'g' ғᴏʀ ɢʟᴏʙᴀʟ, \
ᴏʀ ɴᴏᴛʜɪɴɢ. ᴅᴇʟɪᴍɪᴛᴇʀs ɪɴᴄʟᴜᴅᴇ `/`, `_`, `|`, ᴀɴᴅ `:`. ᴛᴇxᴛ ɢʀᴏᴜᴘɪɴɢ ɪs sᴜᴘᴘᴏʀᴛᴇᴅ. ᴛʜᴇ ʀᴇsᴜʟᴛɪɴɢ ᴍᴇssᴀɢᴇ ᴄᴀɴɴᴏᴛ be \
ʟᴀʀɢᴇʀ ᴛʜᴀɴ {}.

*ʀᴇᴍɪɴᴅᴇʀ:* sᴇᴅ ᴜsᴇs sᴏᴍᴇ sᴘᴇᴄɪᴀʟ ᴄʜᴀʀᴀᴄᴛᴇʀs ᴛᴏ ᴍᴀᴋᴇ ᴍᴀᴛᴄʜɪɴɢ ᴇᴀsɪᴇʀ, sᴜᴄʜ ᴀs ᴛʜᴇsᴇ: `+*.?\\`
If ʏᴏᴜ ᴡᴀɴᴛ ᴛᴏ ᴜsᴇ ᴛʜᴇsᴇ ᴄʜᴀʀᴀᴄᴛᴇʀs, ᴍᴀᴋᴇ sᴜʀᴇ ʏᴏᴜ ᴇsᴄᴀᴘᴇ ᴛʜᴇᴍ!
*Example:* \\?.
""".format(
    telegram.MAX_MESSAGE_LENGTH,
)

__mod_name__ = "𝚁ᴇɢᴇx"

SED_HANDLER = DisableAbleMessageHandler(
    Filters.regex(r"s([{}]).*?\1.*".format("".join(DELIMITERS))),
    sed,
    friendly="sed",
    run_async=True,
)

dispatcher.add_handler(SED_HANDLER)
