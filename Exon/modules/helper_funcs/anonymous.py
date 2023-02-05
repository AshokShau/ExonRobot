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


import functools
from enum import Enum

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode, Update
from telegram.ext import CallbackContext

from Exon import DEV_USERS, DRAGONS, dispatcher
from Exon.modules.helper_funcs.decorators import Exoncallback


class AdminPerms(Enum):
    CAN_RESTRICT_MEMBERS = "can_restrict_members"
    CAN_PROMOTE_MEMBERS = "can_promote_members"
    CAN_INVITE_USERS = "can_invite_users"
    CAN_DELETE_MESSAGES = "can_delete_messages"
    CAN_CHANGE_INFO = "can_change_info"
    CAN_PIN_MESSAGES = "can_pin_messages"


class ChatStatus(Enum):
    CREATOR = "creator"
    ADMIN = "administrator"


anon_callbacks = {}
anon_callback_messages = {}
anon_users = {}


def user_admin(permission: AdminPerms):
    def wrapper(func):
        @functools.wraps(func)
        def awrapper(update: Update, context: CallbackContext, *args, **kwargs):
            nonlocal permission
            if update.effective_chat.type == "private":
                return func(update, context, *args, **kwargs)
            message = update.effective_message
            is_anon = update.effective_message.sender_chat

            if is_anon:
                callback_id = (
                    f"anoncb/{message.chat.id}/{message.message_id}/{permission.value}"
                )
                anon_callbacks[(message.chat.id, message.message_id)] = (
                    (update, context),
                    func,
                )
                anon_callback_messages[(message.chat.id, message.message_id)] = (
                    message.reply_text(
                        "Seems like you're anonymous, click the button below to prove your identity",
                        reply_markup=InlineKeyboardMarkup(
                            [
                                [
                                    InlineKeyboardButton(
                                        text="Prove identity", callback_data=callback_id
                                    )
                                ]
                            ]
                        ),
                    )
                ).message_id
                # send message with callback f'anoncb{callback_id}'
            else:
                user_id = message.from_user.id
                chat_id = message.chat.id
                mem = context.bot.get_chat_member(chat_id=chat_id, user_id=user_id)
                if (
                    getattr(mem, permission.value) is True
                    or mem.status == "creator"
                    or user_id in DRAGONS
                ):
                    return func(update, context, *args, **kwargs)
                else:
                    return message.reply_text(
                        f"You lack the permission: `{permission.name}`",
                        parse_mode=ParseMode.MARKDOWN,
                    )

        return awrapper

    return wrapper


@Exoncallback(pattern="anoncb")
def anon_callback_handler1(upd: Update, _: CallbackContext):
    callback = upd.callback_query
    perm = callback.data.split("/")[3]
    chat_id = int(callback.data.split("/")[1])
    message_id = int(callback.data.split("/")[2])
    try:
        mem = upd.effective_chat.get_member(user_id=callback.from_user.id)
    except BaseException as e:
        callback.answer(f"Error: {e}", show_alert=True)
        return
    if mem.status not in [ChatStatus.ADMIN.value, ChatStatus.CREATOR.value]:
        callback.answer("You're aren't admin.")
        dispatcher.bot.delete_message(
            chat_id, anon_callback_messages.pop((chat_id, message_id), None)
        )
        dispatcher.bot.send_message(
            chat_id, "You lack the permissions required for this command"
        )
    elif (
        getattr(mem, perm) is True
        or mem.status == "creator"
        or mem.user.id in DEV_USERS
    ):
        cb = anon_callbacks.pop((chat_id, message_id), None)
        if cb:
            message_id = anon_callback_messages.pop((chat_id, message_id), None)
            if message_id is not None:
                dispatcher.bot.delete_message(chat_id, message_id)
            return cb[1](cb[0][0], cb[0][1])
    else:
        callback.answer("This isn't for ya")


def resolve_user(user, message_id, chat):
    if user.id == 1087968824:
        try:
            uid = anon_users.pop((chat.id, message_id))
            user = chat.get_member(uid).user
        except KeyError:
            return dispatcher.bot.edit_message_text(
                chat.id,
                message_id,
                "You're now identified as: {}".format(user.first_name),
            )
        except BaseException as e:
            return dispatcher.bot.edit_message_text(chat.id, message_id, f"Error: {e}")

    else:
        user = user
    return user
