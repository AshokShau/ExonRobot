"""
MIT License

Copyright (c) 2022 ABISHNOI69

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

# ""DEAR PRO PEOPLE,  DON'T REMOVE & CHANGE THIS LINE
# TG :- @Abishnoi1m
#     UPDATE   :- Abishnoi_bots
#     GITHUB :- ABISHNOI69 ""

import subprocess

from telegram import ParseMode, Update
from telegram.ext import CallbackContext, CommandHandler

from Exon import LOGGER, dispatcher
from Exon.modules.helper_funcs.chat_status import dev_plus


@dev_plus
def shell(update: Update, context: CallbackContext):
    message = update.effective_message
    cmd = message.text.split(" ", 1)
    if len(cmd) == 1:
        message.reply_text("ɴᴏ ᴄᴏᴍᴍᴀɴᴅ ᴛᴏ ᴇxᴄᴜᴛᴇ ᴡᴀꜱ ɢɪᴠᴇɴ ʙᴀʙʏ.")
        return
    cmd = cmd[1]
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=True,
    )
    stdout, stderr = process.communicate()
    reply = ""
    stderr = stderr.decode()
    stdout = stdout.decode()
    if stdout:
        reply += f"*ꜱᴛᴅᴏᴜᴛ*\n`{stdout}`\n"
        LOGGER.info(f"Shell - {cmd} - {stdout}")
    if stderr:
        reply += f"*Stderr*\n`{stderr}`\n"
        LOGGER.error(f"Shell - {cmd} - {stderr}")
    if len(reply) > 3000:
        with open("shell_output.txt", "w") as file:
            file.write(reply)
        with open("shell_output.txt", "rb") as doc:
            context.bot.send_document(
                document=doc,
                filename=doc.name,
                reply_to_message_id=message.message_id,
                chat_id=message.chat_id,
            )
    else:
        message.reply_text(reply, parse_mode=ParseMode.MARKDOWN)


SHELL_HANDLER = CommandHandler(["sh"], shell, run_async=True)
dispatcher.add_handler(SHELL_HANDLER)
__mod_name__ = "Shell"
__command_list__ = ["sh"]
__handlers__ = [SHELL_HANDLER]
