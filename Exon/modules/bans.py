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

# ""DEAR PRO PEOPLE,  DON'T REMOVE & CHANGE THIS LINE
# TG :- @Abishnoi1m
#     UPDATE   :- Abishnoi_bots
#     GITHUB :- ABISHNOI69 ""

import html
from typing import Optional

from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ParseMode,
    TelegramError,
    Update,
)
from telegram.error import BadRequest
from telegram.ext import CallbackContext, CallbackQueryHandler, CommandHandler, Filters
from telegram.utils.helpers import mention_html

from Exon import (
    DEMONS,
    DEV_USERS,
    DRAGONS,
    LOGGER,
    OWNER_ID,
    TIGERS,
    WOLVES,
    dispatcher,
)
from Exon.modules.disable import DisableAbleCommandHandler
from Exon.modules.helper_funcs.anonymous import AdminPerms, user_admin
from Exon.modules.helper_funcs.chat_status import (
    bot_admin,
    can_delete,
    can_restrict,
    connection_status,
    dev_plus,
    is_user_admin,
    is_user_ban_protected,
    is_user_in_chat,
)
from Exon.modules.helper_funcs.chat_status import user_admin as u_admin
from Exon.modules.helper_funcs.chat_status import user_admin_no_reply, user_can_ban
from Exon.modules.helper_funcs.extraction import extract_user_and_text
from Exon.modules.helper_funcs.filters import CustomFilters
from Exon.modules.helper_funcs.string_handling import extract_time
from Exon.modules.log_channel import gloggable, loggable


# @Exoncmd(command=["ban", "sban", "dban"], pass_args=True)
@connection_status
@bot_admin
@can_restrict
@user_admin(AdminPerms.CAN_RESTRICT_MEMBERS)
@loggable
def ban(
    update: Update, context: CallbackContext
) -> Optional[str]:  # sourcery no-metrics
    chat = update.effective_chat  # type: Optional[Chat]
    user = update.effective_user  # type: Optional[User]
    message = update.effective_message  # type: Optional[Message]
    args = context.args
    bot = context.bot
    log_message = ""
    reason = ""
    if message.reply_to_message and message.reply_to_message.sender_chat:
        r = bot.ban_chat_sender_chat(
            chat_id=chat.id, sender_chat_id=message.reply_to_message.sender_chat.id
        )
        if r:
            message.reply_text(
                "Finally! Channel {} was banned successfully from {}\n\n💡 He can only write with his profile but not through other channels.".format(
                    html.escape(message.reply_to_message.sender_chat.title),
                    html.escape(chat.title),
                ),
                parse_mode="html",
            )
            return (
                f"<b>{html.escape(chat.title)}:</b>\n"
                f"#BANNED\n"
                f"<b>Admin:</b> {mention_html(user.id, user.first_name)}\n"
                f"<b>Channel:</b> {html.escape(message.reply_to_message.sender_chat.title)} ({message.reply_to_message.sender_chat.id})"
            )
        message.reply_text("Failed to ban channel")
        return

    user_id, reason = extract_user_and_text(message, args)

    if not user_id:
        message.reply_text("I doubt that's a user.")
        return log_message

    try:
        member = chat.get_member(user_id)
    except BadRequest as excp:
        if excp.message != "User not found":
            raise

        message.reply_text("Can't seem to find this person.")
        return log_message
    if user_id == context.bot.id:
        message.reply_text("Oh yeah, ban myself, noob!")
        return log_message

    if is_user_ban_protected(update, user_id, member) and user not in DEV_USERS:
        if user_id == OWNER_ID:
            message.reply_text("Fighting with my Master will put user lives at risk")
        elif user_id in DEV_USERS:
            message.reply_text("I can't act against our own.")
        elif user_id in DRAGONS:
            message.reply_text(
                "Fighting this Shadow Slayer here will put user lives at risk."
            )
        elif user_id in DEMONS:
            message.reply_text("Bring an order from Master Servant to fight a Guardian")
        elif user_id in TIGERS:
            message.reply_text(
                "Bring an order from Master Servant to fight a Light Shooters"
            )
        elif user_id in WOLVES:
            message.reply_text("Villain abilities make them ban immune!")
        else:
            message.reply_text("This user has immunity and cannot be banned.")
        return log_message

    if message.text.startswith("/d") and message.reply_to_message:
        message.reply_to_message.delete()

    if message.text.startswith("/s"):
        silent = True
        if not can_delete(chat, context.bot.id):
            return ""
    else:
        silent = False

    log = (
        f"<b>{html.escape(chat.title)}:</b>\n"
        f"#{'S' if silent else ''}BANNED\n"
        f"<b>Admin:</b> {mention_html(user.id, user.first_name)}\n"
        f"<b>User:</b> {mention_html(member.user.id, member.user.first_name)}"
    )
    if reason:
        log += "\n<b>Reason:</b> {}".format(reason)

    try:
        chat.ban_member(user_id)

        if silent:
            if message.reply_to_message:
                message.reply_to_message.delete()
            message.delete()
            return log

        # context.bot.send_sticker(chat.id, BAN_STICKER)  # banhammer marie sticker
        reply = (
            f"Yep! Banned {mention_html(member.user.id, html.escape(member.user.first_name))} from {chat.title}\n"
            f"By {mention_html(user.id, html.escape(user.first_name))}"
        )
        if reason:
            reply += f"\nReason: {html.escape(reason)}"

        bot.sendMessage(
            chat.id,
            reply,
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text="⚠️ Unban", callback_data=f"unbanb_unban={user_id}"
                        ),
                        InlineKeyboardButton(
                            text="❌ Delete", callback_data="unbanb_del"
                        ),
                    ]
                ]
            ),
            parse_mode=ParseMode.HTML,
        )
        return log

    except BadRequest as excp:
        if excp.message == "Reply message not found":
            # Do not reply
            if silent:
                return log
            message.reply_text("Banned!", quote=False)
            return log
        LOGGER.warning(update)
        LOGGER.exception(
            "ERROR banning user %s in chat %s (%s) due to %s",
            user_id,
            chat.title,
            chat.id,
            excp.message,
        )
        message.reply_text("Well damn, I can't ban that user.")

    return ""


