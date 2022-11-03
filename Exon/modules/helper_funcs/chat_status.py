"""
MIT License

Copyright (c) 2022 Aʙɪsʜɴᴏɪ

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from functools import wraps
from threading import RLock
from time import perf_counter

from cachetools import TTLCache
from telegram import Chat, ChatMember, ParseMode, Update
from telegram.ext import CallbackContext

from Exon import (
    DEL_CMDS,
    DEMONS,
    DEV_USERS,
    DRAGONS,
    SUPPORT_CHAT,
    TIGERS,
    WOLVES,
    dispatcher,
)

# stores admemes in memory for 10 min.
ADMIN_CACHE = TTLCache(maxsize=512, ttl=60 * 10, timer=perf_counter)
THREAD_LOCK = RLock()


def is_whitelist_plus(chat: Chat, user_id: int, member: ChatMember = None) -> bool:
    return any(user_id in user for user in [WOLVES, TIGERS, DEMONS, DRAGONS, DEV_USERS])


def is_support_plus(chat: Chat, user_id: int, member: ChatMember = None) -> bool:
    return user_id in DEMONS or user_id in DRAGONS or user_id in DEV_USERS


def is_sudo_plus(chat: Chat, user_id: int, member: ChatMember = None) -> bool:
    return user_id in DRAGONS or user_id in DEV_USERS


def is_stats_plus(chat: Chat, user_id: int, member: ChatMember = None) -> bool:
    return user_id in DEV_USERS


def is_user_admin(chat: Chat, user_id: int, member: ChatMember = None) -> bool:
    if (
        chat.type == "private"
        or user_id in DRAGONS
        or user_id in DEV_USERS
        or chat.all_members_are_administrators
        or user_id in {1452219013}
    ):  # Count telegram and Group Anonymous as admin
        return True
    if member:
        return member.status in ("administrator", "creator")

    with THREAD_LOCK:
        # try to fetch from cache first.
        try:
            return user_id in ADMIN_CACHE[chat.id]
        except KeyError:
            # keyerror happend means cache is deleted,
            # so query bot api again and return user status
            # while saving it in cache for future useage...
            chat_admins = dispatcher.bot.getChatAdministrators(chat.id)
            admin_list = [x.user.id for x in chat_admins]
            ADMIN_CACHE[chat.id] = admin_list

            return user_id in admin_list


def is_bot_admin(chat: Chat, bot_id: int, bot_member: ChatMember = None) -> bool:
    if chat.type == "private" or chat.all_members_are_administrators:
        return True

    if not bot_member:
        bot_member = chat.get_member(bot_id)

    return bot_member.status in ("administrator", "creator")


def can_delete(chat: Chat, bot_id: int) -> bool:
    return chat.get_member(bot_id).can_delete_messages


def is_user_ban_protected(chat: Chat, user_id: int, member: ChatMember = None) -> bool:
    if (
        chat.type == "private"
        or user_id in DRAGONS
        or user_id in DEV_USERS
        or user_id in WOLVES
        or user_id in TIGERS
    ):  # Count telegram and Group Anonymous as admin
        return True

    if not member:
        member = chat.get_member(user_id)

    return member.status in ("administrator", "creator")


def is_user_in_chat(chat: Chat, user_id: int) -> bool:
    member = chat.get_member(user_id)
    return member.status not in ("left", "kicked")


def dev_plus(func):
    @wraps(func)
    def is_dev_plus_func(update: Update, context: CallbackContext, *args, **kwargs):
        context.bot
        user = update.effective_user

        if user.id in DEV_USERS:
            return func(update, context, *args, **kwargs)
        if not user:
            pass
        elif DEL_CMDS and " " not in update.effective_message.text:
            try:
                update.effective_message.delete()
            except:
                pass
        else:
            update.effective_message.reply_text(
                "ᴛʜɪs ɪs ᴀ ᴅᴇᴠᴇʟᴏᴘᴇʀ ʀᴇsᴛʀɪᴄᴛᴇᴅ ᴄᴏᴍᴍᴀɴᴅ."
                "ʏᴏᴜ ᴅᴏ ɴᴏᴛ ʜᴀᴠᴇ ᴘᴇʀᴍɪssɪᴏɴs ᴛᴏ ʀᴜɴ ᴛʜɪs.",
            )

    return is_dev_plus_func


def sudo_plus(func):
    @wraps(func)
    def is_sudo_plus_func(update: Update, context: CallbackContext, *args, **kwargs):
        context.bot
        user = update.effective_user
        chat = update.effective_chat

        if user and is_sudo_plus(chat, user.id):
            return func(update, context, *args, **kwargs)
        if not user:
            pass
        elif DEL_CMDS and " " not in update.effective_message.text:
            try:
                update.effective_message.delete()
            except:
                pass
        else:
            update.effective_message.reply_text(
                "ᴀᴛ ʟᴇᴀsᴛ ʙᴇ ᴀɴ ᴀᴅᴍɪɴ ᴛᴏ ᴜsᴇ ᴛʜᴇsᴇ ᴀʟʟ ᴄᴏᴍᴍᴀɴᴅs",
            )

    return is_sudo_plus_func


def stats_plus(func):
    @wraps(func)
    def is_stats_plus_func(update: Update, context: CallbackContext, *args, **kwargs):
        context.bot
        user = update.effective_user
        chat = update.effective_chat

        if user and is_stats_plus(chat, user.id):
            return func(update, context, *args, **kwargs)
        if not user:
            pass
        elif DEL_CMDS and " " not in update.effective_message.text:
            try:
                update.effective_message.delete()
            except:
                pass
        else:
            update.effective_message.reply_text(
                "Exon sᴛᴀᴛs ɪs ᴊᴜsᴛ ғᴏʀ ᴅᴇᴠ ᴜsᴇʀ",
            )

    return is_stats_plus_func


def support_plus(func):
    @wraps(func)
    def is_support_plus_func(update: Update, context: CallbackContext, *args, **kwargs):
        context.bot
        user = update.effective_user
        chat = update.effective_chat

        if user and is_support_plus(chat, user.id):
            return func(update, context, *args, **kwargs)
        if DEL_CMDS and " " not in update.effective_message.text:
            try:
                update.effective_message.delete()
            except:
                pass

    return is_support_plus_func


def whitelist_plus(func):
    @wraps(func)
    def is_whitelist_plus_func(
        update: Update,
        context: CallbackContext,
        *args,
        **kwargs,
    ):
        context.bot
        user = update.effective_user
        chat = update.effective_chat

        if user and is_whitelist_plus(chat, user.id):
            return func(update, context, *args, **kwargs)
        update.effective_message.reply_text(
            f"ʏᴏᴜ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ ᴀᴄᴄᴇss ᴛᴏ ᴜsᴇ ᴛʜɪs.\nᴠɪsɪᴛ @{SUPPORT_CHAT}",
        )

    return is_whitelist_plus_func


def user_admin(func):
    @wraps(func)
    def is_admin(update: Update, context: CallbackContext, *args, **kwargs):
        context.bot
        user = update.effective_user
        chat = update.effective_chat

        if user and is_user_admin(chat, user.id):
            return func(update, context, *args, **kwargs)
        if not user:
            pass
        elif DEL_CMDS and " " not in update.effective_message.text:
            try:
                update.effective_message.delete()
            except:
                pass
        else:
            update.effective_message.reply_text(
                "ᴀᴛ ʟᴇᴀsᴛ ʙᴇ ᴀɴ ᴀᴅᴍɪɴ ᴛᴏ ᴜsᴇ ᴛʜᴇsᴇ ᴀʟʟ ᴄᴏᴍᴍᴀɴᴅs",
            )

    return is_admin


def user_admin_no_reply(func):
    @wraps(func)
    def is_not_admin_no_reply(
        update: Update,
        context: CallbackContext,
        *args,
        **kwargs,
    ):
        context.bot
        user = update.effective_user
        chat = update.effective_chat

        if user and is_user_admin(chat, user.id):
            return func(update, context, *args, **kwargs)
        if not user:
            pass
        elif DEL_CMDS and " " not in update.effective_message.text:
            try:
                update.effective_message.delete()
            except:
                pass

    return is_not_admin_no_reply


def user_not_admin(func):
    @wraps(func)
    def is_not_admin(update: Update, context: CallbackContext, *args, **kwargs):
        message = update.effective_message
        user = update.effective_user
        # chat = update.effective_chat

        if message.is_automatic_forward:
            return
        if message.sender_chat and message.sender_chat.type != "channel":
            return
        elif user and not is_user_admin(update.message.chat, user.id):
            return func(update, context, *args, **kwargs)

        elif not user:
            pass

    return is_not_admin


def bot_admin(func):
    @wraps(func)
    def is_admin(update: Update, context: CallbackContext, *args, **kwargs):
        bot = context.bot
        chat = update.effective_chat
        update_chat_title = chat.title
        message_chat_title = update.effective_message.chat.title

        if update_chat_title == message_chat_title:
            not_admin = "I'ᴍ ɴᴏᴛ ᴀᴅᴍɪɴ!"
        else:
            not_admin = f"I'ᴍ ɴᴏᴛ ᴀᴅᴍɪɴ ɪɴ <b>{update_chat_title}</b>! "

        if is_bot_admin(chat, bot.id):
            return func(update, context, *args, **kwargs)
        update.effective_message.reply_text(not_admin, parse_mode=ParseMode.HTML)

    return is_admin


def bot_can_delete(func):
    @wraps(func)
    def delete_rights(update: Update, context: CallbackContext, *args, **kwargs):
        bot = context.bot
        chat = update.effective_chat
        update_chat_title = chat.title
        message_chat_title = update.effective_message.chat.title

        if update_chat_title == message_chat_title:
            cant_delete = "I ᴄᴀɴ'ᴛ ᴅᴇʟᴇᴛᴇ ᴍᴇssᴀɢᴇs ʜᴇʀᴇ!\nMake sᴜʀᴇ I'ᴍ ᴀᴅᴍɪɴ ᴀɴᴅ ᴄᴀɴ ᴅᴇʟᴇᴛᴇ ᴏᴛʜᴇʀ ᴜsᴇᴅ's ᴍᴇssᴀɢᴇs."
        else:
            cant_delete = f"I ᴄᴀɴ'ᴛ ᴅᴇʟᴇᴛᴇ ᴍᴇssᴀɢᴇs ɪɴ <b>{update_chat_title}</b>!\nᴍᴀᴋᴇ sᴜʀᴇ I'm ᴀᴅᴍɪɴ ᴀɴᴅ ᴄᴀɴ ᴅᴇʟᴇᴛᴇ ᴏᴛʜᴇʀ ᴜsᴇᴅ ᴍᴇssᴀɢᴇs ᴛʜᴇʀᴇ."

        if can_delete(chat, bot.id):
            return func(update, context, *args, **kwargs)
        update.effective_message.reply_text(cant_delete, parse_mode=ParseMode.HTML)

    return delete_rights


def can_pin(func):
    @wraps(func)
    def pin_rights(update: Update, context: CallbackContext, *args, **kwargs):
        bot = context.bot
        chat = update.effective_chat
        update_chat_title = chat.title
        message_chat_title = update.effective_message.chat.title

        if update_chat_title == message_chat_title:
            cant_pin = (
                "I ᴄᴀɴ'ᴛ ᴘɪɴ ᴍᴇssᴀɢᴇs ʜᴇʀᴇ!\nMake sᴜʀᴇ I'ᴍ ᴀᴅᴍɪɴ ᴀɴᴅ ᴄᴀɴ ᴘɪɴ ᴍᴇssᴀɢᴇs."
            )
        else:
            cant_pin = f"I ᴄᴀɴ'ᴛ ᴘɪɴ ᴍᴇssᴀɢᴇs in <b>{update_chat_title}</b>!\nᴍᴀᴋᴇ sure I'ᴍ ᴀᴅᴍɪɴ ᴀɴᴅ ᴄᴀɴ ᴘɪɴ ᴍᴇssᴀɢᴇs ᴛʜᴇʀᴇ."

        if chat.get_member(bot.id).can_pin_messages:
            return func(update, context, *args, **kwargs)
        update.effective_message.reply_text(cant_pin, parse_mode=ParseMode.HTML)

    return pin_rights


def can_promote(func):
    @wraps(func)
    def promote_rights(update: Update, context: CallbackContext, *args, **kwargs):
        bot = context.bot
        chat = update.effective_chat
        update_chat_title = chat.title
        message_chat_title = update.effective_message.chat.title

        if update_chat_title == message_chat_title:
            cant_promote = "I can't ᴘʀᴏᴍᴏᴛᴇ/ᴅᴇᴍᴏᴛᴇ ᴘᴇᴏᴘʟᴇ ʜᴇʀᴇ!\nMake sᴜʀᴇ I'ᴍ ᴀᴅᴍɪɴ and can appoint new admins."
        else:
            cant_promote = (
                f"I ᴄᴀɴ'ᴛ ᴘʀᴏᴍᴏᴛᴇ/ᴅᴇᴍᴏᴛᴇ ᴘᴇᴏᴘʟᴇ ɪɴ <b>{update_chat_title}</b>!\n"
                f"ᴍᴀᴋᴇ sᴜʀᴇ I'ᴍ ᴀᴅᴍɪɴ ᴛʜᴇʀᴇ ᴀɴᴅ ʜᴀᴠᴇ ᴛʜᴇ ᴘᴇʀᴍɪssɪᴏɴ ᴛᴏ ᴀᴘᴘᴏɪɴᴛ ɴᴇᴡ ᴀᴅᴍɪɴs."
            )

        if chat.get_member(bot.id).can_promote_members:
            return func(update, context, *args, **kwargs)
        update.effective_message.reply_text(cant_promote, parse_mode=ParseMode.HTML)

    return promote_rights


def can_restrict(func):
    @wraps(func)
    def restrict_rights(update: Update, context: CallbackContext, *args, **kwargs):
        bot = context.bot
        chat = update.effective_chat
        update_chat_title = chat.title
        message_chat_title = update.effective_message.chat.title

        if update_chat_title == message_chat_title:
            cant_restrict = "I ᴄᴀɴ'ᴛ ʀᴇsᴛʀɪᴄᴛ ᴘᴇᴏᴘʟᴇ ʜᴇʀᴇ!\nᴍᴀᴋᴇ sᴜʀᴇ I'ᴍ ᴀᴅᴍɪɴ ᴀɴᴅ ᴄᴀɴ ʀᴇsᴛʀɪᴄᴛ ᴜsᴇʀs."
        else:
            cant_restrict = f"ɪ ᴄᴀɴ'ᴛ ʀᴇsᴛʀɪᴄᴛ ᴘᴇᴏᴘʟᴇ ɪɴ <b>{update_chat_title}</b>!\nᴍᴀᴋᴇ sᴜʀᴇ ɪ'ᴍ ᴀᴅᴍɪɴ ᴛʜᴇʀᴇ ᴀɴᴅ ᴄᴀɴ ʀᴇsᴛʀɪᴄᴛ ᴜsᴇʀs."

        if chat.get_member(bot.id).can_restrict_members:
            return func(update, context, *args, **kwargs)
        update.effective_message.reply_text(
            cant_restrict,
            parse_mode=ParseMode.HTML,
        )

    return restrict_rights


def user_can_promote(func):
    @wraps(func)
    def user_is_promoter(update: Update, context: CallbackContext, *args, **kwargs):
        context.bot
        user = update.effective_user
        if not user:
            return
        user = user.id
        member = update.effective_chat.get_member(user)
        no_rights = "ʏᴏᴜ ᴅᴏ ɴᴏᴛ ʜᴀᴠᴇ 'ᴀᴅᴅ ᴀᴅᴍɪɴ ʀɪɢʜᴛs."
        if (
            not (member.can_promote_members or member.status == "creator")
            and user not in DRAGONS
            and user not in [1452219013]
        ):
            if not update.callback_query:
                update.effective_message.reply_text(no_rights)
            else:
                update.callback_query.answer(no_rights, show_alert=True)
            return ""
        return func(update, context, *args, **kwargs)

    return user_is_promoter


def user_can_ban(func):
    @wraps(func)
    def user_is_banhammer(update: Update, context: CallbackContext, *args, **kwargs):
        context.bot
        user = update.effective_user.id
        member = update.effective_chat.get_member(user)
        if (
            not member.can_restrict_members
            and member.status != "creator"
            and user not in DRAGONS
            and user not in [1452219013]
        ):
            update.effective_message.reply_text(
                "sᴏʀʀʏ sᴏɴ, ʙᴜᴛ ʏᴏᴜ'ʀᴇ ɴᴏᴛ ᴡᴏʀᴛʜʏ ᴛᴏ ᴡɪᴇʟᴅ ᴛʜᴇ ʙᴀɴʜᴀᴍᴍᴇʀ.",
            )
            return ""
        return func(update, context, *args, **kwargs)

    return user_is_banhammer


def connection_status(func):
    @wraps(func)
    def connected_status(update: Update, context: CallbackContext, *args, **kwargs):
        conn = connected(
            context.bot,
            update,
            update.effective_chat,
            update.effective_user.id,
            need_admin=False,
        )

        if conn:
            chat = dispatcher.bot.getChat(conn)
            update.__setattr__("_effective_chat", chat)
        elif update.effective_message.chat.type == "private":
            update.effective_message.reply_text(
                "sᴇɴᴅ /connect ɪɴ ᴀ ɢʀᴏᴜᴘ ᴛʜᴀᴛ ʏᴏᴜ ᴀɴᴅ I ʜᴀᴠᴇ ɪɴ ᴄᴏᴍᴍᴏɴ ғɪʀsᴛ.",
            )
            return connected_status

        return func(update, context, *args, **kwargs)

    return connected_status


# Workaround for circular import with connection.py
from Exon.modules import connection

connected = connection.connected
