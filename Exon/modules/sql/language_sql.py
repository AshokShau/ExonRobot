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

from sqlalchemy import Column, String, UnicodeText

from Exon.modules.sql import BASE, SESSION


class ChatLangs(BASE):
    __tablename__ = "chatlangs"
    chat_id = Column(String(14), primary_key=True)
    language = Column(UnicodeText)

    def __init__(self, chat_id, language):
        self.chat_id = str(chat_id)  # ensure string
        self.language = language

    def __repr__(self):
        return "Language {} chat {}".format(self.language, self.chat_id)


CHAT_LANG = {}
LANG_LOCK = threading.RLock()
ChatLangs.__table__.create(checkfirst=True)


def set_lang(chat_id: str, lang: str) -> None:
    with LANG_LOCK:
        curr = SESSION.query(ChatLangs).get(str(chat_id))
        if not curr:
            curr = ChatLangs(str(chat_id), lang)
            SESSION.add(curr)
            SESSION.flush()
        else:
            curr.language = lang

        CHAT_LANG[str(chat_id)] = lang
        SESSION.commit()


def get_chat_lang(chat_id: str) -> str:
    lang = CHAT_LANG.get(str(chat_id))
    if lang is None:
        lang = "en"
    return lang


def __load_chat_language() -> None:
    global CHAT_LANG
    try:
        allchats = SESSION.query(ChatLangs).all()
        CHAT_LANG = {x.chat_id: x.language for x in allchats}
    finally:
        SESSION.close()


__load_chat_language()
