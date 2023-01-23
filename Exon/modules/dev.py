from contextlib import suppress

from telegram import Update
from telegram.error import Forbidden, TelegramError
from telegram.ext import CommandHandler, ContextTypes

from Exon import exon
from Exon.modules.helper_funcs.chat_status import check_admin

ALLOW_CHATS = True


@check_admin(only_dev=True)
async def allow_groups(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if not args:
        state = "ʟᴏᴄᴋᴅᴏᴡɴ ɪs " + "on" if not ALLOW_CHATS else "off"
        await update.effective_message.reply_text(f"ᴄᴜʀʀᴇɴᴛ sᴛᴀᴛᴇ: {state}")
        return
    if args[0].lower() in ["off", "no"]:
        pass
    elif args[0].lower() in ["yes", "on"]:
        pass
    else:
        await update.effective_message.reply_text("ғᴏʀᴍᴀᴛ: /lockdown ʏᴇs/ɴᴏ ᴏʀ ᴏғғ/ᴏɴ")
        return
    await update.effective_message.reply_text("ᴅᴏɴᴇ! ʟᴏᴄᴋᴅᴏᴡɴ ᴠᴀʟᴜᴇ ᴛᴏɢɢʟᴇᴅ.")


@check_admin(only_dev=True)
async def leave(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bot = context.bot
    args = context.args
    if args:
        chat_id = str(args[0])
        try:
            await bot.leave_chat(int(chat_id))
        except TelegramError:
            await update.effective_message.reply_text(
                "ʙᴇᴇᴘ ʙᴏᴏᴘ, I ᴄᴏᴜʟᴅ ɴᴏᴛ ʟᴇᴀᴠᴇ ᴛʜᴀᴛ ɢʀᴏᴜᴘ(ᴅᴜɴɴᴏ ᴡʜʏ ᴛʜᴏ).",
            )
            return
        with suppress(Forbidden):
            await update.effective_message.reply_text("ʙᴇᴇᴘ ʙᴏᴏᴘ, I ʟᴇғᴛ ᴛʜᴀᴛ sᴏᴜᴘ!.")
    else:
        await update.effective_message.reply_text("sᴇɴᴅ ᴀ ᴠᴀʟɪᴅ ᴄʜᴀᴛ ɪᴅ")


LEAVE_HANDLER = CommandHandler("leave", leave)

ALLOWGROUPS_HANDLER = CommandHandler("lockdown", allow_groups)

exon.add_handler(ALLOWGROUPS_HANDLER)
exon.add_handler(LEAVE_HANDLER)


__mod_name__ = "𝐃ᴇᴠ"
__handlers__ = [LEAVE_HANDLER, ALLOWGROUPS_HANDLER]
