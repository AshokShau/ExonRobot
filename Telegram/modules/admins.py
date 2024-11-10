from ptbmod import Admins
from ptbmod.decorator.cache import get_admin_cache_user, is_admin, load_admin_cache
from telegram import ChatMemberAdministrator, Update
from telegram.constants import ChatMemberStatus
from telegram.ext import ContextTypes
from telegram.helpers import mention_html

from .. import Cmd
from ..utils.extract_user import extract_user


@Cmd(command="adminList")
@Admins(permissions="can_promote_members", is_bot=True)
async def adminList(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Gets a list of admins in a chat."""
    chat = update.effective_chat
    _, admins = await load_admin_cache(context.bot, chat.id)

    admin_list_text = "<b>Admins in this chat:</b>\n\n"
    owner_text = ""
    admin_texts = []

    for admin in admins.user_info:
        user = admin.user
        name = (
            f"{user.full_name} (@{user.username})" if user.username else user.full_name
        )
        role = (
            "Owner"
            if admin.status == ChatMemberStatus.OWNER
            else (admin.custom_title or "Admin")
        )

        if role == "Owner":
            owner_text = f"<b>Owner:</b> {name}\n\n"
        else:
            admin_texts.append(f"• {name} - <i>{role}</i>")

    admin_list_text += owner_text + "<b>Admins:</b>\n" + "\n".join(admin_texts)

    await update.effective_message.reply_text(admin_list_text)


@Cmd(command="promote")
@Admins(permissions="can_promote_members", is_both=True)
async def promote(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Promotes a user to admin."""
    msg = update.effective_message
    chat = update.effective_chat
    user_id, name, _, custom_title = await extract_user(msg, context)

    # Basic validation for the user ID
    if not user_id:
        await msg.reply_text(
            "I don't know who you're talking about, you need to specify a user."
        )
        return
    if user_id < 0:
        await msg.reply_text("This can only be used on regular users.")
        return
    if await is_admin(chat.id, user_id):
        await msg.reply_text(
            f"{mention_html(user_id, name)} is already an admin, so promotion isn't necessary."
        )
        return
    if user_id == context.bot.id:
        await msg.reply_text("I can't promote myself.")
        return

    # Get the bot's current admin status and permissions
    _, bot = await get_admin_cache_user(chat.id, context.bot.id)

    if bot and isinstance(bot, ChatMemberAdministrator):
        try:
            # Attempt to promote the user with bot's permissions
            await chat.promote_member(
                user_id,
                can_manage_chat=bot.can_manage_chat,
                can_delete_messages=bot.can_delete_messages,
                can_delete_stories=bot.can_delete_stories,
                can_invite_users=bot.can_invite_users,
                can_change_info=bot.can_change_info,
                can_pin_messages=bot.can_pin_messages,
                can_manage_video_chats=bot.can_manage_video_chats,
            )
        except Exception as e:
            await msg.reply_text(
                "I don't have sufficient permissions to promote this user or or they may be promoted by another admin;"
            )
            raise e

        text = f"Successfully promoted {mention_html(user_id, name)}."

        # Set a custom title if provided and within character limit
        if custom_title:
            custom_title = custom_title[:16]
            try:
                await chat.set_administrator_custom_title(user_id, custom_title)
                text += "\nCustom Title: <code>%s</code>" % custom_title
            except Exception as e:
                await msg.reply_text("Failed to set a custom title.")
                raise e

        await msg.reply_text(text)
    else:
        await msg.reply_text(
            "I am not an administrator or can't fetch my admin status."
        )


@Cmd(command="demote")
@Admins(permissions="can_promote_members", is_both=True)
async def demote(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Demotes an admin to a regular user."""
    msg = update.effective_message
    chat = update.effective_chat
    user_id, name, _, _ = await extract_user(msg, context)

    # Basic validation for the user ID
    if not user_id:
        await msg.reply_text(
            "I don't know who you're talking about, you need to specify a user."
        )
        return
    if user_id < 0:
        await msg.reply_text("This can only be used on regular users.")
        return
    if not await is_admin(chat.id, user_id):
        await msg.reply_text(
            f"{mention_html(user_id, name)} is not an admin, so demotion isn't necessary."
        )
        return
    if user_id == context.bot.id:
        await msg.reply_text("I can't demote myself.")
        return

    try:
        await chat.promote_member(user_id, can_manage_chat=False)
    except Exception as e:
        await msg.reply_text(
            "Failed to demote; I might not be the admin, or they may be promoted by another admin"
        )
        raise e

    await msg.reply_text(f"Successfully demoted {name}.")


@Cmd(command="setTitle")
@Admins(permissions="can_promote_members", is_both=True)
async def setTitle(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sets a custom title for an admin."""
    msg = update.effective_message
    chat = update.effective_chat
    user_id, name, _, custom_title = await extract_user(msg, context)

    # Basic validation for the user ID
    if not user_id:
        await msg.reply_text(
            "I don't know who you're talking about, you need to specify a user."
        )
        return
    if user_id < 0:
        await msg.reply_text("This can only be used on regular users.")
        return
    if not await is_admin(chat.id, user_id):
        await msg.reply_text(f"{name} is not an admin, so demotion isn't necessary.")
        return
    if user_id == context.bot.id:
        await msg.reply_text("I can't demote myself.")
        return

    if not custom_title:
        await msg.reply_text("You need to specify a custom title.")
        return

    title = custom_title[:16]
    try:
        await chat.set_administrator_custom_title(user_id, title)
    except Exception as e:
        raise e

    await msg.reply_text(
        f"Successfully set custom title to {title} for {mention_html(user_id, name)}"
    )


@Cmd(command=["inviteLink", "link"])
@Admins(permissions="can_invite_users", is_both=True)
async def getInviteLinks(update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
    """Gets the invite link for a chat."""
    chat = update.effective_chat
    if chat.username:
        invite_link = f"https://t.me/{chat.username}"
    else:
        invite_link = await chat.export_invite_link()

    await update.effective_message.reply_text(f"Invite Link: {invite_link}")


@Cmd(command=["adminCache", "reload"])
async def adminCache(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Reloads the admin cache."""
    chat = update.effective_chat
    user = update.effective_user

    chat_member = await chat.get_member(user.id)
    if chat_member.status not in [
        ChatMemberStatus.ADMINISTRATOR,
        ChatMemberStatus.OWNER,
    ]:
        await update.effective_message.reply_text(
            "You need to be an admin to use this command."
        )
        return

    done, _ = await load_admin_cache(context.bot, chat.id, True)
    if done:
        await update.effective_message.reply_text("Reloaded admin cache.")
    else:
        await update.effective_message.reply_text("Failed to reload admin cache.")


__help__ = """
<b>Description:</b>
This module contains commands to manage admins and their permissions in the group.
────────────────────────

<b>User Commands:</b>
๏ <code>/adminList</code><b>:</b> Lists all the admins in the group.

<b>The Following Commands Are Admin Only:</b>
๏ <code>/promote</code><b>:</b> Promotes a user to an admin.
๏ <code>/demote</code><b>:</b> Demotes an admin to a regular user.
๏ <code>/title</code><b>:</b> Sets a custom title for an admin.
๏ <code>/link</code><b>:</b> Gets the invite link of the group.
๏ <code>/reload</code><b>:</b> Reloads the admin cache.

<b>Note:</b> The admin list may be cached for performance reasons. Use <code>/adminCache</code> to reload the cache.
"""

__mod_name__ = "Admins"
__alt_name__ = [
    "admin",
    "adminList",
    "promote",
    "demote",
    "title",
    "inviteLink",
    "link",
    "reload",
    "adminCache",
]
