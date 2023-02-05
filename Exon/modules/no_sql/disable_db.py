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

DISABLED_COMMANDS = get_collection("DISABLED_COMMANDS")

DISABLED = {}


def disable_command(chat_id, disable) -> bool:
    data = DISABLED_COMMANDS.find_one({"chat_id": chat_id, "command": disable})
    if not data:
        DISABLED.setdefault(str(chat_id), set()).add(disable)

        DISABLED_COMMANDS.insert_one({"chat_id": chat_id, "command": disable})
        return True
    return False


def enable_command(chat_id, enable) -> bool:
    data = DISABLED_COMMANDS.find_one({"chat_id": chat_id, "command": enable})
    if data:
        if enable in DISABLED.get(str(chat_id)):  # sanity check
            DISABLED.setdefault(str(chat_id), set()).remove(enable)

        DISABLED_COMMANDS.delete_one({"chat_id": chat_id, "command": enable})
        return True
    return False


def is_command_disabled(chat_id, cmd) -> bool:
    return cmd in DISABLED.get(str(chat_id), set())


def get_all_disabled(chat_id) -> dict:
    return DISABLED.get(str(chat_id), set())


def num_chats() -> int:
    chats = DISABLED_COMMANDS.distinct("chat_id")
    return len(chats)


def num_disabled() -> int:
    return DISABLED_COMMANDS.count_documents({})


def migrate_chat(old_chat_id, new_chat_id) -> None:
    DISABLED_COMMANDS.update_many(
        {"chat_id": old_chat_id}, {"$set": {"chat_id": new_chat_id}}
    )

    if str(old_chat_id) in DISABLED:
        DISABLED[str(old_chat_id)] = DISABLED.get(str(old_chat_id), set())


def __load_disabled_commands() -> None:
    all_chats = DISABLED_COMMANDS.find()
    for chat in all_chats:
        DISABLED.setdefault(chat["chat_id"], set()).add(chat["command"])


__load_disabled_commands()
