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

from sqlalchemy import Boolean, Column, Integer, String, UnicodeText, distinct, func

from Exon.modules.helper_funcs.msg_types import Types
from Exon.modules.sql import BASE, SESSION


class Notes(BASE):
    __tablename__ = "notes"
    chat_id = Column(String(14), primary_key=True)
    name = Column(UnicodeText, primary_key=True)
    value = Column(UnicodeText, nullable=False)
    file = Column(UnicodeText)
    is_reply = Column(Boolean, default=False)
    has_buttons = Column(Boolean, default=False)
    msgtype = Column(Integer, default=Types.BUTTON_TEXT.value)

    def __init__(self, chat_id, name, value, msgtype, file=None):
        self.chat_id = str(chat_id)  # ensure string
        self.name = name
        self.value = value
        self.msgtype = msgtype
        self.file = file

    def __repr__(self):
        return "<Note %s>" % self.name


class Buttons(BASE):
    __tablename__ = "note_urls"
    id = Column(Integer, primary_key=True, autoincrement=True)
    chat_id = Column(String(14), primary_key=True)
    note_name = Column(UnicodeText, primary_key=True)
    name = Column(UnicodeText, nullable=False)
    url = Column(UnicodeText, nullable=False)
    same_line = Column(Boolean, default=False)

    def __init__(self, chat_id, note_name, name, url, same_line=False):
        self.chat_id = str(chat_id)
        self.note_name = note_name
        self.name = name
        self.url = url
        self.same_line = same_line


Notes.__table__.create(checkfirst=True)
Buttons.__table__.create(checkfirst=True)

NOTES_INSERTION_LOCK = threading.RLock()
BUTTONS_INSERTION_LOCK = threading.RLock()


def add_note_to_db(chat_id, note_name, note_data, msgtype, buttons=None, file=None):
    if not buttons:
        buttons = []

    with NOTES_INSERTION_LOCK:
        prev = SESSION.query(Notes).get((str(chat_id), note_name))
        if prev:
            with BUTTONS_INSERTION_LOCK:
                prev_buttons = (
                    SESSION.query(Buttons)
                    .filter(
                        Buttons.chat_id == str(chat_id),
                        Buttons.note_name == note_name,
                    )
                    .all()
                )
                for btn in prev_buttons:
                    SESSION.delete(btn)
            SESSION.delete(prev)
        note = Notes(
            str(chat_id),
            note_name,
            note_data or "",
            msgtype=msgtype.value,
            file=file,
        )
        SESSION.add(note)
        SESSION.commit()

    for b_name, url, same_line in buttons:
        add_note_button_to_db(chat_id, note_name, b_name, url, same_line)


def get_note(chat_id, note_name):
    try:
        return (
            SESSION.query(Notes)
            .filter(func.lower(Notes.name) == note_name, Notes.chat_id == str(chat_id))
            .first()
        )
    finally:
        SESSION.close()


def rm_note(chat_id, note_name):
    with NOTES_INSERTION_LOCK:
        note = (
            SESSION.query(Notes)
            .filter(func.lower(Notes.name) == note_name, Notes.chat_id == str(chat_id))
            .first()
        )
        if note:
            with BUTTONS_INSERTION_LOCK:
                buttons = (
                    SESSION.query(Buttons)
                    .filter(
                        Buttons.chat_id == str(chat_id),
                        Buttons.note_name == note_name,
                    )
                    .all()
                )
                for btn in buttons:
                    SESSION.delete(btn)

            SESSION.delete(note)
            SESSION.commit()
            return True
        SESSION.close()
        return False


def get_all_chat_notes(chat_id):
    try:
        return (
            SESSION.query(Notes)
            .filter(Notes.chat_id == str(chat_id))
            .order_by(Notes.name.asc())
            .all()
        )
    finally:
        SESSION.close()


def add_note_button_to_db(chat_id, note_name, b_name, url, same_line):
    with BUTTONS_INSERTION_LOCK:
        button = Buttons(chat_id, note_name, b_name, url, same_line)
        SESSION.add(button)
        SESSION.commit()


def get_buttons(chat_id, note_name):
    try:
        return (
            SESSION.query(Buttons)
            .filter(Buttons.chat_id == str(chat_id), Buttons.note_name == note_name)
            .order_by(Buttons.id)
            .all()
        )
    finally:
        SESSION.close()


def num_notes():
    try:
        return SESSION.query(Notes).count()
    finally:
        SESSION.close()


def num_chats():
    try:
        return SESSION.query(func.count(distinct(Notes.chat_id))).scalar()
    finally:
        SESSION.close()


def migrate_chat(old_chat_id, new_chat_id):
    with NOTES_INSERTION_LOCK:
        chat_notes = (
            SESSION.query(Notes).filter(Notes.chat_id == str(old_chat_id)).all()
        )
        for note in chat_notes:
            note.chat_id = str(new_chat_id)

        with BUTTONS_INSERTION_LOCK:
            chat_buttons = (
                SESSION.query(Buttons).filter(Buttons.chat_id == str(old_chat_id)).all()
            )
            for btn in chat_buttons:
                btn.chat_id = str(new_chat_id)

        SESSION.commit()
