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

from Exon.modules.no_sql import get_collection

BL = get_collection("BLACKLIST")
BL_SETTING = get_collection("BLACKLIST_SETTINGS")


CHAT_BLACKLISTS = {}
CHAT_SETTINGS_BLACKLISTS = {}


def add_to_blacklist(chat_id, trigger):
    BL.find_one_and_update(
        {"chat_id": chat_id, "trigger": trigger},
        {"$set": {"chat_id": chat_id, "trigger": trigger}},
        upsert=True,
    )
    if CHAT_BLACKLISTS.get(str(chat_id), set()) == set():
        CHAT_BLACKLISTS[str(chat_id)] = {trigger}
    else:
        CHAT_BLACKLISTS.get(str(chat_id), set()).add(trigger)


def rm_from_blacklist(chat_id, trigger) -> bool:
    data = BL.find_one_and_delete({"chat_id": chat_id, "trigger": trigger})
    if data:
        if trigger in CHAT_BLACKLISTS.get(str(chat_id), set()):
            CHAT_BLACKLISTS.get(str(chat_id), set()).remove(trigger)
        return True
    return False


def get_chat_blacklist(chat_id) -> set:
    return CHAT_BLACKLISTS.get(str(chat_id), set())


def num_blacklist_filters() -> int:
    return BL.count_documents({})


def num_blacklist_chat_filters(chat_id) -> int:
    return BL.count_documents({"chat_id": chat_id})


def num_blacklist_filter_chats() -> int:
    data = BL.distinct("chat_id")
    return len(data)


def set_blacklist_strength(chat_id, blacklist_type, value):
    """For blacklist type settings
    `blacklist_type` (int):
        - 0 = nothing
        - 1 = delete
        - 2 = warn
        - 3 = mute
        - 4 = kick
        - 5 = ban
        - 6 = tban
        - 7 = tmute.
    """
    BL_SETTING.update_one(
        {"chat_id": chat_id},
        {"$set": {"blacklist_type": int(blacklist_type), "value": str(value)}},
        upsert=True,
    )
    CHAT_SETTINGS_BLACKLISTS[str(chat_id)] = {
        "blacklist_type": int(blacklist_type),
        "value": value,
    }


def get_blacklist_setting(chat_id) -> [int, str]:
    setting = CHAT_SETTINGS_BLACKLISTS.get(str(chat_id))
    if setting:
        return setting["blacklist_type"], setting["value"]
    return 1, "0"


def __load_chat_blacklists():
    for chat in BL.find():
        CHAT_BLACKLISTS[chat["chat_id"]] = []

    for x in BL.find():
        CHAT_BLACKLISTS[x["chat_id"]] += [x["trigger"]]

    CHAT_BLACKLISTS = {str(x): set(y) for x, y in CHAT_BLACKLISTS.items()}


def __load_chat_settings_blacklists():
    for x in BL_SETTING.find():
        CHAT_SETTINGS_BLACKLISTS[x["chat_id"]] = {
            "blacklist_type": x["blacklist_type"],
            "value": x["value"],
        }


def migrate_chat(old_chat_id, new_chat_id):
    BL.update_many({"chat_id": old_chat_id}, {"$set": {"chat_id": new_chat_id}})
    __load_chat_blacklists()
    __load_chat_settings_blacklists()


__load_chat_blacklists()
__load_chat_settings_blacklists()
