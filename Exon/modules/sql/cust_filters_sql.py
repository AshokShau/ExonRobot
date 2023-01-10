import threading

from sqlalchemy import Boolean, Column, Integer, String, UnicodeText, distinct, func

from Exon.modules.helper_funcs.msg_types import Types
from Exon.modules.sql import BASE, SESSION


class CustomFilters(BASE):
    __tablename__ = "cust_filters"
    chat_id = Column(String(14), primary_key=True)
    keyword = Column(UnicodeText, primary_key=True, nullable=False)
    reply = Column(UnicodeText, nullable=False)
    reply_text = Column(UnicodeText)
    file_type = Column(Integer, nullable=False, default=1)
    file_id = Column(UnicodeText, default=None)
    has_buttons = Column(Boolean, nullable=False, default=False)

    has_media_spoiler = Column(Boolean, nullable=False, default=False)

    def __init__(
        self,
        chat_id: int | str,
        keyword: str,
        reply: str,
        reply_text: str,
        has_buttons: bool,
        has_media_spoiler: bool,
        file_type: int,
        file_id: str,
    ):
        self.chat_id = str(chat_id)  # ensure string
        self.keyword = keyword
        self.reply = reply
        self.reply_text = reply_text
        self.has_buttons = has_buttons
        self.has_media_spoiler = has_media_spoiler
        self.file_type = file_type
        self.file_id = file_id

    def __repr__(self):
        return "<Filter for %s>" % self.chat_id

    def __eq__(self, other):
        return bool(
            isinstance(other, CustomFilters)
            and self.chat_id == other.chat_id
            and self.keyword == other.keyword,
        )


class Buttons(BASE):
    __tablename__ = "cust_filter_urls"
    id = Column(Integer, primary_key=True, autoincrement=True)
    chat_id = Column(String(14), primary_key=True)
    keyword = Column(UnicodeText, primary_key=True)
    name = Column(UnicodeText, nullable=False)
    url = Column(UnicodeText, nullable=False)
    same_line = Column(Boolean, default=False)

    def __init__(self, chat_id, keyword, name, url, same_line=False):
        self.chat_id = str(chat_id)
        self.keyword = keyword
        self.name = name
        self.url = url
        self.same_line = same_line


CustomFilters.__table__.create(checkfirst=True)
Buttons.__table__.create(checkfirst=True)

CUST_FILT_LOCK = threading.RLock()
BUTTON_LOCK = threading.RLock()
CHAT_FILTERS = {}


def get_all_filters():
    try:
        return SESSION.query(CustomFilters).all()
    finally:
        SESSION.close()


def new_add_filter(
    chat_id, keyword, reply_text, file_type, file_id, buttons, media_spoiler
):
    global CHAT_FILTERS

    if buttons is None:
        buttons = []

    with CUST_FILT_LOCK:
        prev = SESSION.query(CustomFilters).get((str(chat_id), keyword))
        if prev:
            with BUTTON_LOCK:
                prev_buttons = (
                    SESSION.query(Buttons)
                    .filter(Buttons.chat_id == str(chat_id), Buttons.keyword == keyword)
                    .all()
                )
                for btn in prev_buttons:
                    SESSION.delete(btn)
            SESSION.delete(prev)

        filt = CustomFilters(
            str(chat_id),
            keyword,
            reply="there is should be a new reply",
            has_buttons=bool(buttons),
            has_media_spoiler=media_spoiler,
            reply_text=reply_text,
            file_type=file_type.value,
            file_id=file_id,
        )

        if keyword not in CHAT_FILTERS.get(str(chat_id), []):
            CHAT_FILTERS[str(chat_id)] = sorted(
                CHAT_FILTERS.get(str(chat_id), []) + [keyword],
                key=lambda x: (-len(x), x),
            )

        SESSION.add(filt)
        SESSION.commit()

    for b_name, url, same_line in buttons:
        add_note_button_to_db(chat_id, keyword, b_name, url, same_line)


