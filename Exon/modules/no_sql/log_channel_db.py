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

LOG_DATA = get_collection("LOG_CHANNELS")

CHANNELS = {}


def set_chat_log_channel(chat_id, log_channel):
    LOG_DATA.update_one(
        {"chat_id": chat_id}, {"$set": {"log_channel": log_channel}}, upsert=True
    )
    CHANNELS[str(chat_id)] = log_channel


def get_chat_log_channel(chat_id) -> int:
    return CHANNELS.get(str(chat_id))


def stop_chat_logging(chat_id) -> int:
    res = LOG_DATA.find_one_and_delete({"chat_id": chat_id})
    if str(chat_id) in CHANNELS:
        del CHANNELS[str(chat_id)]
    return res["log_channel"]


def num_logchannels() -> int:
    return LOG_DATA.count_documents({})


def migrate_chat(old_chat_id, new_chat_id):
    LOG_DATA.update_one({"chat_id": old_chat_id}, {"$set": {"chat_id": new_chat_id}})
    if str(old_chat_id) in CHANNELS:
        CHANNELS[str(new_chat_id)] = CHANNELS.get(str(old_chat_id))


def __load_log_channels():
    global CHANNELS
    CHANNELS = {
        str(chat["chat_id"]): str(chat["log_channel"]) for chat in LOG_DATA.find()
    }


__load_log_channels()
