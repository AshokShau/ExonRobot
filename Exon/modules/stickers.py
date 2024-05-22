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
import math
import os
import textwrap
import urllib.request as urllib
from html import escape
from urllib.parse import quote as urlquote

import cv2
import ffmpeg
from io import BytesIO
from bs4 import BeautifulSoup
from cloudscraper import CloudScraper
from PIL import Image, ImageDraw, ImageFont
from telegram import (
    Bot,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ParseMode,
    TelegramError,
    Update,
)
from telegram.ext import CallbackContext, CallbackQueryHandler, CommandHandler
from telegram.utils.helpers import mention_html

from Exon import dispatcher
from Exon import telethn as bot
from Exon.events import register as asux

combot_stickers_url = "https://combot.org/telegram/stickers?q="

def sticker_count(bot: Bot, pname: str) -> int:
    resp = bot._request.post(
        f"{bot.base_url}/getStickerSet",
        {
            "name": pname,
        },
    )
    return len(resp["stickers"])

def convert_gif(input):
    """ғᴜɴᴄᴛɪᴏɴ ᴛᴏ ᴄᴏɴᴠᴇʀᴛ ᴍᴘ4 ᴛᴏ ᴡᴇʙᴍ(ᴠᴘ9)!(ᴀʙɪsʜɴᴏɪ)"""

    vid = cv2.VideoCapture(input)
    height = vid.get(cv2.CAP_PROP_FRAME_HEIGHT)
    width = vid.get(cv2.CAP_PROP_FRAME_WIDTH)

    # check height and width to scale
    if width > height:
        width = 512
        height = -1
    elif height > width:
        height = 512
        width = -1
    elif width == height:
        width = 512
        height = 512

    converted_name = "kangsticker.webm"

    (
        ffmpeg.input(input)
        .filter("fps", fps=30, round="up")
        .filter("scale", width=width, height=height)
        .trim(start="00:00:00", end="00:00:03", duration="3")
        .output(
            converted_name,
            vcodec="libvpx-vp9",
            **{
                #'vf': 'scale=512:-1',
                "crf": "30"
            },
        )
        .overwrite_output()
        .run()
    )

    return converted_name


def stickerid(update: Update, context: CallbackContext):
    msg = update.effective_message
    if msg.reply_to_message and msg.reply_to_message.sticker:
        update.effective_message.reply_text(
            "ʜᴇʟʟᴏ "
            + f"{mention_html(msg.from_user.id, msg.from_user.first_name)}"
            + ", ᴛʜᴇ sᴛɪᴄᴋᴇʀ ɪᴅ ʏᴏᴜ ᴀʀᴇ ʀᴇᴘʟʏɪɴɢ ɪs:\n<code>"
            + escape(msg.reply_to_message.sticker.file_id)
            + "</code>",
            parse_mode=ParseMode.HTML,
        )
    else:
        update.effective_message.reply_text(
            "ʜᴇʟʟᴏ "
            + f"{mention_html(msg.from_user.id, msg.from_user.first_name)}"
            + ", ᴘʟᴇᴀsᴇ ʀᴇᴘʟʏ ᴛᴏ sᴛɪᴄᴋᴇʀ ᴍᴇssᴀɢᴇ ᴛᴏ ɢᴇᴛ ɪᴅ sᴛɪᴄᴋᴇʀ",
            parse_mode=ParseMode.HTML,
        )


scraper = CloudScraper()


def get_cbs_data(query, page, user_id):
    # returns (text, buttons)
    text = scraper.get(f"{combot_stickers_url}{urlquote(query)}&page={page}").text
    soup = BeautifulSoup(text, "lxml")
    div = soup.find("div", class_="page__container")
    packs = div.find_all("a", class_="sticker-pack__btn")
    titles = div.find_all("div", "sticker-pack__title")
    has_prev_page = has_next_page = None
    highlighted_page = div.find("a", class_="pagination__link is-active")
    if highlighted_page is not None and user_id is not None:
        highlighted_page = highlighted_page.parent
        has_prev_page = highlighted_page.previous_sibling.previous_sibling is not None
        has_next_page = highlighted_page.next_sibling.next_sibling is not None
    buttons = []
    if has_prev_page:
        buttons.append(
            InlineKeyboardButton(text="⟨", callback_data=f"cbs_{page - 1}_{user_id}")
        )
    if has_next_page:
        buttons.append(
            InlineKeyboardButton(text="⟩", callback_data=f"cbs_{page + 1}_{user_id}")
        )
    buttons = InlineKeyboardMarkup([buttons]) if buttons else None
    text = f"sᴛɪᴄᴋᴇʀs ғᴏʀ <code>{escape(query)}</code>:\nᴘᴀɢᴇ: {page}"
    if packs and titles:
        for pack, title in zip(packs, titles):
            link = pack["href"]
            text += f"\n• <a href='{link}'>{escape(title.get_text())}</a>"
    elif page == 1:
        text = "ɴᴏ ʀᴇsᴜʟᴛs ғᴏᴜɴᴅ, ᴛʀʏ ᴀ ᴅɪғғᴇʀᴇɴᴛ ᴛᴇʀᴍ"
    else:
        text += "\n\nɪɴᴛᴇʀᴇsᴛɪɴɢʟʏ, ᴛʜᴇʀᴇ's  ɴᴏᴛʜɪɴɢ ʜᴇʀᴇ."
    return text, buttons


