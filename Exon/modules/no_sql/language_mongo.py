import threading
from pymongo import MongoClient
from Exon.modules.no_sql import Asudb 

LANGS_COLLECTION = Asubd.lang

CHAT_LANG = {}
LANG_LOCK = threading.RLock()


class ChatLangs:
    @staticmethod
    @handle_error
    def set_lang(chat_id: str, lang: str) -> None:
        with LANG_LOCK:
            curr = LANGS_COLLECTION.find_one({"chat_id": str(chat_id)})
            if not curr:
                curr = {"chat_id": str(chat_id), "language": lang}
                LANGS_COLLECTION.insert_one(curr)
            else:
                LANGS_COLLECTION.update_one(
                    {"chat_id": str(chat_id)},
                    {"$set": {"language": lang}},
                )

            CHAT_LANG[str(chat_id)] = lang

    @staticmethod
    @handle_error
    def get_chat_lang(chat_id: str) -> str:
        lang = CHAT_LANG.get(str(chat_id))
        if lang is None:
            lang = "en"
        return lang

    @staticmethod
    @handle_error
    def __load_chat_language() -> None:
        global CHAT_LANG
        try:
            all_chats = LANGS_COLLECTION.find()
            CHAT_LANG = {x["chat_id"]: x["language"] for x in all_chats}
        finally:
            Asudb.close()

ChatLangs.__load_chat_language()