@connection_status
@bot_admin
@can_restrict
@u_admin
@user_can_ban
@loggable
def temp_ban(update: Update, context: CallbackContext) -> str:
    chat = update.effective_chat
    user = update.effective_user
    message = update.effective_message
    log_message = ""
    bot, args = context.bot, context.args

    user_id, reason = extract_user_and_text(message, args)

    if not user_id:
        message.reply_text("Dude! at least refer some user to ban...")
        return log_message

    try:
        member = chat.get_member(user_id)
    except BadRequest as excp:
        if excp.message != "User not found":
            raise
        message.reply_text("I can't seem to find this user.")
        return log_message
    if user_id == bot.id:
        message.reply_text("I'm not gonna BAN myself, are you crazy?")
        return log_message

    if is_user_ban_protected(chat, user_id, member):
        message.reply_text("I don't feel like it.")
        return log_message

    if not reason:
        message.reply_text("You haven't specified a time to ban this user for!")
        return log_message

    split_reason = reason.split(None, 1)

    time_val = split_reason[0].lower()
    reason = split_reason[1] if len(split_reason) > 1 else ""
    bantime = extract_time(message, time_val)

    if not bantime:
        return log_message

    log = (
        f"<b>{html.escape(chat.title)}:</b>\n"
        "#TEMP BANNED\n"
        f"<b>Admin:</b> {mention_html(user.id, html.escape(user.first_name))}\n"
        f"<b>User:</b> {mention_html(member.user.id, html.escape(member.user.first_name))}\n"
        f"<b>Time:</b> {time_val}"
    )
    if reason:
        log += "\n<b>Reason:</b> {}".format(reason)

    try:
        chat.ban_member(user_id, until_date=bantime)
        # bot.send_sticker(chat.id, BAN_STICKER)  # banhammer marie sticker

        reply_msg = (
            f"Yep! Temporary Banned {mention_html(member.user.id, html.escape(member.user.first_name))} from {chat.title}\n"
            f"By {mention_html(user.id, html.escape(user.first_name))}"
        )
        if reason:
            reply_msg += f"\nReason: {html.escape(reason)}"

        bot.sendMessage(
            chat.id,
            reply_msg,
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text="⚠️ Unban", callback_data=f"unbanb_unban={user_id}"
                        ),
                        InlineKeyboardButton(
                            text="❌ Delete", callback_data="unbanb_del"
                        ),
                    ]
                ]
            ),
            parse_mode=ParseMode.HTML,
        )
        return log

    except BadRequest as excp:
        if excp.message == "Reply message not found":
            # Do not reply
            message.reply_text(
                f"Banned! User will be banned for {time_val}.", quote=False
            )
            return log
        LOGGER.warning(update)
        LOGGER.exception(
            "ERROR banning user %s in chat %s (%s) due to %s",
            user_id,
            chat.title,
            chat.id,
            excp.message,
        )
        message.reply_text("Well damn, I can't ban that user.")

    return log_message