def cb_sticker(update: Update, context: CallbackContext):
    msg = update.effective_message
    query = " ".join(msg.text.split()[1:])
    if not query:
        msg.reply_text("ᴘʀᴏᴠɪᴅᴇ sᴏᴍᴇ ᴛᴇʀᴍ ᴛᴏ sᴇᴀʀᴄʜ ғᴏʀ ᴀ sᴛɪᴄᴋᴇʀ ᴘᴀᴄᴋ.")
        return
    if len(query) > 50:
        msg.reply_text("ᴘʀᴏᴠɪᴅᴇ ᴀ sᴇᴀʀᴄʜ ǫᴜᴇʀʏ ᴜɴᴅᴇʀ 50 ᴄʜᴀʀᴀᴄᴛᴇʀs")
        return
    user_id = msg.from_user.id if msg.from_user else None
    text, buttons = get_cbs_data(query, 1, user_id)
    msg.reply_text(text, parse_mode=ParseMode.HTML, reply_markup=buttons)


def cbs_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    _, page, user_id = query.data.split("_", 2)
    if int(user_id) != query.from_user.id:
        query.answer("ɴᴏᴛ ғᴏʀ ʏᴏᴜ", cache_time=60 * 60)
        return
    search_query = query.message.text.split("\n", 1)[0].split(maxsplit=2)[2][:-1]
    text, buttons = get_cbs_data(search_query, int(page), query.from_user.id)
    query.edit_message_text(text, parse_mode=ParseMode.HTML, reply_markup=buttons)
    query.answer()


def getsticker(update: Update, context: CallbackContext):
    msg = update.effective_message
    if msg.reply_to_message and msg.reply_to_message.sticker:
        file_id = msg.reply_to_message.sticker.file_id
        bot = context.bot
        is_anim = msg.reply_to_message.sticker.is_animated
        sticker_data = bot.get_file(file_id).download(out=BytesIO())
        sticker_data.seek(0)
        filename = "animated_sticker.tgs.hmm_" if is_anim else "sticker.png"
        
        bot.send_document(
            update.effective_chat.id,
            document=sticker_data,
            filename=filename,
        )

    else:
        update.effective_message.reply_text(
            "ᴘʟᴇᴀsᴇ ʀᴇᴘʟʏ ᴛᴏ ᴀ sᴛɪᴄᴋᴇʀ ғᴏʀ ᴍᴇ ᴛᴏ ᴜᴘʟᴏᴀᴅ ɪᴛs PNG.",
        )


