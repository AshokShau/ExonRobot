import html

from alphabet_detector import AlphabetDetector
from telegram import (
    Chat,
    ChatMemberAdministrator,
    ChatPermissions,
    MessageEntity,
    Update,
)
from telegram.constants import ParseMode
from telegram.error import BadRequest, TelegramError
from telegram.ext import CommandHandler, ContextTypes, MessageHandler, filters
from telegram.helpers import mention_html

import Exon.modules.sql.locks_sql as sql
from Exon import DRAGONS, LOGGER, application
from Exon.modules.connection import connected
from Exon.modules.disable import DisableAbleCommandHandler
from Exon.modules.helper_funcs.alternate import send_message, typing_action
from Exon.modules.helper_funcs.chat_status import (
    check_admin,
    is_bot_admin,
    user_not_admin,
)
from Exon.modules.log_channel import loggable
from Exon.modules.sql.approve_sql import is_approved

ad = AlphabetDetector()

LOCK_TYPES = {
    "audio": filters.AUDIO,
    "voice": filters.VOICE,
    "document": filters.Document.ALL,
    "video": filters.VIDEO,
    "contact": filters.CONTACT,
    "photo": filters.PHOTO,
    "url": filters.Entity(MessageEntity.URL) | filters.CaptionEntity(MessageEntity.URL),
    "bots": filters.StatusUpdate.NEW_CHAT_MEMBERS,
    "forward": filters.FORWARDED,
    "game": filters.GAME,
    "location": filters.LOCATION,
    "egame": filters.Dice.ALL,
    "rtl": "rtl",
    "button": "button",
    "inline": "inline",
    "phone": filters.Entity(MessageEntity.PHONE_NUMBER)
    | filters.CaptionEntity(MessageEntity.PHONE_NUMBER),
    "command": filters.COMMAND,
    "email": filters.Entity(MessageEntity.EMAIL)
    | filters.CaptionEntity(MessageEntity.EMAIL),
    "anonchannel": "anonchannel",
    "forwardchannel": "forwardchannel",
    "forwardbot": "forwardbot",
    # "invitelink": ,
    "videonote": filters.VIDEO_NOTE,
    "emojicustom": filters.Entity(MessageEntity.CUSTOM_EMOJI)
    | filters.CaptionEntity(MessageEntity.CUSTOM_EMOJI),
    "stickerpremium": filters.Sticker.PREMIUM,
    "stickeranimated": filters.Sticker.ANIMATED,
}

LOCK_CHAT_RESTRICTION = {
    "all": {
        "can_send_messages": False,
        "can_send_media_messages": False,
        "can_send_polls": False,
        "can_send_other_messages": False,
        "can_add_web_page_previews": False,
        "can_change_info": False,
        "can_invite_users": False,
        "can_pin_messages": False,
        "can_manage_topics": False,
    },
    "messages": {"can_send_messages": False},
    "media": {"can_send_media_messages": False},
    "sticker": {"can_send_other_messages": False},
    "gif": {"can_send_other_messages": False},
    "poll": {"can_send_polls": False},
    "other": {"can_send_other_messages": False},
    "previews": {"can_add_web_page_previews": False},
    "info": {"can_change_info": False},
    "invite": {"can_invite_users": False},
    "pin": {"can_pin_messages": False},
    "topics": {"can_manage_topics": False},
}

UNLOCK_CHAT_RESTRICTION = {
    "all": {
        "can_send_messages": True,
        "can_send_media_messages": True,
        "can_send_polls": True,
        "can_send_other_messages": True,
        "can_add_web_page_previews": True,
        "can_invite_users": True,
        "can_manage_topics": True,
    },
    "messages": {"can_send_messages": True},
    "media": {"can_send_media_messages": True},
    "sticker": {"can_send_other_messages": True},
    "gif": {"can_send_other_messages": True},
    "poll": {"can_send_polls": True},
    "other": {"can_send_other_messages": True},
    "previews": {"can_add_web_page_previews": True},
    "info": {"can_change_info": True},
    "invite": {"can_invite_users": True},
    "pin": {"can_pin_messages": True},
    "topics": {"can_manage_topics": True},
}

