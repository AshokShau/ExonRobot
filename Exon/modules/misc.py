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

import contextlib
import datetime
import html
import platform
import time
from io import BytesIO
from platform import python_version
from subprocess import PIPE, Popen

from psutil import boot_time, cpu_percent, disk_usage, virtual_memory
from telegram import Chat, MessageEntity, ParseMode, Update, User
from telegram import __version__ as ptbver
from telegram.error import BadRequest
from telegram.ext import CallbackContext, Filters
from telegram.utils.helpers import escape_markdown, mention_html

import Exon.modules.sql.users_sql as sql
from Exon import DEMONS as SUPPORT_USERS
from Exon import DEV_USERS
from Exon import DRAGONS as SUDO_USERS
from Exon import INFOPIC, OWNER_ID
from Exon import OWNER_USERNAME as AKBOSS
from Exon import TIGERS
from Exon import WOLVES as WHITELIST_USERS
from Exon import StartTime, dispatcher, sw
from Exon.__main__ import STATS, USER_INFO
from Exon.modules.disable import DisableAbleCommandHandler
from Exon.modules.helper_funcs.chat_status import sudo_plus, user_admin
from Exon.modules.helper_funcs.decorators import Exoncmd
from Exon.modules.helper_funcs.extraction import extract_user
from Exon.modules.users import __user_info__ as chat_count

MARKDOWN_HELP = f"""
ᴍᴀʀᴋᴅᴏᴡɴ ɪs ᴀ ᴠᴇʀʏ ᴘᴏᴡᴇʀғᴜʟ ғᴏʀᴍᴀᴛᴛɪɴɢ ᴛᴏᴏʟ sᴜᴘᴘᴏʀᴛᴇᴅ ʙʏ ᴛᴇʟᴇɢʀᴀᴍ. {dispatcher.bot.first_name} ʜᴀs sᴏᴍᴇ ᴇɴʜᴀɴᴄᴇᴍᴇɴᴛs, ᴛᴏ ᴍᴀᴋᴇ sᴜʀᴇ ᴛʜᴀᴛ \
sᴀᴠᴇᴅ ᴍᴇssᴀɢᴇs ᴀʀᴇ ᴄᴏʀʀᴇᴄᴛʟʏ ᴘᴀʀsᴇᴅ, ᴀɴᴅ ᴛᴏ ᴀʟʟᴏᴡ ʏᴏᴜ ᴛᴏ ᴄʀᴇᴀᴛᴇ ʙᴜᴛᴛᴏɴs.

❂ <code>_italic_</code>: wrapping text with '_' will produce italic text
❂ <code>*bold*</code>: wrapping text with '*' will produce bold text
❂ <code>`code`</code>: wrapping text with '`' will produce monospaced text, also known as 'code'
❂ <code>[sometext](someURL)</code>: this will create a link - the message will just show <code>sometext</code>, \
ᴀɴᴅ ᴛᴀᴘᴘɪɴɢ ᴏɴ ɪᴛ ᴡɪʟʟ ᴏᴘᴇɴ ᴛʜᴇ ᴘᴀɢᴇ ᴀᴛ <code>someURL</code>.
<b>ᴇxᴀᴍᴘʟᴇ:</b><code>[test](example.com)</code>

❂ <code>[buttontext](buttonurl:someURL)</code>: this is a special enhancement to allow users to have telegram \
buttons in their markdown. <code>buttontext</code> will be what is displayed on the button, and <code>someurl</code> \

ᴡɪʟʟ be ᴛʜᴇ ᴜʀʟ ᴡʜɪᴄʜ ɪs ᴏᴘᴇɴᴇᴅ.

<b>ᴇxᴀᴍᴘʟᴇ:</b> <code>[ᴛʜɪs ɪs ᴀ ʙᴜᴛᴛᴏɴ](buttonurl:example.com)</code>

If you want multiple buttons on the same line, use :same, as such:
<code>[one](buttonurl://example.com)
[two](buttonurl://google.com:same)</code>

ᴛʜɪs ᴡɪʟʟ ᴄʀᴇᴀᴛᴇ ᴛᴡᴏ ʙᴜᴛᴛᴏɴs ᴏɴ ᴀ sɪɴɢʟᴇ ʟɪɴᴇ, ɪɴsᴛᴇᴀᴅ ᴏғ ᴏɴᴇ ʙᴜᴛᴛᴏɴ ᴘᴇʀ ʟɪɴᴇ.

Keep in mind that your message <b>MUST</b> contain some text other than just a button!
"""


