import asyncio

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.error import BadRequest, Forbidden
from telegram.ext import CallbackQueryHandler, CommandHandler, ContextTypes

import Exon.modules.sql.global_bans_sql as gban_sql
import Exon.modules.sql.users_sql as user_sql
from Exon import DEV_USERS, OWNER_ID, application
from Exon.modules.helper_funcs.chat_status import check_admin


async def get_invalid_chats(
    update: Update, context: ContextTypes.DEFAULT_TYPE, remove: bool = False
):
    bot = context.bot
    chat_id = update.effective_chat.id
    chats = user_sql.get_all_chats()
    kicked_chats, progress = 0, 0
    chat_list = []
    progress_message = None

    for chat in chats:

        if ((100 * chats.index(chat)) / len(chats)) > progress:
            progress_bar = f"{progress}% completed in getting invalid chats."
            if progress_message:
                try:
                    await bot.editMessageText(
                        progress_bar,
                        chat_id,
                        progress_message.message_id,
                    )
                except:
                    pass
            else:
                progress_message = await bot.sendMessage(
                    chat_id,
                    progress_bar,
                    message_thread_id=update.effective_message.message_thread_id
                    if chat.is_forum
                    else None,
                )
            progress += 5

        cid = chat.chat_id
        await asyncio.sleep(0.1)
        try:
            await bot.get_chat(cid, timeout=60)
        except (BadRequest, Forbidden):
            kicked_chats += 1
            chat_list.append(cid)
        except:
            pass

    try:
        await progress_message.delete()
    except:
        pass

    if not remove:
        return kicked_chats
    else:
        for muted_chat in chat_list:
            await asyncio.sleep(0.1)
            user_sql.rem_chat(muted_chat)
        return kicked_chats


async def get_invalid_gban(
    update: Update, context: ContextTypes.DEFAULT_TYPE, remove: bool = False
):
    bot = context.bot
    banned = gban_sql.get_gban_list()
    ungbanned_users = 0
    ungban_list = []

    for user in banned:
        user_id = user["user_id"]
        await asyncio.sleep(0.1)
        try:
            await bot.get_chat(user_id)
        except BadRequest:
            ungbanned_users += 1
            ungban_list.append(user_id)
        except:
            pass

    if not remove:
        return ungbanned_users
    else:
        for user_id in ungban_list:
            await asyncio.sleep(0.1)
            gban_sql.ungban_user(user_id)
        return ungbanned_users


@check_admin(only_dev=True)
async def dbcleanup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.effective_message

    await msg.reply_text("ɢᴇᴛᴛɪɴɢ ɪɴᴠᴀʟɪᴅ ᴄʜᴀᴛ ᴄᴏᴜɴᴛ ...")
    invalid_chat_count = get_invalid_chats(update, context)

    await msg.reply_text("ɢᴇᴛᴛɪɴɢ ɪɴᴠᴀʟɪᴅ ɢʙᴀɴɴᴇᴅ ᴄᴏᴜɴᴛ ...")
    invalid_gban_count = get_invalid_gban(update, context)

    reply = f"ᴛᴏᴛᴀʟ ɪɴᴠᴀʟɪᴅ ᴄʜᴀᴛs - {invalid_chat_count}\n"
    reply += f"ᴛᴏᴛᴀʟ ɪɴᴠᴀʟɪᴅ ɢʙᴀɴɴᴇᴅ ᴜsᴇʀs - {invalid_gban_count}"

    buttons = [[InlineKeyboardButton("ᴄʟᴇᴀɴᴜᴘ ᴅʙ", callback_data="db_cleanup")]]

    await update.effective_message.reply_text(
        reply,
        reply_markup=InlineKeyboardMarkup(buttons),
    )


async def callback_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bot = context.bot
    query = update.callback_query
    message = query.message
    chat_id = update.effective_chat.id
    query_type = query.data

    admin_list = [OWNER_ID] + DEV_USERS

    await bot.answer_callback_query(query.id)

    if query_type == "db_leave_chat":
        if query.from_user.id in admin_list:
            await bot.editMessageText("ʟᴇᴀᴠɪɴɢ ᴄʜᴀᴛs ...", chat_id, message.message_id)
            chat_count = get_invalid_chats(update, context, True)
            await bot.sendMessage(
                chat_id,
                f"ʟᴇғᴛ {chat_count} chats.",
                message_thread_id=message.message_thread_id
                if update.effective_chat.is_forum
                else None,
            )
        else:
            await query.answer("ʏᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴀʟʟᴏᴡᴇᴅ ᴛᴏ ᴜsᴇ ᴛʜɪs.")
    elif query_type == "db_cleanup":
        if query.from_user.id in admin_list:
            await bot.editMessageText("ᴄʟᴇᴀɴɪɴɢ ᴜᴘ DB ...", chat_id, message.message_id)
            invalid_chat_count = get_invalid_chats(update, context, True)
            invalid_gban_count = get_invalid_gban(update, context, True)
            reply = "ᴄʟᴇᴀɴᴇᴅ ᴜᴘ {} ᴄʜᴀᴛs ᴀɴᴅ {} ɢʙᴀɴɴᴇᴅ ᴜsᴇʀs ғʀᴏᴍ ᴅʙ.".format(
                invalid_chat_count,
                invalid_gban_count,
            )
            await bot.sendMessage(
                chat_id,
                reply,
                message_thread_id=message.message_thread_id
                if update.effective_chat.is_forum
                else None,
            )
        else:
            await query.answer("ʏᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴀʟʟᴏᴡᴇᴅ ᴛᴏ ᴜsᴇ ᴛʜɪs.")


DB_CLEANUP_HANDLER = CommandHandler("dbcleanup", dbcleanup, block=False)
BUTTON_HANDLER = CallbackQueryHandler(callback_button, pattern="db_.*", block=False)

application.add_handler(DB_CLEANUP_HANDLER)
application.add_handler(BUTTON_HANDLER)

__mod_name__ = "𝐃𝐁-ᴄʟᴇᴀɴ"
__handlers__ = [DB_CLEANUP_HANDLER, BUTTON_HANDLER]