PERM_GROUP = 1
REST_GROUP = 2


# NOT ASYNC
async def restr_members(
    bot,
    chat_id,
    members,
    messages=False,
    media=False,
    other=False,
    previews=False,
):
    for mem in members:
        if mem.user in DRAGONS:
            pass
        elif mem.user == 777000 or mem.user == 1087968824:
            pass
        try:
            await bot.restrict_chat_member(
                chat_id,
                mem.user,
                permissions=ChatPermissions(
                    can_send_messages=messages,
                    can_send_media_messages=media,
                    can_send_other_messages=other,
                    can_add_web_page_previews=previews,
                ),
            )
        except TelegramError:
            pass


async def unrestr_members(
    bot,
    chat_id,
    members,
    messages=True,
    media=True,
    other=True,
    previews=True,
):
    for mem in members:
        try:
            await bot.restrict_chat_member(
                chat_id,
                mem.user,
                permissions=ChatPermissions(
                    can_send_messages=messages,
                    can_send_media_messages=media,
                    can_send_other_messages=other,
                    can_add_web_page_previews=previews,
                ),
            )
        except TelegramError:
            pass


async def locktypes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.effective_message.reply_text(
        "\n • ".join(
            ["Locks available: "]
            + sorted(list(LOCK_TYPES) + list(LOCK_CHAT_RESTRICTION)),
        ),
    )


