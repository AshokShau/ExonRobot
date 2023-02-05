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
from sqlalchemy import Column, Numeric, String

from Exon.modules.sql import BASE, SESSION


class forceSubscribe(BASE):
    __tablename__ = "forceSubscribe"
    chat_id = Column(Numeric, primary_key=True)
    channel = Column(String)

    def __init__(self, chat_id, channel):
        self.chat_id = chat_id
        self.channel = channel


forceSubscribe.__table__.create(checkfirst=True)


def fs_settings(chat_id):
    try:
        return (
            SESSION.query(forceSubscribe)
            .filter(forceSubscribe.chat_id == chat_id)
            .one()
        )
    except:
        return None
    finally:
        SESSION.close()


def add_channel(chat_id, channel):
    adder = SESSION.query(forceSubscribe).get(chat_id)
    if adder:
        adder.channel = channel
    else:
        adder = forceSubscribe(chat_id, channel)
    SESSION.add(adder)
    SESSION.commit()


def disapprove(chat_id):
    rem = SESSION.query(forceSubscribe).get(chat_id)
    if rem:
        SESSION.delete(rem)
        SESSION.commit()
