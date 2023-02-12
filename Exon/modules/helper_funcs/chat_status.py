"""
MIT License

Copyright (c) 2022 ABISHNOI69 

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
from pyrogram import filters
from telegram import Chat, ChatMember, ParseMode, TelegramError, Update, User
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


def user_can_changeinfo(chat: Chat, user: User, bot_id: int) -> bool:
    return chat.get_member(user.id).can_change_info


def user_can_promote(chat: Chat, user: User, bot_id: int) -> bool:
    return chat.get_member(user.id).can_promote_members


def user_can_pin(chat: Chat, user: User, bot_id: int) -> bool:
    return chat.get_member(user.id).can_pin_messages


def is_user_admin(update: Update, user_id: int, member: ChatMember = None) -> bool:
    chat = update.effective_chat
    msg = update.effective_message
    if (
        chat.type == "private"
        or user_id in DEMONS
        or user_id in DEV_USERS
        or chat.all_members_are_administrators
        or (
            msg.reply_to_message
            and msg.reply_to_message.sender_chat is not None
            and msg.reply_to_message.sender_chat.type != "channel"
        )
    ):
        return True

    if not member:
        # try to fetch from cache first.
        try:
            return user_id in ADMIN_CACHE[chat.id]
        except KeyError:
            # KeyError happened means cache is deleted,
            # so query bot api again and return user status
            # while saving it in cache for future usage...
            chat_admins = dispatcher.bot.getChatAdministrators(chat.id)
            admin_list = [x.user.id for x in chat_admins]
            ADMIN_CACHE[chat.id] = admin_list

            if user_id in admin_list:
                return True
            return False


def is_user_mod(update: Update, user_id: int, member: ChatMember = None) -> bool:
    chat = update.effective_chat
    msg = update.effective_message
    if (
        chat.type == "private"
        or user_id in MOD_USERS
        or user_id in DEMONS
        or user_id in DEV_USERS
        or chat.all_members_are_administrators
        or (msg.sender_chat is not None and msg.sender_chat.type != "channel")
    ):  # Count telegram and Group Anonymous as admin
        return True

    if not member:
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

            if user_id in admin_list:
                return True
            return False


def is_bot_admin(chat: Chat, bot_id: int, bot_member: ChatMember = None) -> bool:
    if chat.type == "private" or chat.all_members_are_administrators:
        return True

    if not bot_member:
        bot_member = chat.get_member(bot_id)

    return bot_member.status in ("administrator", "creator")


def can_delete(chat: Chat, bot_id: int) -> bool:
    return chat.get_member(bot_id).can_delete_messages


def is_user_ban_protected(
    update: Update, user_id: int, member: ChatMember = None
) -> bool:
    chat = update.effective_chat
    msg = update.effective_message
    if (
        chat.type == "private"
        or user_id in DEMONS
        or user_id in DEV_USERS
        or user_id in DRAGONS
        or user_id in TIGERS
        or chat.all_members_are_administrators
        or (
            msg.reply_to_message
            and msg.reply_to_message.sender_chat is not None
            and msg.reply_to_message.sender_chat.type != "channel"
        )
    ):
        return True

    if not member:
        member = chat.get_member(user_id)

    return member.status in ("administrator", "creator")


def is_user_ban_protectedd(chat: Chat, user_id: int, member: ChatMember = None) -> bool:
    if (
        chat.type == "private"
        or user_id in DRAGONS
        or user_id in DEV_USERS
        or user_id in WOLVES
        or user_id in TIGERS
        or chat.all_members_are_administrators
        or user_id in {777000, 1087968824}
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
                "This is a developer restricted command."
                " You do not have permissions to run this."
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
                "Who dis non-admin telling me what to do?"
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
                "Yuzuki stats is just for Dev User",
            )

    return is_sudo_plus_func


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
        update: Update, context: CallbackContext, *args, **kwargs
    ):
        context.bot
        user = update.effective_user
        chat = update.effective_chat

        if user and is_whitelist_plus(chat, user.id):
            return func(update, context, *args, **kwargs)
        update.effective_message.reply_text(
            f"You don't have access to use this.\nVisit @{SUPPORT_CHAT}"
        )

    return is_whitelist_plus_func


def user_admin(func):
    @wraps(func)
    def is_admin(update: Update, context: CallbackContext, *args, **kwargs):
        context.bot
        user = update.effective_user
        update.effective_chat

        if user and is_user_admin(update, user.id):
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
                "Who dis non-admin telling me what to do?"
            )

    return is_admin


def user_admin_no_reply(func):
    @wraps(func)
    def is_not_admin_no_reply(
        update: Update, context: CallbackContext, *args, **kwargs
    ):
        context.bot
        user = update.effective_user
        update.effective_chat

        if user and is_user_admin(update, user.id):
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
        context.bot
        user = update.effective_user
        update.effective_chat

        if user and not is_user_admin(update, user.id):
            return func(update, context, *args, **kwargs)
        if not user:
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
            not_admin = "I'm not admin! - REEEEEE"
        else:
            not_admin = f"I'm not admin in <b>{update_chat_title}</b>! - REEEEEE"

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
            cant_delete = "I can't delete messages here!\nMake sure I'm admin and can delete other user's messages."
        else:
            cant_delete = f"I can't delete messages in <b>{update_chat_title}</b>!\nMake sure I'm admin and can delete other user's messages there."

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
                "I can't pin messages here!\nMake sure I'm admin and can pin messages."
            )
        else:
            cant_pin = f"I can't pin messages in <b>{update_chat_title}</b>!\nMake sure I'm admin and can pin messages there."

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
            cant_promote = "I can't promote/demote people here!\nMake sure I'm admin and can appoint new admins."
        else:
            cant_promote = (
                f"I can't promote/demote people in <b>{update_chat_title}</b>!\n"
                f"Make sure I'm admin there and can appoint new admins."
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
            cant_restrict = "I can't restrict people here!\nMake sure I'm admin and can restrict users."
        else:
            cant_restrict = f"I can't restrict people in <b>{update_chat_title}</b>!\nMake sure I'm admin there and can restrict users."

        if chat.get_member(bot.id).can_restrict_members:
            return func(update, context, *args, **kwargs)
        update.effective_message.reply_text(cant_restrict, parse_mode=ParseMode.HTML)

    return restrict_rights


def user_can_ban(func):
    @wraps(func)
    def user_is_banhammer(update: Update, context: CallbackContext, *args, **kwargs):
        context.bot
        user = update.effective_user.id
        member = update.effective_chat.get_member(user)

        if (
            not (member.can_restrict_members or member.status == "creator")
            and not user in DEV_USERS
        ):
            update.effective_message.reply_text(
                "Sorry son, but you're not worthy to wield the banhammer."
            )
            return ""

        return func(update, context, *args, **kwargs)

    return user_is_banhammer


def callbacks_in_filters(data):
    return filters.create(lambda flt, _, query: flt.data in query.data, data=data)


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
            return func(update, context, *args, **kwargs)
        if update.effective_message.chat.type == "private":
            update.effective_message.reply_text(
                "Send /connect in a group that you and I have in common first."
            )
            return connected_status

        return func(update, context, *args, **kwargs)

    return connected_status


def user_admin_no_reply(func):
    @wraps(func)
    def is_not_admin_no_reply(
        update: Update, context: CallbackContext, *args, **kwargs
    ):
        # bot = context.bot
        user = update.effective_user
        # chat = update.effective_chat
        query = update.callback_query

        if user:
            if is_user_admin(update, user.id):
                return func(update, context, *args, **kwargs)
            else:
                query.answer("this is not for you")
        elif not user:
            query.answer("this is not for you")
        elif DEL_CMDS and " " not in update.effective_message.text:
            try:
                update.effective_message.delete()
            except TelegramError:
                pass

    return is_not_admin_no_reply


def user_can_restrict_no_reply(func):
    @wraps(func)
    def u_can_restrict_noreply(
        update: Update, context: CallbackContext, *args, **kwargs
    ):
        context.bot
        user = update.effective_user
        chat = update.effective_chat
        query = update.callback_query
        member = chat.get_member(user.id)

        if user:
            if (
                member.can_restrict_members
                or member.status == "creator"
                or user.id in DRAGONS
            ):
                return func(update, context, *args, **kwargs)
            elif member.status == "administrator":
                query.answer("You're missing the `can_restrict_members` permission.")
            else:
                query.answer(
                    "You need to be admin with `can_restrict_users` permission to do this."
                )
        elif DEL_CMDS and " " not in update.effective_message.text:
            try:
                update.effective_message.delete()
            except:
                pass

    return u_can_restrict_noreply


ADMIN_PERMS = [
    "can_delete_messages",
    "can_restrict_members",
    "can_pin_messages",
    "can_promote_members",
]

MESSAGES = [
    "You don't have sufficient permissions to delete messages!",
    "You don't have sufficient permissions to restrict users!",
    "You don't have sufficient permissions to pin messages!",
    "You don't have sufficient permissions to promote users!",
]


def check_perms(update: Update, type: str):
    chat = update.effective_chat
    user = update.effective_user

    admin = chat.get_member(int(user.id))
    admin_perms = (
        admin[ADMIN_PERMS[type]]
        if admin["status"] != "creator" and user.id not in DRAGONS
        else True
    )

    if not admin_perms:
        update.effective_message.reply_text(MESSAGES[type])
        return False

    return True


# Workaround for circular import with connection.py
from Exon.modules import connection

connected = connection.connected
