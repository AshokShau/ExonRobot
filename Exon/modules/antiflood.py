import html
import re

from telegram import ChatPermissions, Update
from telegram.error import BadRequest
from telegram.ext import (
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)
from telegram.helpers import mention_html

from Exon import application
from Exon.modules.connection import connected
from Exon.modules.helper_funcs.alternate import send_message
from Exon.modules.helper_funcs.chat_status import check_admin, is_user_admin
from Exon.modules.helper_funcs.string_handling import extract_time
from Exon.modules.log_channel import loggable
from Exon.modules.sql import antiflood_sql as sql
from Exon.modules.sql.approve_sql import is_approved

FLOOD_GROUP = 3


@loggable
async def check_flood(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    user = update.effective_user  # type: Optional[User]
    chat = update.effective_chat  # type: Optional[Chat]
    msg = update.effective_message  # type: Optional[Message]
    if not user:  # ignore channels
        return ""

    # ignore admins
    if await is_user_admin(chat, user.id):
        sql.update_flood(chat.id, None)
        return ""
    # ignore approved users
    if is_approved(chat.id, user.id):
        sql.update_flood(chat.id, None)
        return
    should_ban = sql.update_flood(chat.id, user.id)
    if not should_ban:
        return ""

    try:
        getmode, getvalue = sql.get_flood_setting(chat.id)
        if getmode == 1:
            await chat.ban_member(user.id)
            execstrings = "ʙᴀɴɴᴇᴅ"
            tag = "BANNED"
        elif getmode == 2:
            await chat.ban_member(user.id)
            await chat.unban_member(user.id)
            execstrings = "ᴋɪᴄᴋᴇᴅ"
            tag = "KICKED"
        elif getmode == 3:
            await context.bot.restrict_chat_member(
                chat.id,
                user.id,
                permissions=ChatPermissions(can_send_messages=False),
            )
            execstrings = "ᴍᴜᴛᴇᴅ"
            tag = "MUTED"
        elif getmode == 4:
            bantime = await extract_time(msg, getvalue)
            await chat.ban_member(user.id, until_date=bantime)
            execstrings = "ʙᴀɴɴᴇᴅ ғᴏʀ {}".format(getvalue)
            tag = "TBAN"
        elif getmode == 5:
            mutetime = await extract_time(msg, getvalue)
            await context.bot.restrict_chat_member(
                chat.id,
                user.id,
                until_date=mutetime,
                permissions=ChatPermissions(can_send_messages=False),
            )
            execstrings = "ᴍᴜᴛᴇᴅ ғᴏʀ {}".format(getvalue)
            tag = "TMUTE"
        await send_message(
            update.effective_message,
            "ʙᴇᴇᴘ ʙᴏᴏᴘ! ʙᴏᴏᴘ ʙᴇᴇᴘ!\n{}!".format(execstrings),
        )

        return (
            "<b>{}:</b>"
            "\n#{}"
            "\n<b>ᴜsᴇʀ:</b> {}"
            "\nғʟᴏᴏᴅᴇᴅ ᴛʜᴇ ɢʀᴏᴜᴘ.".format(
                tag,
                html.escape(chat.title),
                mention_html(user.id, html.escape(user.first_name)),
            )
        )

    except BadRequest:
        await msg.reply_text(
            "I ᴄᴀɴ'ᴛ ʀᴇsᴛʀɪᴄᴛ ᴘᴇᴏᴘʟᴇ ʜᴇʀᴇ, ɢɪᴠᴇ ᴍᴇ ᴘᴇʀᴍɪssɪᴏɴs ғɪʀsᴛ! ᴜɴᴛɪʟ ᴛʜᴇɴ, I'ʟʟ ᴅɪsᴀʙʟᴇ ᴀɴᴛɪ-ғʟᴏᴏᴅ.",
        )
        sql.set_flood(chat.id, 0)
        return (
            "<b>{}:</b>"
            "\n#𝐈𝐍𝐅𝐎"
            "\nᴅᴏɴ'ᴛ ʜᴀᴠᴇ ᴇɴᴏᴜɢʜ ᴘᴇʀᴍɪssɪᴏɴ ᴛᴏ ʀᴇsᴛʀɪᴄᴛ ᴜsᴇʀs sᴏ ᴀᴜᴛᴏᴍᴀᴛɪᴄᴀʟʟʏ ᴅɪsᴀʙʟᴇᴅ ᴀɴᴛɪ-ғʟᴏᴏᴅ".format(
                chat.title,
            )
        )


@check_admin(permission="can_restrict_members", is_both=True, no_reply=True)
async def flood_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bot = context.bot
    query = update.callback_query
    user = update.effective_user
    match = re.match(r"unmute_flooder\((.+?)\)", query.data)
    if match:
        user_id = match.group(1)
        chat = update.effective_chat.id
        try:
            await bot.restrict_chat_member(
                chat,
                int(user_id),
                permissions=ChatPermissions(
                    can_send_messages=True,
                    can_send_media_messages=True,
                    can_send_other_messages=True,
                    can_add_web_page_previews=True,
                ),
            )
            await update.effective_message.edit_text(
                f"ᴜɴᴍᴜᴛᴇᴅ ʙʏ {mention_html(user.id, html.escape(user.first_name))}.",
                parse_mode="HTML",
            )
        except:
            pass


@loggable
@check_admin(is_user=True)
async def set_flood(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    chat = update.effective_chat  # type: Optional[Chat]
    user = update.effective_user  # type: Optional[User]
    message = update.effective_message  # type: Optional[Message]
    args = context.args

    conn = await connected(context.bot, update, chat, user.id, need_admin=True)
    if conn:
        chat_id = conn
        chat_obj = await application.bot.getChat(conn)
        chat_name = chat_obj.title
    else:
        if update.effective_message.chat.type == "private":
            await send_message(
                update.effective_message,
                "ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ ɪs ᴍᴇᴀɴᴛ ᴛᴏ ᴜsᴇ ɪɴ ɢʀᴏᴜᴘ ɴᴏᴛ ɪɴ PM",
            )
            return ""
        chat_id = update.effective_chat.id
        chat_name = update.effective_message.chat.title

    if len(args) >= 1:
        val = args[0].lower()
        if val in ["off", "no", "0"]:
            sql.set_flood(chat_id, 0)
            if conn:
                text = await message.reply_text(
                    "ᴀɴᴛɪғʟᴏᴏᴅ ʜᴀs ʙᴇᴇɴ ᴅɪsᴀʙʟᴇᴅ ɪɴ {}.".format(chat_name),
                )
            else:
                text = await message.reply_text("ᴀɴᴛɪғʟᴏᴏᴅ ʜᴀs ʙᴇᴇɴ ᴅɪsᴀʙʟᴇᴅ.")

        elif val.isdigit():
            amount = int(val)
            if amount <= 0:
                sql.set_flood(chat_id, 0)
                if conn:
                    text = await message.reply_text(
                        "ᴀɴᴛɪғʟᴏᴏᴅ ʜᴀs ʙᴇᴇɴ ᴅɪsᴀʙʟᴇᴅ ɪɴ {}.".format(chat_name),
                    )
                else:
                    text = await message.reply_text("ᴀɴᴛɪғʟᴏᴏᴅ ʜᴀs ʙᴇᴇɴ ᴅɪsᴀʙʟᴇᴅ.")
                return (
                    "<b>{}:</b>"
                    "\n#𝐒𝐄𝐓𝐅𝐋𝐎𝐎𝐃"
                    "\n<b>ᴀᴅᴍɪɴ:</b> {}"
                    "\nᴅɪsᴀʙʟᴇ ᴀɴᴛɪғʟᴏᴏᴅ.".format(
                        html.escape(chat_name),
                        mention_html(user.id, html.escape(user.first_name)),
                    )
                )

            elif amount <= 3:
                await send_message(
                    update.effective_message,
                    "ᴀɴᴛɪғʟᴏᴏᴅ ᴍᴜsᴛ ʙᴇ ᴇɪᴛʜᴇʀ 0 (disabled) ᴏʀ ɴᴜᴍʙᴇʀ ɢʀᴇᴀᴛᴇʀ ᴛʜᴀɴ 3!",
                )
                return ""

            else:
                sql.set_flood(chat_id, amount)
                if conn:
                    text = await message.reply_text(
                        "ᴀɴᴛɪ-ғʟᴏᴏᴅ ʜᴀs ʙᴇᴇɴ sᴇᴛ ᴛᴏ {} ɪɴ ᴄʜᴀᴛ: {}".format(
                            amount,
                            chat_name,
                        ),
                    )
                else:
                    text = await message.reply_text(
                        "sᴜᴄᴄᴇssғᴜʟʟʏ ᴜᴘᴅᴀᴛᴇᴅ anti-ғʟᴏᴏᴅ ʟɪᴍɪᴛ to {}!".format(amount),
                    )
                return (
                    "<b>{}:</b>"
                    "\n#𝐒𝐄𝐓𝐅𝐋𝐎𝐎𝐃"
                    "\n<b>ᴀᴅᴍɪɴ:</b> {}"
                    "\nsᴇᴛ ᴀɴᴛɪғʟᴏᴏᴅ ᴛᴏ <code>{}</code>.".format(
                        html.escape(chat_name),
                        mention_html(user.id, html.escape(user.first_name)),
                        amount,
                    )
                )

        else:
            await message.reply_text(
                "ɪɴᴠᴀʟɪᴅ ᴀʀɢᴜᴍᴇɴᴛ ᴘʟᴇᴀsᴇ ᴜsᴇ ᴀ ɴᴜᴍʙᴇʀ, 'off' ᴏʀ 'no'"
            )
    else:
        await message.reply_text(
            (
                "ᴜsᴇ `/setflood number` ᴛᴏ ᴇɴᴀʙʟᴇ ᴀɴᴛɪ-ғʟᴏᴏᴅ .\nᴏʀ ᴜsᴇ `/setflood off` ᴛᴏ ᴅɪsᴀʙʟᴇ ᴀɴᴛɪ-ғʟᴏᴏᴅ!."
            ),
            parse_mode="markdown",
        )
    return ""


async def flood(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat  # type: Optional[Chat]
    user = update.effective_user  # type: Optional[User]
    msg = update.effective_message

    conn = await connected(context.bot, update, chat, user.id, need_admin=False)
    if conn:
        chat_id = conn
        chat_obj = await application.bot.getChat(conn)
        chat_name = chat_obj.title
    else:
        if update.effective_message.chat.type == "private":
            await send_message(
                update.effective_message,
                "ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ ɪs ᴍᴇᴀɴᴛ ᴛᴏ ᴜsᴇ ɪɴ ɢʀᴏᴜᴘ ɴᴏᴛ ɪɴ PM",
            )
            return
        chat_id = update.effective_chat.id
        chat_name = update.effective_message.chat.title

    limit = sql.get_flood_limit(chat_id)
    if limit == 0:
        if conn:
            text = await msg.reply_text(
                "I'm ɴᴏᴛ ᴇɴғᴏʀᴄɪɴɢ ᴀɴʏ ғʟᴏᴏᴅ ᴄᴏɴᴛʀᴏʟ ɪɴ {}!".format(chat_name),
            )
        else:
            text = await msg.reply_text("I'ᴍ ɴᴏᴛ ᴇɴғᴏʀᴄɪɴɢ ᴀɴʏ ғʟᴏᴏᴅ ᴄᴏɴᴛʀᴏʟ ʜᴇʀᴇ!")
    else:
        if conn:
            text = await msg.reply_text(
                "I'ᴍ ᴄᴜʀʀᴇɴᴛʟʏ ʀᴇsᴛʀɪᴄᴛɪɴɢ ᴍᴇᴍʙᴇʀs ᴀғᴛᴇʀ {} ᴄᴏɴsᴇᴄᴜᴛɪᴠᴇ ᴍᴇssᴀɢᴇs ɪɴ {}.".format(
                    limit,
                    chat_name,
                ),
            )
        else:
            text = await msg.reply_text(
                "I'ᴍ ᴄᴜʀʀᴇɴᴛʟʏ ʀᴇsᴛʀɪᴄᴛɪɴɢ ᴍᴇᴍʙᴇʀs ᴀғᴛᴇʀ {} ᴄᴏɴsᴇᴄᴜᴛɪᴠᴇ ᴍᴇssᴀɢᴇs.".format(
                    limit,
                ),
            )


@check_admin(is_user=True)
async def set_flood_mode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat  # type: Optional[Chat]
    user = update.effective_user  # type: Optional[User]
    msg = update.effective_message  # type: Optional[Message]
    args = context.args

    conn = await connected(context.bot, update, chat, user.id, need_admin=True)
    if conn:
        chat = await application.bot.getChat(conn)
        chat_id = conn
        chat_obj = await application.bot.getChat(conn)
        chat_name = chat_obj.title
    else:
        if update.effective_message.chat.type == "private":
            await send_message(
                update.effective_message,
                "ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ ɪs ᴍᴇᴀɴᴛ ᴛᴏ ᴜsᴇ ɪɴ ɢʀᴏᴜᴘ ɴᴏᴛ ɪɴ PM",
            )
            return ""
        chat = update.effective_chat
        chat_id = update.effective_chat.id
        chat_name = update.effective_message.chat.title

    if args:
        if args[0].lower() == "ban":
            settypeflood = "ʙᴀɴ"
            sql.set_flood_strength(chat_id, 1, "0")
        elif args[0].lower() == "kick":
            settypeflood = "ᴋɪᴄᴋ"
            sql.set_flood_strength(chat_id, 2, "0")
        elif args[0].lower() == "mute":
            settypeflood = "ᴍᴜᴛᴇ"
            sql.set_flood_strength(chat_id, 3, "0")
        elif args[0].lower() == "tban":
            if len(args) == 1:
                teks = """ɪᴛ ʟᴏᴏᴋs ʟɪᴋᴇ ʏᴏᴜ ᴛʀɪᴇᴅ ᴛᴏ sᴇᴛ ᴛɪᴍᴇ ᴠᴀʟᴜᴇ ғᴏʀ ᴀɴᴛɪғʟᴏᴏᴅ ʙᴜᴛ ʏᴏᴜ ᴅɪᴅɴ'ᴛ sᴘᴇᴄɪғɪᴇᴅ ᴛɪᴍᴇ; ᴛʀʏ, `/setfloodmode tban <ᴛɪᴍᴇᴠᴀʟᴜᴇ>`.
ᴇxᴀᴍᴘʟᴇs ᴏғ ᴛɪᴍᴇ ᴠᴀʟᴜᴇ: 4m = 4 ᴍɪɴᴜᴛᴇs, 3h = 3 ʜᴏᴜʀs, 6d = 6 ᴅᴀʏs, 5w = 5 ᴡᴇᴇᴋs."""
                await send_message(
                    update.effective_message, teks, parse_mode="markdown"
                )
                return
            settypeflood = "ᴛʙᴀɴ ғᴏʀ {}".format(args[1])
            sql.set_flood_strength(chat_id, 4, str(args[1]))
        elif args[0].lower() == "tmute":
            if len(args) == 1:
                teks = (
                    update.effective_message,
                    """It looks like you tried to set time value for antiflood but you didn't specified time; Try, `/setfloodmode tmute <timevalue>`.
Examples of time value: 4m = 4 minutes, 3h = 3 hours, 6d = 6 days, 5w = 5 weeks.""",
                )
                await send_message(
                    update.effective_message, teks, parse_mode="markdown"
                )
                return
            settypeflood = "ᴛᴍᴜᴛᴇ ғᴏʀ {}".format(args[1])
            sql.set_flood_strength(chat_id, 5, str(args[1]))
        else:
            await send_message(
                update.effective_message,
                "ɪ ᴏɴʟʏ ᴜɴᴅᴇʀsᴛᴀɴᴅ ban/kick/mute/tban/tmute!",
            )
            return
        if conn:
            text = await msg.reply_text(
                "ᴇxᴄᴇᴇᴅɪɴɢ ᴄᴏɴsᴇᴄᴜᴛɪᴠᴇ ғʟᴏᴏᴅ ʟɪᴍɪᴛ ᴡɪʟʟ ʀᴇsᴜʟᴛ ɪɴ {} in {}!".format(
                    settypeflood,
                    chat_name,
                ),
            )
        else:
            text = await msg.reply_text(
                "ᴇxᴄᴇᴇᴅɪɴɢ ᴄᴏɴsᴇᴄᴜᴛɪᴠᴇ ғʟᴏᴏᴅ ʟɪᴍɪᴛ ᴡɪʟʟ ʀᴇsᴜʟᴛ ɪɴ {}!".format(
                    settypeflood,
                ),
            )
        return (
            "<b>{}:</b>\n"
            "<b>ᴀᴅᴍɪɴ:</b> {}\n"
            "ʜᴀs ᴄʜᴀɴɢᴇᴅ ᴀɴᴛɪ-ғʟᴏᴏᴅ ᴍᴏᴅᴇ. ᴜsᴇʀ ᴡɪʟʟ {}.".format(
                settypeflood,
                html.escape(chat.title),
                mention_html(user.id, html.escape(user.first_name)),
            )
        )
    else:
        getmode, getvalue = sql.get_flood_setting(chat.id)
        if getmode == 1:
            settypeflood = "ʙᴀɴ"
        elif getmode == 2:
            settypeflood = "ᴋɪᴄᴋ"
        elif getmode == 3:
            settypeflood = "ᴍᴜᴛᴇ"
        elif getmode == 4:
            settypeflood = "ᴛʙᴀɴ ғᴏʀ {}".format(getvalue)
        elif getmode == 5:
            settypeflood = "ᴛᴍᴜᴛᴇ ғᴏʀ {}".format(getvalue)
        if conn:
            text = await msg.reply_text(
                "sᴇɴᴅɪɴɢ ᴍᴏʀᴇ ᴍᴇssᴀɢᴇs ᴛʜᴀɴ ғʟᴏᴏᴅ ʟɪᴍɪᴛ ᴡɪʟʟ ʀᴇsᴜʟᴛ ɪɴ {} ɪɴ {}.".format(
                    settypeflood,
                    chat_name,
                ),
            )
        else:
            text = await msg.reply_text(
                "sᴇɴᴅɪɴɢ ᴍᴏʀᴇ ᴍᴇssᴀɢᴇ ᴛʜᴀɴ ғʟᴏᴏᴅ ʟɪᴍɪᴛ ᴡɪʟʟ ʀᴇsᴜʟᴛ ɪɴ {}.".format(
                    settypeflood,
                ),
            )
    return ""


def __migrate__(old_chat_id, new_chat_id):
    sql.migrate_chat(old_chat_id, new_chat_id)


def __chat_settings__(chat_id, user_id):
    limit = sql.get_flood_limit(chat_id)
    if limit == 0:
        return "ɴᴏᴛ ᴇɴғᴏʀᴄɪɴɢ ᴛᴏ ғʟᴏᴏᴅ ᴄᴏɴᴛʀᴏʟ."
    else:
        return "ᴀɴᴛɪғʟᴏᴏᴅ ʜᴀs ʙᴇᴇɴ sᴇᴛ ᴛᴏ`{}`.".format(limit)


__help__ = """
ᴀɴᴛɪғʟᴏᴏᴅ ᴀʟʟᴏᴡs ʏᴏᴜ ᴛᴏ ᴛᴀᴋᴇ ᴀᴄᴛɪᴏɴ ᴏɴ ᴜsᴇʀs ᴛʜᴀᴛ sᴇɴᴅ ᴍᴏʀᴇ ᴛʜᴀɴ x ᴍᴇssᴀɢᴇs ɪɴ ᴀ ʀᴏᴡ. ᴇxᴄᴇᴇᴅɪɴɢ ᴛʜᴇ sᴇᴛ ғʟᴏᴏᴅ ᴡɪʟʟ ʀᴇsᴜʟᴛ ɪɴ ʀᴇsᴛʀɪᴄᴛɪɴɢ ᴛʜᴀᴛ ᴜsᴇʀ.
*ᴀᴅᴍɪɴ ᴏɴʟʏ*
•➥ /flood: ɢᴇᴛ ᴛʜᴇ ᴄᴜʀʀᴇɴᴛ ᴀɴᴛɪғʟᴏᴏᴅ sᴇᴛᴛɪɴɢs
•➥ /setflood <number/off/no>: sᴇᴛ ᴛʜᴇ ɴᴜᴍʙᴇʀ ᴏғ ᴍᴇssᴀɢᴇs ᴀғᴛᴇʀ ᴡʜɪᴄʜ ᴛᴏ ᴛᴀᴋᴇ ᴀᴄᴛɪᴏɴ ᴏɴ ᴀ ᴜsᴇʀ. sᴇᴛ ᴛᴏ '0', 'off', or 'no' ᴛᴏ ᴅɪsᴀʙʟᴇ.
•➥ /setfloodmode <ᴀᴄᴛɪᴏɴ ᴛʏᴘᴇ>: ᴄʜᴏᴏsᴇ ᴡʜɪᴄʜ ᴀᴄᴛɪᴏɴ ᴛᴏ ᴛᴀᴋᴇ ᴏɴ ᴀ ᴜsᴇʀ ᴡʜᴏ ʜᴀs ʙᴇᴇɴ ғʟᴏᴏᴅɪɴɢ. ᴏᴘᴛɪᴏɴs: ban/kick/mute/tban/tmute.
 """

__mod_name__ = "𝐀-ғʟᴏᴏᴅ"

FLOOD_BAN_HANDLER = MessageHandler(
    filters.ALL & ~filters.StatusUpdate.ALL & filters.ChatType.GROUPS,
    check_flood,
    block=False,
)
SET_FLOOD_HANDLER = CommandHandler(
    "setflood", set_flood, filters=filters.ChatType.GROUPS, block=False
)
SET_FLOOD_MODE_HANDLER = CommandHandler(
    "setfloodmode", set_flood_mode, block=False
)  # , filters=filters.ChatType.GROUPS)
FLOOD_QUERY_HANDLER = CallbackQueryHandler(
    flood_button, pattern=r"unmute_flooder", block=False
)
FLOOD_HANDLER = CommandHandler(
    "flood", flood, filters=filters.ChatType.GROUPS, block=False
)

application.add_handler(FLOOD_BAN_HANDLER, FLOOD_GROUP)
application.add_handler(FLOOD_QUERY_HANDLER)
application.add_handler(SET_FLOOD_HANDLER)
application.add_handler(SET_FLOOD_MODE_HANDLER)
application.add_handler(FLOOD_HANDLER)

__handlers__ = [
    (FLOOD_BAN_HANDLER, FLOOD_GROUP),
    SET_FLOOD_HANDLER,
    FLOOD_HANDLER,
    SET_FLOOD_MODE_HANDLER,
]