@Exoncmd(command="gifid")
def gifid(update: Update, _):
    msg = update.effective_message
    if msg.reply_to_message and msg.reply_to_message.animation:
        update.effective_message.reply_text(
            f"ɢɪғ ɪᴅ:\n<code>{msg.reply_to_message.animation.file_id}</code>",
            parse_mode=ParseMode.HTML,
        )
    else:
        update.effective_message.reply_text("ᴘʟᴇᴀsᴇ ʀᴇᴘʟʏ ᴛᴏ ᴀ ɢɪғ ᴛᴏ ɢᴇᴛ ɪᴛs ID.")


@Exoncmd(command="info", pass_args=True)
def info(update: Update, context: CallbackContext):  # sourcery no-metrics
    bot = context.bot
    args = context.args
    message = update.effective_message
    chat = update.effective_chat
    if user_id := extract_user(update.effective_message, args):
        user = bot.get_chat(user_id)

    elif not message.reply_to_message and not args:
        user = (
            message.sender_chat
            if message.sender_chat is not None
            else message.from_user
        )

    elif not message.reply_to_message and (
        not args
        or (
            len(args) >= 1
            and not args[0].startswith("@")
            and not args[0].lstrip("-").isdigit()
            and not message.parse_entities([MessageEntity.TEXT_MENTION])
        )
    ):
        message.reply_text("I ᴄᴀɴ'ᴛ ᴇxᴛʀᴀᴄᴛ ᴀ ᴜsᴇʀ ғʀᴏᴍ ᴛʜɪs.")
        return

    else:
        return

    if hasattr(user, "type") and user.type != "private":
        text = get_chat_info(user)
        is_chat = True
    else:
        text = get_user_info(chat, user)
        is_chat = False

    if INFOPIC:
        if is_chat:
            try:
                pic = user.photo.big_file_id
                pfp = bot.get_file(pic).download(out=BytesIO())
                pfp.seek(0)
                message.reply_document(
                    document=pfp,
                    filename=f"{user.id}.jpg",
                    caption=text,
                    parse_mode=ParseMode.HTML,
                )
            except AttributeError:  # AttributeError means no chat pic so just send text
                message.reply_text(
                    text,
                    parse_mode=ParseMode.HTML,
                    disable_web_page_preview=True,
                )
        else:
            try:
                profile = bot.get_user_profile_photos(user.id).photos[0][-1]
                _file = bot.get_file(profile["file_id"])

                _file = _file.download(out=BytesIO())
                _file.seek(0)

                message.reply_document(
                    document=_file,
                    caption=(text),
                    parse_mode=ParseMode.HTML,
                )

            # Incase user don't have profile pic, send normal text
            except IndexError:
                message.reply_text(
                    text, parse_mode=ParseMode.HTML, disable_web_page_preview=True
                )

    else:
        message.reply_text(
            text, parse_mode=ParseMode.HTML, disable_web_page_preview=True
        )


