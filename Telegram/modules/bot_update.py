from ptbmod.decorator.cache import load_admin_cache
from telegram import ChatMember, InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.constants import ChatType
from telegram.ext import ChatMemberHandler, ContextTypes

from Telegram import CMember
from Telegram.database.chats_db import ChatsDB


@CMember(ChatMemberHandler.CHAT_MEMBER, group=-1)
async def chat_member_update(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Update admins cache when admins are added or removed from a group."""
    status_change = update.chat_member.difference().get("status")

    if status_change is None:
        return None

    old_status, new_status = status_change

    # luckily, we need do not worry about creator demote, they get promoted to admin automatically
    if old_status == ChatMember.ADMINISTRATOR and new_status != ChatMember.OWNER:
        await load_admin_cache(context.bot, update.effective_chat.id, True)
    elif new_status in [ChatMember.ADMINISTRATOR, ChatMember.OWNER]:
        await load_admin_cache(context.bot, update.effective_chat.id, True)


@CMember(ChatMemberHandler.MY_CHAT_MEMBER, group=-1)
async def my_chat_member_update(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """The bot was added or removed from a group."""
    if update.effective_chat.type not in [ChatType.GROUP, ChatType.SUPERGROUP]:
        # we only care if we were added or removed from a group
        return None

    status_change = update.my_chat_member.difference().get("status")

    if status_change is None:
        return None

    _, new_status = status_change
    chats_db = ChatsDB(update.effective_chat.id)

    if new_status in [
        ChatMember.LEFT,
        ChatMember.BANNED,
        ChatMember.RESTRICTED,
    ]:
        await chats_db.remove_chat()
    elif new_status in [ChatMember.ADMINISTRATOR, ChatMember.MEMBER]:
        chat = update.effective_chat

        await chats_db.update_chat(chat.title, chat.username)
        await load_admin_cache(context.bot, update.effective_chat.id)

        keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text="Oᴘᴇɴ Hᴇʟᴘ",
                        url=f"t.me/{context.bot.username}?start=start_help",
                    ),
                ],
            ],
        )

        return await context.bot.send_message(
            chat.id,
            f"<b>ᴡᴇʟᴄᴏᴍᴇ {context.bot.first_name} !</b>\n\nCheck out the help for more information on how best to protect your groups.",
            reply_markup=keyboard,
        )
