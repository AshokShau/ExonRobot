import re
import random
from html import escape

from telegram import InlineKeyboardMarkup, Message, InlineKeyboardButton, Update
from telegram.constants import ParseMode, MessageLimit, ChatMemberStatus
from telegram.error import BadRequest
from telegram.ext import (
    CommandHandler,
    MessageHandler,
    ApplicationHandlerStop,
    CallbackQueryHandler,
    ContextTypes,
)
from telegram.ext import filters as filters_module
from telegram.helpers import mention_html, escape_markdown

from Exon import application, LOGGER, DRAGONS
from Exon.modules.disable import DisableAbleCommandHandler
from Exon.modules.helper_funcs.handlers import MessageHandlerChecker
from Exon.modules.helper_funcs.chat_status import check_admin
from Exon.modules.helper_funcs.extraction import extract_text

from Exon.modules.helper_funcs.misc import build_keyboard_parser
from Exon.modules.helper_funcs.msg_types import get_filter_type
from Exon.modules.helper_funcs.string_handling import (
    split_quotes,
    button_markdown_parser,
    escape_invalid_curly_brackets,
    markdown_to_html,
)
from Exon.modules.sql import cust_filters_sql as sql

from Exon.modules.connection import connected

from Exon.modules.helper_funcs.alternate import send_message, typing_action

HANDLER_GROUP = 10

ENUM_FUNC_MAP = {
    sql.Types.TEXT.value: application.bot.send_message,
    sql.Types.BUTTON_TEXT.value: application.bot.send_message,
    sql.Types.STICKER.value: application.bot.send_sticker,
    sql.Types.DOCUMENT.value: application.bot.send_document,
    sql.Types.PHOTO.value: application.bot.send_photo,
    sql.Types.AUDIO.value: application.bot.send_audio,
    sql.Types.VOICE.value: application.bot.send_voice,
    sql.Types.VIDEO.value: application.bot.send_video,
    # sql.Types.VIDEO_NOTE.value: application.bot.send_video_note
}