def get_user_info(chat: Chat, user: User) -> str:
    bot = dispatcher.bot
    text = (
        f"╒═══「<b> ᴀɴᴀʟʏᴢᴇᴅ ʀᴇsᴜʟᴛs:</b> 」\n"
        f"✦ ᴜsᴇʀ ID: <code>{user.id}</code>\n"
        f"✦ ғɪʀsᴛ ɴᴀᴍᴇ: {html.escape(user.first_name)}"
    )
    if user.last_name:
        text += f"\n✦ ʟᴀsᴛ ɴᴀᴍᴇ: {html.escape(user.last_name)}"
    if user.username:
        text += f"\n✦ ᴜsᴇʀɴᴀᴍᴇ: @{html.escape(user.username)}"
    text += f"\n✦ ᴜsᴇʀ ʟɪɴᴋ: {mention_html(user.id, 'link')}"
    with contextlib.suppress(Exception):
        if spamwtc := sw.get_ban(int(user.id)):
            text += "<b>\n\nsᴘᴀᴍᴡᴀᴛᴄʜ:\n</b>"
            text += "<b>ᴛʜɪs ᴘᴇʀsᴏɴ is ʙᴀɴɴᴇᴅ ɪɴ sᴘᴀᴍᴡᴀᴛᴄʜ!</b>"
            text += f"\nʀᴇᴀsᴏɴ: <pre>{spamwtc.reason}</pre>"
            text += "\nAppeal ᴀᴛ @SpamWatchSupport"
        else:
            text += "<b>\n\nSpamWatch:</b> Not banned"
    disaster_level_present = False
    num_chats = sql.get_user_num_chats(user.id)
    text += f"\n\n<b>ᴄʜᴀᴛ ᴄᴏᴜɴᴛ</b>: <code>{num_chats}</code>"
    with contextlib.suppress(BadRequest):
        user_member = chat.get_member(user.id)
        if user_member.status == "administrator":
            result = bot.get_chat_member(chat.id, user.id)
            if result.custom_title:
                text += (
                    f"\n\nᴛʜɪs ᴜsᴇʀ ʜᴏʟᴅs ᴛʜᴇ ᴛɪᴛʟᴇ <b>{result.custom_title}</b> ʜᴇʀᴇ."
                )
    if user.id == OWNER_ID:
        text += "\n\n<code>ᴏᴜʀ ᴄᴜᴛᴇ ᴏᴡɴᴇʀ </code> :3"
        disaster_level_present = True
    elif user.id in DEV_USERS:
        text += "\n\n<code>ᴛʜɪs ᴜsᴇʀ ɪs a ᴘᴀʀᴛ ᴏғ ᴏᴜʀ ғᴀᴍɪʟʏ</code> "
        disaster_level_present = True
    elif user.id in SUDO_USERS:
        text += "\n\n<code>ᴏɴᴇ ᴏғ ᴏᴜʀ ʙᴇsᴛᴏ ғʀɪᴇɴᴅᴏs, ᴛᴏᴜᴄʜ ʜɪᴍ ᴀɴᴅ ʏᴏᴜ ᴀʀᴇ ᴅᴇᴀᴅ ᴍᴇᴀᴛ</code>"
        disaster_level_present = True
    elif user.id in SUPPORT_USERS:
        text += "\n\n<code>ᴛʜɪs user is ᴏᴜʀ ғʀɪᴇɴᴅ</code> ✨"
        disaster_level_present = True
    elif user.id in TIGERS:
        text += "\n\n<code>ᴏɴᴇ ᴏғ ᴍʏ ᴄʟᴀssᴍᴀᴛᴇs</code> :p"
        disaster_level_present = True
    elif user.id in WHITELIST_USERS:
        text += "\n\n<code>ᴍᴇᴍʙᴇʀ ᴏғ Exon ᴛᴇᴄʜ, ᴛᴏᴛᴀʟʟʏ ᴄᴏᴏʟ ʀɪɢʜᴛ ?</code>"
        disaster_level_present = True
    if disaster_level_present:
        text += ' [<a href="https://t.me/abishnoi_bots/60">?</a>]'
    text += "\n"
    for mod in USER_INFO:
        if mod.__mod_name__ == "Users":
            continue

        try:
            mod_info = mod.__user_info__(user.id)
        except TypeError:
            mod_info = mod.__user_info__(user.id, chat.id)
        if mod_info:
            text += "\n" + mod_info
    return text


def get_chat_info(user):
    text = f"<b>ᴄʜᴀᴛ ɪɴғᴏʀᴍᴀᴛɪᴏɴ:</b>\n" f"<b>ᴄʜᴀᴛ ᴛɪᴛʟᴇ:</b> {user.title}"
    if user.username:
        text += f"\n<b>ᴜsᴇʀɴᴀᴍᴇ:</b> @{html.escape(user.username)}"
    text += f"\n<b>ᴄʜᴀᴛ ɪᴅ:</b> <code>{user.id}</code>"
    text += f"\n<b>ᴄʜᴀᴛ ᴛʏᴘᴇ:</b> {user.type.capitalize()}"
    text += "\n" + chat_count(user.id)

    return text


def shell(command):
    process = Popen(command, stdout=PIPE, shell=True, stderr=PIPE)
    stdout, stderr = process.communicate()
    return (stdout, stderr)


