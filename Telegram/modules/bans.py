import asyncio
import re

from ptbmod import Admins
from ptbmod.decorator.cache import is_admin
from telegram import Update
from telegram.ext import ContextTypes
from telegram.helpers import mention_html

from Telegram import Cmd
from Telegram.utils.extract_user import extract_user
from Telegram.utils.formatters import create_time, tl_time
from Telegram.utils.misc import try_to_delete


@Cmd(command=["ban", "dban", "tBan", "dtBan", "sBan", "stBan"])
@Admins(permissions="can_restrict_members", is_both=True)
async def ban(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str | None:
    chat = update.effective_chat
    m = update.effective_message
    reply_msg = m.reply_to_message or m

    user_id, user_first_name, user_name, _reason = await extract_user(m, context)

    if not user_id or user_id == context.bot.id or await is_admin(chat.id, user_id):
        await m.reply_text(
            "I don't know who you're talking about, you need to specify a user."
            if user_id is None
            else "I can't ban myself."
            if user_id == context.bot.id
            else "What are you trying to do? You can't ban someone who's an admin."
        )
        return None

    ban_time = "367d"
    reason = ""

    if _reason:
        match = re.match(r"([0-9]{1,})([dhms])\s*(.*)", _reason)
        if match:
            ban_time = match.group(1) + match.group(2)
            reason = match.group(3) if match.lastindex > 2 else ""
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
    chat = update.effective_chat
    m = update.effective_message
    reply_msg = m.reply_to_message or m

    user_id, user_first_name, user_name, _reason = await extract_user(m, context)

    if not user_id or user_id == context.bot.id or await is_admin(chat.id, user_id):
        await m.reply_text(
            "I don't know who you're talking about, you need to specify a user."
            if user_id is None
            else "wtf are you trying to do?"
            if user_id == context.bot.id
            else "What are you trying to do? You can't ban someone who's an admin."
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
