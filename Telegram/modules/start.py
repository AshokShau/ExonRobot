import html
from random import choice
from typing import cast

from telegram import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
    Update,
)
from telegram.constants import ChatType
from telegram.error import BadRequest, Forbidden
from telegram.ext import ContextTypes

from Telegram import HELP_COMMANDS, LOGGER, Cb, Cmd
from Telegram.utils.misc import StartPic, ikb
from Telegram.utils.start import (
    PM_HELP_TEXT,
    PM_START_TEXT,
    gen_help_keyboard,
    get_help_msg,
)


@Cmd(command="start")
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Start command"""
    args = context.args
    message = update.effective_message
    chat = update.effective_chat
    if chat.type == ChatType.PRIVATE:
        if args:
            help_option = args[0].lower()
            if help_option.startswith("rules") and (
                help_option not in ("rule", "rules")
            ):
                return None

            if help_option.startswith("note") and (
                help_option not in ("note", "notes")
            ):
                return None

            if help_option.startswith("captcha") and (
                help_option not in ("captcha", "captchas")
            ):
                return None

            help_msg, help_kb = await get_help_msg(help_option)
            if not help_msg:
                LOGGER.warning(f"No help_msg found for help_option - {help_option}.")
                return None
            await message.reply_photo(
                photo=choice(StartPic),
                caption=help_msg,
                reply_markup=help_kb,
            )
            return None

        try:
            await message.reply_photo(
                photo=choice(StartPic),
                caption=PM_START_TEXT.format(
                    html.escape(update.effective_user.first_name),
                    context.bot.first_name,
                ),
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                text="Aᴅᴅ ᴍᴇ ɪɴ ʏᴏᴜʀ ɢʀᴏᴜᴘ",
                                url=f"https://t.me/{context.bot.username}?startgroup=new",
                            )
                        ],
                        [
                            InlineKeyboardButton(
                                text="Hᴇʟᴘ & Cᴏᴍᴍᴀɴᴅs",
                                callback_data="commands",
                            )
                        ],
                    ]
                ),
            )
        except BadRequest as exc:
            raise exc
        except Forbidden as exc:
            if "user is deactivated" not in exc.message:
                raise exc

    else:
        help_option = args[0].lower() if args else "help"
        await message.reply_photo(
            photo=choice(StartPic),
            caption="ʜᴇʏᴀ; ᴘᴍ ᴍᴇ ɪғ ʏᴏᴜ ʜᴀᴠᴇ ᴀɴʏ ǫᴜᴇsᴛɪᴏɴs ᴏɴ ʜᴏᴡ ᴛᴏ ᴜsᴇ ᴍᴇ.",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text=" ᴏᴩᴇɴ ɪɴ ᴩʀɪᴠᴀᴛᴇ ",
                            url=f"https://t.me/{context.bot.username}?start={help_option}",
                        )
                    ]
                ]
            ),
        )

    return None


@Cmd(command="help")
async def help_(update: Update, context: ContextTypes.DEFAULT_TYPE) -> Message | None:
    """Help command"""
    arg = context.args
    m = cast(Message, update.effective_message)
    if arg:
        help_option = arg[0]
        help_msg, help_kb = await get_help_msg(help_option)
        if not help_msg:
            LOGGER.warning(f"ɴᴏ ʜᴇʟᴘ_ᴍsɢ ғᴏᴜɴᴅ ғᴏʀ ʜᴇʟᴘ_ᴏᴘᴛɪᴏɴ - {help_option}.")
            return None
        if update.effective_chat.type == ChatType.PRIVATE:
            if len(help_msg) >= 1026:
                return await m.reply_text(help_msg, reply_markup=help_kb)
            await m.reply_photo(
                photo=str(choice(StartPic)),
                caption=help_msg,
                reply_markup=help_kb,
            )
        else:
            await m.reply_photo(
                photo=str(choice(StartPic)),
                caption=f"ᴘʀᴇss ᴛʜᴇ ʙᴜᴛᴛᴏɴ ʙᴇʟᴏᴡ ᴛᴏ ɢᴇᴛ ʜᴇʟᴘ ғᴏʀ <b>{help_option}</b>",
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                "Hᴇʟᴘ",
                                url=f"t.me/{context.bot.username}?start={help_option}",
                            ),
                        ],
                    ],
                ),
            )
    else:
        if m.chat.type == ChatType.PRIVATE:
            keyboard = ikb(gen_help_keyboard(), "start_back")
            msg = "<b>ᴄʟɪᴄᴋ ᴏɴ ᴛʜᴇ ʜᴇʟᴩ ʙᴜᴛᴛᴏɴ ᴛᴏ ɢᴇᴛ ɪɴғᴏʀᴍᴀᴛɪᴏɴ ᴀʙᴏᴜᴛ ᴍʏ ᴍᴏᴅᴜʟᴇs ᴀɴᴅ ᴄᴏᴍᴍᴀɴᴅs.</b>"
        else:
            keyboard = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "Hᴇʟᴘ",
                            url=f"t.me/{context.bot.username}?start=start_help",
                        ),
                    ],
                ],
            )
            msg = "ᴄᴏɴᴛᴀᴄᴛ ᴍᴇ ɪɴ <b>PM</b> ᴛᴏ ɢᴇᴛ ᴛʜᴇ ʟɪsᴛ ᴏғ ᴘᴏssɪʙʟᴇ ᴄᴏᴍᴍᴀɴᴅs."
        await m.reply_photo(
            photo=str(choice(StartPic)),
            caption=msg,
            reply_markup=keyboard,
        )


@Cb(pattern="^modules.")
async def modules(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Callback for help command"""
    q = cast(CallbackQuery, update.callback_query)
    module = q.data.split(".", 1)[1]

    help_msg = HELP_COMMANDS[f"modules.{module}"]["help_msg"]

    help_kb = HELP_COMMANDS[f"modules.{module}"]["buttons"]
    try:
        await q.edit_message_caption(
            caption=help_msg,
            reply_markup=ikb(help_kb, "commands"),
        )
    except BadRequest as exc:
        if exc.message in [
            "Message is not modified",
            "Message to edit not found",
            "Message is not modified: specified new message content",
        ]:
            pass
        elif "too long" in str(exc):
            await q.message.delete()
            await context.bot.send_message(
                chat_id=q.message.chat.id,
                text=help_msg,
                reply_markup=ikb(help_kb, "commands"),
            )
        else:
            raise exc


