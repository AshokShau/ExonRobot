import asyncio
import base64
import io
import random
from functools import wraps

import telethon
from requests import exceptions, get, post
from telethon import Button, types
from webcolors import hex_to_name, name_to_hex

from Exon import DRAGONS as AUTH
from Exon import OWNER_ID
from Exon import db as qdb
from Exon import telethn as bot

# ʙʏ @Abishnoi1M
# ==============================================
# ǫᴜᴏᴛʟʏ ᴅᴀᴛᴀʙᴀsᴇ
quotly = qdb.get_collection("quotly")


def set_qrate(chat_id, mode: bool):
    quotly.update_one({"chat_id": chat_id}, {"$set": {"qrate": mode}}, upsert=True)


def get_qrate(chat_id):
    q = quotly.find_one({"chat_id": chat_id})
    if q:
        return q.get("qrate") or False
    return False


def add_quote(chat_id, quote):
    quotly.update_one({"chat_id": chat_id}, {"$push": {"quotes": quote}}, upsert=True)


def get_quotes(chat_id):
    q = quotly.find_one({"chat_id": chat_id})
    if q:
        return q["quotes"]
    return False


# =====================================) =))) ========


# ============+==+=============+=++============

ERRORS = []


def command(**args):
    args["pattern"] = "^(?i)[?/!]" + args["pattern"] + "(?: |$|asu)(.*)"

    def decorator(func):
        async def wrapper(ev):
            try:
                await func(ev)
            except Exception as e:
                ERRORS.append(e)
                await ev.reply(str(e))

        bot.add_event_handler(wrapper, telethon.events.NewMessage(**args))
        return func

    return decorator


def InlineQuery(**args):
    def decorator(func):
        async def wrapper(ev):
            try:
                await func(ev)
            except Exception as e:
                ERRORS.append(e)

        bot.add_event_handler(wrapper, telethon.events.InlineQuery(**args))
        return func

    return decorator


def Callback(**args):
    def decorator(func):
        async def wrapper(ev):
            try:
                await func(ev)
            except Exception as e:
                ERRORS.append(e)
                await ev.answer(str(e), alert=True)

        bot.add_event_handler(func, telethon.events.CallbackQuery(**args))
        return func

    return decorator


def auth(func):
    @wraps(func)
    async def sed(e):
        if e.sender_id and (e.sender_id in AUTH or e.sender_id == OWNER_ID):
            await func(e)
        else:
            await e.reply("ʏᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴀᴜᴛʜᴏʀɪᴢᴇᴅ ᴛᴏ ᴜsᴇ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ")

    return sed


def master(func):
    @wraps(func)
    async def sed(e):
        if e.sender_id == OWNER_ID:
            await func(e)
        else:
            await e.reply("ʏᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴀᴜᴛʜᴏʀɪᴢᴇᴅ ᴛᴏ ᴜsᴇ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ :sᴇᴅ")

    return sed


async def get_user(e: telethon.events.NewMessage.Event):
    user: telethon.tl.types.User
    arg = ""
    Args = e.text.split(maxsplit=2)
    if e.is_reply:
        user = (await e.get_reply_message()).sender
        arg = (Args[1] + (Args[2] if len(Args) > 2 else "")) if len(Args) > 1 else ""
    else:
        if len(Args) == 1:
            await e.reply("ɴᴏ ᴜsᴇʀ sᴘᴇᴄɪғɪᴇᴅ")
            return None, ""
        try:
            user = await e.client.get_entity(Args[1])
        except BaseException as ex:
            await e.reply(str(ex))
            return
        arg = Args[2] if len(Args) > 2 else ""
    return user, arg


async def HasRight(chat_id, user_id, right):
    if user_id == OWNER_ID:
        return True
    if user_id in AUTH:
        return True
    p = await bot(
        telethon.tl.functions.channels.GetParticipantRequest(chat_id, user_id)
    )
    p: telethon.tl.types.ChannelParticipant.to_dict
    if p.participant.admin_rights.to_dict()[right] == True:
        return True
    return False


async def getSender(e: telethon.events.NewMessage.Event):
    if e.sender != None:
        return e.sender
    else:
        if e.sender_chat != None:
            return e.sender_chat
        else:
            return None


