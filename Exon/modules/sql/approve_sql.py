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

from sqlalchemy import Column, String
from sqlalchemy.sql.sqltypes import BigInteger

from Exon.modules.sql import BASE, SESSION


class Approvals(BASE):
    __tablename__ = "approval"
    chat_id = Column(String(14), primary_key=True)
    user_id = Column(BigInteger, primary_key=True)

    def __init__(self, chat_id, user_id):
        self.chat_id = str(chat_id)  # ensure string
        self.user_id = user_id

    def __repr__(self):
        return "<Approve %s>" % self.user_id


Approvals.__table__.create(checkfirst=True)

APPROVE_INSERTION_LOCK = threading.RLock()


def approve(chat_id, user_id):
    with APPROVE_INSERTION_LOCK:
        approve_user = Approvals(str(chat_id), user_id)
        SESSION.add(approve_user)
        SESSION.commit()


def is_approved(chat_id, user_id):
    try:
        return SESSION.query(Approvals).get((str(chat_id), user_id))
    finally:
        SESSION.close()


def disapprove(chat_id, user_id):
    with APPROVE_INSERTION_LOCK:
        disapprove_user = SESSION.query(Approvals).get((str(chat_id), user_id))
        if disapprove_user:
            SESSION.delete(disapprove_user)
            SESSION.commit()
            return True
        SESSION.close()
        return False


def list_approved(chat_id):
    try:
        return (
            SESSION.query(Approvals)
            .filter(Approvals.chat_id == str(chat_id))
            .order_by(Approvals.user_id.asc())
            .all()
        )
    finally:
        SESSION.close()