@Exoncmd(command="markdownhelp", filters=Filters.chat_type.private)
def markdown_help(update: Update, _):
    update.effective_chat
    update.effective_message.reply_text(f"{MARKDOWN_HELP}", parse_mode=ParseMode.HTML)
    update.effective_message.reply_text(
        "ᴛʀʏ ғᴏʀᴡᴀʀᴅɪɴɢ ᴛʜᴇ ғᴏʟʟᴏᴡɪɴɢ ᴍᴇssᴀɢᴇ ᴛᴏ ᴍᴇ, ᴀɴᴅ ʏᴏᴜ'ʟʟ sᴇᴇ!"
    )
    update.effective_message.reply_text(
        "/save test ᴛʜɪs ɪs ᴀ ᴍᴀʀᴋᴅᴏᴡɴ ᴛᴇsᴛ. _italics_, *bold*, `code`, "
        "[ᴜʀʟ](example.com) [button](buttonurl:github.com) "
        "[ʙᴜᴛᴛᴏɴ2](buttonurl://google.com:same)"
    )


def get_readable_time(seconds: int) -> str:
    count = 0
    ping_time = ""
    time_list = []
    time_suffix_list = ["s", "ᴍ", "ʜ", "ᴅᴀʏs"]

    while count < 4:
        count += 1
        remainder, result = divmod(seconds, 60) if count < 3 else divmod(seconds, 24)
        if seconds == 0 and remainder == 0:
            break
        time_list.append(int(result))
        seconds = int(remainder)

    for x in range(len(time_list)):
        time_list[x] = str(time_list[x]) + time_suffix_list[x]
    if len(time_list) == 4:
        ping_time += f"{time_list.pop()}, "

    time_list.reverse()
    ping_time += ":".join(time_list)

    return ping_time


stats_str = """
"""


@Exoncmd(command="stats", can_disable=False)
@sudo_plus
def stats(update, context):
    uptime = datetime.datetime.fromtimestamp(boot_time()).strftime("%Y-%m-%d %H:%M:%S")
    botuptime = get_readable_time((time.time() - StartTime))
    status = "*  「 sʏsᴛᴇᴍ sᴛᴀᴛɪsᴛɪᴄs: 」*\n\n"
    status += f"*• sʏsᴛᴇᴍ sᴛᴀʀᴛ ᴛɪᴍᴇ:* {str(uptime)}" + "\n"
    uname = platform.uname()
    status += f"*• sʏsᴛᴇᴍ:* {str(uname.system)}" + "\n"
    status += f"*• ɴᴏᴅᴇ ɴᴀᴍᴇ:* {escape_markdown(str(uname.node))}" + "\n"
    status += f"*• ʀᴇʟᴇᴀsᴇ:* {escape_markdown(str(uname.release))}" + "\n"
    status += f"*• ᴍᴀᴄʜɪɴᴇ:* {escape_markdown(str(uname.machine))}" + "\n"

    mem = virtual_memory()
    cpu = cpu_percent()
    disk = disk_usage("/")
    status += f"*• ᴄᴘᴜ:* {str(cpu)}" + " %\n"
    status += f"*• ʀᴀᴍ:* {str(mem[2])}" + " %\n"
    status += f"*• sᴛᴏʀᴀɢᴇ:* {str(disk[3])}" + " %\n\n"
    status += f"*• ᴘʏᴛʜᴏɴ ᴠᴇʀsɪᴏɴ:* {python_version()}" + "\n"
    status += f"*• ᴘʏᴛʜᴏɴ ᴛᴇʟᴇɢʀᴀᴍ:* {str(ptbver)}" + "\n"
    status += f"*• ᴜᴘᴛɪᴍᴇ:* {str(botuptime)}" + "\n"

    try:
        update.effective_message.reply_text(
            status
            + "\n*ʙᴏᴛ sᴛᴀᴛɪsᴛɪᴄs*:\n"
            + "\n".join([mod.__stats__() for mod in STATS])
            + "\n\n[ɢɪᴛʜᴜʙ](https://github.com/KingAbishnoi/ExonRobot) | [ᴛᴇʟᴇɢʀᴀᴍ](https://t.me/AbishnoiMF)\n\n"
            + f"「 ʙʏ[ᴀʙɪsʜɴᴏɪ](t.me/{AKBOSS}) 」\n",
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
        )
    except BaseException:
        update.effective_message.reply_text(
            (
                (
                    (
                        "\n*ʙᴏᴛ sᴛᴀᴛɪsᴛɪᴄs*:\n"
                        + "\n".join(mod.__stats__() for mod in STATS)
                    )
                    + "\n\n⍙ [ɢɪᴛʜᴜʙ](https://github.com/KingAbishnoi/ExonRobot) | [ᴛᴇʟᴇɢʀᴀᴍ](https://t.me/AbishnoiMF)\n\n"
                )
                + f"「 ʙʏ [ᴀʙɪsʜɴᴏɪ](t.me/{AKBOSS}) 」\n"
            ),
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
        )


