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

from sqlalchemy import Column, String, UnicodeText, distinct, func

from Exon.modules.sql import BASE, SESSION


class Rules(BASE):
    __tablename__ = "rules"
    chat_id = Column(String(14), primary_key=True)
    rules = Column(UnicodeText, default="")

    def __init__(self, chat_id):
        self.chat_id = chat_id

    def __repr__(self):
        return "<Chat {} rules: {}>".format(self.chat_id, self.rules)


Rules.__table__.create(checkfirst=True)

INSERTION_LOCK = threading.RLock()


def set_rules(chat_id, rules_text):
    with INSERTION_LOCK:
        rules = SESSION.query(Rules).get(str(chat_id))
        if not rules:
            rules = Rules(str(chat_id))
        rules.rules = rules_text

        SESSION.add(rules)
        SESSION.commit()


def get_rules(chat_id):
    rules = SESSION.query(Rules).get(str(chat_id))
    ret = rules.rules if rules else ""
    SESSION.close()
    return ret


def num_chats():
    try:
        return SESSION.query(func.count(distinct(Rules.chat_id))).scalar()
    finally:
        SESSION.close()


def migrate_chat(old_chat_id, new_chat_id):
    with INSERTION_LOCK:
        chat = SESSION.query(Rules).get(str(old_chat_id))
        if chat:
            chat.chat_id = str(new_chat_id)
        SESSION.commit()
