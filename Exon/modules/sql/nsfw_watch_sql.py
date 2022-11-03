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

from sqlalchemy import Column, String

from Exon.modules.sql import BASE, SESSION


class Nsfwatch(BASE):
    __tablename__ = "nsfwatch"
    chat_id = Column(String(14), primary_key=True)

    def __init__(self, chat_id):
        self.chat_id = chat_id


Nsfwatch.__table__.create(checkfirst=True)


def add_nsfwatch(chat_id: str):
    nsfws = Nsfwatch(str(chat_id))
    SESSION.add(nsfws)
    SESSION.commit()


def rmnsfwatch(chat_id: str):
    nsfwm = SESSION.query(Nsfwatch).get(str(chat_id))
    if nsfwm:
        SESSION.delete(nsfwm)
        SESSION.commit()


def get_all_nsfw_enabled_chat():
    stark = SESSION.query(Nsfwatch).all()
    SESSION.close()
    return stark


def is_nsfwatch_indb(chat_id: str):
    try:
        s__ = SESSION.query(Nsfwatch).get(str(chat_id))
        if s__:
            return str(s__.chat_id)
    finally:
        SESSION.close()
