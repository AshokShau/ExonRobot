import html
import json
import traceback
from typing import cast

from telegram import Update
from telegram.error import BadRequest, Forbidden
from telegram.ext import ContextTypes

from Telegram import LOGGER
from config import LOGGER_ID


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    if update.callback_query:
        await update.callback_query.answer(
            "Hey, an error happened. I notified my developer. If you think you can help him, PM @AshokShau. Thanks",
            show_alert=True,
        )
    else:
        await update.effective_message.reply_text(
            "Hey, an error happened. I notified my developer. If you think you can help him, PM @Shau. Thanks"
        )
    """
    """Log the error and send a telegram message to notify the developer."""
    # Log the error before we do anything else, so we can see it even if something breaks.
    LOGGER.error(msg="Exception while handling an update:", exc_info=context.error)

    # traceback.format_exception returns the usual python message about an exception, but as a
    # list of strings rather than a single string, so we have to join them together.
    tb_list = traceback.format_exception(
        None, context.error, cast(Exception, context.error).__traceback__
    )
    tb_string = "".join(tb_list)

    # Build the message with some markup and additional information about what happened.
    # You might need to add some logic to deal with messages longer than the 4096 character limit.
    update_str = update.to_dict() if isinstance(update, Update) else str(update)
    message_1 = (
        f"An exception was raised while handling an update\n\n"
        f"<pre>update = {html.escape(json.dumps(update_str, indent=2, ensure_ascii=False))}</pre>"
    )
    message_2 = f"<pre>{html.escape(tb_string)}</pre>"

    # Finally, send the messages
    # We send update and traceback in two parts to reduce the chance of hitting max length
    try:
        sent_message = await context.bot.send_message(chat_id=LOGGER_ID, text=message_1)
        await sent_message.reply_html(message_2)
    except BadRequest as exc:
        if "too long" not in str(exc):
            raise exc
        message = (
            f"Hey.\nThe error <code>{html.escape(str(context.error))}</code> happened."
            f" The traceback is too long to send, but it was written to the log."
        )
        await context.bot.send_message(chat_id=LOGGER_ID, text=message)
    except Forbidden:
        LOGGER.error(msg="bot can't send error on log group:", exc_info=context.error)