def kang(update, context):
    msg = update.effective_message
    args = context.args
    packnum = 0
    user = update.effective_user
    packname = f"a{str(user.id)}_by_{context.bot.username}"
    packname_found = 0
    max_stickers = 120

    while packname_found == 0:
        try:
            if sticker_count(context.bot, packname) >= max_stickers:
                packnum += 1
                packname = f"a{str(packnum)}_{str(user.id)}_by_{context.bot.username}"
            else:
                packname_found = 1
        except TelegramError as e:
            if e.message == "Stickerset_invalid":
                packname_found = 1

    kangsticker = "kangsticker.png"
    is_animated = False
    is_video = False
    # convert gif method
    is_gif = False
    file_id = ""

    if msg.reply_to_message:
        if msg.reply_to_message.sticker:
            if msg.reply_to_message.sticker.is_animated:
                is_animated = True
            elif msg.reply_to_message.sticker.is_video:
                is_video = True
            file_id = msg.reply_to_message.sticker.file_id
        elif msg.reply_to_message.photo:
            file_id = msg.reply_to_message.photo[-1].file_id
        elif (
            msg.reply_to_message.document
            and msg.reply_to_message.document.mime_type != "video/mp4"
        ):
            file_id = msg.reply_to_message.document.file_id
        elif msg.reply_to_message.animation:
            file_id = msg.reply_to_message.animation.file_id
            is_gif = True
        else:
            msg.reply_text("ʏᴇᴀ, ɪ ᴄᴀɴ'ᴛ ᴋᴀɴɢ ᴛʜᴀᴛ.")
        kang_file = context.bot.get_file(file_id)
        if not is_animated and not is_video and not is_gif:
            kang_file.download("kangsticker.png")
        elif is_animated:
            kang_file.download("kangsticker.tgs")
        elif is_video and not is_gif:
            kang_file.download("kangsticker.webm")
        else:
            kang_file.download("kang.mp4")
            convert_gif("kang.mp4")

        if args:
            sticker_emoji = str(args[0])
        elif msg.reply_to_message.sticker and msg.reply_to_message.sticker.emoji:
            sticker_emoji = msg.reply_to_message.sticker.emoji
        else:
            sticker_emoji = "🙂"

        adding_process = msg.reply_text(
            "<b>ᴘʟᴇᴀsᴇ ᴡᴀɪᴛ...ғᴏʀ ᴀ ᴍᴏᴍᴇɴᴛ</b>",
            parse_mode=ParseMode.HTML,
        )

        if not is_animated and not is_video and not is_gif:
            try:
                im = Image.open(kangsticker)
                maxsize = (512, 512)
                if (im.width and im.height) < 512:
                    size1 = im.width
                    size2 = im.height
                    if im.width > im.height:
                        scale = 512 / size1
                        size1new = 512
                        size2new = size2 * scale
                    else:
                        scale = 512 / size2
                        size1new = size1 * scale
                        size2new = 512
                    size1new = math.floor(size1new)
                    size2new = math.floor(size2new)
                    sizenew = (size1new, size2new)
                    im = im.resize(sizenew)
                else:
                    im.thumbnail(maxsize)
                if not msg.reply_to_message.sticker:
                    im.save(kangsticker, "PNG")
                context.bot.add_sticker_to_set(
                    user_id=user.id,
                    name=packname,
                    png_sticker=open("kangsticker.png", "rb"),
                    emojis=sticker_emoji,
                )
                edited_keyboard = InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                text="⎋ ᴘᴀᴄᴋ ⎋", url=f"t.me/addstickers/{packname}"
                            )
                        ]
                    ]
                )
                adding_process.edit_text(
                    f"<b>ʏᴏᴜʀ sᴛɪᴄᴋᴇʀ ʜᴀs ʙᴇᴇɴ ᴀᴅᴅᴇᴅ!</b>"
                    f"\nᴇᴍᴏᴊɪ ɪs ➼ : {sticker_emoji}",
                    reply_markup=edited_keyboard,
                    parse_mode=ParseMode.HTML,
                )

            except OSError as e:
                print(e)
                return

            except TelegramError as e:
                if (
                    e.message
                    == "Internal Server Error: sticker set not found (500)"
                ):
                    edited_keyboard = InlineKeyboardMarkup(
                        [
                            [
                                InlineKeyboardButton(
                                    text="⎋ ᴘᴀᴄᴋ ⎋", url=f"t.me/addstickers/{packname}"
                                )
                            ]
                        ]
                    )
                    msg.reply_text(
                        f"<b>ʏᴏᴜʀ sᴛɪᴄᴋᴇʀ ʜᴀs ʙᴇᴇɴ ᴀᴅᴅᴇᴅ!</b>"
                        f"\nᴇᴍᴏᴊɪ ɪs ➼ : {sticker_emoji}",
                        reply_markup=edited_keyboard,
                        parse_mode=ParseMode.HTML,
                    )
                elif e.message == "Invalid sticker emojis":
                    msg.reply_text("Invalid emoji(s).")
                elif e.message == "Sticker_png_dimensions":
                    im.save(kangsticker, "PNG")
                    adding_process = msg.reply_text(
                        "<b>ᴡᴀɪᴛ.... ғᴏʀ ᴀ ᴍᴏᴍᴇɴᴛ ..</b>",
                        parse_mode=ParseMode.HTML,
                    )
                    context.bot.add_sticker_to_set(
                        user_id=user.id,
                        name=packname,
                        png_sticker=open("kangsticker.png", "rb"),
                        emojis=sticker_emoji,
                    )
                    edited_keyboard = InlineKeyboardMarkup(
                        [
                            [
                                InlineKeyboardButton(
                                    text="⎋ ᴘᴀᴄᴋ ⎋", url=f"t.me/addstickers/{packname}"
                                )
                            ]
                        ]
                    )
                    adding_process.edit_text(
                        f"<b>ʏᴏᴜʀ sᴛɪᴄᴋᴇʀ ʜᴀs ʙᴇᴇɴ ᴀᴅᴅᴇᴅ!</b>"
                        f"\nᴇᴍᴏᴊɪ ɪs ➼ : {sticker_emoji}",
                        reply_markup=edited_keyboard,
                        parse_mode=ParseMode.HTML,
                    )
                elif e.message == "Stickers_too_much":
                    msg.reply_text("Max packsize reached. Press F to pay respecc.")
                elif e.message == "Stickerset_invalid":
                    makepack_internal(
                        update,
                        context,
                        msg,
                        user,
                        sticker_emoji,
                        packname,
                        packnum,
                        png_sticker=open("kangsticker.png", "rb"),
                    )
                    adding_process.delete()
                print(e)

        elif is_animated:
            packname = f"animated{str(user.id)}_by_{context.bot.username}"
            packname_found = 0
            max_stickers = 50
            while packname_found == 0:
                try:
                    if sticker_count(context.bot, packname) >= max_stickers:
                        packnum += 1
                        packname = f"animated{str(packnum)}_{str(user.id)}_by_{context.bot.username}"
                    else:
                        packname_found = 1
                except TelegramError as e:
                    if e.message == "Stickerset_invalid":
                        packname_found = 1
            try:
                context.bot.add_sticker_to_set(
                    user_id=user.id,
                    name=packname,
                    tgs_sticker=open("kangsticker.tgs", "rb"),
                    emojis=sticker_emoji,
                )
                edited_keyboard = InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                text="⎋ ᴘᴀᴄᴋ ⎋", url=f"t.me/addstickers/{packname}"
                            )
                        ]
                    ]
                )
                adding_process.edit_text(
                    f"<b>ʏᴏᴜʀ sᴛɪᴄᴋᴇʀ ʜᴀs ʙᴇᴇɴ ᴀᴅᴅᴇᴅ!</b>"
                    f"\nᴇᴍᴏᴊɪ ɪs ➼ : {sticker_emoji}",
                    reply_markup=edited_keyboard,
                    parse_mode=ParseMode.HTML,
                )
            except TelegramError as e:
                if (
                    e.message
                    == "Internal Server Error: sticker set not found (500)"
                ):
                    edited_keyboard = InlineKeyboardMarkup(
                        [
                            [
                                InlineKeyboardButton(
                                    text="⎋ ᴘᴀᴄᴋ ⎋", url=f"t.me/addstickers/{packname}"
                                )
                            ]
                        ]
                    )
                    adding_process.edit_text(
                        f"<b>ʏᴏᴜʀ sᴛɪᴄᴋᴇʀ ʜᴀs ʙᴇᴇɴ ᴀᴅᴅᴇᴅ!</b>"
                        f"\nᴇᴍᴏᴊɪ ɪs ➼ : {sticker_emoji}",
                        reply_markup=edited_keyboard,
                        parse_mode=ParseMode.HTML,
                    )
                elif e.message == "Invalid sticker emojis":
                    msg.reply_text("Invalid emoji(s).")
                elif e.message == "Stickerset_invalid":
                    makepack_internal(
                        update,
                        context,
                        msg,
                        user,
                        sticker_emoji,
                        packname,
                        packnum,
                        tgs_sticker=open("kangsticker.tgs", "rb"),
                    )
                    adding_process.delete()
                print(e)

        else:
            packname = f"video{str(user.id)}_by_{context.bot.username}"
            packname_found = 0
            max_stickers = 50
            while packname_found == 0:
                try:
                    if sticker_count(context.bot, packname) >= max_stickers:
                        packnum += 1
                        packname = (
                            "video"
                            + str(packnum)
                            + "_"
                            + str(user.id)
                            + "_by_"
                            + context.bot.username
                        )
                    else:
                        packname_found = 1
                except TelegramError as e:
                    if e.message == "Stickerset_invalid":
                        packname_found = 1
            try:
                context.bot.add_sticker_to_set(
                    user_id=user.id,
                    name=packname,
                    webm_sticker=open("kangsticker.webm", "rb"),
                    emojis=sticker_emoji,
                )
                edited_keyboard = InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                text="⎋ ᴘᴀᴄᴋ ⎋", url=f"t.me/addstickers/{packname}"
                            )
                        ]
                    ]
                )
                adding_process.edit_text(
                    f"<b>ʏᴏᴜʀ sᴛɪᴄᴋᴇʀ ʜᴀs ʙᴇᴇɴ ᴀᴅᴅᴇᴅ!</b>"
                    f"\nᴇᴍᴏᴊɪ ɪs ➼ : {sticker_emoji}",
                    reply_markup=edited_keyboard,
                    parse_mode=ParseMode.HTML,
                )
            except TelegramError as e:
                if (
                    e.message
                    == "Internal Server Error: sticker set not found (500)"
                ):
                    edited_keyboard = InlineKeyboardMarkup(
                        [
                            [
                                InlineKeyboardButton(
                                    text="⎋ ᴘᴀᴄᴋ ⎋", url=f"t.me/addstickers/{packname}"
                                )
                            ]
                        ]
                    )
                    adding_process.edit_text(
                        f"<b>ʏᴏᴜʀ sᴛɪᴄᴋᴇʀ ʜᴀs ʙᴇᴇɴ ᴀᴅᴅᴇᴅ!</b>"
                        f"\nᴇᴍᴏᴊɪ ɪs ➼ : {sticker_emoji}",
                        reply_markup=edited_keyboard,
                        parse_mode=ParseMode.HTML,
                    )
                elif e.message == "Invalid sticker emojis":
                    msg.reply_text("Invalid emoji(s).")
                elif e.message == "Stickerset_invalid":
                    makepack_internal(
                        update,
                        context,
                        msg,
                        user,
                        sticker_emoji,
                        packname,
                        packnum,
                        webm_sticker=open("kangsticker.webm", "rb"),
                    )
                    adding_process.delete()
                print(e)

    elif args:
        try:
            try:
                urlemoji = msg.text.split(" ")
                png_sticker = urlemoji[1]
                sticker_emoji = urlemoji[2]
            except IndexError:
                sticker_emoji = "🙃"
            urllib.urlretrieve(png_sticker, kangsticker)
            im = Image.open(kangsticker)
            maxsize = (512, 512)
            if (im.width and im.height) < 512:
                size1 = im.width
                size2 = im.height
                if im.width > im.height:
                    scale = 512 / size1
                    size1new = 512
                    size2new = size2 * scale
                else:
                    scale = 512 / size2
                    size1new = size1 * scale
                    size2new = 512
                size1new = math.floor(size1new)
                size2new = math.floor(size2new)
                sizenew = (size1new, size2new)
                im = im.resize(sizenew)
            else:
                im.thumbnail(maxsize)
            im.save(kangsticker, "PNG")
            msg.reply_photo(photo=open("kangsticker.png", "rb"))
            context.bot.add_sticker_to_set(
                user_id=user.id,
                name=packname,
                png_sticker=open("kangsticker.png", "rb"),
                emojis=sticker_emoji,
            )
            edited_keyboard = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text="⎋ ᴘᴀᴄᴋ ⎋", url=f"t.me/addstickers/{packname}"
                        )
                    ]
                ]
            )
            adding_process.edit_text(
                f"<b>ʏᴏᴜʀ sᴛɪᴄᴋᴇʀ ʜᴀs ʙᴇᴇɴ ᴀᴅᴅᴇᴅ!</b>"
                f"\nᴇᴍᴏᴊɪ ɪs ➼ : {sticker_emoji}",
                reply_markup=edited_keyboard,
                parse_mode=ParseMode.HTML,
            )
        except OSError as e:
            msg.reply_text(" sᴏʀʀʏ ɪ ᴄᴀɴ'ᴛ ᴋᴀɴɢ ᴛʜᴀᴛ.")
            print(e)
            return
        except TelegramError as e:
            if (
                e.message
                == "Internal Server Error: sticker set not found (500)"
            ):
                msg.reply_text(
                    f"<b>ʏᴏᴜʀ sᴛɪᴄᴋᴇʀ ʜᴀs ʙᴇᴇɴ ᴀᴅᴅᴇᴅ!</b>"
                    f"\nᴇᴍᴏᴊɪ ɪs ➼ : {sticker_emoji}",
                    reply_markup=edited_keyboard,
                    parse_mode=ParseMode.HTML,
                )
            elif e.message == "Invalid sticker emojis":
                msg.reply_text("Invalid emoji(s).")
            elif e.message == "Sticker_png_dimensions":
                im.save(kangsticker, "png")
                context.bot.add_sticker_to_set(
                    user_id=user.id,
                    name=packname,
                    png_sticker=open("kangsticker.png", "rb"),
                    emojis=sticker_emoji,
                )
                edited_keyboard = InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                text="⎋ ᴘᴀᴄᴋ ⎋", url=f"t.me/addstickers/{packname}"
                            )
                        ]
                    ]
                )
                adding_process.edit_text(
                    f"<b>ʏᴏᴜʀ sᴛɪᴄᴋᴇʀ ʜᴀs ʙᴇᴇɴ ᴀᴅᴅᴇᴅ!</b>"
                    f"\nᴇᴍᴏᴊɪ ɪs ➼ : {sticker_emoji}",
                    reply_markup=edited_keyboard,
                    parse_mode=ParseMode.HTML,
                )
            elif e.message == "Stickers_too_much":
                msg.reply_text("Max packsize reached. Press F to pay respect.")
            elif e.message == "Stickerset_invalid":
                makepack_internal(
                    update,
                    context,
                    msg,
                    user,
                    sticker_emoji,
                    packname,
                    packnum,
                    png_sticker=open("kangsticker.png", "rb"),
                )
                adding_process.delete()
            print(e)
    else:
        packs_text = "*ᴘʟᴇᴀsᴇ ʀᴇᴘʟʏ ᴛᴏ ᴀ sᴛɪᴄᴋᴇʀ, ᴏʀ ɪᴍᴀɢᴇ ᴛᴏ ᴋᴀɴɢ ɪᴛ!*\n"
        if packnum > 0:
            firstpackname = f"a{str(user.id)}_by_{context.bot.username}"
            for i in range(packnum + 1):
                if i == 0:
                    packs = f"t.me/addstickers/{firstpackname}"
                else:
                    packs = f"t.me/addstickers/{packname}"
        else:
            packs = f"t.me/addstickers/{packname}"

        edited_keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(text="sᴛɪᴄᴋᴇʀ ᴘᴀᴄᴋ", url=f"{packs}"),
                ],
            ]
        )
        msg.reply_text(
            packs_text, reply_markup=edited_keyboard, parse_mode=ParseMode.MARKDOWN
        )
    try:
        if os.path.isfile("kangsticker.png"):
            os.remove("kangsticker.png")
        elif os.path.isfile("kangsticker.tgs"):
            os.remove("kangsticker.tgs")
        elif os.path.isfile("kangsticker.webm"):
            os.remove("kangsticker.webm")
        elif os.path.isfile("kang.mp4"):
            os.remove("kang.mp4")
    except Exception:
        pass


