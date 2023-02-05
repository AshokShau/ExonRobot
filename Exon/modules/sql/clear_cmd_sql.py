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

from sqlalchemy import Column, Integer, String, UnicodeText

from Exon.modules.sql import BASE, SESSION


class ClearCmd(BASE):
    __tablename__ = "clear_cmd"
    chat_id = Column(String(14), primary_key=True)
    cmd = Column(UnicodeText, primary_key=True, nullable=False)
    time = Column(Integer)

    def __init__(self, chat_id, cmd, time):
        self.chat_id = chat_id
        self.cmd = cmd
        self.time = time


ClearCmd.__table__.create(checkfirst=True)

CLEAR_CMD_LOCK = threading.RLock()


def get_allclearcmd(chat_id):
    try:
        return SESSION.query(ClearCmd).filter(ClearCmd.chat_id == str(chat_id)).all()
    finally:
        SESSION.close()


def get_clearcmd(chat_id, cmd):
    try:
        clear_cmd = SESSION.query(ClearCmd).get((str(chat_id), cmd))
        if clear_cmd:
            return clear_cmd
        return False
    finally:
        SESSION.close()


def set_clearcmd(chat_id, cmd, time):
    with CLEAR_CMD_LOCK:
        clear_cmd = SESSION.query(ClearCmd).get((str(chat_id), cmd))
        if not clear_cmd:
            clear_cmd = ClearCmd(str(chat_id), cmd, time)

        clear_cmd.time = time
        SESSION.add(clear_cmd)
        SESSION.commit()


def del_clearcmd(chat_id, cmd):
    with CLEAR_CMD_LOCK:
        del_cmd = SESSION.query(ClearCmd).get((str(chat_id), cmd))
        if del_cmd:
            SESSION.delete(del_cmd)
            SESSION.commit()
            return True
        else:
            SESSION.close()
        return False


def del_allclearcmd(chat_id):
    with CLEAR_CMD_LOCK:
        del_cmd = SESSION.query(ClearCmd).filter(ClearCmd.chat_id == str(chat_id)).all()
        if del_cmd:
            for cmd in del_cmd:
                SESSION.delete(cmd)
                SESSION.commit()
            return True
        else:
            SESSION.close()
        return False


def migrate_chat(old_chat_id, new_chat_id):
    with CLEAR_CMD_LOCK:
        chat_filters = (
            SESSION.query(ClearCmd).filter(ClearCmd.chat_id == str(old_chat_id)).all()
        )
        for filt in chat_filters:
            filt.chat_id = str(new_chat_id)
        SESSION.commit()