def sizeof_fmt(num, suffix="B"):
    for unit in ["", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"]:
        if abs(num) < 1024.0:
            return f"{num:3.1f}{unit}{suffix}"
        num /= 1024.0
    return f"{num:.1f}Yi{suffix}"


# @Abishnoi1M
async def bash(code):
    cmd = code.split(" ")
    process = await asyncio.create_subprocess_exec(
        *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate()
    result = str(stdout.decode().strip()) + str(stderr.decode().strip())
    return result


async def get_reply_image(v):
    if not v.reply_to:
        return None
    r = await v.get_reply_message()
    if not r.media:
        return None
    if isinstance(r.media, telethon.tl.types.MessageMediaDocument):
        if r.media.document.mime_type.split("/")[0] == "image":
            return r
        else:
            return None
    elif isinstance(r.media, telethon.tl.types.MessageMediaPhoto):
        return r
    else:
        return None


async def get_reply_gif(e):
    r = await e.get_reply_message()
    if not r.gif:
        return None
    return r


async def get_reply_video(e):
    r = await e.get_reply_message()
    if not r.video:
        return None
    return r


# ) =======================================++=+====)) ============


REDIRECT_THUMB = "https://img.icons8.com/external-flaticons-lineal-color-flat-icons/64/undefined/external-redirect-internet-marketing-flaticons-lineal-color-flat-icons-2.png"


async def answer_query(
    e: telethon.events.InlineQuery.Event, title, text, desc, thumb, buttons
):
    builder = e.builder
    result = builder.article(title=title, text=text, description=desc, buttons=buttons)
    await e.answer([result])


@InlineQuery(pattern="url")
async def _url(e):
    try:
        q = e.text.split(" ")[1]
    except IndexError:
        return await answer_query(
            e,
            "ᴇʀʀᴏʀ",
            "ɴᴏ ᴜʀʟ ᴘʀᴏᴠɪᴅᴇᴅ",
            "ᴘʀᴏᴠɪᴅᴇ ᴀɴʏ ᴜʀʟ ᴛᴏ ɢᴇᴛ ɪᴛs ʀᴇᴅɪʀᴇᴄᴛ ʟɪɴᴋ",
            REDIRECT_THUMB,
            [Button.switch_inline("ᴛʀʏ ᴀɢᴀɪɴ", "url", True)],
        )
    try:
        r = get(q, allow_redirects=True, timeout=10)
    except exceptions.ConnectionError:
        return await answer_query(
            e,
            "ᴇʀʀᴏʀ",
            "ᴄᴏɴɴᴇᴄᴛɪᴏɴ Error",
            "ᴘʀᴏᴠɪᴅᴇ ᴀɴʏ url ᴛᴏ ɢᴇᴛ ɪᴛs ʀᴇᴅɪʀᴇᴄᴛ ʟɪɴᴋ",
            REDIRECT_THUMB,
            [Button.switch_inline("ᴛʀʏ ᴀɢᴀɪɴ", "url", True)],
        )
    except exceptions.Timeout:
        return await answer_query(
            e,
            "ᴇʀʀᴏʀ",
            "ᴛɪᴍᴇᴏᴜᴛ ᴇʀʀᴏʀ",
            "ᴘʀᴏᴠɪᴅᴇ ᴀɴʏ ᴜʀʟ ᴛᴏ ɢᴇᴛ ɪᴛs ʀᴇᴅɪʀᴇᴄᴛ ʟɪɴᴋ",
            REDIRECT_THUMB,
            [Button.switch_inline("ᴛʀʏ ᴀɢᴀɪɴ", "url", True)],
        )
    except exceptions.TooManyRedirects:
        return await answer_query(
            e,
            "ᴇʀʀᴏʀ",
            "ᴛᴏᴏ ᴍᴀɴʏ ʀᴇᴅɪʀᴇᴄᴛs",
            "ᴘʀᴏᴠɪᴅᴇ ᴀɴʏ ᴜʀʟ ᴛᴏ ɢᴇᴛ ɪᴛs ʀᴇᴅɪʀᴇᴄᴛ ʟɪɴᴋ",
            REDIRECT_THUMB,
            [Button.switch_inline("ᴛʀʏ ᴀɢᴀɪɴ", "url", True)],
        )
    except exceptions.HTTPError:
        return await answer_query(
            e,
            "ᴇʀʀᴏʀ",
            "ʜᴛᴛᴘ ᴇʀʀᴏʀ",
            "ᴘʀᴏᴠɪᴅᴇ ᴀɴʏ ᴜʀʟ ᴛᴏ ɢᴇᴛ ɪᴛs ʀᴇᴅɪʀᴇᴄᴛ ʟɪɴᴋ",
            REDIRECT_THUMB,
            [Button.switch_inline("ᴛʀʏ ᴀɢᴀɪɴ", "url", True)],
        )
    URL_STAT = "`ᴜʀʟ sᴛᴀᴛᴜs:` **" + str(r.status_code) + "**"
    URL_STAT += "\n`ᴜʀʟ ᴄᴏɴᴛᴇɴᴛ ᴛʏᴘᴇ:` **" + str(r.headers["Content-Type"]) + "**"
    URL_STAT += "\n`ᴜʀʟ ᴄᴏɴᴛᴇɴᴛ ʟᴇɴɢᴛʜ:` **" + str(r.headers["Content-Length"]) + "**"
    URL_STAT += "\n`ʀᴇsᴘᴏɴsᴇ ᴛɪᴍᴇ:` **" + str(r.elapsed.total_seconds()) + "**"
    URL_STAT += "\n`ʀᴇᴅɪʀᴇᴄᴛ ᴜʀʟ:` **" + str(r.url) + "**"
    URL_STAT += "\n`ɪᴘ ᴀᴅᴅʀᴇss:` **" + str(r.headers["X-Client-IP"]) + "**"
    await answer_query(
        e,
        "Redirect Link (" + str(r.status_code) + ")",
        "Redirect Link: " + r.url,
        "",
        REDIRECT_THUMB,
        [Button.url("ᴏᴘᴇɴ ᴜʀʟ", r.url)],
    )


# ========+++++++=============
qr = {}


@command(pattern="(q|quote)")
async def _quotly_api_(e):
    if not e.reply_to:
        return await e.reply("ᴛʜɪs ʜᴀs ᴛᴏ ʙᴇ sᴇɴᴅ ᴡʜɪʟᴇ ʀᴇᴘʟʏɪɴɢ ᴛᴏ ᴀ ᴍᴇssᴀɢᴇ.")
    r = await e.get_reply_message()
    try:
        d = e.text.split(maxsplit=1)[1]
    except IndexError:
        d = ""
    color = None
    for y in d.split():
        try:
            color, g = name_to_hex(y), "hex"
        except ValueError:
            try:
                color, g = hex_to_name(y), "name"
            except ValueError:
                continue
    if color:
        d = d.replace(hex_to_name(color) if g == "hex" else color, "")
    else:
        color = "#1b1429"
    photo = True if "p" in d else False
    messages = []
    num = [int(x) for x in d.split() if x.isdigit()]
    num = num[0] if num else None
    msgs = (
        [
            i
            async for i in e.client.iter_messages(
                e.chat_id,
                ids=list(range(e.reply_to_msg_id, e.reply_to_msg_id + num)),
            )
            if i
        ]
        if num
        else [r]
    )
    c = [1]
    for _x in msgs:
        if _x:
            if _x.sender and isinstance(_x.sender, types.Channel):
                _name = _x.chat.title
                _first_name = _last_name = _username = ""
                _id = _x.chat_id
                _title = "Admin"
            elif _x.sender and isinstance(_x.sender, types.User):
                _name = _x.sender.first_name
                _name = _name + _x.sender.last_name if _x.sender.last_name else _name
                if _x.fwd_from and _x.fwd_from.from_name:
                    _name = _x.fwd_from.from_name
                _first_name = _x.sender.first_name
                _last_name = _x.sender.last_name
                _username = _x.sender.username
                _id = _x.sender_id
                _title = "Admin"
            elif not _x.sender:
                _name = _x.chat.title
                _first_name = _last_name = _x.chat.title
                _username = ""
                _id = _x.chat_id
                _title = "Anon"
            _text = _x.raw_text or ""
            _from = {
                "id": _id,
                "first_name": _first_name,
                "last_name": _last_name,
                "username": _username,
                "language_code": "en",
                "title": _title,
                "type": "group",
                "name": _name if c[-1] != _id else "",
            }
            if len(msgs) == 1:
                if _x.reply_to and "r" in d:
                    reply = await _x.get_reply_message()
                    if isinstance(reply.sender, types.Channel):
                        _r = {
                            "chatId": e.chat_id,
                            "first_name": reply.chat.title,
                            "last_name": "",
                            "username": reply.chat.username,
                            "text": reply.text,
                            "name": reply.chat.title,
                        }
                    elif reply.sender:
                        name = reply.sender.first_name
                        name = (
                            name + " " + reply.sender.last_name
                            if reply.sender.last_name
                            else name
                        )
                        if reply.fwd_from and reply.fwd_from.from_name:
                            _name = reply.fwd_from.from_name
                        _r = {
                            "chatId": e.chat_id,
                            "first_name": reply.sender.first_name,
                            "last_name": "reply.sender.last_name",
                            "username": reply.sender.username,
                            "text": reply.text,
                            "name": name,
                        }
                    else:
                        _r = {}
                else:
                    _r = {}
            else:
                _r = {}
            if _x.sticker:
                mediaType = "sticker"
                media = [
                    {
                        "file_id": _x.file.id,
                        "file_size": _x.file.size,
                        "height": _x.file.height,
                        "width": _x.file.width,
                    }
                ]
            elif _x.photo:
                mediaType = "photo"
                media = [
                    {
                        "file_id": _x.file.id,
                        "file_size": _x.file.size,
                        "height": _x.file.height,
                        "width": _x.file.width,
                    }
                ]
            else:
                media = None
            avatar = True
            if c[-1] == _id:
                avatar = False
            c.append(_id)
            if not media:
                messages.append(
                    {
                        "entities": get_entites(_x),
                        "chatId": e.chat_id,
                        "avatar": avatar,
                        "from": _from,
                        "text": _text,
                        "replyMessage": _r,
                    }
                )
            elif media:
                messages.append(
                    {
                        "chatId": e.chat_id,
                        "avatar": avatar,
                        "media": media,
                        "mediaType": mediaType,
                        "from": _from,
                        "replyMessage": {},
                    }
                )
    post_data = {
        "type": "quote",
        "backgroundColor": color,
        "width": 512,
        "height": 768,
        "scale": 2,
        "messages": messages,
    }
    req = post(
        "https://bot.lyo.su/quote/generate",
        headers={"Content-type": "application/json"},
        json=post_data,
    )
    if get_qrate(e.chat_id):
        cd = str(e.id) + "|" + str(0) + "|" + str(0)
        buttons = buttons = Button.inline("💖", data=f"upq_{cd}"), Button.inline(
            "💔", data=f"doq_{cd}"
        )
        qr[e.id] = [[], []]
    else:
        buttons = None
    try:
        fq = req.json()["result"]["image"]
        with io.BytesIO(base64.b64decode((bytes(fq, "utf-8")))) as f:
            f.name = "sticker.png" if photo else "sticker.webp"
            qs = await e.respond(file=f, force_document=photo, buttons=buttons)
            add_quote(
                e.chat_id,
                [
                    qs.media.document.id,
                    qs.media.document.access_hash,
                    qs.media.document.file_reference,
                ],
            )
    except Exception as ep:
        await e.reply("error: " + str(ep))


def get_entites(x):
    q = []
    for y in x.entities or []:
        if isinstance(y, types.MessageEntityCode):
            type = "code"
        elif isinstance(y, types.MessageEntityBold):
            type = "bold"
        elif isinstance(y, types.MessageEntityItalic):
            type = "italic"
        elif isinstance(y, types.MessageEntityBotCommand):
            type = "bot_command"
        elif isinstance(y, types.MessageEntityUrl):
            type = "url"
        elif isinstance(y, types.MessageEntityEmail):
            type = "email"
        elif isinstance(y, types.MessageEntityPhone):
            type = "phone_number"
        elif isinstance(y, types.MessageEntityUnderline):
            type = "underline"
        elif isinstance(y, types.MessageEntityMention):
            type = "mention"
        else:
            continue
        q.append({"type": type, "offset": y.offset, "length": y.length})
    return q


@command(pattern="qrate")
async def e_q_rating(e):
    if e.is_private:
        return await e.reply("ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ ɪs ᴍᴀᴅᴇ ᴛᴏ ʙᴇ ᴜsᴇᴅ ɪɴ ɢʀᴏᴜᴘ ᴄʜᴀᴛs.")
    if not e.from_id:
        return
    if not await HasRight(e.chat_id, await getSender(e), "change_info"):
        return
    try:
        d = e.text.split(maxsplit=1)[1]
    except IndexError:
        if get_qrate(e.chat_id):
            await e.reply("ǫᴜᴏᴛᴇs ʀᴀᴛɪɴɢ ɪs ᴏɴ.")
        else:
            await e.reply("ʀᴀᴛɪɴɢ ғᴏʀ ǫᴜᴏᴛᴇs ɪs ᴏғғ.")
        return
    if d in ["True", "yes", "on", "y"]:
        await e.reply("ǫᴜᴏᴛᴇs ʀᴀᴛɪɴɢ ʜᴀs ʙᴇᴇɴ ᴛᴜʀɴᴇᴅ ᴏɴ.")
        set_qrate(e.chat_id, True)
    elif d in ["False", "no", "off", "n"]:
        await e.reply("ʀᴀᴛɪɴɢ ғᴏʀ ǫᴜᴏᴛᴇs ʜᴀs ʙᴇᴇɴ ᴛᴜʀɴᴇᴅ ᴏғғ.")
        set_qrate(e.chat_id, False)
    else:
        await e.reply("ʏᴏᴜʀ ɪɴᴘᴜᴛ was not recognised ᴀs ᴏɴᴇ ᴏғ: yes/no/on/off")


@Callback(pattern="upq_(.*)")
async def quotly_upvote(e):
    d = e.pattern_match.group(1).decode()
    x, y, z = d.split("|")
    x, y, z = int(x), int(y), int(z)
    try:
        ya = qr[x]
    except IndexError:
        await e.edit(buttons=None)
    if e.sender_id in ya[0]:
        y -= 1
        qr[x][0].remove(e.sender_id)
        await e.answer("ʏᴏᴜ ɢᴏᴛ ʏᴏᴜʀ ᴠᴏᴛᴇ ʙᴀᴄᴋ")
    elif e.sender_id in ya[1]:
        y += 1
        z -= 1
        qr[x][1].remove(e.sender_id)
        qr[x][0].append(e.sender_id)
        await e.answer("ʏᴏᴜ 💖 ᴛʜɪs")
    elif e.sender_id not in ya[0]:
        y += 1
        qr[x][0].append(e.sender_id)
        await e.answer("ʏᴏᴜ 💖 ᴛʜɪs")
    cd = "{}|{}|{}".format(x, y, z)
    if y == 0:
        y = ""
    if z == 0:
        z = ""
    await e.edit(
        buttons=[
            Button.inline(f"💖 {y}", data=f"upq_{cd}"),
            Button.inline(f"💔 {z}", data=f"doq_{cd}"),
        ]
    )


@Callback(pattern="doq_(.*)")
async def quotly_downvote(e):
    d = e.pattern_match.group(1).decode()
    x, y, z = d.split("|")
    x, y, z = int(x), int(y), int(z)
    try:
        ya = qr[x]
    except IndexError:
        await e.edit(buttons=None)
    if e.sender_id in ya[1]:
        z -= 1
        qr[x][1].remove(e.sender_id)
        await e.answer("ʏᴏᴜ ɢᴏᴛ ʏᴏᴜʀ ᴠᴏᴛᴇ ʙᴀᴄᴋ")
    elif e.sender_id in ya[0]:
        z += 1
        y -= 1
        qr[x][0].remove(e.sender_id)
        qr[x][1].append(e.sender_id)
        await e.answer("ʏᴏᴜ 💔 ᴛʜɪs")
    elif e.sender_id not in ya[1]:
        z += 1
        qr[x][1].append(e.sender_id)
        await e.answer("ʏᴏᴜ 💔 ᴛʜɪs")
    cd = "{}|{}|{}".format(x, y, z)
    if y == 0:
        y = ""
    if z == 0:
        z = ""
    await e.edit(
        buttons=[
            Button.inline(f"💖 {y}", data=f"upq_{cd}"),
            Button.inline(f"💔 {z}", data=f"doq_{cd}"),
        ]
    )


@command(pattern="qtop")
async def qtop_q(e):
    await e.reply(
        "**ᴛᴏᴘ ɢʀᴏᴜᴘ ǫᴜᴏᴛᴇs:**",
        buttons=Button.switch_inline(
            "ᴏᴘᴇɴ ᴛᴏᴘ", "top:{}".format(e.chat_id), same_peer=True
        ),
    )


@InlineQuery(pattern="top:(.*)")
async def qtop_cb_(e):
    x = e.pattern_match.group(1)
    q = get_quotes(int(x))
    if not q:
        return
    c = []
    xe = False
    n = 0
    if get_qrate(e.chat_id):
        qr[e.id] = [[], []]
        cd = str(e.id) + "|" + str(0) + "|" + str(0)
        xe = True
    for _x in q:
        n += 1
        c.append(
            await e.builder.document(
                title=str(n),
                description=str(n),
                text=str(n),
                file=types.InputDocument(
                    id=_x[0], access_hash=_x[1], file_reference=_x[2]
                ),
                buttons=[
                    Button.inline("💖", data=f"upq_{cd}"),
                    Button.inline("💔", data=f"doq_{cd}"),
                ]
                if xe
                else None,
            )
        )
    await e.answer(c, gallery=True)


@command(pattern="qrand")
async def qrand_s_(e):
    q = get_quotes(e.chat_id)
    if not q:
        return
    c, xe = random.choice(q), False
    if get_qrate(e.chat_id):
        qr[e.id] = [[], []]
        cd = str(e.id) + "|" + str(0) + "|" + str(0)
        xe = True
    await e.reply(
        file=types.InputDocument(c[0], c[1], c[2]),
        buttons=[
            Button.inline("💖", data=f"upq_{cd}"),
            Button.inline("💔", data=f"doq_{cd}"),
        ]
        if xe
        else None,
    )


__help__ = """
⍟ /q*:* ᴄʀᴇᴀᴛᴇ ᴀ ǫᴜᴏᴛᴇ ғʀᴏᴍ ᴛʜᴇ ᴍᴇssᴀɢᴇ 
⍟ /q r*:* ᴄʀᴇᴀᴛᴇ ᴀ ǫᴜᴏᴛᴇ ғʀᴏᴍ ᴛʜᴇ ᴍᴇssᴀɢᴇ ᴡɪᴛʜ ʀᴇᴘʟʏ
⍟ /q ᴄᴏʟᴏʀ ɴᴀᴍᴇ*:* ɢᴇᴛ ᴀ ǫᴜᴏᴛᴇᴅ ᴡɪᴛʜ ʏᴏᴜʀ ᴄᴏʟᴏʀ ʙɢ 
⍟ /qrate*:* ᴏɴ ᴛʜɪs ɪɴ ɢʀᴏᴜᴘ 
⍟ /qtop*:* ɢᴇᴛ ᴛᴏᴘ ϙᴜᴏᴛᴇᴅ 
⍟ /qrand*:* ɢᴇᴛ ᴀ ʀᴀɴᴅᴏᴍ ǫᴜᴏᴛᴇᴅ 
⍟ /q 1ᴛᴏ 9 *:* ɢᴇᴛ ǫᴜᴏᴛᴇᴅ 
⍟ /q s2.5*:* ǫᴜᴏᴛᴇᴅ ᴡɪᴛʜ ǫᴜᴀʟɪᴛʏ 
"""

__mod_name__ = "𝐐ᴜᴏᴛʟʏ"
