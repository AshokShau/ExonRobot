import os
import random
import re
from httpx import AsyncClient
from Exon import application
from Exon.modules.disable import DisableAbleCommandHandler
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes
from bs4 import BeautifulSoup
from geniuses import GeniusClient
from GoogleSearch import Search
from requests import get, post
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.error import BadRequest
from telegram.ext import ContextTypes
import wikipedia
from Exon import application
from Exon.modules.disable import DisableAbleCommandHandler
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes
from wikipedia.exceptions import DisambiguationError, PageError

from Exon import application
from Exon import register as Asubot
from Exon.modules.disable import DisableAbleCommandHandler


@Asubot(pattern="^/google ?(.*)")
async def google_search(e):
    try:
        query = e.text.split(None, 1)[1]
    except IndexError:
        return await e.reply(
            "ᴛʜᴇ ǫᴜᴇʀʏ ᴛᴇxᴛ ʜᴀs ɴᴏᴛ ʙᴇᴇɴ ᴘʀᴏᴠɪᴅᴇᴅ.",
        )
    url = f"https://www.google.com/search?&q={query}&num=5"
    usr_agent = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/61.0.3163.100 Safari/537.36"
    }
    r = get(url, headers=usr_agent)
    soup = BeautifulSoup(r.text, "html.parser")
    results = soup.find_all("div", attrs={"class": "g"})
    final = f"sᴇᴀʀᴄʜ ʀᴇsᴜʟᴛs for <b>{query}</b>:"
    if not results or len(results) == 0:
        return await e.reply(
            "ɴᴏ ʀᴇsᴜʟᴛs ғᴏᴜɴᴅ!",
        )
    for x in results:
        link = (x.find("a", href=True))["href"]
        name = x.find("h3")
        if link and name:
            if not name == "Images" and not name == "Description":
                final += f"\n- <a href='{link}'>{name}</a>"
    await e.reply(final, parse_mode="html", link_preview=False)


@Asubot(pattern="^/lyrics ?(.*)")
async def lyrics_get_(e):
    GENIUSES_API_KEY = (
        "gIgMyTXuwJoY9VCPNwKdb_RUOA_9mCMmRlbrrdODmNvcpslww_2RIbbWOB8YdBW9"
    )
    q = e.pattern_match.group(1)
    if not q:
        return await e.reply(
            "ᴘʟᴇᴀsᴇ ᴘʀᴏᴠɪᴅᴇ ᴛʜᴇ sᴏɴɢ ɴᴀᴍᴇ, ᴛᴏ ғᴇᴛᴄʜ ɪᴛs ʟʏʀɪᴄs!",
        )
    g_client = GeniusClient(GENIUSES_API_KEY)
    songs = g_client.search(q)
    if len(songs) == 0:
        return await e.reply(
            "ɴᴏ ʀᴇsᴜʟᴛ ғᴏᴜɴᴅ ғᴏʀ ᴛʜᴇ ɢɪᴠᴇɴ sᴏɴɢ ɴᴀᴍᴇ!",
        )
    song = songs[0]
    name = song.title
    song.header_image_thumbnail_url
    lyrics = song.lyrics
    for x in ["Embed", "Share URL", "Copy"]:
        if x in lyrics:
            lyrics = lyrics.replace(x, "")
    pattern = re.compile("\n+")
    lyrics = pattern.sub("\n", lyrics)
    out_str = f"**{name}**\n__{lyrics}__"
    await e.reply(out_str)


kEys = [
    "mHfAkGq8Wi6dHHwt591nMAM7",
    "NSazBmGo6XfkS2LbTNZRiDdK",
    "Ad5bs76jsbssAAnEbx5PtBKe",
    "nDZ4WFe93Hn8Kjz3By8ALR7s",
]


@Asubot(pattern="^/rmbg ?(.*)")
async def remove_bg_photo_room__(e):
    if not e.reply_to:
        return await e.reply(
            "ʀᴇᴘʟʏ ᴛᴏ ᴀɴʏ ɪᴍᴀɢᴇ ᴛᴏ ʀᴇᴍᴏᴠᴇ ɪᴛ's ʙᴀᴄᴋɢʀᴏᴜɴᴅ.",
        )
    r = await e.get_reply_message()
    if not r.photo and not r.sticker:
        return await e.reply(
            "ᴛʜᴀᴛ's ɴᴏᴛ ᴀ sᴛɪᴄᴋᴇʀ/ɪᴍᴀɢᴇ ᴛᴏ remove.bg",
        )
    mxe = await e.reply(
        "`ʀᴇᴍᴏᴠɪɴɢ ʙɢ....`",
    )
    f = await e.client.download_media(r)
    r = post(
        "https://api.remove.bg/v1.0/removebg",
        files={"image_file": open(f, "rb")},
        data={"size": "auto"},
        headers={"X-Api-Key": random.choice(kEys)},
    )
    if r.ok:
        with open("rmbg.jpg", "wb") as w:
            w.write(r.content)
        await e.reply(file="rmbg.jpg", force_document=True)
        await mxe.delete()
    else:
        await e.reply(r.text)
    os.remove(f)


