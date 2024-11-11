import asyncio
import re

from ptbmod import Admins
from ptbmod.decorator.cache import is_admin
from telegram import ChatMember, ChatPermissions, Message, Update
from telegram.ext import ContextTypes
from telegram.helpers import mention_html

from Telegram import Cmd
from Telegram.utils.extract_user import extract_user
from Telegram.utils.formatters import create_time, tl_time
from Telegram.utils.misc import try_to_delete


@Cmd(command=["ban", "dban", "tBan", "dtBan", "sBan", "stBan"])
@Admins(permissions="can_restrict_members", is_both=True)
async def ban(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str | None:
    """Ban a user."""
    chat = update.effective_chat
    m = update.effective_message
    reply_msg = m.reply_to_message or m

    user_id, user_first_name, _, _reason = await extract_user(m, context)

    if not user_id or user_id == context.bot.id or await is_admin(chat.id, user_id):
        await m.reply_text(
            "I don't know who you're talking about, you need to specify a user."
            if user_id is None
            else (
                "I can't ban myself."
                if user_id == context.bot.id
                else "What are you trying to do? You can't ban someone who's an admin."
            )
        )
        return None

    ban_time = "367d"
    reason = ""

    if _reason:
        if match := re.match(r"([0-9]{1,})([dhms])\s*(.*)", _reason):
            ban_time = match[1] + match[2]
            reason = match[3] if match.lastindex > 2 else ""
        else:
            reason = _reason

    delete = bool(m.text.startswith("/d") or m.text.startswith("!d"))
    silent = bool(m.text.startswith("/s") or m.text.startswith("!s"))

    try:
        if user_id < 0:
            await chat.ban_sender_chat(user_id)
        else:
            await chat.ban_member(user_id, until_date=create_time(ban_time))
    except Exception as e:
        await m.reply_text("Failed to ban;")
        raise e
    if delete:
        await try_to_delete(reply_msg)
    elif silent:
        await asyncio.gather(try_to_delete(reply_msg), try_to_delete(m))
        return

    text = (
        f"<b>{mention_html(user_id, user_first_name)}</b> was banned for {tl_time(ban_time)}."
        + (f"\n<b>Reason:</b> <code>{reason}</code>" if reason else "")
    )
    await m.reply_text(text)
    return None


@Cmd(command=["unban", "sUnban"])
@Admins(permissions="can_restrict_members", is_both=True)
async def unban(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str | None:
    """Unban a user."""
    chat = update.effective_chat
    m = update.effective_message
    reply_msg = m.reply_to_message or m

    user_id, user_first_name, _, _reason = await extract_user(m, context)

    if not user_id or user_id == context.bot.id or await is_admin(chat.id, user_id):
        await m.reply_text(
            "I don't know who you're talking about, you need to specify a user."
            if user_id is None
            else (
                "wtf; What are you trying to do?"
                if user_id == context.bot.id
                else "What are you trying to do? You can't ban someone who's an admin."
            )
        )
        return None

    try:
        await chat.unban_member(user_id, only_if_banned=True)
    except Exception as e:
        await m.reply_text("Failed to unban;")
        raise e

    delete = bool(m.text.startswith("/d") or m.text.startswith("!d"))
    silent = bool(m.text.startswith("/s") or m.text.startswith("!s"))

    if delete:
        await try_to_delete(reply_msg)
    elif silent:
        await asyncio.gather(try_to_delete(reply_msg), try_to_delete(m))
        return

    text = f"<b>{mention_html(user_id, user_first_name)}</b> was unbanned."
    if _reason:
        text += f"\n<b>Reason:</b> <code>{_reason}</code>"
    await m.reply_text(text)
    return


@Cmd(command=["kick", "dKick", "skick"])
@Admins(permissions="can_restrict_members", is_both=True)
async def kick(update: Update, context: ContextTypes.DEFAULT_TYPE) -> Message:
    """Kick a user."""
    chat = update.effective_chat
    m = update.effective_message
    reply_msg = m.reply_to_message or m

    user_id, user_first_name, _, _reason = await extract_user(m, context)

    if not user_id or user_id == context.bot.id or await is_admin(chat.id, user_id):
        return await m.reply_text(
            "I don't know who you're talking about, you need to specify a user."
            if user_id is None
            else (
                "I can't kick myself."
                if user_id == context.bot.id
                else "What are you trying to do? You can't kick someone who's an admin."
            )
        )

    try:
        await chat.unban_member(user_id)
    except Exception as e:
        await m.reply_text("Failed to kick;")
        raise e

    delete = bool(m.text.startswith("/d") or m.text.startswith("!d"))
    silent = bool(m.text.startswith("/s") or m.text.startswith("!s"))

    if delete:
        await try_to_delete(reply_msg)
    elif silent:
        await asyncio.gather(try_to_delete(reply_msg), try_to_delete(m))

    text = f"<b>{mention_html(user_id, user_first_name)}</b> was kicked."
    if _reason:
        text += f"\n<b>Reason:</b> <code>{_reason}</code>"
    await m.reply_text(text)


@Cmd(command=["mute", "dMute", "sMute", "tMute"])
@Admins(permissions="can_restrict_members", is_both=True)
async def mute(update: Update, context: ContextTypes.DEFAULT_TYPE) -> Message | None:
    """Mute a user."""
    chat = update.effective_chat
    m = update.effective_message
    reply_msg = m.reply_to_message or m

    user_id, user_first_name, _, _reason = await extract_user(m, context)
    if not user_id or user_id == context.bot.id or await is_admin(chat.id, user_id):
        return await m.reply_text(
            "I don't know who you're talking about, you need to specify a user."
            if user_id is None
            else (
                "I can't mute myself."
                if user_id == context.bot.id
                else "What are you trying to do? You can't mute someone who's an admin."
            )
        )

    delete = bool(m.text.startswith("/d") or m.text.startswith("!d"))
    silent = bool(m.text.startswith("/s") or m.text.startswith("!s"))

    match = re.match(r"([0-9]{1,})([dhms])*$", _reason) if _reason else None
    if match:
        ban_time = match.group(0)
        reason = _reason[match.end() :].strip()
    else:
        ban_time = "367d"
        reason = _reason

    try:
        await chat.restrict_member(
            user_id, until_date=create_time(ban_time), permissions=ChatPermissions()
        )
    except Exception as e:
        await m.reply_text("Failed to mute;")
        raise e

    if delete:
        await try_to_delete(reply_msg)
    elif silent:
        await asyncio.gather(try_to_delete(reply_msg), try_to_delete(m))
        return None

    text = f"<b>{mention_html(user_id, user_first_name)}</b> was muted for {tl_time(ban_time)}."
    if reason:
        text += f"\n<b>Reason:</b> <code>{reason}</code>"
    await m.reply_text(text)
    return None


@Cmd(command=["unmute", "sUnmute"])
@Admins(permissions="can_restrict_members", is_both=True)
async def unmute(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str | None:
    """Unmute a user."""
    chat = update.effective_chat
    m = update.effective_message

    reply_msg = m.reply_to_message or m

    user_id, user_first_name, _, _reason = await extract_user(m, context)

    if not user_id or user_id == context.bot.id or await is_admin(chat.id, user_id):
        await m.reply_text(
            "I don't know who you're talking about, you need to specify a user."
            if user_id is None
            else (
                "look I can speak."
                if user_id == context.bot.id
                else "What are you trying to do? This user is admin so how possible is it to unmute them."
            )
        )
        return None

    member = await chat.get_member(int(user_id))
    if member.status != ChatMember.RESTRICTED:
        await m.reply_text("This user is not muted.")
        return None

    delete = bool(m.text.startswith("/d") or m.text.startswith("!d"))
    silent = bool(m.text.startswith("/s") or m.text.startswith("!s"))

    try:
        await chat.restrict_member(
            user_id, permissions=ChatPermissions.all_permissions()
        )
    except Exception as e:
        await m.reply_text("Failed to unmute;")
        raise e
    if delete:
        await try_to_delete(reply_msg)
    elif silent:
        await asyncio.gather(try_to_delete(reply_msg), try_to_delete(m))
        return

    text = f"Fine, <b>{mention_html(user_id, user_first_name)}</b> can speak again."
    if _reason:
        text += f"\n<b>Reason:</b> <code>{_reason}</code>"
    await m.reply_text(text)
    return


__mod_name__ = "Bans"

__alt_name__ = ["ban", "unban", "mute", "unmute", "kick"]

__help__ = """
<b>Description :</b>
Some people need to be publicly banned; spammers, annoyances, or just trolls.

This module allows you to do that easily, by exposing some common actions, so everyone will see!
────────────────────────

<b>The Following Commands Are Admin Only :</b>

๏ /ban X time reason<b>:</b> Bans the user replied to or tagged.
๏ /sBan X time <b>:</b> Bans the user replied or tagged and deletes your message.
๏ /dban X time reason<b>:</b> Bans the user replied and deletes their message.
๏ /mute X time reason<b>:</b> Mutes the user replied to or tagged.
๏ /sMute X time <b>:</b> Mutes the user replied or tagged and deletes your message.
๏ /dMute X time reason<b>:</b> Mutes the user replied and deletes their message.
"""
