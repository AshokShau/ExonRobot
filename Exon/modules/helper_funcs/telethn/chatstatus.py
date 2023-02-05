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


from telethon.tl.types import ChannelParticipantsAdmins

from Exon import DRAGONS
from Exon.modules.helper_funcs.telethn import IMMUNE_USERS, telethn


async def user_is_ban_protected(user_id: int, message):
    status = False
    if message.is_private or user_id in (IMMUNE_USERS):
        return True

    async for user in telethn.iter_participants(
        message.chat_id,
        filter=ChannelParticipantsAdmins,
    ):
        if user_id == user.id:
            status = True
            break
    return status


async def user_is_admin(user_id: int, message):
    status = False
    if message.is_private:
        return True

    async for user in telethn.iter_participants(
        message.chat_id,
        filter=ChannelParticipantsAdmins,
    ):
        if user_id == user.id or user_id in DRAGONS:
            status = True
            break
    return status


async def is_user_admin(user_id: int, chat_id):
    status = False
    async for user in telethn.iter_participants(
        chat_id,
        filter=ChannelParticipantsAdmins,
    ):
        if user_id == user.id or user_id in DRAGONS:
            status = True
            break
    return status


async def natsunagi_is_admin(chat_id: int):
    status = False
    natsunagi = await telethn.get_me()
    async for user in telethn.iter_participants(
        chat_id,
        filter=ChannelParticipantsAdmins,
    ):
        if natsunagi.id == user.id:
            status = True
            break
    return status


async def is_user_in_chat(chat_id: int, user_id: int):
    status = False
    async for user in telethn.iter_participants(chat_id):
        if user_id == user.id:
            status = True
            break
    return status


async def can_change_info(message):
    return message.chat.admin_rights.change_info if message.chat.admin_rights else False


async def can_ban_users(message):
    return message.chat.admin_rights.ban_users if message.chat.admin_rights else False


async def can_pin_messages(message):
    return (
        message.chat.admin_rights.pin_messages if message.chat.admin_rights else False
    )


async def can_invite_users(message):
    return (
        message.chat.admin_rights.invite_users if message.chat.admin_rights else False
    )


async def can_add_admins(message):
    return message.chat.admin_rights.add_admins if message.chat.admin_rights else False


async def can_delete_messages(message):
    if message.is_private:
        return True
    if message.chat.admin_rights:
        return message.chat.admin_rights.delete_messages
    return False