@check_admin(permission="can_delete_messages", is_both=True)
@loggable
@typing_action
async def lock(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    args = context.args
    chat = update.effective_chat
    user = update.effective_user

    if len(args) >= 1:
        ltype = args[0].lower()
        if ltype in LOCK_TYPES:
            # Connection check
            conn = await connected(context.bot, update, chat, user.id, need_admin=True)
            if conn:
                chat = await application.bot.getChat(conn)
                chat_id = conn
                chat_name = chat.title
                text = "ʟᴏᴄᴋᴇᴅ {} ғᴏʀ ɴᴏɴ-ᴀᴅᴍɪɴs ɪɴ {}!".format(ltype, chat_name)
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
                text = "ʟᴏᴄᴋᴇᴅ {} ғᴏʀ ɴᴏɴ-ᴀᴅᴍɪɴs!".format(ltype)
            sql.update_lock(chat.id, ltype, locked=True)
            await send_message(update.effective_message, text, parse_mode="markdown")

            return (
                "<b>{}:</b>"
                "\n#𝐋𝐎𝐂𝐊"
                "\n<b>ᴀᴅᴍɪɴ:</b> {}"
                "\nʟᴏᴄᴋᴇᴅ <code>{}</code>.".format(
                    html.escape(chat.title),
                    mention_html(user.id, user.first_name),
                    ltype,
                )
            )

        elif ltype in LOCK_CHAT_RESTRICTION:
            # Connection check
            conn = await connected(context.bot, update, chat, user.id, need_admin=True)
            if conn:
                chat = await application.bot.getChat(conn)
                chat_id = conn
                chat_name = chat.title
                text = "ʟᴏᴄᴋᴇᴅ {} ғᴏʀ ᴀʟʟ ɴᴏɴ-ᴀᴅᴍɪɴ ɪɴ {}!".format(
                    ltype,
                    chat_name,
                )
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
                text = "ʟᴏᴄᴋᴇᴅ {} ғᴏʀ ᴀʟʟ ɴᴏɴ-ᴀᴅᴍɪɴs!".format(ltype)

            chat_obj = await context.bot.getChat(chat_id)
            current_permission = chat_obj.permissions
            await context.bot.set_chat_permissions(
                chat_id=chat_id,
                permissions=get_permission_list(
                    current_permission.to_dict(),
                    LOCK_CHAT_RESTRICTION[ltype.lower()],
                ),
            )

            await context.bot.restrict_chat_member(
                chat.id,
                int(777000),
                permissions=ChatPermissions(
                    can_send_messages=True,
                    can_send_media_messages=True,
                    can_send_other_messages=True,
                    can_add_web_page_previews=True,
                ),
            )

            await context.bot.restrict_chat_member(
                chat.id,
                int(1087968824),
                permissions=ChatPermissions(
                    can_send_messages=True,
                    can_send_media_messages=True,
                    can_send_other_messages=True,
                    can_add_web_page_previews=True,
                ),
            )

            await send_message(update.effective_message, text, parse_mode="markdown")
            return (
                "<b>{}:</b>"
                "\n#𝐏𝐞𝐫𝐦𝐢𝐬𝐬𝐢𝐨𝐧_𝐋𝐎𝐂𝐊"
                "\n<b>ᴀᴅᴍɪɴ:</b> {}"
                "\nLocked <code>{}</code>.".format(
                    html.escape(chat.title),
                    mention_html(user.id, user.first_name),
                    ltype,
                )
            )

        else:
            await send_message(
                update.effective_message,
                "ᴡʜᴀᴛ ᴀʀᴇ ʏᴏᴜ ᴛʀʏɪɴɢ ᴛᴏ ʟᴏᴄᴋ...? ᴛʀʏ /locktypes ғᴏʀ ᴛʜᴇ ʟɪsᴛ ᴏғ ʟᴏᴄᴋᴀʙʟᴇs",
            )
    else:
        await send_message(update.effective_message, "ᴡʜᴀᴛ ᴀʀᴇ ʏᴏᴜ ᴛʀʏɪɴɢ ᴛᴏ ʟᴏᴄᴋ...?")

    return ""


@check_admin(permission="can_delete_messages", is_both=True)
@loggable
@typing_action
async def unlock(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    args = context.args
    chat = update.effective_chat
    user = update.effective_user
    update.effective_message

    if len(args) >= 1:
        ltype = args[0].lower()
        if ltype in LOCK_TYPES:
            # Connection check
            conn = await connected(context.bot, update, chat, user.id, need_admin=True)
            if conn:
                chat = await application.bot.getChat(conn)
                chat_id = conn
                chat_name = chat.title
                text = "ᴜɴʟᴏᴄᴋᴇᴅ {} ғᴏʀ ᴇᴠᴇʀʏᴏɴᴇ in {}!".format(ltype, chat_name)
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
                text = "ᴜɴʟᴏᴄᴋᴇᴅ {} ғᴏʀ ᴇᴠᴇʀʏᴏɴᴇ!".format(ltype)
            sql.update_lock(chat.id, ltype, locked=False)
            await send_message(update.effective_message, text, parse_mode="markdown")
            return (
                "<b>{}:</b>"
                "\n#𝐔𝐍𝐋𝐎𝐂𝐊"
                "\n<b>ᴀᴅᴍɪɴ:</b> {}"
                "\nᴜɴʟᴏᴄᴋᴇᴅ <code>{}</code>.".format(
                    html.escape(chat.title),
                    mention_html(user.id, user.first_name),
                    ltype,
                )
            )

        elif ltype in UNLOCK_CHAT_RESTRICTION:
            # Connection check
            conn = await connected(context.bot, update, chat, user.id, need_admin=True)
            if conn:
                chat = await application.bot.getChat(conn)
                chat_id = conn
                chat_name = chat.title
                text = "ᴜɴʟᴏᴄᴋᴇᴅ {} ғᴏʀ ᴇᴠᴇʀʏᴏɴᴇ ɪɴ {}!".format(ltype, chat_name)
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
                text = "ᴜɴʟᴏᴄᴋᴇᴅ {} ғᴏʀ ᴇᴠᴇʀʏᴏɴᴇ!".format(ltype)

            member = await chat.get_member(context.bot.id)

            if isinstance(member, ChatMemberAdministrator):
                can_change_info = member.can_change_info
            else:
                can_change_info = True

            if not can_change_info:
                await send_message(
                    update.effective_message,
                    "I ᴅᴏɴ'ᴛ ʜᴀᴠᴇ ᴘᴇʀᴍɪssɪᴏɴ ᴛᴏ ᴄʜᴀɴɢᴇ ɢʀᴏᴜᴘ ɪɴғᴏ.",
                    parse_mode="markdown",
                )
                return

            chat_obj = await context.bot.getChat(chat_id)
            current_permission = chat_obj.permissions
            await context.bot.set_chat_permissions(
                chat_id=chat_id,
                permissions=get_permission_list(
                    current_permission.to_dict(),
                    UNLOCK_CHAT_RESTRICTION[ltype.lower()],
                ),
            )

            await send_message(update.effective_message, text, parse_mode="markdown")

            return (
                "<b>{}:</b>"
                "\n#𝐔𝐍𝐋𝐎𝐂𝐊"
                "\n<b>ᴀᴅᴍɪɴ:</b> {}"
                "\nᴜɴʟᴏᴄᴋᴇᴅ <code>{}</code>.".format(
                    html.escape(chat.title),
                    mention_html(user.id, user.first_name),
                    ltype,
                )
            )
        else:
            await send_message(
                update.effective_message,
                "ᴡʜᴀᴛ ᴀʀᴇ ʏᴏᴜ ᴛʀʏɪɴɢ ᴛᴏ ᴜɴʟᴏᴄᴋ...? ᴛʀʏ /locktypes ғᴏʀ ᴛʜᴇ ʟɪsᴛ ᴏғ ʟᴏᴄᴋᴀʙʟᴇs.",
            )

    else:
        await send_message(
            update.effective_message, "ᴡʜᴀᴛ ᴀʀᴇ ʏᴏᴜ ᴛʀʏɪɴɢ ᴛᴏ ᴜɴʟᴏᴄᴋ...?"
        )


@user_not_admin
@check_admin(permission="can_delete_messages", is_bot=True, no_reply=True)
async def del_lockables(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat  # type: Optional[Chat]
    message = update.effective_message  # type: Optional[Message]
    user = update.effective_user
    if is_approved(chat.id, user.id):
        return
    for lockable, filter in LOCK_TYPES.items():
        if lockable == "rtl":
            if sql.is_locked(chat.id, lockable):
                if message.caption:
                    check = ad.detect_alphabet("{}".format(message.caption))
                    if "ARABIC" in check:
                        try:
                            await message.delete()
                        except BadRequest as excp:
                            if excp.message == "ᴍᴇssᴀɢᴇ ᴛᴏ ᴅᴇʟᴇᴛᴇ ɴᴏᴛ ғᴏᴜɴᴅ":
                                pass
                            else:
                                LOGGER.exception("ᴇʀʀᴏʀ ɪɴ ʟᴏᴄᴋᴀʙʟᴇs - rtl:caption")
                        break
                if message.text:
                    check = ad.detect_alphabet("{}".format(message.text))
                    if "ARABIC" in check:
                        try:
                            await message.delete()
                        except BadRequest as excp:
                            if excp.message == "ᴍᴇssᴀɢᴇ ᴛᴏ ᴅᴇʟᴇᴛᴇ ɴᴏᴛ ғᴏᴜɴᴅ":
                                pass
                            else:
                                LOGGER.exception("ᴇʀʀᴏʀ ɪɴ ʟᴏᴄᴋᴀʙʟᴇs - rtl:text")
                        break
            continue
        if lockable == "button":
            if sql.is_locked(chat.id, lockable):
                if message.reply_markup and message.reply_markup.inline_keyboard:
                    try:
                        await message.delete()
                    except BadRequest as excp:
                        if excp.message == "ᴍᴇssᴀɢᴇ ᴛᴏ ᴅᴇʟᴇᴛᴇ ɴᴏᴛ ғᴏᴜɴᴅ":
                            pass
                        else:
                            LOGGER.exception("ERROR ɪɴ ʟᴏᴄᴋᴀʙʟᴇs - ʙᴜᴛᴛᴏɴ")
                    break
            continue
        if lockable == "inline":
            if sql.is_locked(chat.id, lockable):
                if message and message.via_bot:
                    try:
                        await message.delete()
                    except BadRequest as excp:
                        if excp.message == "ᴍᴇssᴀɢᴇ ᴛᴏ ᴅᴇʟᴇᴛᴇ ɴᴏᴛ ғᴏᴜɴᴅ":
                            pass
                        else:
                            LOGGER.exception("ERROR in ʟᴏᴄᴋᴀʙʟᴇs - ɪɴʟɪɴᴇ")
                    break
            continue
        if lockable == "forwardchannel":
            if sql.is_locked(chat.id, lockable):
                if message.forward_from_chat:
                    if message.forward_from_chat.type == "channel":
                        try:
                            await message.delete()
                        except BadRequest as excp:
                            if excp.message == "ᴍᴇssᴀɢᴇ ᴛᴏ ᴅᴇʟᴇᴛᴇ ɴᴏᴛ ғᴏᴜɴᴅ":
                                pass
                            else:
                                LOGGER.exception("ERROR ɪɴ ʟᴏᴄᴋᴀʙʟᴇs - ғᴏʀᴡᴀʀᴅᴄʜᴀɴɴᴇʟ")
                        break
                continue
            continue
        if lockable == "forwardbot":
            if sql.is_locked(chat.id, lockable):
                if message.forward_from:
                    if message.forward_from.is_bot:
                        try:
                            await message.delete()
                        except BadRequest as excp:
                            if excp.message == "ᴍᴇssᴀɢᴇ ᴛᴏ ᴅᴇʟᴇᴛᴇ ɴᴏᴛ ғᴏᴜɴᴅ":
                                pass
                            else:
                                LOGGER.exception("ERROR ɪɴ ʟᴏᴄᴋᴀʙʟᴇs - ғᴏʀᴡᴀʀᴅᴄʜᴀɴɴᴇʟ")
                        break
                continue
            continue
        if lockable == "anonchannel":
            if sql.is_locked(chat.id, lockable):
                if message.from_user:
                    if message.from_user.id == 136817688:
                        try:
                            await message.delete()
                        except BadRequest as excp:
                            if excp.message == "ᴍᴇssᴀɢᴇ ᴛᴏ ᴅᴇʟᴇᴛᴇ ɴᴏᴛ ғᴏᴜɴᴅ":
                                pass
                            else:
                                LOGGER.exception("ᴇʀʀᴏʀ ɪɴ ʟᴏᴄᴋᴀʙʟᴇs - anonchannel")
                        break
                continue
            continue
        if filter.check_update(update) and sql.is_locked(chat.id, lockable):
            if lockable == "bots":
                new_members = update.effective_message.new_chat_members
                for new_mem in new_members:
                    if new_mem.is_bot:
                        if not await is_bot_admin(chat, context.bot.id):
                            await send_message(
                                update.effective_message,
                                "I sᴇᴇ ᴀ ʙᴏᴛ ᴀɴᴅ I'ᴠᴇ ʙᴇᴇɴ ᴛᴏʟᴅ ᴛᴏ sᴛᴏᴘ ᴛʜᴇᴍ ғʀᴏᴍ ᴊᴏɪɴɪɴɢ..."
                                "ʙᴜᴛ I'ᴍ ɴᴏᴛ ᴀᴅᴍɪɴ!",
                            )
                            return

                        await chat.ban_member(new_mem.id)
                        await send_message(
                            update.effective_message,
                            "ᴏɴʟʏ ᴀᴅᴍɪɴs ᴀʀᴇ ᴀʟʟᴏᴡᴇᴅ ᴛᴏ ᴀᴅᴅ ʙᴏᴛs ɪɴ ᴛʜɪs ᴄʜᴀᴛ! ɢᴇᴛ ᴏᴜᴛᴛᴀ ʜᴇʀᴇ.",
                        )
                        break
            else:
                try:
                    await message.delete()
                except BadRequest as excp:
                    if excp.message == "ᴍᴇssᴀɢᴇ ᴛᴏ ᴅᴇʟᴇᴛᴇ ɴᴏᴛ ғᴏᴜɴᴅ":
                        pass
                    else:
                        LOGGER.exception("ᴇʀʀᴏʀ ɪɴ ʟᴏᴄᴋᴀʙʟᴇs")

                break


async def build_lock_message(chat_id):
    locks = sql.get_locks(chat_id)
    res = ""
    locklist = []
    permslist = []
    if locks:
        res += "*" + "ᴛʜᴇsᴇ ᴀʀᴇ ᴛʜᴇ ᴄᴜʀʀᴇɴᴛ ʟᴏᴄᴋs ɪɴ ᴛʜɪs ᴄʜᴀᴛ:" + "*"
        if locks:
            locklist.append("sticker = `{}`".format(locks.sticker))
            locklist.append("audio = `{}`".format(locks.audio))
            locklist.append("voice = `{}`".format(locks.voice))
            locklist.append("document = `{}`".format(locks.document))
            locklist.append("video = `{}`".format(locks.video))
            locklist.append("contact = `{}`".format(locks.contact))
            locklist.append("photo = `{}`".format(locks.photo))
            locklist.append("gif = `{}`".format(locks.gif))
            locklist.append("url = `{}`".format(locks.url))
            locklist.append("bots = `{}`".format(locks.bots))
            locklist.append("forward = `{}`".format(locks.forward))
            locklist.append("game = `{}`".format(locks.game))
            locklist.append("location = `{}`".format(locks.location))
            locklist.append("rtl = `{}`".format(locks.rtl))
            locklist.append("button = `{}`".format(locks.button))
            locklist.append("egame = `{}`".format(locks.egame))
            locklist.append("phone = `{}`".format(locks.phone))
            locklist.append("command = `{}`".format(locks.command))
            locklist.append("email = `{}`".format(locks.email))
            locklist.append("anonchannel = `{}`".format(locks.anonchannel))
            locklist.append("forwardchannel = `{}`".format(locks.forwardchannel))
            locklist.append("forwardbot = `{}`".format(locks.forwardbot))
            locklist.append("videonote = `{}`".format(locks.videonote))
            locklist.append("emojicustom = `{}`".format(locks.emojicustom))
            locklist.append("stickerpremium = `{}`".format(locks.stickerpremium))
            locklist.append("stickeranimated = `{}`".format(locks.stickeranimated))

    permissions = await application.bot.get_chat(chat_id)
    if isinstance(permissions, Chat):
        permissions = permissions.permissions
        permslist.append("messages = `{}`".format(permissions.can_send_messages))
        permslist.append("media = `{}`".format(permissions.can_send_media_messages))
        permslist.append("poll = `{}`".format(permissions.can_send_polls))
        permslist.append("other = `{}`".format(permissions.can_send_other_messages))
        permslist.append(
            "previews = `{}`".format(permissions.can_add_web_page_previews)
        )
        permslist.append("info = `{}`".format(permissions.can_change_info))
        permslist.append("invite = `{}`".format(permissions.can_invite_users))
        permslist.append("pin = `{}`".format(permissions.can_pin_messages))
        permslist.append("topics = `{}`".format(permissions.can_manage_topics))

    if locklist:
        # Ordering lock list
        locklist.sort()
        # Building lock list string
        for x in locklist:
            res += "\n • {}".format(x)
    res += "\n\n*" + "ᴛʜᴇsᴇ ᴀʀᴇ ᴛʜᴇ ᴄᴜʀʀᴇɴᴛ ᴄʜᴀᴛ ᴘᴇʀᴍɪssɪᴏɴs:" + "*"
    for x in permslist:
        res += "\n • {}".format(x)
    return res


@typing_action
@check_admin(is_user=True)
async def list_locks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat  # type: Optional[Chat]
    user = update.effective_user

    # Connection check
    conn = await connected(context.bot, update, chat, user.id, need_admin=True)
    if conn:
        chat = await application.bot.getChat(conn)
        chat_name = chat.title
    else:
        if update.effective_message.chat.type == "private":
            await send_message(
                update.effective_message,
                "ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ ɪs ᴍᴇᴀɴᴛ ᴛᴏ ᴜsᴇ ɪɴ ɢʀᴏᴜᴘ ɴᴏᴛ ɪɴ PM",
            )
            return ""
        chat = update.effective_chat
        chat_name = update.effective_message.chat.title

    res = await build_lock_message(chat.id)
    if conn:
        res = res.replace("ʟᴏᴄᴋs ɪɴ", "*{}*".format(chat_name))

    await send_message(update.effective_message, res, parse_mode=ParseMode.MARKDOWN)


def get_permission_list(current, new):
    permissions = {
        "can_send_messages": None,
        "can_send_media_messages": None,
        "can_send_polls": None,
        "can_send_other_messages": None,
        "can_add_web_page_previews": None,
        "can_change_info": None,
        "can_invite_users": None,
        "can_pin_messages": None,
        "can_manage_topics": None,
    }
    permissions.update(current)
    permissions.update(new)
    new_permissions = ChatPermissions(**permissions)
    return new_permissions


async def __import_data__(chat_id, data, message):
    # set chat locks
    locks = data.get("locks", {})
    for itemlock in locks:
        if itemlock in LOCK_TYPES:
            sql.update_lock(chat_id, itemlock, locked=True)
        elif itemlock in LOCK_CHAT_RESTRICTION:
            sql.update_restriction(chat_id, itemlock, locked=True)
        else:
            pass


def __migrate__(old_chat_id, new_chat_id):
    sql.migrate_chat(old_chat_id, new_chat_id)


async def __chat_settings__(chat_id, user_id):
    return await build_lock_message(chat_id)


__help__ = """
ᴅᴏ sᴛɪᴄᴋᴇʀs ᴀɴɴᴏʏ ʏᴏᴜ? ᴏʀ ᴡᴀɴᴛ ᴛᴏ ᴀᴠᴏɪᴅ ᴘᴇᴏᴘʟᴇ sʜᴀʀɪɴɢ ʟɪɴᴋs? ᴏʀ ᴘɪᴄᴛᴜʀᴇs? \
ʏᴏᴜ'ʀᴇ ɪɴ ᴛʜᴇ ʀɪɢʜᴛ ᴘʟᴀᴄᴇ!
ᴛʜᴇ ʟᴏᴄᴋs ᴍᴏᴅᴜʟᴇ ᴀʟʟᴏᴡs ʏᴏᴜ ᴛᴏ ʟᴏᴄᴋ ᴀᴡᴀʏ sᴏᴍᴇ ᴄᴏᴍᴍᴏɴ ɪᴛᴇᴍs ɪɴ the \
ᴛᴇʟᴇɢʀᴀᴍ ᴡᴏʀʟᴅ; ᴏᴜʀ ʙᴏᴛ ᴡɪʟʟ ᴀᴜᴛᴏᴍᴀᴛɪᴄᴀʟʟʏ delete them!

• /locktypes*:* ʟɪsᴛs ᴀʟʟ ᴘᴏssɪʙʟᴇ ʟᴏᴄᴋᴛʏᴘᴇs

*ᴀᴅᴍɪɴs ᴏɴʟʏ:*
• /lock <ᴛʏᴘᴇ>*:* ʟᴏᴄᴋ ɪᴛᴇᴍs ᴏғ ᴀ ᴄᴇʀᴛᴀɪɴ ᴛʏᴘᴇ (ɴᴏᴛ ᴀᴠᴀɪʟᴀʙʟᴇ ɪɴ ᴘʀɪᴠᴀᴛᴇ)
• /unlock <ᴛʏᴘᴇ>*:* ᴜɴʟᴏᴄᴋ ɪᴛᴇᴍs ᴏғ ᴀ ᴄᴇʀᴛᴀɪɴ ᴛʏᴘᴇ (ɴᴏᴛ ᴀᴠᴀɪʟᴀʙʟᴇ ɪɴ ᴘʀɪᴠᴀᴛᴇ)
• /locks*:* ᴛʜᴇ ᴄᴜʀʀᴇɴᴛ ʟɪsᴛ ᴏғ ʟᴏᴄᴋs ɪɴ ᴛʜɪs ᴄʜᴀᴛ.

ʟᴏᴄᴋs ᴄᴀɴ ʙᴇ ᴜsᴇᴅ ᴛᴏ ʀᴇsᴛʀɪᴄᴛ ᴀ ɢʀᴏᴜᴘ ᴜsᴇʀs.
ᴇɢ:
ʟᴏᴄᴋɪɴɢ ᴜʀʟs ᴡɪʟʟ ᴀᴜᴛᴏ-ᴅᴇʟᴇᴛᴇ ᴀʟʟ ᴍᴇssᴀɢᴇs ᴡɪᴛʜ ᴜʀʟs, ʟᴏᴄᴋɪɴɢ sᴛɪᴄᴋᴇʀs ᴡɪʟʟ ʀᴇsᴛʀɪᴄᴛ ᴀʟʟ \
*ɴᴏɴ-ᴀᴅᴍɪɴ* ᴜsᴇʀs ғʀᴏᴍ sᴇɴᴅɪɴɢ sᴛɪᴄᴋᴇʀs, ᴇᴛᴄ.
ʟᴏᴄᴋɪɴɢ ʙᴏᴛs ᴡɪʟʟ sᴛᴏᴘ ɴᴏɴ-ᴀᴅᴍɪɴs ғʀᴏᴍ ᴀᴅᴅɪɴɢ ʙᴏᴛs ᴛᴏ ᴛʜᴇ ᴄʜᴀᴛ.
ʟᴏᴄᴋɪɴɢ ᴀɴᴏɴᴄʜᴀɴɴᴇʟ ᴡɪʟʟ sᴛᴏᴘ ᴀɴᴏɴʏᴍᴏᴜs ᴄʜᴀɴɴᴇʟ ғʀᴏᴍ ᴍᴇssᴀɢɪɴɢ ɪɴ ʏᴏᴜʀ ɢʀᴏᴜᴘ.

*ɴᴏᴛᴇ:*
• ᴜɴʟᴏᴄᴋɪɴɢ ᴘᴇʀᴍɪssɪᴏɴ *ɪɴғᴏ* ᴡɪʟʟ ᴀʟʟᴏᴡ ᴍᴇᴍʙᴇʀs (ɴᴏɴ-ᴀᴅᴍɪɴs) ᴛᴏ ᴄʜᴀɴɢᴇ ᴛʜᴇ ɢʀᴏᴜᴘ ɪɴғᴏʀᴍᴀᴛɪᴏɴ, sᴜᴄʜ ᴀs ᴛʜᴇ ᴅᴇsᴄʀɪᴘᴛɪᴏɴ ᴏʀ ᴛʜᴇ ɢʀᴏᴜᴘ ɴᴀᴍᴇ
• ᴜɴʟᴏᴄᴋɪɴɢ ᴘᴇʀᴍɪssɪᴏɴ *ᴘɪɴ* ᴡɪʟʟ ᴀʟʟᴏᴡ ᴍᴇᴍʙᴇʀs (ɴᴏɴ-ᴀᴅᴍɪɴs) ᴛᴏ ᴘɪɴ ᴀ ᴍᴇssᴀɢᴇ ɪɴ ᴀ ɢʀᴏᴜᴘ
"""

__mod_name__ = "𝐋ᴏᴄᴋs"

LOCKTYPES_HANDLER = DisableAbleCommandHandler("locktypes", locktypes, block=False)
LOCK_HANDLER = CommandHandler(
    "lock", lock, block=False
)  # , filters=filters.ChatType.GROUPS)
UNLOCK_HANDLER = CommandHandler(
    "unlock", unlock, block=False
)  # , filters=filters.ChatType.GROUPS)
LOCKED_HANDLER = CommandHandler(
    "locks", list_locks, block=False
)  # , filters=filters.ChatType.GROUPS)

application.add_handler(LOCK_HANDLER)
application.add_handler(UNLOCK_HANDLER)
application.add_handler(LOCKTYPES_HANDLER)
application.add_handler(LOCKED_HANDLER)

application.add_handler(
    MessageHandler(filters.ALL & filters.ChatType.GROUPS, del_lockables, block=False),
    PERM_GROUP,
)
