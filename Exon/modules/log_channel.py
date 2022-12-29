from datetime import datetime
from functools import wraps

from telegram.constants import ChatType
from telegram.ext import ContextTypes

from Exon.modules.helper_funcs.misc import is_module_loaded

# from Exon.modules.sql.topics_sql import get_action_topic

FILENAME = __name__.rsplit(".", 1)[-1]

if is_module_loaded(FILENAME):
    from telegram import Update
    from telegram.constants import ParseMode
    from telegram.error import BadRequest, Forbidden
    from telegram.ext import CommandHandler, JobQueue
    from telegram.helpers import escape_markdown

    from Exon import EVENT_LOGS, LOGGER, application
    from Exon.modules.helper_funcs.chat_status import check_admin
    from Exon.modules.sql import log_channel_sql as sql

    def loggable(func):
        @wraps(func)
        async def log_action(
            update: Update,
            context: ContextTypes.DEFAULT_TYPE,
            job_queue: JobQueue = None,
            *args,
            **kwargs,
        ):
            if not job_queue:
                result = await func(update, context, *args, **kwargs)
            else:
                result = await func(update, context, job_queue, *args, **kwargs)

            chat = update.effective_chat
            message = update.effective_message

            if result and isinstance(result, str):
                datetime_fmt = "%H:%M - %d-%m-%Y"
                result += f"\n<b>ᴇᴠᴇɴᴛ sᴛᴀᴍᴘ</b>: <code>{datetime.utcnow().strftime(datetime_fmt)}</code>"

                if chat.is_forum and chat.username:
                    result += f'\n<b>ʟɪɴᴋ:</b> <a href="https://t.me/{chat.username}/{message.message_thread_id}/{message.message_id}">ᴄʟɪᴄᴋ ʜᴇʀᴇ</a>'

                if message.chat.type == chat.SUPERGROUP and message.chat.username:
                    result += f'\n<b>ʟɪɴᴋ:</b> <a href="https://t.me/{chat.username}/{message.message_id}">ᴄʟɪᴄᴋ ʜᴇʀᴇ</a>'
                log_chat = sql.get_chat_log_channel(chat.id)
                if log_chat:
                    await send_log(context, log_chat, chat.id, result)

            return result

        return log_action

    def gloggable(func):
        @wraps(func)
        async def glog_action(
            update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs
        ):
            result = await func(update, context, *args, **kwargs)
            chat = update.effective_chat
            message = update.effective_message

            if result:
                datetime_fmt = "%H:%M - %d-%m-%Y"
                result += "\n<b>ᴇᴠᴇɴᴛ sᴛᴀᴍᴘ</b>: <code>{}</code>".format(
                    datetime.utcnow().strftime(datetime_fmt),
                )
                if chat.is_forum and chat.username:
                    result += f'\n<b>ʟɪɴᴋ:</b> <a href="https://t.me/{chat.username}/{message.message_thread_id}/{message.message_id}">ᴄʟɪᴄᴋ ʜᴇʀᴇ</a>'
                elif message.chat.type == chat.SUPERGROUP and message.chat.username:
                    result += f'\n<b>ʟɪɴᴋ:</b> <a href="https://t.me/{chat.username}/{message.message_id}">ᴄʟɪᴄᴋ ʜᴇʀᴇ</a>'
                log_chat = str(EVENT_LOGS)
                if log_chat:
                    await send_log(context, log_chat, chat.id, result)

            return result

        return glog_action

    async def send_log(
        context: ContextTypes.DEFAULT_TYPE,
        log_chat_id: str,
        orig_chat_id: str,
        result: str,
    ):
        bot = context.bot
        # topic_chat = get_action_topic(orig_chat_id)
        try:
            await bot.send_message(
                log_chat_id,
                result,
                parse_mode=ParseMode.HTML,
                disable_web_page_preview=True,
            )
        except BadRequest as excp:
            if excp.message == "ᴄʜᴀᴛ ɴᴏᴛ ғᴏᴜɴᴅ":
                try:
                    await bot.send_message(
                        orig_chat_id,
                        "ᴛʜɪs ʟᴏɢ ᴄʜᴀɴɴᴇʟ ʜᴀs ʙᴇᴇɴ ᴅᴇʟᴇᴛᴇᴅ - ᴜɴsᴇᴛᴛɪɴɢ.",
                        message_thread_id=1,
                    )
                except:
                    await bot.send_message(
                        orig_chat_id,
                        "ᴛʜɪs ʟᴏɢ ᴄʜᴀɴɴᴇʟ ʜᴀs ʙᴇᴇɴ ᴅᴇʟᴇᴛᴇᴅ - ᴜɴsᴇᴛᴛɪɴɢ.",
                    )
                sql.stop_chat_logging(orig_chat_id)
            else:
                LOGGER.warning(excp.message)
                LOGGER.warning(result)
                LOGGER.exception("ᴄᴏᴜʟᴅ ɴᴏᴛ parse")

                await bot.send_message(
                    log_chat_id,
                    result
                    + "\n\nғᴏʀᴍᴀᴛᴛɪɴɢ ʜᴀs ʙᴇᴇɴ ᴅɪsᴀʙʟᴇᴅ ᴅᴜᴇ ᴛᴏ ᴀɴ ᴜɴᴇxᴘᴇᴄᴛᴇᴅ ᴇʀʀᴏʀ.",
                )

    @check_admin(is_user=True)
    async def logging(update: Update, context: ContextTypes.DEFAULT_TYPE):
        bot = context.bot
        message = update.effective_message
        chat = update.effective_chat

        log_channel = sql.get_chat_log_channel(chat.id)
        if log_channel:
            log_channel_info = await bot.get_chat(log_channel)
            await message.reply_text(
                f"ᴛʜɪs ɢʀᴏᴜᴘ ʜᴀs ᴀʟʟ ɪᴛ's ʟᴏɢs sᴇɴᴛ ᴛᴏ:"
                f" {escape_markdown(log_channel_info.title)} (`{log_channel}`)",
                parse_mode=ParseMode.MARKDOWN,
            )

        else:
            await message.reply_text("ɴᴏ ʟᴏɢ ᴄʜᴀɴɴᴇʟ ʜᴀs ʙᴇᴇɴ sᴇᴛ ғᴏʀ ᴛʜɪs ɢʀᴏᴜᴘ!")

    @check_admin(is_user=True)
    async def setlog(update: Update, context: ContextTypes.DEFAULT_TYPE):
        bot = context.bot
        message = update.effective_message
        chat = update.effective_chat
        if chat.type == ChatType.CHANNEL:
            await bot.send_message(
                chat.id,
                "ɴᴏᴡ, ғᴏʀᴡᴀʀᴅ ᴛʜᴇ /setlog ᴛᴏ ᴛʜᴇ ɢʀᴏᴜᴘ ʏᴏᴜ ᴡᴀɴᴛ ᴛᴏ ᴛɪᴇ ᴛʜɪs ᴄʜᴀɴɴᴇʟ ᴛᴏ!",
            )

        elif message.forward_from_chat:
            sql.set_chat_log_channel(chat.id, message.forward_from_chat.id)

            try:
                await bot.send_message(
                    message.forward_from_chat.id,
                    f"ᴛʜɪs ᴄʜᴀɴɴᴇʟ ʜᴀs ʙᴇᴇɴ sᴇᴛ ᴀs ᴛʜᴇ ʟᴏɢ ᴄʜᴀɴɴᴇʟ ғᴏʀ {chat.title or chat.first_name}.",
                )
            except Forbidden as excp:
                if excp.message == "ғᴏʀʙɪᴅᴅᴇɴ: ʙᴏᴛ ɪs ɴᴏᴛ ᴀ ᴍᴇᴍʙᴇʀ ᴏғ ᴛʜᴇ ᴄʜᴀɴɴᴇʟ ᴄʜᴀᴛ":
                    if chat.is_forum:
                        await bot.send_message(
                            chat.id,
                            "sᴜᴄᴄᴇssғᴜʟʟʏ sᴇᴛ ʟᴏɢ ᴄʜᴀɴɴᴇʟ!",
                            message_thread_id=message.message_thread_id,
                        )
                    else:
                        await bot.send_message(chat.id, "Successfully set log channel!")
                else:
                    LOGGER.exception("ERROR ɪɴ sᴇᴛᴛɪɴɢ ᴛʜᴇ ʟᴏɢ ᴄʜᴀɴɴᴇʟ.")

            if chat.is_forum:
                await bot.send_message(
                    chat.id,
                    "sᴜᴄᴄᴇssғᴜʟʟʏ sᴇᴛ ʟᴏɢ ᴄʜᴀɴɴᴇʟ!",
                    message_thread_id=message.message_thread_id,
                )
            else:
                await bot.send_message(chat.id, "sᴜᴄᴄᴇssғᴜʟʟʏ sᴇᴛ ʟᴏɢ ᴄʜᴀɴɴᴇʟ!")

        else:
            await message.reply_text(
                "ᴛʜᴇ sᴛᴇᴘs ᴛᴏ sᴇᴛ ᴀ ʟᴏɢ ᴄʜᴀɴɴᴇʟ are:\n"
                " - ᴀᴅᴅ ʙᴏᴛ ᴛᴏ ᴛʜᴇ ᴅᴇsɪʀᴇᴅ ᴄʜᴀɴɴᴇʟ\n"
                " - sᴇɴᴅ /setlog ᴛᴏ ᴛʜᴇ ᴄʜᴀɴɴᴇʟ\n"
                " - ғᴏʀᴡᴀʀᴅ ᴛʜᴇ /sᴇᴛʟᴏɢ ᴛᴏ ᴛʜᴇ ɢʀᴏᴜᴘ\n",
            )

    @check_admin(is_user=True)
    async def unsetlog(update: Update, context: ContextTypes.DEFAULT_TYPE):
        bot = context.bot
        message = update.effective_message
        chat = update.effective_chat

        log_channel = sql.stop_chat_logging(chat.id)
        if log_channel:
            await bot.send_message(
                log_channel,
                f"ᴄʜᴀɴɴᴇʟ ʜᴀs ʙᴇᴇɴ ᴜɴʟɪɴᴋᴇᴅ ғʀᴏᴍ {chat.title}",
            )
            await message.reply_text("ʟᴏɢ ᴄʜᴀɴɴᴇʟ ʜᴀs ʙᴇᴇɴ ᴜɴ-sᴇᴛ.")

        else:
            await message.reply_text("ɴᴏ ʟᴏɢ ᴄʜᴀɴɴᴇʟ ʜᴀs ʙᴇᴇɴ sᴇᴛ ʏᴇᴛ!")

    def __stats__():
        return f"• {sql.num_logchannels()} ʟᴏɢ ᴄʜᴀɴɴᴇʟs sᴇᴛ."

    def __migrate__(old_chat_id, new_chat_id):
        sql.migrate_chat(old_chat_id, new_chat_id)

    async def __chat_settings__(chat_id, user_id):
        log_channel = sql.get_chat_log_channel(chat_id)
        if log_channel:
            log_channel_info = await application.bot.get_chat(log_channel)
            return f"ᴛʜɪs ɢʀᴏᴜᴘ ʜᴀs ᴀʟʟ ɪᴛ's ʟᴏɢs sᴇɴᴛ ᴛᴏ: {escape_markdown(log_channel_info.title)} (`{log_channel}`)"
        return "ɴᴏ ʟᴏɢ ᴄʜᴀɴɴᴇʟ ɪs sᴇᴛ ғᴏʀ ᴛʜɪs ɢʀᴏᴜᴘ!"

    __help__ = """
*ᴀᴅᴍɪɴs ᴏɴʟʏ:*
• /logchannel*:* ɢᴇᴛ ʟᴏɢ ᴄʜᴀɴɴᴇʟ ɪɴғᴏ
• /setlog*:* sᴇᴛ ᴛʜᴇ ʟᴏɢ ᴄʜᴀɴɴᴇʟ.
• /unsetlog*:* ᴜɴsᴇᴛ ᴛʜᴇ ʟᴏɢ channel.

sᴇᴛᴛɪɴɢ ᴛʜᴇ ʟᴏɢ ᴄʜᴀɴɴᴇʟ ɪs ᴅᴏɴᴇ ʙʏ:
• ᴀᴅᴅɪɴɢ ᴛʜᴇ ʙᴏᴛ ᴛᴏ ᴛʜᴇ ᴅᴇsɪʀᴇᴅ ᴄʜᴀɴɴᴇʟ (ᴀs ᴀɴ ᴀᴅᴍɪɴ!)
• sᴇɴᴅɪɴɢ `/setlog` ɪɴ ᴛʜᴇ ᴄʜᴀɴɴᴇʟ
• ғᴏʀᴡᴀʀᴅɪɴɢ ᴛʜᴇ `/setlog` ᴛᴏ ᴛʜᴇ ɢʀᴏᴜᴘ
"""

    __mod_name__ = "𝐋ᴏɢs"

    LOG_HANDLER = CommandHandler("logchannel", logging, block=False)
    SET_LOG_HANDLER = CommandHandler("setlog", setlog, block=False)
    UNSET_LOG_HANDLER = CommandHandler("unsetlog", unsetlog, block=False)

    application.add_handler(LOG_HANDLER)
    application.add_handler(SET_LOG_HANDLER)
    application.add_handler(UNSET_LOG_HANDLER)

else:
    # run anyway if module not loaded
    def loggable(func):
        return func

    def gloggable(func):
        return func