def makepack_internal(
    update,
    context,
    msg,
    user,
    emoji,
    packname,
    packnum,
    png_sticker=None,
    tgs_sticker=None,
    webm_sticker=None,
):
    name = user.first_name
    name = name[:50]
    keyboard = InlineKeyboardMarkup(
        [[InlineKeyboardButton(text="⎋ ᴘᴀᴄᴋ ⎋", url=f"t.me/addstickers/{packname}")]]
    )
    try:
        extra_version = f" {str(packnum)}" if packnum > 0 else ""
        if png_sticker:
            sticker_pack_name = f"{name}'s sticker pack (@{context.bot.username}){extra_version}"
            success = context.bot.create_new_sticker_set(
                user.id,
                packname,
                sticker_pack_name,
                png_sticker=png_sticker,
                emojis=emoji,
            )
        if tgs_sticker:
            sticker_pack_name = f"{name}'s animated pack (@{context.bot.username}){extra_version}"
            success = context.bot.create_new_sticker_set(
                user.id,
                packname,
                sticker_pack_name,
                tgs_sticker=tgs_sticker,
                emojis=emoji,
            )
        if webm_sticker:
            sticker_pack_name = (
                f"{name}'s video pack (@{context.bot.username}){extra_version}"
            )
            success = context.bot.create_new_sticker_set(
                user.id,
                packname,
                sticker_pack_name,
                webm_sticker=webm_sticker,
                emojis=emoji,
            )

    except TelegramError as e:
        print(e)
        if e.message == "Sticker set name is already occupied":
            msg.reply_text(
                "<b>Your Sticker Pack is already created!</b>"
                "\n\nYou can now reply to images, stickers and animated sticker with /steal to add them to your pack"
                "\n\n<b>Send /stickers to find any sticker pack.</b>",
                reply_markup=keyboard,
                parse_mode=ParseMode.HTML,
            )
        else:
            msg.reply_text(
                f"{context.bot.first_name} was blocked by you.",
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                text="ᴜɴʙʟᴏᴄᴋ", url=f"t.me/{context.bot.username}"
                            )
                        ]
                    ]
                ),
            )
        return

    if success:
        msg.reply_text(
            "<b>Your Sticker Pack has been created!</b>"
            "\n\nYou can now reply to images, stickers and animated sticker with /steal to add them to your pack"
            "\n\n<b>Send /stickers to find sticker pack.</b>",
            reply_markup=keyboard,
            parse_mode=ParseMode.HTML,
        )
    else:
        msg.reply_text("Failed to create sticker pack. Possibly due to blek mejik.")


