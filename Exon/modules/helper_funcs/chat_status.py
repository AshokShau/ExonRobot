from functools import wraps
from threading import RLock
from time import perf_counter

from cachetools import TTLCache
from telegram import Chat, ChatMember, ChatMemberAdministrator, ChatMemberOwner, Update
from telegram.constants import ChatMemberStatus, ChatType
from telegram.error import Forbidden
from telegram.ext import ContextTypes

from Exon import DEL_CMDS, DEV_USERS, DRAGONS, SUPPORT_CHAT, exon

# stores admemes in memory for 10 min.
ADMIN_CACHE = TTLCache(maxsize=512, ttl=60 * 10, timer=perf_counter)
THREAD_LOCK = RLock()


def check_admin(
    permission: str = None,
    is_bot: bool = False,
    is_user: bool = False,
    is_both: bool = False,
    only_owner: bool = False,
    only_sudo: bool = False,
    only_dev: bool = False,
    no_reply: object = False,
) -> object:
    def wrapper(func):
        @wraps(func)
        async def wrapped(
            update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs
        ):
            nonlocal permission
            chat = update.effective_chat
            user = update.effective_user
            message = update.effective_message

            if message.from_user.id == 1087968824:
                return await func(update, context, *args, **kwargs)

            if chat.type == ChatType.PRIVATE and not (
                only_dev or only_sudo or only_owner
            ):
                return await func(update, context, *args, **kwargs)

            bot_member = (
                await chat.get_member(context.bot.id) if is_bot or is_both else None
            )
            user_member = await chat.get_member(user.id) if is_user or is_both else None

            if only_owner:
                if isinstance(user_member, ChatMemberOwner) or user.id in DEV_USERS:
                    return await func(update, context, *args, **kwargs)
                else:
                    return await message.reply_text(
                        "ᴏɴʟʏ ᴄʜᴀᴛ ᴏᴡɴᴇʀ ᴄᴀɴ ᴘᴇʀғᴏʀᴍ ᴛʜɪs ᴀᴄᴛɪᴏɴ."
                    )
            if only_dev:
                if user.id in DEV_USERS:
                    return await func(update, context, *args, **kwargs)
                else:
                    return await update.effective_message.reply_text(
                        "ᴛʜɪs ɪs ᴀ ᴅᴇᴠᴇʟᴏᴘᴇʀ ʀᴇsᴛʀɪᴄᴛᴇᴅ ᴄᴏᴍᴍᴀɴᴅ."
                        "ʏᴏᴜ ᴅᴏ ɴᴏᴛ ʜᴀᴠᴇ ᴘᴇʀᴍɪssɪᴏɴs ᴛᴏ ʀᴜɴ ᴛʜɪs",
                    )

            if only_sudo:
                if user.id in DRAGONS:
                    return await func(update, context, *args, **kwargs)
                else:
                    return await update.effective_message.reply_text(
                        "ᴡʜᴏ ᴛʜᴇ ʜᴇʟʟ ᴀʀᴇ ʏᴏᴜ ᴛᴏ sᴀʏ ᴍᴇ ᴡʜᴀᴛ ᴛᴏ ᴅᴏ?",
                    )

            if permission:
                no_permission = permission.replace("_", " ").replace("can", "")
                if is_bot:
                    if (
                        getattr(bot_member, permission)
                        if isinstance(bot_member, ChatMemberAdministrator)
                        else False
                    ):
                        return await func(update, context, *args, **kwargs)
                    elif no_reply:
                        return
                    else:
                        return await message.reply_text(
                            f"ɪ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ ᴘᴇʀᴍɪssɪᴏɴ ᴛᴏ :- {no_permission}."
                        )
                if is_user:
                    if isinstance(user_member, ChatMemberOwner):
                        return await func(update, context, *args, **kwargs)
                    elif (
                        getattr(user_member, permission)
                        if isinstance(user_member, ChatMemberAdministrator)
                        else False or user.id in DRAGONS
                    ):
                        return await func(update, context, *args, **kwargs)
                    elif no_reply:
                        return
                    else:
                        return await message.reply_text(
                            f"ʏᴏᴜ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ ᴘᴇʀᴍɪssɪᴏɴ ᴛᴏ {no_permission}."
                        )
                if is_both:
                    if (
                        getattr(bot_member, permission)
                        if isinstance(bot_member, ChatMemberAdministrator)
                        else False
                    ):
                        pass
                    elif no_reply:
                        return
                    else:
                        return await message.reply_text(
                            f"I ᴅᴏɴ'ᴛ ʜᴀᴠᴇ ᴘᴇʀᴍɪssɪᴏɴ ᴛᴏ - {no_permission}."
                        )

                    if isinstance(user_member, ChatMemberOwner) or user.id in DEV_USERS:
                        pass
                    elif (
                        getattr(user_member, permission)
                        if isinstance(user_member, ChatMemberAdministrator)
                        else False or user.id in DRAGONS
                    ):
                        pass
                    elif no_reply:
                        return
                    else:
                        return await message.reply_text(
                            f"ʏᴏᴜ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ ᴘᴇʀᴍɪssɪᴏɴ ᴛᴏ {no_permission}."
                        )
                    return await func(update, context, *args, **kwargs)
            else:
                if is_bot:
                    if bot_member.status == ChatMemberStatus.ADMINISTRATOR:
                        return await func(update, context, *args, **kwargs)
                    else:
                        return await message.reply_text("I'ᴍ ɴᴏᴛ ᴀᴅᴍɪɴ ʜᴇʀᴇ.")
                elif is_user:
                    if user_member.status in [
                        ChatMemberStatus.ADMINISTRATOR,
                        ChatMemberStatus.OWNER,
                    ]:
                        return await func(update, context, *args, **kwargs)
                    elif user.id in DRAGONS:
                        return await func(update, context, *args, **kwargs)
                    else:
                        return await message.reply_text("ʏᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴀᴅᴍɪɴ ʜᴇʀᴇ.")
                elif is_both:
                    if bot_member.status == ChatMemberStatus.ADMINISTRATOR:
                        pass
                    else:
                        return await message.reply_text("ɪ'ᴍ ɴᴏᴛ ᴀᴅᴍɪɴ ʜᴇʀᴇ.")

                    if user_member.status in [
                        ChatMemberStatus.ADMINISTRATOR,
                        ChatMemberStatus.OWNER,
                    ]:
                        pass
                    elif user.id in DRAGONS:
                        pass
                    else:
                        return await message.reply_text("ʏᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴀᴅᴍɪɴ ʜᴇʀᴇ.")
                    return await func(update, context, *args, **kwargs)

        return wrapped

    return wrapper


