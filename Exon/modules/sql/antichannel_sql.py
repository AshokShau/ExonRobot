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

from sqlalchemy import Boolean, Column
from sqlalchemy.sql.sqltypes import String

from Exon.modules.sql import BASE, SESSION


class AntiChannelSettings(BASE):
    __tablename__ = "anti_channel_settings"

    chat_id = Column(String(14), primary_key=True)
    setting = Column(Boolean, default=False, nullable=False)

    def __init__(self, chat_id: int, disabled: bool):
        self.chat_id = str(chat_id)
        self.setting = disabled

    def __repr__(self):
        return "<ᴀɴᴛɪғʟᴏᴏᴅ sᴇᴛᴛɪɴɢ {} ({})>".format(self.chat_id, self.setting)


AntiChannelSettings.__table__.create(checkfirst=True)
ANTICHANNEL_SETTING_LOCK = threading.RLock()


def enable_antichannel(chat_id: int):
    with ANTICHANNEL_SETTING_LOCK:
        chat = SESSION.query(AntiChannelSettings).get(str(chat_id))
        if not chat:
            chat = AntiChannelSettings(str(chat_id), True)

        chat.setting = True
        SESSION.add(chat)
        SESSION.commit()


def disable_antichannel(chat_id: int):
    with ANTICHANNEL_SETTING_LOCK:
        chat = SESSION.query(AntiChannelSettings).get(str(chat_id))
        if not chat:
            chat = AntiChannelSettings(str(chat_id), False)

        chat.setting = False
        SESSION.add(chat)
        SESSION.commit()


def antichannel_status(chat_id: int) -> bool:
    with ANTICHANNEL_SETTING_LOCK:
        d = SESSION.query(AntiChannelSettings).get(str(chat_id))
        if not d:
            return False
        return d.setting


def migrate_chat(old_chat_id, new_chat_id):
    with ANTICHANNEL_SETTING_LOCK:
        chat = SESSION.query(AntiChannelSettings).get(str(old_chat_id))
        if chat:
            chat.chat_id = new_chat_id
            SESSION.add(chat)

        SESSION.commit()