@connection_status
@bot_admin
@can_restrict
@user_admin_no_reply
@user_can_ban
@loggable
def unbanb_btn(update: Update, context: CallbackContext) -> str:
    bot = context.bot
    query = update.callback_query
    chat = update.effective_chat
    user = update.effective_user
    if query.data != "unbanb_del":
        splitter = query.data.split("=")
        query_match = splitter[0]
        if query_match == "unbanb_unban":
            user_id = splitter[1]
            if not is_user_admin(update, int(user.id)):
                bot.answer_callback_query(
                    query.id,
                    text="You don't have enough rights to unmute people",
                    show_alert=True,
                )
                return ""

            try:
                member = chat.get_member(user_id)
            except BadRequest:
                pass

            dick = (
                f"Yep! Unbanned {mention_html(member.user.id, html.escape(member.user.first_name))} from {chat.title}\n"
                f"Unbanned By: {mention_html(user.id, html.escape(user.first_name))}"
            )
            chat.unban_member(user_id)
            query.message.edit_text(
                dick,
                parse_mode=ParseMode.HTML,
            )
            bot.answer_callback_query(query.id, text="Unbanned!")
            return (
                f"<b>{html.escape(chat.title)}:</b>\n"
                f"#UNBANNED\n"
                f"<b>Admin:</b> {mention_html(user.id, user.first_name)}\n"
                f"<b>User:</b> {mention_html(member.user.id, member.user.first_name)}"
            )

    else:
        if not is_user_admin(update, int(user.id)):
            bot.answer_callback_query(
                query.id,
                text="You don't have enough rights to delete this message.",
                show_alert=True,
            )
            return ""
        query.message.delete()
        bot.answer_callback_query(query.id, text="Deleted!")
        return ""


@connection_status
@bot_admin
@can_restrict
@u_admin
@user_can_ban
@loggable
def punch(update: Update, context: CallbackContext) -> str:
    chat = update.effective_chat
    user = update.effective_user
    message = update.effective_message
    log_message = ""
    bot, args = context.bot, context.args

    user_id, reason = extract_user_and_text(message, args)

    if not user_id:
        message.reply_text("I doubt that's a user.")
        return log_message

    try:
        member = chat.get_member(user_id)
    except BadRequest as excp:
        if excp.message != "User not found":
            raise

        message.reply_text("I can't seem to find this user.")
        return log_message
    if user_id == bot.id:
        message.reply_text("Yeahhh I'm not gonna do that.")
        return log_message

    if is_user_ban_protected(update, user_id):
        message.reply_text("I really wish I could punch this user....")
        return log_message

    res = chat.unban_member(user_id)  # unban on current user = kick
    if res:
        # bot.send_sticker(chat.id, BAN_STICKER)  # banhammer marie sticker
        bot.sendMessage(
            chat.id,
            f"One kicked! {mention_html(member.user.id, html.escape(member.user.first_name))}.",
            parse_mode=ParseMode.HTML,
        )
        log = (
            f"<b>{html.escape(chat.title)}:</b>\n"
            f"#KICKED\n"
            f"<b>Admin:</b> {mention_html(user.id, html.escape(user.first_name))}\n"
            f"<b>User:</b> {mention_html(member.user.id, html.escape(member.user.first_name))}"
        )
        if reason:
            log += f"\n<b>Reason:</b> {reason}"

        return log
    message.reply_text("Well damn, I can't punch that user.")

    return log_message