def getsticker(update: Update, context: CallbackContext):
    msg = update.effective_message
    if msg.reply_to_message and msg.reply_to_message.sticker:
        file_id = msg.reply_to_message.sticker.file_id
        bot = context.bot
        new_file = bot.get_file(file_id)
        new_file.download("sticker.png")
        chat_id = update.effective_chat.id
        bot.send_document(chat_id, document=open("sticker.png", "rb"))
        os.remove("sticker.png")
    else:
        update.effective_message.reply_text(
            "Please reply to a sticker for me to upload its PNG."
        )


def getvidsticker(update: Update, context: CallbackContext):
    msg = update.effective_message
    if msg.reply_to_message and msg.reply_to_message.sticker:
        file_id = msg.reply_to_message.sticker.file_id
        bot = context.bot
        new_file = bot.get_file(file_id)
        new_file.download("sticker.mp4")
        chat_id = update.effective_chat.id
        bot.send_video(chat_id, video=open("sticker.mp4", "rb"))
        os.remove("sticker.mp4")
    else:
        update.effective_message.reply_text(
            "Please reply to a video sticker to upload its MP4."
        )


def delsticker(update, context):
    msg = update.effective_message
    if msg.reply_to_message and msg.reply_to_message.sticker:
        file_id = msg.reply_to_message.sticker.file_id
        context.bot.delete_sticker_from_set(file_id)
        msg.reply_text("ᴅᴇʟᴇᴛᴇᴅ!")
    else:
        update.effective_message.reply_text(
            "Please reply to sticker message to del sticker"
        )


