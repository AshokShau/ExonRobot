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

from sqlalchemy import Column, String

from Exon.modules.sql import BASE, SESSION


class Nightmode(BASE):
    __tablename__ = "nightmode"
    chat_id = Column(String(14), primary_key=True)

    def __init__(self, chat_id):
        self.chat_id = chat_id


Nightmode.__table__.create(checkfirst=True)


def add_nightmode(chat_id: str):
    nightmoddy = Nightmode(str(chat_id))
    SESSION.add(nightmoddy)
    SESSION.commit()


def rmnightmode(chat_id: str):
    rmnightmoddy = SESSION.query(Nightmode).get(str(chat_id))
    if rmnightmoddy:
        SESSION.delete(rmnightmoddy)
        SESSION.commit()


def get_all_chat_id():
    stark = SESSION.query(Nightmode).all()
    SESSION.close()
    return stark


def is_nightmode_indb(chat_id: str):
    try:
        s__ = SESSION.query(Nightmode).get(str(chat_id))
        if s__:
            return str(s__.chat_id)
    finally:
        SESSION.close()
