from datetime import datetime
from typing import Optional, Union

from telegram import MessageEntity, Update
from telegram.ext import ContextTypes, filters
from telegram.helpers import mention_html

from Telegram import Cmd, Msg
from Telegram.database.afk_db import AfkDB
from Telegram.database.users_db import Users
from Telegram.utils.msg_types import Types, get_welcome_type, send_cmd


def till_date(date):
    """Converts date to datetime object"""
    form = "%Y-%m-%d %H:%M:%S"
    return datetime.strptime(date, form)


def get_hours(hour: str):
    """Converts time to hours, minutes and seconds"""
    tim = hour.strip().split(":")
    txt = ""
    if int(tim[0]):
        txt += f"{tim[0]} Hours "
    if int(tim[1]):
        txt += f"{tim[1]} Minutes "
    if int(round(float(tim[2]))):
        txt += f"{str(round(float(tim[2])))} Seconds"

    return txt


@Cmd(command=["afk", "brb"])
async def afkUser(update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
    """Sets you as AFK"""
    user = update.effective_user
    msg = update.effective_message

    time = str(datetime.now()).rsplit(".", 1)[0]
    reason, data_type, content = await get_welcome_type(msg)
    await AfkDB(user.id).add_afk(time, reason, data_type, content)
    reply = f"{mention_html(user.id, user.full_name)} is AFK."
    if reason:
        reply += f"\nReason: {reason}"
    await msg.reply_text(reply)


@Msg(filters.ChatType.GROUPS, group=2)
async def afk_checker(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> Union[(Optional[int], Optional[str])]:
    """Checks if user is AFK"""
    user = update.effective_user
    chat = update.effective_chat
    m = update.effective_message
    bot = context.bot
    repl = m.reply_to_message

    rep_user_id = None
    rep_user_name = None

    if m.entities and m.parse_entities(
        [MessageEntity.TEXT_MENTION, MessageEntity.MENTION],
    ):
        entities = m.parse_entities(
            [MessageEntity.TEXT_MENTION, MessageEntity.MENTION],
        )

        for ent in entities:
            if ent.type == MessageEntity.TEXT_MENTION:
                rep_user_id = ent.user.id
                rep_user_name = ent.user.first_name

            elif ent.type == MessageEntity.MENTION:
                userInfo = await Users.get_user_info(
                    m.text[ent.offset : ent.offset + ent.length]
                )
                try:
                    rep_user_id = userInfo["_id"]
                    rep_user_name = userInfo["name"]
                except KeyError:
                    return None
                if not rep_user_id:
                    return None

    elif repl and repl.from_user:
        rep_user_id = repl.from_user.id
        rep_user_name = repl.from_user.first_name

    is_afk = await AfkDB(user.id).check_afk()
    is_rep_afk = await AfkDB(rep_user_id).check_afk() if rep_user_id else False
    if is_rep_afk and rep_user_id != user:
        con = await AfkDB.get_afk(rep_user_id)
        time = till_date(con["time"])
        media = con["media"]
        media_type = con["media_type"]
        tim_ = datetime.now() - time
        tim_ = str(tim_).split(",")
        tim = get_hours(tim_[-1])
        tims = ""
        if len(tim_) == 1:
            tims = tim
        elif len(tim_) == 2:
            tims = f"{tim_[0]} {tim}"
        reason = f"{rep_user_name} is AFK.\n<b>Since:</b> {tims}"
        if con["reason"]:
            reason += f"\n<b>Reason:</b> {con['reason']}"
        txt = reason

        if media_type == Types.TEXT:
            await (await send_cmd(bot, media_type))(
                chat.id,
                txt,
                reply_to_message_id=m.id,
            )
        elif media_type in (
            Types.STICKER,
            Types.VIDEO_NOTE,
            Types.CONTACT,
            Types.ANIMATED_STICKER,
        ):
            await (await send_cmd(bot, media_type))(
                chat.id, media, reply_to_message_id=m.id
            )
        else:
            await (await send_cmd(bot, media_type))(
                chat.id, media, txt, reply_to_message_id=m.id
            )

    if is_afk:
        txt = False
        if m.text:
            txt = m.text.split(None, 1)[0]

        if txt and txt in ["!afk", "brb", "/afk"]:
            return None

        con = await AfkDB.get_afk(user.id)
        time = till_date(con["time"])
        tim_ = datetime.now() - time
        tim_ = str(tim_).split(",")
        tim = get_hours(tim_[-1])
        tims = ""
        if len(tim_) == 1:
            tims = tim
        elif len(tim_) == 2:
            tims = f"{tim_[0]} {tim}"
        txt = f"{user.mention_html()} is back online\nAFK for: {tims}"
        if con["reason"]:
            txt += f"\n<b>Reason:</b> {con['reason']}"
        await m.reply_text(txt)

        await AfkDB(user.id).remove_afk()
    return


__help__ = """
Description:
When someone mentions you in a chat, the user will be notified you are AFK. You can even provide a reason for going AFK, which will be provided to the user as well.
────────────────────────

User Commands:
• /afk: This will set you offline.
• /afk reason: This will set you offline with a reason.
• /afk replied to a sticker/photo: This will set you offline with an image or sticker.
• /afk replied to a sticker/photo reason: This will set you AFK with an image and reason both.
"""

__mod_name__ = "AFK"
__alt_name__ = ["afk", "away"]
