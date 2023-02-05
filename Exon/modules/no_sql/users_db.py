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
# TG :- @Abishnoi
#     TG  :- Abishnoi_bots
#     GITHUB :- Abishnoi69 ""

"""Users Database."""

from Exon import dispatcher
from Exon.modules.no_sql import get_collection

USERS_DB = get_collection("USERS")
CHATS_DB = get_collection("CHATS")
CHAT_MEMBERS_DB = get_collection("CHAT_MEMBERS")


def ensure_bot_in_db():
    USERS_DB.update_one(
        {"_id": dispatcher.bot.id},
        {"$set": {"username": dispatcher.bot.username}},
        upsert=True,
    )


def update_user(user_id, username, chat_id=None, chat_name=None):
    USERS_DB.update_one({"_id": user_id}, {"$set": {"username": username}}, upsert=True)

    if not (chat_id or chat_name):
        return

    CHATS_DB.update_one(
        {"chat_id": chat_id}, {"$set": {"chat_name": chat_name}}, upsert=True
    )

    member = CHAT_MEMBERS_DB.find_one({"chat_id": chat_id, "user_id": user_id})
    if member is None:
        CHAT_MEMBERS_DB.insert_one({"chat_id": chat_id, "user_id": user_id})


def get_userid_by_name(username) -> dict:
    return list(USERS_DB.find({"username": username}))


def get_name_by_userid(user_id) -> dict:
    return list(USERS_DB.find_one({"_id": user_id}))


def get_chat_members(chat_id) -> list:
    return list(CHAT_MEMBERS_DB.find({"chat_id": chat_id}))


def get_all_chats() -> list:
    return list(CHATS_DB.find())


def get_all_users() -> list:
    return list(USERS_DB.find())


def get_user_num_chats(user_id) -> int:
    return CHAT_MEMBERS_DB.count_documents({"user_id": user_id})


def get_user_com_chats(user_id) -> int:
    return list(CHAT_MEMBERS_DB.find({"user_id": user_id}))


def num_chats() -> int:
    return CHATS_DB.count_documents({})


def num_users() -> int:
    return USERS_DB.count_documents({})


def rem_chat(chat_id) -> None:
    CHATS_DB.delete_one({"chat_id": chat_id})


def migrate_chat(old_chat_id, new_chat_id) -> None:
    CHATS_DB.update_one({"chat_id": old_chat_id}, {"$set": {"chat_id": new_chat_id}})

    chat_members = CHAT_MEMBERS_DB.find({"chat_id": old_chat_id})
    for member in chat_members:
        CHAT_MEMBERS_DB.update_one(
            {"chat_id": member["chat_id"]}, {"$set": {"chat_id": new_chat_id}}
        )


ensure_bot_in_db()