@bot_admin
@can_restrict
def punchme(update: Update, context: CallbackContext):
    user_id = update.effective_message.from_user.id
    if is_user_admin(update, user_id):
        update.effective_message.reply_text("I wish I could... but you're an admin.")
        return

    res = update.effective_chat.unban_member(user_id)  # unban on current user = kick
    if res:
        update.effective_message.reply_text("*punches you out of the group*")
    else:
        update.effective_message.reply_text("Huh? I can't :/")


@connection_status
@bot_admin
@can_restrict
@u_admin
@user_can_ban
@loggable
def unban(update: Update, context: CallbackContext) -> Optional[str]:
    message = update.effective_message
    user = update.effective_user
    chat = update.effective_chat
    log_message = ""
    bot, args = context.bot, context.args
    if message.reply_to_message and message.reply_to_message.sender_chat:
        r = bot.unban_chat_sender_chat(
            chat_id=chat.id, sender_chat_id=message.reply_to_message.sender_chat.id
        )
        if r:
            message.reply_text(
                "Finally! Channel {} was unbanned successfully from {}\n\n💡 Now this users can send the messages with they channel again".format(
                    html.escape(message.reply_to_message.sender_chat.title),
                    html.escape(chat.title),
                ),
                parse_mode="html",
            )
        else:
            message.reply_text("Failed to unban channel")
        return

    user_id, reason = extract_user_and_text(message, args)
    if not user_id:
        message.reply_text("I doubt that's a user.")
        return log_message

    try:
        member = chat.get_member(user_id)
    except BadRequest as excp:
        if excp.message != "User not found":
            raise
        message.reply_text("I can't seem to find this user.")
        return log_message
    if user_id == bot.id:
        message.reply_text("How would I unban myself if I wasn't here...?")
        return log_message

    if is_user_in_chat(chat, user_id):
        message.reply_text("Isn't this person already here??")
        return log_message

    chat.unban_member(user_id)
    message.reply_text(
        f"Yep! Unbanned {mention_html(member.user.id, html.escape(member.user.first_name))} from {chat.title}\n"
        f"Unbanned By: {mention_html(user.id, html.escape(user.first_name))}!",
        parse_mode=ParseMode.HTML,
    )

    log = (
        f"<b>{html.escape(chat.title)}:</b>\n"
        f"#UNBANNED\n"
        f"<b>Admin:</b> {mention_html(user.id, html.escape(user.first_name))}\n"
        f"<b>User:</b> {mention_html(member.user.id, html.escape(member.user.first_name))}"
    )
    if reason:
        log += f"\n<b>Reason:</b> {reason}"

    return log


@connection_status
@bot_admin
@can_restrict
@gloggable
def selfunban(update: Update, context: CallbackContext) -> str:
    message = update.effective_message
    user = update.effective_user
    bot, args = context.bot, context.args
    if user.id not in DRAGONS or user.id not in TIGERS:
        return

    try:
        chat_id = int(args[0])
    except:
        message.reply_text("Give a valid chat ID.")
        return

    chat = bot.getChat(chat_id)

    try:
        member = chat.get_member(user.id)
    except BadRequest as excp:
        if excp.message == "User not found":
            message.reply_text("I can't seem to find this user.")
            return
        raise

    if is_user_in_chat(chat, user.id):
        message.reply_text("Aren't you already in the chat??")
        return

    chat.unban_member(user.id)
    message.reply_text(
        f"Yep! I Have Unbanned You {mention_html(member.user.id, html.escape(member.user.first_name))} from {chat.title}\n"
        f"Unbanned By: {mention_html(user.id, html.escape(user.first_name))}.",
        parse_mode=ParseMode.HTML,
    )

    log = (
        f"<b>{html.escape(chat.title)}:</b>\n"
        f"#UNBANNED\n"
        f"<b>User:</b> {mention_html(member.user.id, html.escape(member.user.first_name))}"
    )

    return log