def remove_filter(chat_id, keyword):
    global CHAT_FILTERS
    with CUST_FILT_LOCK:
        filt = SESSION.query(CustomFilters).get((str(chat_id), keyword))
        if filt:
            if keyword in CHAT_FILTERS.get(str(chat_id), []):  # Sanity check
                CHAT_FILTERS.get(str(chat_id), []).remove(keyword)

            with BUTTON_LOCK:
                prev_buttons = (
                    SESSION.query(Buttons)
                    .filter(Buttons.chat_id == str(chat_id), Buttons.keyword == keyword)
                    .all()
                )
                for btn in prev_buttons:
                    SESSION.delete(btn)

            SESSION.delete(filt)
            SESSION.commit()
            return True

        SESSION.close()
        return False


def get_chat_triggers(chat_id):
    return CHAT_FILTERS.get(str(chat_id), set())


def get_chat_filters(chat_id):
    try:
        return (
            SESSION.query(CustomFilters)
            .filter(CustomFilters.chat_id == str(chat_id))
            .order_by(func.length(CustomFilters.keyword).desc())
            .order_by(CustomFilters.keyword.asc())
            .all()
        )
    finally:
        SESSION.close()


def get_filter(chat_id, keyword) -> CustomFilters:
    try:
        return SESSION.query(CustomFilters).get((str(chat_id), keyword))
    finally:
        SESSION.close()


def add_note_button_to_db(chat_id, keyword, b_name, url, same_line):
    with BUTTON_LOCK:
        button = Buttons(chat_id, keyword, b_name, url, same_line)
        SESSION.add(button)
        SESSION.commit()


def get_buttons(chat_id, keyword):
    try:
        return (
            SESSION.query(Buttons)
            .filter(Buttons.chat_id == str(chat_id), Buttons.keyword == keyword)
            .order_by(Buttons.id)
            .all()
        )
    finally:
        SESSION.close()


def num_filters():
    try:
        return SESSION.query(CustomFilters).count()
    finally:
        SESSION.close()


def num_chats():
    try:
        return SESSION.query(func.count(distinct(CustomFilters.chat_id))).scalar()
    finally:
        SESSION.close()


def __load_chat_filters():
    global CHAT_FILTERS
    try:
        chats = SESSION.query(CustomFilters.chat_id).distinct().all()
        for (chat_id,) in chats:  # remove tuple by ( ,)
            CHAT_FILTERS[chat_id] = []

        all_filters = SESSION.query(CustomFilters).all()
        for x in all_filters:
            CHAT_FILTERS[x.chat_id] += [x.keyword]

        CHAT_FILTERS = {
            x: sorted(set(y), key=lambda i: (-len(i), i))
            for x, y in CHAT_FILTERS.items()
        }

    finally:
        SESSION.close()


# ONLY USE FOR MIGRATE OLD FILTERS TO NEW FILTERS
def __migrate_filters():
    try:
        all_filters = SESSION.query(CustomFilters).distinct().all()
        for x in all_filters:
            if x.is_document:
                file_type = Types.DOCUMENT
            elif x.is_image:
                file_type = Types.PHOTO
            elif x.is_video:
                file_type = Types.VIDEO
            elif x.is_sticker:
                file_type = Types.STICKER
            elif x.is_audio:
                file_type = Types.AUDIO
            elif x.is_voice:
                file_type = Types.VOICE
            else:
                file_type = Types.TEXT

            if file_type == Types.TEXT:
                filt = CustomFilters(
                    str(x.chat_id),
                    x.keyword,
                    x.reply,
                    file_type.value,
                    None,
                )
            else:
                filt = CustomFilters(
                    str(x.chat_id),
                    x.keyword,
                    None,
                    file_type.value,
                    x.reply,
                )

            SESSION.add(filt)
            SESSION.commit()

    finally:
        SESSION.close()


def migrate_chat(old_chat_id, new_chat_id):
    with CUST_FILT_LOCK:
        chat_filters = (
            SESSION.query(CustomFilters)
            .filter(CustomFilters.chat_id == str(old_chat_id))
            .all()
        )
        for filt in chat_filters:
            filt.chat_id = str(new_chat_id)
        SESSION.commit()
        old_filt = CHAT_FILTERS.get(str(old_chat_id))
        if old_filt:
            CHAT_FILTERS[str(new_chat_id)] = old_filt
            del CHAT_FILTERS[str(old_chat_id)]

        with BUTTON_LOCK:
            chat_buttons = (
                SESSION.query(Buttons).filter(Buttons.chat_id == str(old_chat_id)).all()
            )
            for btn in chat_buttons:
                btn.chat_id = str(new_chat_id)
            SESSION.commit()


__load_chat_filters()
