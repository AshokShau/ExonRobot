import inspect
import io
import os
import re
import subprocess as sub
import sys
import traceback
import uuid
from html import escape
from os import execvp
from sys import executable
from typing import Any, List, Optional, Tuple, cast

import telegram
from meval import meval
from ptbmod import Admins
from telegram import Message, Update
from telegram.ext import ContextTypes

from Telegram import LOGGER, Cmd


@Cmd(command="logs")
@Admins(no_reply=True, only_devs=True)
async def logs(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
#   todo: implement this, logs file: Telegram/logs.txt
    pass

@Cmd(command=["restart", "update"])
@Admins(no_reply=True, only_devs=True)
async def update_(update: Update, _: ContextTypes.DEFAULT_TYPE) -> Optional[Message]:
    m = cast(Message, update.effective_message)
    cmd = m.text.split(sep=None, maxsplit=1)
    command = cmd[0][1:]
    msg: Message = await m.reply_text(
        f"Restarting{' and updating ' if command == 'update' else ' '}the bot..."
    )
    try:
        if command == "update":
            try:
                out = sub.check_output(["git", "pull"]).decode("UTF-8")
                if "Already up to date." in str(out):
                    return await msg.edit_text("Already up to date.")
                if len(out) > 4096:
                    with io.BytesIO(str.encode(out)) as out_file:
                        out_file.name = str(uuid.uuid4()).split("-")[0].upper() + ".TXT"
                        caption = "Log of the update"
                        await m.reply_document(
                            document=out_file,
                            caption=caption,
                            disable_notification=True,
                        )
                else:
                    await msg.edit_text(f"<pre>{out}</pre>")
            except Exception as e:
                return await msg.edit_text(str(e))
            await msg.reply_text("Restarting and pushing the changes...")

        if command == "restart":
            LOGGER.info("Restarting")

        execvp(executable, args=[executable, "-m", "Telegram"])

    except Exception as e:
        return await msg.edit_text(f"Failed to restart the bot due to\n{e}")

def format_exception(
        exp: BaseException, tb: Optional[List[traceback.FrameSummary]] = None
) -> str:
    """Formats an exception traceback as a string."""
    if tb is None:
        tb = traceback.extract_tb(exp.__traceback__)

    # Replace absolute paths with relative paths
    cwd = os.getcwd()
    for frame in tb:
        if cwd in frame.filename:
            frame.filename = os.path.relpath(frame.filename)

    stack = "".join(traceback.format_list(tb))
    msg = str(exp)
    return f"Traceback (most recent call last):\n{stack}{type(exp).__name__}{': ' + msg if msg else ''}"


@Cmd(command="eval")
@Admins(only_devs=True)
async def eval_(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    bot = context.bot
    m = update.effective_message
    text = m.text.split(None, 1)
    if len(text) <= 1:
        return
    code = text[1]
    out_buf = io.StringIO()

    async def _eval() -> Tuple[str, Optional[str]]:
        async def send(*args: Any, **kwargs: Any) -> telegram.Message:
            return await m.reply_text(*args, **kwargs)

        def _print(*args: Any, **kwargs: Any) -> None:
            if "file" not in kwargs:
                kwargs["file"] = out_buf
            return print(*args, **kwargs)

        eval_vars = {
            "bot": bot,
            "update": update,
            "context": context,
            "m": m,
            "reply": m.reply_to_message,
            "chat": update.effective_chat,
            "user": update.effective_user,
            "IKB": telegram.InlineKeyboardButton,
            "IKM": telegram.InlineKeyboardMarkup,
            "telegram": telegram,
            "send": send,
            "print": _print,
            "inspect": inspect,
            "os": os,
            "re": re,
            "sys": sys,
            "traceback": traceback,
        }

        try:
            return "", await meval(code, globals(), **eval_vars)
        except Exception as e:
            tb = traceback.extract_tb(e.__traceback__)
            first_snip_idx = next((i for i, frame in enumerate(tb) if frame.filename == "<string>"), -1)
            if first_snip_idx == -1:
                raise e
            stripped_tb = tb[first_snip_idx:]
            formatted_tb = format_exception(e, tb=stripped_tb)
            return "⚠️ Error executing snippet\n\n", formatted_tb

    prefix, result = await _eval()

    if not out_buf.getvalue() or result is not None:
        print(result, file=out_buf)

    out = out_buf.getvalue().rstrip("\n")  # Strip only ONE final newline
    result_msg = f"<b>Output:</b>\n<pre language='python'>{escape(out)}</pre>"

    if len(result_msg) > 4096:
        with io.BytesIO(str.encode(out)) as out_file:
            out_file.name = str(uuid.uuid4()).split("-")[0].upper() + ".txt"
            await m.reply_document(
                document=out_file,
                disable_notification=True,
            )
        return

    await m.reply_text(result_msg)