@typing_action
async def list_handlers(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    user = update.effective_user

    conn = await connected(context.bot, update, chat, user.id, need_admin=False)
    if not conn is False:
        chat_id = conn
        chat_obj = await application.bot.getChat(conn)
        chat_name = chat_obj.title
        filter_list = "*Filter in {}:*\n"
    else:
        chat_id = update.effective_chat.id
        if chat.type == "private":
            chat_name = "Local filters"
            filter_list = "*local filters:*\n"
        else:
            chat_name = chat.title
            filter_list = "*Filters in {}*:\n"

    all_handlers = sql.get_chat_triggers(chat_id)

    if not all_handlers:
        await send_message(
            update.effective_message, "No filters saved in {}!".format(chat_name),
        )
        return

    for keyword in all_handlers:
        entry = " • `{}`\n".format(escape_markdown(keyword))
        if len(entry) + len(filter_list) > MessageLimit.MAX_TEXT_LENGTH:
            await send_message(
                update.effective_message,
                filter_list.format(chat_name),
                parse_mode=ParseMode.MARKDOWN,
            )
            filter_list = entry
        else:
            filter_list += entry

    await send_message(
        update.effective_message,
        filter_list.format(chat_name),
        parse_mode=ParseMode.MARKDOWN,
    )

@typing_action
@check_admin(is_user=True)
async def filters(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    user = update.effective_user
    msg = update.effective_message
    args = msg.text.split(None, 1)  # use python's maxsplit to separate Cmd, keyword, and reply_text

    conn = await connected(context.bot, update, chat, user.id)
    if not conn is False:
        chat_id = conn
        chat_obj = await application.bot.getChat(conn)
        chat_name = chat_obj.title
    else:
        chat_id = update.effective_chat.id
        if chat.type == "private":
            chat_name = "local filters"
        else:
            chat_name = chat.title

    if not msg.reply_to_message and len(args) < 2:
        await send_message(
            update.effective_message,
            "Please provide keyboard keyword for this filter to reply with!",
        )
        return

    if msg.reply_to_message and not msg.reply_to_message.forum_topic_created:
        if len(args) < 2:
            await send_message(
                update.effective_message,
                "Please provide keyword for this filter to reply with!",
            )
            return
        else:
            keyword = args[1]
    else:
        extracted = split_quotes(args[1])
        if len(extracted) < 1:
            return
        # set trigger -> lower, so as to avoid adding duplicate filters with different cases
        keyword = extracted[0].lower()

    # Add the filter
    # Note: perhaps handlers can be removed somehow using sql.get_chat_filters
    for handler in application.handlers.get(HANDLER_GROUP, []):
        if handler.filters == (keyword, chat_id):
            application.remove_handler(handler, HANDLER_GROUP)

    text, file_type, file_id = get_filter_type(msg)
    if not msg.reply_to_message and len(extracted) >= 2:
        offset = len(extracted[1]) - len(
            msg.text,
        )  # set correct offset relative to command + notename
        text, buttons = button_markdown_parser(
            extracted[1], entities=msg.parse_entities(), offset=offset,
        )
        text = text.strip()
        if not text:
            await send_message(
                update.effective_message,
                "There is no note message - You can't JUST have buttons, you need a message to go with it!",
            )
            return

    if len(args) >= 2:
        if msg.reply_to_message:
            if msg.reply_to_message.forum_topic_created:
                offset = len(extracted[1]) - len(msg.text)

                text, buttons = button_markdown_parser(
                    extracted[1], entities=msg.parse_entities(), offset=offset
                )

                text = text.strip()
                if not text:
                    await send_message(
                        update.effective_message,
                        "There is no note message - You can't JUST have buttons, you need a message to go with it!",
                    )
                    return
            else:
                pass

    elif msg.reply_to_message and len(args) >= 1:
        if msg.reply_to_message.text:
            text_to_parsing = msg.reply_to_message.text
        elif msg.reply_to_message.caption:
            text_to_parsing = msg.reply_to_message.caption
        else:
            text_to_parsing = ""
        offset = len(
            text_to_parsing,
        )  # set correct offset relative to command + notename
        text, buttons = button_markdown_parser(
            text_to_parsing, entities=msg.parse_entities(), offset=offset,
        )
        text = text.strip()

    elif not text and not file_type:
        await send_message(
            update.effective_message,
            "Please provide keyword for this filter reply with!",
        )
        return

    elif msg.reply_to_message:
        if msg.reply_to_message.forum_topic_created:
            return

        if msg.reply_to_message.text:
            text_to_parsing = msg.reply_to_message.text
        elif msg.reply_to_message.caption:
            text_to_parsing = msg.reply_to_message.caption
        else:
            text_to_parsing = ""
        offset = len(
            text_to_parsing,
        )  # set correct offset relative to command + notename
        text, buttons = button_markdown_parser(
            text_to_parsing, entities=msg.parse_entities(), offset=offset,
        )
        text = text.strip()
        if (msg.reply_to_message.text or msg.reply_to_message.caption) and not text:
            await send_message(
                update.effective_message,
                "There is no note message - You can't JUST have buttons, you need a message to go with it!",
            )
            return

    else:
        await send_message(update.effective_message, "Invalid filter!")
        return

    add = await addnew_filter(update, chat_id, keyword, text, file_type, file_id, buttons)
    # This is an old method
    # sql.add_filter(chat_id, keyword, content, is_sticker, is_document, is_image, is_audio, is_voice, is_video, buttons)

    if add is True:
        await send_message(
            update.effective_message,
            "Saved filter '{}' in *{}*!".format(keyword, chat_name),
            parse_mode=ParseMode.MARKDOWN,
        )
    raise ApplicationHandlerStop

@typing_action
@check_admin(is_user=True)
async def stop_filter(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    user = update.effective_user
    args = update.effective_message.text.split(None, 1)

    conn = await connected(context.bot, update, chat, user.id)
    if not conn is False:
        chat_id = conn
        chat_obj = await application.bot.getChat(conn)
        chat_name = chat_obj.title
    else:
        chat_id = update.effective_chat.id
        if chat.type == "private":
            chat_name = "Local filters"
        else:
            chat_name = chat.title

    if len(args) < 2:
        await send_message(update.effective_message, "What should i stop?")
        return

    chat_filters = sql.get_chat_triggers(chat_id)

    if not chat_filters:
        await send_message(update.effective_message, "No filters active here!")
        return

    for keyword in chat_filters:
        if keyword == args[1]:
            sql.remove_filter(chat_id, args[1])
            await send_message(
                update.effective_message,
                "Okay, I'll stop replying to that filter in *{}*.".format(chat_name),
                parse_mode=ParseMode.MARKDOWN,
            )
            raise ApplicationHandlerStop

    await send_message(
        update.effective_message,
        "That's not a filter - Click: /filters to get currently active filters.",
    )



async def reply_filter(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat  
    message = update.effective_message  

    if not update.effective_user or update.effective_user.id == 777000:
        return
    to_match = await extract_text(message)
    if not to_match:
        return

    chat_filters = sql.get_chat_triggers(chat.id)
    for keyword in chat_filters:
        pattern = r"( |^|[^\w])" + re.escape(keyword) + r"( |$|[^\w])"
        if re.search(pattern, to_match, flags=re.IGNORECASE):
            if MessageHandlerChecker.check_user(update.effective_user.id):
                return
            filt = sql.get_filter(chat.id, keyword)
            if filt.reply == "there is should be a new reply":
                buttons = sql.get_buttons(chat.id, filt.keyword)
                keyb = build_keyboard_parser(context.bot, chat.id, buttons)
                keyboard = InlineKeyboardMarkup(keyb)

                VALID_WELCOME_FORMATTERS = [
                    "first",
                    "last",
                    "fullname",
                    "username",
                    "id",
                    "chatname",
                    "mention",
                ]
                if filt.reply_text:
                    if "%%%" in filt.reply_text:
                        split = filt.reply_text.split("%%%")
                        if all(split):
                            text = random.choice(split)
                        else:
                            text = filt.reply_text
                    else:
                        text = filt.reply_text
                    if text.startswith("~!") and text.endswith("!~"):
                        sticker_id = text.replace("~!", "").replace("!~", "")
                        try:
                            await context.bot.send_sticker(
                                chat.id,
                                sticker_id,
                                reply_to_message_id=message.message_id,
                                message_thread_id=message.message_thread_id if chat.is_forum else None
                            )
                            return
                        except BadRequest as excp:
                            if (
                                excp.message
                                == "Wrong remote file identifier specified: wrong padding in the string"
                            ):
                                await context.bot.send_message(
                                    chat.id,
                                    "Message couldn't be sent, Is the sticker id valid?",
                                    message_thread_id=message.message_thread_id if chat.is_forum else None
                                )
                                return
                            else:
                                LOGGER.exception("Error in filters: " + excp.message)
                                return
                    valid_format = escape_invalid_curly_brackets(
                        text, VALID_WELCOME_FORMATTERS,
                    )
                    if valid_format:
                        filtext = valid_format.format(
                            first=escape(message.from_user.first_name),
                            last=escape(
                                message.from_user.last_name
                                or message.from_user.first_name,
                            ),
                            fullname=" ".join(
                                [
                                    escape(message.from_user.first_name),
                                    escape(message.from_user.last_name),
                                ]
                                if message.from_user.last_name
                                else [escape(message.from_user.first_name)],
                            ),
                            username="@" + escape(message.from_user.username)
                            if message.from_user.username
                            else mention_html(
                                message.from_user.id, message.from_user.first_name,
                            ),
                            mention=mention_html(
                                message.from_user.id, message.from_user.first_name,
                            ),
                            chatname=escape(message.chat.title)
                            if message.chat.type != "private"
                            else escape(message.from_user.first_name),
                            id=message.from_user.id,
                        )
                    else:
                        filtext = ""
                else:
                    filtext = ""

                if filt.file_type in (sql.Types.BUTTON_TEXT, sql.Types.TEXT):
                    try:
                        await message.reply_text(
                            markdown_to_html(filtext),
                            parse_mode=ParseMode.HTML,
                            disable_web_page_preview=True,
                            reply_markup=keyboard
                        )
                    except BadRequest as excp:
                        LOGGER.exception("Error in filters: " + excp.message)
                        try:
                            await send_message(
                                update.effective_message,
                                get_exception(excp, filt, chat),
                            )
                        except BadRequest as excp:
                            LOGGER.exception(
                                "Failed to send message: " + excp.message,
                            )
                else:
                    try:
                        await ENUM_FUNC_MAP[filt.file_type](
                            chat.id,
                            filt.file_id,
                            reply_markup=keyboard,
                            reply_to_message_id=message.message_id,
                            message_thread_id=message.message_thread_id if chat.is_forum else None
                        )
                    except BadRequest:
                        await send_message(
                            message,
                            "I don't have the permission to send the content of the filter.",
                        )
                break
            else:
                if filt.is_sticker:
                    await message.reply_sticker(filt.reply)
                elif filt.is_document:
                    await message.reply_document(filt.reply)
                elif filt.is_image:
                    await message.reply_photo(filt.reply)
                elif filt.is_audio:
                    await message.reply_audio(filt.reply)
                elif filt.is_voice:
                    await message.reply_voice(filt.reply)
                elif filt.is_video:
                    await message.reply_video(filt.reply)
                elif filt.has_markdown:
                    buttons = sql.get_buttons(chat.id, filt.keyword)
                    keyb = build_keyboard_parser(context.bot, chat.id, buttons)
                    keyboard = InlineKeyboardMarkup(keyb)

                    try:
                        await context.bot.send_message(
                            chat.id,
                            markdown_to_html(filt.reply),
                            parse_mode=ParseMode.HTML,
                            disable_web_page_preview=True,
                            reply_markup=keyboard,
                            message_thread_id=message.message_thread_id if chat.is_forum else None
                        )
                    except BadRequest as excp:
                        if excp.message == "Unsupported url protocol":
                            try:
                                await send_message(
                                    update.effective_message,
                                    "You seem to be trying to use an unsupported url protocol. "
                                    "Telegram doesn't support buttons for some protocols, such as tg://. Please try "
                                    "again...",
                                )
                            except BadRequest as excp:
                                LOGGER.exception("Error in filters: " + excp.message)
                        else:
                            try:
                                await send_message(
                                    update.effective_message,
                                    "This message couldn't be sent as it's incorrectly formatted.",
                                )
                            except BadRequest as excp:
                                LOGGER.exception("Error in filters: " + excp.message)
                            LOGGER.warning(
                                "Message %s could not be parsed", str(filt.reply),
                            )
                            LOGGER.exception(
                                "Could not parse filter %s in chat %s",
                                str(filt.keyword),
                                str(chat.id),
                            )

                else:
                    # LEGACY - all new filters will have has_markdown set to True.
                    try:
                        await context.bot.send_message(
                            chat.id, 
                            filt.reply, 
                            message_thread_id=message.message_thread_id if chat.is_forum else None
                        )
                    except BadRequest as excp:
                        LOGGER.exception("Error in filters: " + excp.message)
                break



async def rmall_filters(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    user = update.effective_user
    member = await chat.get_member(user.id)
    if member.status != ChatMemberStatus.OWNER and user.id not in DRAGONS:
        await update.effective_message.reply_text(
            "Only the chat owner can clear all notes at once.",
        )
    else:
        buttons = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text="Stop all filters", callback_data="filters_rmall",
                    ),
                ],
                [InlineKeyboardButton(text="Cancel", callback_data="filters_cancel")],
            ],
        )
        await update.effective_message.reply_text(
            f"Are you sure you would like to stop ALL filters in {chat.title}? This action cannot be undone.",
            reply_markup=buttons,
            parse_mode=ParseMode.MARKDOWN,
        )



async def rmall_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    chat = update.effective_chat
    msg = update.effective_message
    member = await chat.get_member(query.from_user.id)
    if query.data == "filters_rmall":
        if member.status == "creator" or query.from_user.id in DRAGONS:
            allfilters = sql.get_chat_triggers(chat.id)
            if not allfilters:
                msg.edit_text("No filters in this chat, nothing to stop!")
                return

            count = 0
            filterlist = []
            for x in allfilters:
                count += 1
                filterlist.append(x)

            for i in filterlist:
                sql.remove_filter(chat.id, i)

            msg.edit_text(f"Cleaned {count} filters in {chat.title}")

        if member.status == "administrator":
            await query.answer("Only owner of the chat can do this.")

        if member.status == "member":
            await query.answer("You need to be admin to do this.")
    elif query.data == "filters_cancel":
        if member.status == "creator" or query.from_user.id in DRAGONS:
            msg.edit_text("Clearing of all filters has been cancelled.")
            return
        if member.status == "administrator":
            await query.answer("Only owner of the chat can do this.")
        if member.status == "member":
            await query.answer("You need to be admin to do this.")


# NOT ASYNC NOT A HANDLER
def get_exception(excp, filt, chat):
    if excp.message == "Unsupported url protocol":
        return "You seem to be trying to use the URL protocol which is not supported. Telegram does not support key for multiple protocols, such as tg: //. Please try again!"
    elif excp.message == "Reply message not found":
        return "noreply"
    else:
        LOGGER.warning("Message %s could not be parsed", str(filt.reply))
        LOGGER.exception(
            "Could not parse filter %s in chat %s", str(filt.keyword), str(chat.id),
        )
        return "This data could not be sent because it is incorrectly formatted."


# NOT ASYNC NOT A HANDLER
async def addnew_filter(update, chat_id, keyword, text, file_type, file_id, buttons):
    msg = update.effective_message
    totalfilt = sql.get_chat_triggers(chat_id)
    if len(totalfilt) >= 150:  # Idk why i made this like function....
        await msg.reply_text("This group has reached its max filters limit of 150.")
        return False
    else:
        sql.new_add_filter(chat_id, keyword, text, file_type, file_id, buttons)
        return True


def __stats__():
    return "• {} filters, across {} chats.".format(sql.num_filters(), sql.num_chats())


async def __import_data__(chat_id, data, message):
    # set chat filters
    filters = data.get("filters", {})
    for trigger in filters:
        sql.add_to_blacklist(chat_id, trigger)


def __migrate__(old_chat_id, new_chat_id):
    sql.migrate_chat(old_chat_id, new_chat_id)


def __chat_settings__(chat_id, user_id):
    cust_filters = sql.get_chat_triggers(chat_id)
    return "There are `{}` custom filters here.".format(len(cust_filters))



__help__ = """
• /filters*:* ʟɪsᴛ ᴀʟʟ ᴀᴄᴛɪᴠᴇ ғɪʟᴛᴇʀs sᴀᴠᴇᴅ ɪɴ ᴛʜᴇ ᴄʜᴀᴛ.

*ᴀᴅᴍɪɴ ᴏɴʟʏ:*

• /filter <ᴋᴇʏᴡᴏʀᴅ> <ʀᴇᴘʟʏ ᴍᴇssᴀɢᴇ>*:* ᴀᴅᴅ ᴀ ғɪʟᴛᴇʀ ᴛᴏ ᴛʜɪs ᴄʜᴀᴛ. ᴛʜᴇ ʙᴏᴛ ᴡɪʟʟ ɴᴏᴡ ʀᴇᴘʟʏ ᴛʜᴀᴛ ᴍᴇssᴀɢᴇ ᴡʜᴇɴᴇᴠᴇʀ 'ᴋᴇʏᴡᴏʀᴅ\
ɪs ᴍᴇɴᴛɪᴏɴᴇᴅ. ɪғ ʏᴏᴜ ʀᴇᴘʟʏ ᴛᴏ ᴀ sᴛɪᴄᴋᴇʀ ᴡɪᴛʜ ᴀ ᴋᴇʏᴡᴏʀᴅ, ᴛʜᴇ ʙᴏᴛ ᴡɪʟʟ ʀᴇᴘʟʏ ᴡɪᴛʜ ᴛʜᴀᴛ sᴛɪᴄᴋᴇʀ. 
ɴᴏᴛᴇ: ᴀʟʟ ғɪʟᴛᴇʀ \
ᴋᴇʏᴡᴏʀᴅs ᴀʀᴇ ɪɴ ʟᴏᴡᴇʀᴄᴀsᴇ. ɪғ ʏᴏᴜ ᴡᴀɴᴛ ʏᴏᴜʀ ᴋᴇʏᴡᴏʀᴅ ᴛᴏ ʙᴇ a sᴇɴᴛᴇɴᴄᴇ, ᴜsᴇ ǫᴜᴏᴛᴇs. ᴇɢ: /filter "ʜᴇʏ ᴛʜᴇʀᴇ" ʜᴏᴡ ʏᴏᴜ \
ᴅᴏɪɴ? 
 sᴇᴘᴀʀᴀᴛᴇ ᴅɪғғ ʀᴇᴘʟɪᴇs ʙʏ `%%%` ᴛᴏ ɢᴇᴛ ʀᴀɴᴅᴏᴍ ʀᴇᴘʟɪᴇs
 
 *ᴇxᴀᴍᴘʟᴇ:*
 `/filter "filtername"
 ʀᴇᴘʟʏ 1
 %%%
 ʀᴇᴘʟʏ 2
 %%%
 ʀᴇᴘʟʏ 3`
• /stop <ғɪʟᴛᴇʀ ᴋᴇʏᴡᴏʀᴅ>*:* sᴛᴏᴘ ᴛʜᴀᴛ ғɪʟᴛᴇʀ.

*ᴄʜᴀᴛ ᴄʀᴇᴀᴛᴏʀ ᴏɴʟʏ:*
• /removeallfilters*:* ʀᴇᴍᴏᴠᴇ ᴀʟʟ ᴄʜᴀᴛ ғɪʟᴛᴇʀs ᴀᴛ ᴏɴᴄᴇ.

*ɴᴏᴛᴇ*: ғɪʟᴛᴇʀs ᴀʟsᴏ sᴜᴘᴘᴏʀᴛ ᴍᴀʀᴋᴅᴏᴡɴ ғᴏʀᴍᴀᴛᴛᴇʀs ʟɪᴋᴇ: {first}, {last} ᴇᴛᴄ.. ᴀɴᴅ ʙᴜᴛᴛᴏɴs.

ᴄʜᴇᴄᴋ `/markdownhelp` ᴛᴏ ᴋɴᴏᴡ ᴍᴏʀᴇ!

"""

__mod_name__ = "𝐅ɪʟᴛᴇʀs"


FILTER_HANDLER = CommandHandler("filter", filters, block=False)
STOP_HANDLER = CommandHandler("stop", stop_filter, block=False)
RMALLFILTER_HANDLER = CommandHandler(
    "removeallfilters", rmall_filters, filters=filters_module.ChatType.GROUPS, block=False
)
RMALLFILTER_CALLBACK = CallbackQueryHandler(rmall_callback, pattern=r"filters_.*", block=False)
LIST_HANDLER = DisableAbleCommandHandler("filters", list_handlers, admin_ok=True, block=False)
CUST_FILTER_HANDLER = MessageHandler(
    filters_module.TEXT & ~filters_module.UpdateType.EDITED_MESSAGE, reply_filter, block=False
)

application.add_handler(FILTER_HANDLER)
application.add_handler(STOP_HANDLER)
application.add_handler(LIST_HANDLER)
application.add_handler(CUST_FILTER_HANDLER, HANDLER_GROUP)
application.add_handler(RMALLFILTER_HANDLER)
application.add_handler(RMALLFILTER_CALLBACK)

__handlers__ = [
    FILTER_HANDLER,
    STOP_HANDLER,
    LIST_HANDLER,
    (CUST_FILTER_HANDLER, HANDLER_GROUP, RMALLFILTER_HANDLER),
]