async def reverse(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.effective_message
    args = context.args

    if args:
        if len(args) <= 1:
            url = args[0]
            if url.startswith(("https://", "http://")):
                msg = await message.reply_text("ᴜᴘʟᴏᴀᴅɪɴɢ ᴜʀʟ ᴛᴏ ɢᴏᴏɢʟᴇ..")

                result = Search(url=url)
                name = result["output"]
                link = result["similar"]

                await msg.edit_text("ᴜᴘʟᴏᴀᴅᴇᴅ ᴛᴏ ɢᴏᴏɢʟᴇ, ғᴇᴛᴄʜɪɴɢ ʀᴇsᴜʟᴛs...")
                await msg.edit_text(
                    text=f"{name}",
                    reply_markup=InlineKeyboardMarkup(
                        [
                            [
                                InlineKeyboardButton(
                                    text="sɪᴍɪʟᴀʀ",
                                    url=link,
                                ),
                            ],
                        ],
                    ),
                )
                return
        else:
            await message.reply_text(
                "ᴄᴏᴍᴍᴀɴᴅ ᴍᴜsᴛ ʙᴇ ᴜsᴇᴅ ᴡɪᴛʜ ᴀ ʀᴇᴘʟʏ ᴛᴏ ᴀɴ ɪᴍᴀɢᴇ ᴏʀ sʜᴏᴜʟᴅ ɢɪᴠᴇ ᴜʀʟ"
            )

    elif message.reply_to_message and message.reply_to_message.photo:
        try:
            edit = await message.reply_text("ᴅᴏᴡɴʟᴏᴀᴅɪɴɢ ɪᴍᴀɢᴇ")
        except BadRequest:
            return

        photo = message.reply_to_message.photo[-1]
        file = await context.bot.get_file(photo.file_id)
        await file.download_to_drive("reverse.jpg")

        await edit.edit_text("ᴅᴏᴡɴʟᴏᴀᴅᴇᴅ ɪᴍᴀɢᴇ, ᴜᴘʟᴏᴀᴅɪɴɢ ᴛᴏ ɢᴏᴏɢʟᴇ...")

        result = Search(file_path="reverse.jpg")
        await edit.edit_text("ᴜᴘʟᴏᴀᴅᴇᴅ ᴛᴏ ɢᴏᴏɢʟᴇ, ғᴇᴛᴄʜɪɴɢ ʀᴇsᴜʟᴛs...")
        name = result["output"]
        link = result["similar"]

        await edit.edit_text(
            text=f"{name}",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text="sɪᴍɪʟᴀʀ",
                            url=link,
                        ),
                    ],
                ],
            ),
        )
        return
    else:
        await message.reply_text(
            "ᴄᴏᴍᴍᴀɴᴅ sʜᴏᴜʟᴅ ʙᴇ ᴜsᴇᴅ ᴡɪᴛʜ ʀᴇᴘʟʏɪɴɢ ᴛᴏ ᴀɴ ɪᴍᴀɢᴇ ᴏʀ ᴜʀʟ sʜᴏᴜʟᴅ ɢɪᴠᴇɴ."
        )
        
