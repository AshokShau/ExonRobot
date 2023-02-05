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

import threading
from typing import Union

from sqlalchemy import Boolean, Column, String
from sqlalchemy.sql.sqltypes import BigInteger

from Exon.modules.sql import BASE, SESSION


class ReportingUserSettings(BASE):
    __tablename__ = "user_report_settings"
    user_id = Column(BigInteger, primary_key=True)
    should_report = Column(Boolean, default=True)

    def __init__(self, user_id):
        self.user_id = user_id

    def __repr__(self):
        return "<User report settings ({})>".format(self.user_id)


class ReportingChatSettings(BASE):
    __tablename__ = "chat_report_settings"
    chat_id = Column(String(14), primary_key=True)
    should_report = Column(Boolean, default=True)

    def __init__(self, chat_id):
        self.chat_id = str(chat_id)

    def __repr__(self):
        return "<Chat report settings ({})>".format(self.chat_id)


ReportingUserSettings.__table__.create(checkfirst=True)
ReportingChatSettings.__table__.create(checkfirst=True)

CHAT_LOCK = threading.RLock()
USER_LOCK = threading.RLock()


def chat_should_report(chat_id: Union[str, int]) -> bool:
    try:
        chat_setting = SESSION.query(ReportingChatSettings).get(str(chat_id))
        if chat_setting:
            return chat_setting.should_report
        return False
    finally:
        SESSION.close()


def user_should_report(user_id: int) -> bool:
    try:
        user_setting = SESSION.query(ReportingUserSettings).get(user_id)
        if user_setting:
            return user_setting.should_report
        return True
    finally:
        SESSION.close()


def set_chat_setting(chat_id: Union[int, str], setting: bool):
    with CHAT_LOCK:
        chat_setting = SESSION.query(ReportingChatSettings).get(str(chat_id))
        if not chat_setting:
            chat_setting = ReportingChatSettings(chat_id)

        chat_setting.should_report = setting
        SESSION.add(chat_setting)
        SESSION.commit()


def set_user_setting(user_id: int, setting: bool):
    with USER_LOCK:
        user_setting = SESSION.query(ReportingUserSettings).get(user_id)
        if not user_setting:
            user_setting = ReportingUserSettings(user_id)

        user_setting.should_report = setting
        SESSION.add(user_setting)
        SESSION.commit()


def migrate_chat(old_chat_id, new_chat_id):
    with CHAT_LOCK:
        chat_notes = (
            SESSION.query(ReportingChatSettings)
            .filter(ReportingChatSettings.chat_id == str(old_chat_id))
            .all()
        )
        for note in chat_notes:
            note.chat_id = str(new_chat_id)
        SESSION.commit()