def is_whitelist_plus(chat: Chat, user_id: int, member: ChatMember = None) -> bool:
    return any(user_id in user for user in [DRAGONS, DEV_USERS])


def is_support_plus(chat: Chat, user_id: int, member: ChatMember = None) -> bool:
    return user_id in DRAGONS or user_id in DEV_USERS


async def is_user_admin(chat: Chat, user_id: int, member: ChatMember = None) -> bool:
    if (
        chat.type == "private"
        or user_id in DRAGONS
        or user_id in DEV_USERS
        or user_id in [777000, 1087968824]
    ):  # Count telegram and Group Anonymous as admin
        return True
    if not member:
        with THREAD_LOCK:
            # try to fetch from cache first.
            try:
                return user_id in ADMIN_CACHE[chat.id]
            except KeyError:
                try:
                    chat_admins = await exon.bot.getChatAdministrators(chat.id)
                except Forbidden:
                    return False
                admin_list = [x.user.id for x in chat_admins]
                ADMIN_CACHE[chat.id] = admin_list

                return user_id in admin_list
    else:
        return member.status in (ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER)


async def is_bot_admin(chat: Chat, bot_id: int, bot_member: ChatMember = None) -> bool:
    if chat.type == "private":
        return True

    if not bot_member:
        bot_member = await chat.get_member(bot_id)

    return bot_member.status in (ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER)


async def can_delete(chat: Chat, bot_id: int) -> bool:
    chat_member = await chat.get_member(bot_id)
    if isinstance(chat_member, ChatMemberAdministrator):
        return chat_member.can_delete_messages


async def is_user_ban_protected(
    chat: Chat, user_id: int, member: ChatMember = None
) -> bool:
    if (
        chat.type == "private"
        or user_id in DRAGONS
        or user_id in DEV_USERS
        or user_id in [777000, 1087968824]
    ):  # Count telegram and Group Anonymous as admin
        return True

    if not member:
        member = await chat.get_member(user_id)

    return member.status in (ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER)


async def is_user_in_chat(chat: Chat, user_id: int) -> bool:
    member = await chat.get_member(user_id)
    return member.status in (ChatMemberStatus.LEFT, ChatMemberStatus.RESTRICTED)


def support_plus(func):
    @wraps(func)
    async def is_support_plus_func(
        update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs
    ):
        bot = context.bot
        user = update.effective_user
        chat = update.effective_chat

        if user and is_support_plus(chat, user.id):
            return await func(update, context, *args, **kwargs)
        elif DEL_CMDS and " " not in update.effective_message.text:
            try:
                await update.effective_message.delete()
            except:
                pass

    return is_support_plus_func


def whitelist_plus(func):
    @wraps(func)
    async def is_whitelist_plus_func(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
        *args,
        **kwargs,
    ):
        bot = context.bot
        user = update.effective_user
        chat = update.effective_chat

        if user and is_whitelist_plus(chat, user.id):
            return await func(update, context, *args, **kwargs)
        else:
            await update.effective_message.reply_text(
                f"ʏᴏᴜ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ ᴀᴄᴄᴇss ᴛᴏ ᴜsᴇ ᴛʜɪs.\nVisit @{SUPPORT_CHAT}",
            )

    return is_whitelist_plus_func


def user_not_admin(func):
    @wraps(func)
    async def is_not_admin(
        update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs
    ):
        bot = context.bot
        user = update.effective_user
        chat = update.effective_chat

        if user and not await is_user_admin(chat, user.id):
            return await func(update, context, *args, **kwargs)
        elif not user:
            pass

    return is_not_admin


def connection_status(func):
    @wraps(func)
    async def connected_status(
        update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs
    ):
        conn = await connected(
            context.bot,
            update,
            update.effective_chat,
            update.effective_user.id,
            need_admin=False,
        )

        if conn:
            chat = await exon.bot.getChat(conn)
            update.__setattr__("_effective_chat", chat)
            return await func(update, context, *args, **kwargs)
        else:
            if update.effective_message.chat.type == "private":
                await update.effective_message.reply_text(
                    "sᴇɴᴅ /connect ɪɴ ᴀ ɢʀᴏᴜᴘ ᴛʜᴀᴛ ʏᴏᴜ ᴀɴᴅ ɪ ʜᴀᴠᴇ ɪɴ ᴄᴏᴍᴍᴏɴ ғɪʀsᴛ.",
                )
                return connected_status

            return await func(update, context, *args, **kwargs)

    return connected_status


try:
    from Exon.modules import connection
except ImportError as e:
    print(e)

connected = connection.connected