@Cb(pattern="^commands")
async def commands(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Callback for help command"""
    query = cast(CallbackQuery, update.callback_query)
    keyboard = ikb(gen_help_keyboard(), "start_back")
    try:
        await query.message.edit_caption(
            caption=PM_HELP_TEXT,
            reply_markup=keyboard,
        )
    except BadRequest as exc:
        if exc.message in [
            "Message is not modified",
            "Message to edit not found",
            "Message is not modified: specified new message content",
        ]:
            pass
        elif "too long" in str(exc):
            await context.bot.send_message(
                chat_id=query.message.chat.id,
                text=PM_HELP_TEXT,
                reply_markup=keyboard,
            )
            return await query.message.delete()
        else:
            raise exc


@Cb(pattern="^start_")
async def callbacks(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Callback for help command"""
    query = update.callback_query
    if query.data == "start_back":
        await query.answer(text="Home menu")
        try:
            await query.message.edit_caption(
                caption=PM_START_TEXT.format(
                    html.escape(update.effective_user.first_name),
                    context.bot.first_name,
                ),
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                text="Aᴅᴅ ᴍᴇ ɪɴ ʏᴏᴜʀ ɢʀᴏᴜᴘ",
                                url=f"https://t.me/{context.bot.username}?startgroup=new",
                            )
                        ],
                        [
                            InlineKeyboardButton(
                                text="Hᴇʟᴘ & Cᴏᴍᴍᴀɴᴅs",
                                callback_data="commands",
                            )
                        ],
                    ]
                ),
            )
        except BadRequest as exc:
            if exc.message not in [
                "Message is not modified",
                "Message to edit not found",
                "Can't access the chat",
                "Chat not found",
            ]:
                raise exc