def video(update: Update, context: CallbackContext):
    msg = update.effective_message
    if msg.reply_to_message and msg.reply_to_message.animation:
        file_id = msg.reply_to_message.animation.file_id
        bot = context.bot
        new_file = bot.get_file(file_id)
        new_file.download("video.mp4")
        chat_id = update.effective_chat.id
        bot.send_video(chat_id, video=open("video.mp4", "rb"))
        os.remove("video.mp4")
    else:
        update.effective_message.reply_text(
            "Please reply to a gif for me to get it's video."
        )


Credit = "Abishnoi69"


@asux(pattern="^/mmf ?(.*)")
async def handler(event):
    if event.fwd_from:
        return

    if not event.reply_to_msg_id:
        await event.reply("Provide Some Text To Draw!")

        return

    reply_message = await event.get_reply_message()

    if not reply_message.media:
        await event.reply("```ʀᴇᴘʟʏ ᴛᴏ ᴀ ɪᴍᴀɢᴇ/sᴛɪᴄᴋᴇʀ.```")

        return

    file = await bot.download_media(reply_message)

    msg = await event.reply("```ᴍᴇᴍɪғʏɪɴɢ ᴛʜɪs ɪᴍᴀɢᴇ! 😉 ```")

    if "Abishnoi69" not in Credit:
        await event.reply("ᴛʜɪs ɴɪɢɢᴀ ʀᴇᴍᴏᴠᴇᴅ ᴄʀᴇᴅɪᴛ ʟɪɴᴇ ғʀᴏᴍ ᴄᴏᴅᴇ 😶")

    text = str(event.pattern_match.group(1)).strip()

    if not text:
        return await msg.reply("ʏᴏᴜ ᴍɪɢʜᴛ ᴡᴀɴᴛ ᴛᴏ ᴛʀʏ `/mmf text`")

    meme = await drawText(file, text)

    await bot.send_file(event.chat_id, file=meme, force_document=False)

    await msg.delete()

    os.remove(meme)