@user_admin
def echo(update: Update, context: CallbackContext):
    args = update.effective_message.text.split(None, 1)
    message = update.effective_message

    if message.reply_to_message:
        message.reply_to_message.reply_text(
            args[1],
            parse_mode="MARKDOWN",
            disable_web_page_preview=True,
        )
    else:
        message.reply_text(
            args[1],
            quote=False,
            parse_mode="MARKDOWN",
            disable_web_page_preview=True,
        )
    message.delete()


__help__ = """
*ᴀᴠᴀɪʟᴀʙʟᴇ ᴄᴏᴍᴍᴀɴᴅs:*

📐 ᴍᴀʀᴋᴅᴏᴡɴ:

⍟ /markdownhelp : `ǫᴜɪᴄᴋ sᴜᴍᴍᴀʀʏ ᴏғ ʜᴏᴡ ᴍᴀʀᴋᴅᴏᴡɴ ᴡᴏʀᴋs ɪɴ ᴛᴇʟᴇɢʀᴀᴍ - ᴄᴀɴ ᴏɴʟʏ ʙᴇ ᴄᴀʟʟᴇᴅ ɪɴ ᴘʀɪᴠᴀᴛᴇ ᴄʜᴀᴛs `


🗳  ᴏᴛʜᴇʀ ᴄᴏᴍᴍᴀɴᴅs:

Paste:
⍟ /paste*:*` sᴀᴠᴇs ʀᴇᴘʟɪᴇᴅ ᴄᴏɴᴛᴇɴᴛ ᴛᴏ ɴᴇᴋᴏʙɪɴ.ᴄᴏᴍ ᴀɴᴅ ʀᴇᴘʟɪᴇs ᴡɪᴛʜ ᴀ ᴜʀʟ

ʀᴇᴀᴄᴛ:
⍟ /react *:* `ʀᴇᴀᴄᴛs ᴡɪᴛʜ a ʀᴀɴᴅᴏᴍ ʀᴇᴀᴄᴛɪᴏɴ `

Urban Dictonary:
⍟ /ud <word> *:* `ᴛʏᴘᴇ ᴛʜᴇ ᴡᴏʀᴅ ᴏʀ ᴇxᴘʀᴇssɪᴏɴ ʏᴏᴜ ᴡᴀɴᴛ ᴛᴏ sᴇᴀʀᴄʜ ᴜsᴇ `

ᴡɪᴋɪᴘᴇᴅɪᴀ:
⍟ ❂ /wiki <query> *:* `ᴡɪᴋɪᴘᴇᴅɪᴀ ʏᴏᴜʀ ǫᴜᴇʀʏ `

ᴡᴀʟʟᴘᴀᴘᴇʀs:
⍟ /wall <query>*:* `get ᴀ ᴡᴀʟʟᴘᴀᴘᴇʀ ғʀᴏᴍ ᴀʟᴘʜᴀᴄᴏᴅᴇʀs `

ʙᴏᴏᴋs:
⍟ /book <book name>*:* `ɢᴇᴛs ɪɴsᴛᴀɴᴛ ᴅᴏᴡɴʟᴏᴀᴅ ʟɪɴᴋ ᴏғ ɢɪᴠᴇɴ ʙᴏᴏᴋ `.

"""

ECHO_HANDLER = DisableAbleCommandHandler(
    "echo", echo, filters=Filters.chat_type.groups, run_async=True
)

dispatcher.add_handler(ECHO_HANDLER)

__mod_name__ = "𝙴xᴛʀᴀs"
__command_list__ = ["gifid", "echo"]
__handlers__ = [ECHO_HANDLER]
