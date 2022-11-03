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

from sqlalchemy import BigInteger, Boolean, Column, String

from Exon.modules.sql import BASE, SESSION


class SPinSettings(BASE):
    __tablename__ = "pin_settings"

    chat_id = Column(String(14), primary_key=True)
    message_id = Column(BigInteger)
    suacpmo = Column(Boolean, default=False)
    scldpmo = Column(Boolean, default=False)

    def __init__(self, chat_id, message_id):
        self.chat_id = str(chat_id)
        self.message_id = message_id

    def __repr__(self):
        return "<ᴘɪɴ sᴇᴛᴛɪɴɢs ғᴏʀ {} ɪɴ {}>".format(self.chat_id, self.message_id)


SPinSettings.__table__.create(checkfirst=True)

PIN_INSERTION_LOCK = threading.RLock()


def add_mid(chat_id, message_id):
    with PIN_INSERTION_LOCK:
        chat = SESSION.query(SPinSettings).get(str(chat_id))
        if not chat:
            chat = SPinSettings(str(chat_id), message_id)
        SESSION.add(chat)
        SESSION.commit()
        SESSION.close()


def remove_mid(chat_id):
    with PIN_INSERTION_LOCK:
        chat = SESSION.query(SPinSettings).get(str(chat_id))
        if chat:
            SESSION.delete(chat)
            SESSION.commit()
        SESSION.close()


def add_acp_o(chat_id, setting):
    with PIN_INSERTION_LOCK:
        chat = SESSION.query(SPinSettings).get(str(chat_id))
        if not chat:
            chat = SPinSettings(str(chat_id), 0)
        chat.suacpmo = setting
        SESSION.add(chat)
        SESSION.commit()
        SESSION.close()


def add_ldp_m(chat_id, setting):
    with PIN_INSERTION_LOCK:
        chat = SESSION.query(SPinSettings).get(str(chat_id))
        if not chat:
            chat = SPinSettings(str(chat_id), 0)
        chat.scldpmo = setting
        SESSION.add(chat)
        SESSION.commit()
        SESSION.close()


def get_current_settings(chat_id):
    with PIN_INSERTION_LOCK:
        chat = SESSION.query(SPinSettings).get(str(chat_id))
        return chat