async def drawText(image_path, text):
    img = Image.open(image_path)

    os.remove(image_path)

    i_width, i_height = img.size

    fnt = "ariel.ttf" if os.name == "nt" else "./Exon/modules/resources/asu.ttf"
    m_font = ImageFont.truetype(fnt, int((70 / 640) * i_width))

    if ";" in text:
        upper_text, lower_text = text.split(";")

    else:
        upper_text = text

        lower_text = ""

    draw = ImageDraw.Draw(img)

    current_h, pad = 10, 5

    if upper_text:
        for u_text in textwrap.wrap(upper_text, width=15):
            u_width, u_height = draw.textsize(u_text, font=m_font)

            draw.text(
                xy=(((i_width - u_width) / 2) - 2, int((current_h / 640) * i_width)),
                text=u_text,
                font=m_font,
                fill=(0, 0, 0),
            )

            draw.text(
                xy=(((i_width - u_width) / 2) + 2, int((current_h / 640) * i_width)),
                text=u_text,
                font=m_font,
                fill=(0, 0, 0),
            )

            draw.text(
                xy=((i_width - u_width) / 2, int(((current_h / 640) * i_width)) - 2),
                text=u_text,
                font=m_font,
                fill=(0, 0, 0),
            )

            draw.text(
                xy=(((i_width - u_width) / 2), int(((current_h / 640) * i_width)) + 2),
                text=u_text,
                font=m_font,
                fill=(0, 0, 0),
            )

            draw.text(
                xy=((i_width - u_width) / 2, int((current_h / 640) * i_width)),
                text=u_text,
                font=m_font,
                fill=(255, 255, 255),
            )

            current_h += u_height + pad

    if lower_text:
        for l_text in textwrap.wrap(lower_text, width=15):
            u_width, u_height = draw.textsize(l_text, font=m_font)

            draw.text(
                xy=(
                    ((i_width - u_width) / 2) - 2,
                    i_height - u_height - int((20 / 640) * i_width),
                ),
                text=l_text,
                font=m_font,
                fill=(0, 0, 0),
            )

            draw.text(
                xy=(
                    ((i_width - u_width) / 2) + 2,
                    i_height - u_height - int((20 / 640) * i_width),
                ),
                text=l_text,
                font=m_font,
                fill=(0, 0, 0),
            )

            draw.text(
                xy=(
                    (i_width - u_width) / 2,
                    (i_height - u_height - int((20 / 640) * i_width)) - 2,
                ),
                text=l_text,
                font=m_font,
                fill=(0, 0, 0),
            )

            draw.text(
                xy=(
                    (i_width - u_width) / 2,
                    (i_height - u_height - int((20 / 640) * i_width)) + 2,
                ),
                text=l_text,
                font=m_font,
                fill=(0, 0, 0),
            )

            draw.text(
                xy=(
                    (i_width - u_width) / 2,
                    i_height - u_height - int((20 / 640) * i_width),
                ),
                text=l_text,
                font=m_font,
                fill=(255, 255, 255),
            )

            current_h += u_height + pad

    image_name = "memify.webp"

    webp_file = os.path.join(image_name)

    img.save(webp_file, "webp")

    return webp_file


