"""
MIT License

Copyright (c) 2022 Aʙɪsʜɴᴏɪ

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

import threading
import time

from sqlalchemy import Column, Integer, String, UnicodeText
from sqlalchemy.sql.sqltypes import BigInteger

from Exon.modules.sql import BASE, SESSION


class Reminds(BASE):
    __tablename__ = "reminds"
    chat_id = Column(String(14), primary_key=True)
    time_seconds = Column(Integer, primary_key=True)
    remind_message = Column(UnicodeText, default="")
    user_id = Column(BigInteger, default=0)

    def __init__(self, chat_id, time_seconds):
        self.chat_id = str(chat_id)
        self.time_seconds = int(time_seconds)

    def __repr__(self):
        return "<ʀᴇᴍɪɴᴅ ɪɴ {} ғᴏʀ ᴛɪᴍᴇ {}>".format(
            self.chat_id,
            self.time_seconds,
        )


# Reminds.__table__.drop()
Reminds.__table__.create(checkfirst=True)

INSERTION_LOCK = threading.RLock()

REMINDERS = {}


def set_remind(chat_id, time_sec, remind_message, user_id):
    with INSERTION_LOCK:
        reminds = SESSION.query(Reminds).get((str(chat_id), time_sec))
        if not reminds:
            reminds = Reminds(chat_id, time_sec)
        reminds.remind_message = remind_message
        reminds.user_id = user_id
        SESSION.add(reminds)
        SESSION.commit()
        if not time_sec in REMINDERS:
            REMINDERS[time_sec] = []
        REMINDERS[time_sec].append(
            {"chat_id": str(chat_id), "message": remind_message, "user_id": user_id}
        )


def rem_remind(chat_id, time_sec, remind_message, user_id):
    with INSERTION_LOCK:
        reminds = SESSION.query(Reminds).get((str(chat_id), time_sec))
        if reminds:
            SESSION.delete(reminds)
            SESSION.commit()
            REMINDERS[time_sec].remove(
                {"chat_id": str(chat_id), "message": remind_message, "user_id": user_id}
            )
            return True
        SESSION.close()
        return False


def get_remind_in_chat(chat_id, timestamp):
    return (
        SESSION.query(Reminds)
        .filter(Reminds.chat_id == str(chat_id), Reminds.time_seconds == timestamp)
        .first()
    )


def num_reminds_in_chat(chat_id):
    return SESSION.query(Reminds).filter(Reminds.chat_id == str(chat_id)).count()


def get_reminds_in_chat(chat_id):
    try:
        return (
            SESSION.query(Reminds)
            .filter(Reminds.chat_id == str(chat_id))
            .order_by(Reminds.time_seconds.asc())
            .all()
        )
    finally:
        SESSION.close()


def __get_all_reminds():
    try:
        chats = SESSION.query(Reminds).all()
        for chat in chats:
            if (chat.time_seconds <= round(time.time())) or chat.user_id == 0:
                try:
                    rem_remind(
                        chat.chat_id,
                        chat.time_seconds,
                        chat.remind_message,
                        chat.user_id,
                    )
                except:
                    pass
                continue
            REMINDERS[chat.time_seconds] = [
                {
                    "chat_id": chat.chat_id,
                    "message": chat.remind_message,
                    "user_id": chat.user_id,
                }
            ]
    finally:
        SESSION.close()


__get_all_reminds()
