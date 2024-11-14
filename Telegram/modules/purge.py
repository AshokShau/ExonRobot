import asyncio

from ptbmod import Admins
from telegram import Update
from telegram.ext import ContextTypes

from Telegram import Cmd


@Cmd(command=["delete", "del"])
@Admins(permissions="can_delete_messages", is_both=True)
async def delete(update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.effective_message
    replied = message.reply_to_message
    tasks = [message.delete()]

    if replied:
        tasks.append(replied.delete())
    else:
        tasks.append(message.reply_text(text="Reply to a message to delete it."))

    await asyncio.gather(*tasks)


@Cmd(command=["purge", "spurge"])
@Admins(permissions="can_delete_messages", is_both=True)
async def purge(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    bot = context.bot
    m = update.effective_message
    if m.reply_to_message:
        message_ids = list(range(m.reply_to_message.id, m.id))
        await asyncio.gather(
            *(
                bot.delete_messages(chat_id=m.chat.id, message_ids=x)
                for x in (
                    message_ids[i : i + 100] for i in range(0, len(message_ids), 100)
                )
            )
        )
        await m.delete()
        await m.reply_text(text=f"Deleted <b>{len(message_ids)}</b> messages")
        return None
    await m.reply_text("Reply to a message to delete it.")
    return None