@bot_admin
@can_restrict
@loggable
def banme(update: Update, context: CallbackContext):
    user_id = update.effective_message.from_user.id
    chat = update.effective_chat
    user = update.effective_user
    if is_user_admin(update, user_id):
        update.effective_message.reply_text("Yeahhh.. not gonna ban an admin.")
        return

    res = update.effective_chat.ban_member(user_id)
    if res:
        update.effective_message.reply_text("Yes, you're right! GTFO..")
        return (
            "<b>{}:</b>"
            "\n#BANME"
            "\n<b>User:</b> {}"
            "\n<b>ID:</b> <code>{}</code>".format(
                html.escape(chat.title),
                mention_html(user.id, user.first_name),
                user_id,
            )
        )
    update.effective_message.reply_text("Huh? I can't :/")


@dev_plus
def snipe(update: Update, context: CallbackContext):
    args = context.args
    bot = context.bot
    try:
        chat_id = str(args[0])
        del args[0]
    except TypeError:
        update.effective_message.reply_text("Please give me a chat to echo to!")
    to_send = " ".join(args)
    if len(to_send) >= 2:
        try:
            bot.sendMessage(int(chat_id), str(to_send))
        except TelegramError:
            LOGGER.warning("Couldn't send to group %s", str(chat_id))
            update.effective_message.reply_text(
                "Couldn't send the message. Perhaps I'm not part of that group?"
            )


__mod_name__ = "𝐁ᴀɴs"


BAN_HANDLER = CommandHandler(["ban", "sban", "dban"], ban, run_async=True)
TEMPBAN_HANDLER = CommandHandler(["tban"], temp_ban, run_async=True)
KICK_HANDLER = CommandHandler(["kick", "punch"], punch, run_async=True)
UNBAN_HANDLER = CommandHandler("unban", unban, run_async=True)
ROAR_HANDLER = CommandHandler("roar", selfunban, run_async=True)
UNBAN_BUTTON_HANDLER = CallbackQueryHandler(
    unbanb_btn, pattern=r"unbanb_", run_async=True
)
KICKME_HANDLER = DisableAbleCommandHandler(
    ["kickme", "punchme"], punchme, filters=Filters.chat_type.groups, run_async=True
)
SNIPE_HANDLER = CommandHandler(
    "snipe", snipe, pass_args=True, filters=CustomFilters.dev_filter, run_async=True
)
BANME_HANDLER = CommandHandler("banme", banme, run_async=True)

dispatcher.add_handler(BAN_HANDLER)
dispatcher.add_handler(TEMPBAN_HANDLER)
dispatcher.add_handler(KICK_HANDLER)
dispatcher.add_handler(UNBAN_HANDLER)
dispatcher.add_handler(ROAR_HANDLER)
dispatcher.add_handler(KICKME_HANDLER)
dispatcher.add_handler(UNBAN_BUTTON_HANDLER)
dispatcher.add_handler(SNIPE_HANDLER)
dispatcher.add_handler(BANME_HANDLER)

__handlers__ = [
    BAN_HANDLER,
    TEMPBAN_HANDLER,
    KICK_HANDLER,
    UNBAN_HANDLER,
    ROAR_HANDLER,
    KICKME_HANDLER,
    UNBAN_BUTTON_HANDLER,
    SNIPE_HANDLER,
    BANME_HANDLER,
]