async def ud(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.effective_message
    text = message.text[len("/ud ") :]
    async with AsyncClient() as client:
        r = await client.get(f"https://api.urbandictionary.com/v0/define?term={text}")
    results = r.json()
    try:
        reply_text = f'*{text}*\n\n{results["list"][0]["definition"]}\n\n_{results["list"][0]["example"]}_'
    except:
        reply_text = "ɴᴏ ʀᴇsᴜʟᴛs ғᴏᴜɴᴅ."
    await message.reply_text(reply_text, parse_mode=ParseMode.MARKDOWN)

async def wiki(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = (
        update.effective_message.reply_to_message
        if update.effective_message.reply_to_message and not update.effective_message.reply_to_message.forum_topic_created
        else update.effective_message
    )
    res = ""
    if msg == update.effective_message:
        search = msg.text.split(" ", maxsplit=1)[1]
    else:
        search = msg.text
    try:
        res = wikipedia.summary(search)
    except DisambiguationError as e:
        await update.message.reply_text(
            "ᴅɪsᴀᴍʙɪɢᴜᴀᴛᴇᴅ ᴘᴀɢᴇs ғᴏᴜɴᴅ! ᴀᴅᴊᴜsᴛ ʏᴏᴜʀ ǫᴜᴇʀʏ ᴀᴄᴄᴏʀᴅɪɴɢʟʏ.\n<i>{}</i>".format(
                e,
            ),
            parse_mode=ParseMode.HTML,
        )
    except PageError as e:
        await update.message.reply_text(
            "<code>{}</code>".format(e), parse_mode=ParseMode.HTML,
        )
    if res:
        result = f"<b>{search}</b>\n\n"
        result += f"<i>{res}</i>\n"
        result += f"""<a href="https://en.wikipedia.org/wiki/{search.replace(" ", "%20")}">Read more...</a>"""
        if len(result) > 4000:
            with open("result.txt", "w") as f:
                f.write(f"{result}\n\nUwU OwO OmO UmU")
            with open("result.txt", "rb") as f:
                await context.bot.send_document(
                    document=f,
                    filename=f.name,
                    reply_to_message_id=update.message.message_id,
                    chat_id=update.effective_chat.id,
                    parse_mode=ParseMode.HTML,
                )
        else:
            await update.message.reply_text(
                result, parse_mode=ParseMode.HTML, disable_web_page_preview=True,
            )
            
REVERSE_HANDLER = DisableAbleCommandHandler(["reverse", "pp"], reverse, block=False)
UD_HANDLER = DisableAbleCommandHandler(["ud"], ud, block=False)
WIKI_HANDLER = DisableAbleCommandHandler("wiki", wiki, block=False)
application.add_handler(WIKI_HANDLER)
application.add_handler(UD_HANDLER)
application.add_handler(REVERSE_HANDLER)


__command_list__ = ["ud"]
__handlers__ = [UD_HANDLER]

__help__ = """
⍟ /google `<ǫᴜᴇʀʏ>` *:* ᴘᴇʀғᴏʀᴍ ᴀ ɢᴏᴏɢʟᴇ sᴇᴀʀᴄʜ ᴡɪᴛʜ ᴛʜᴇ ɢɪᴠᴇɴ ǫᴜᴇʀʏ.
⍟ /lyrics `<ǫᴜᴇʀʏ>` *:* ɢᴀᴛʜᴇʀ ᴛʜᴇ ʟʏʀɪᴄs ᴏғ ᴛʜᴇ ǫᴜᴇʀɪᴇᴅ sᴏɴɢ ғʀᴏᴍ ʟʏʀɪᴄsɢᴇɴɪᴜs.
⍟ /rmbg `<ʀᴇᴘʟʏ>` *:* ʀᴇᴍᴏᴠᴇ ʙɢ ᴏғ ᴛʜᴇ ɪᴍᴀɢᴇ ᴜsɪɴɢ `remove.bg` ᴀᴘɪ
⍟ /ud `<ǫᴜᴇʀʏ>` *:* sᴇᴀʀᴄʜs ᴛʜᴇ ɢɪᴠᴇɴ ᴛᴇxᴛ ᴏɴ ᴜʀʙᴀɴ ᴅɪᴄᴛɪᴏɴᴀʀʏ ᴀɴᴅ sᴇɴᴅs ʏᴏᴜ ᴛʜᴇ ɪɴғᴏʀᴍᴀᴛɪᴏɴ.
⍟ /wiki `<ǫᴜᴇʀʏ>` *:* sᴇᴀʀᴄʜs ᴀʙᴏᴜᴛ ᴛʜᴇ ɢɪᴠᴇɴ ᴛᴇxᴛ ᴏɴ ᴡɪᴋɪᴘᴇᴅɪᴀ.
ʀᴇᴠᴇʀsᴇ sᴇᴀʀᴄʜ ᴀɴʏ ɪᴍᴀɢᴇ ᴜsɪɴɢ ɢᴏᴏɢʟᴇ ɪᴍᴀɢᴇ sᴇᴀʀᴄʜ.

*ᴜsᴀɢᴇ:*
⍟ sᴇɴᴅɪɴɢ /reverse ʙʏ ʀᴇᴘʟʏɪɴɢ ᴛᴏ ᴀɴʏ ɪᴍᴀɢᴇ
⍟ /reverse ᴛʜᴇɴ ᴜʀʟ 
"""

__mod_name__ = "𝐆ᴏᴏɢʟᴇ"