__mod_name__ = "𝐒ᴛɪᴄᴋᴇʀ"


# ғᴏʀ ʜᴇʟᴘ ᴍᴇɴᴜ


# """
from Exon.modules.language import gs


def get_help(chat):
    return gs(chat, "sticker_help")


# """

STICKERID_HANDLER = CommandHandler("stickerid", stickerid, run_async=True)
GETSTICKER_HANDLER = CommandHandler("getsticker", getsticker, run_async=True)
GETVIDSTICKER_HANDLER = CommandHandler("getvidsticker", getvidsticker, run_async=True)
KANG_HANDLER = CommandHandler("kang", kang, pass_args=True, run_async=True)
DEL_HANDLER = CommandHandler("delsticker", delsticker, run_async=True)
STICKERS_HANDLER = CommandHandler("stickers", cb_sticker, run_async=True)
VIDEO_HANDLER = CommandHandler("getvideo", video, run_async=True)
CBSCALLBACK_HANDLER = CallbackQueryHandler(cbs_callback, pattern="cbs_", run_async=True)

dispatcher.add_handler(VIDEO_HANDLER)
dispatcher.add_handler(CBSCALLBACK_HANDLER)
dispatcher.add_handler(STICKERS_HANDLER)
dispatcher.add_handler(STICKERID_HANDLER)
dispatcher.add_handler(GETSTICKER_HANDLER)
dispatcher.add_handler(GETVIDSTICKER_HANDLER)
dispatcher.add_handler(KANG_HANDLER)
dispatcher.add_handler(DEL_HANDLER)
