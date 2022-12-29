import math
import os
import urllib.request as urllib
from html import escape

import cv2
import ffmpeg
from bs4 import BeautifulSoup as bs
from httpx import AsyncClient
from PIL import Image
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Message, Update, User
from telegram.constants import ParseMode
from telegram.error import BadRequest, TelegramError
from telegram.ext import ContextTypes
from telegram.helpers import mention_html

from Exon import LOGGER, application
from Exon.modules.disable import DisableAbleCommandHandler

combot_stickers_url = "https://combot.org/telegram/stickers?q="


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


async def stickerid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.effective_message
    if (
        msg.reply_to_message
        and msg.reply_to_message.sticker
        and not msg.reply_to_message.forum_topic_created
    ):
        await update.effective_message.reply_text(
            "ʜᴇʟʟᴏ "
            + f"{mention_html(msg.from_user.id, msg.from_user.first_name)}"
            + ", ᴛʜᴇ sᴛɪᴄᴋᴇʀ ɪᴅ ʏᴏᴜ ᴀʀᴇ ʀᴇᴘʟʏɪɴɢ ɪs :\n <code>"
            + escape(msg.reply_to_message.sticker.file_id)
            + "</code>",
            parse_mode=ParseMode.HTML,
        )
    else:
        await update.effective_message.reply_text(
            "ʜᴇʟʟᴏ "
            + f"{mention_html(msg.from_user.id, msg.from_user.first_name)}"
            + ", ᴘʟᴇᴀsᴇ ʀᴇᴘʟʏ ᴛᴏ sᴛɪᴄᴋᴇʀ ᴍᴇssᴀɢᴇ ᴛᴏ ɢᴇᴛ ɪᴅ sᴛɪᴄᴋᴇʀ",
            parse_mode=ParseMode.HTML,
        )


async def cb_sticker(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.effective_message
    split = msg.text.split(" ", 1)
    if len(split) == 1:
        await msg.reply_text("ᴘʀᴏᴠɪᴅᴇ sᴏᴍᴇ ɴᴀᴍᴇ ᴛᴏ sᴇᴀʀᴄʜ ғᴏʀ ᴘᴀᴄᴋ.")
        return
    async with AsyncClient() as client:
        r = await client.get(combot_stickers_url + split[1])
    text = r.text
    soup = bs(text, "lxml")
    results = soup.find_all("a", {"class": "sticker-pack__btn"})
    titles = soup.find_all("div", "sticker-pack__title")
    if not results:
        await msg.reply_text("ɴᴏ ʀᴇsᴜʟᴛs ғᴏᴜɴᴅ :(.")
        return
    reply = f"sᴛɪᴄᴋᴇʀs ғᴏʀ *{split[1]}*:"
    for result, title in zip(results, titles):
        link = result["href"]
        reply += f"\n• [{title.get_text()}]({link})"
    await msg.reply_text(reply, parse_mode=ParseMode.MARKDOWN)


async def getsticker(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bot = context.bot
    msg = update.effective_message
    chat = update.effective_chat
    user = update.effective_user
    if msg.reply_to_message and msg.reply_to_message.sticker:
        file_id = msg.reply_to_message.sticker.file_id
        new_file = await bot.get_file(file_id)
        await new_file.download_to_drive(f"sticker_{user.id}.png")
        await bot.send_document(
            chat.id,
            document=open(f"sticker_{user.id}.png", "rb"),
            reply_to_message_id=msg.message_id,
            message_thread_id=msg.message_thread_id if chat.is_forum else None,
        )
        os.remove(f"sticker_{user.id}.png")
    else:
        await update.effective_message.reply_text(
            "ᴘʟᴇᴀsᴇ ʀᴇᴘʟʏ ᴛᴏ ᴀ sᴛɪᴄᴋᴇʀ ғᴏʀ ᴍᴇ ᴛᴏ ᴜᴘʟᴏᴀᴅ ɪᴛs PNG.",
        )


async def kang(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.effective_message
    user = update.effective_user
    args = context.args
    packnum = 0
    packname = "a" + str(user.id) + "_by_" + context.bot.username
    packname_found = 0
    max_stickers = 120
    while packname_found == 0:
        try:
            stickerset = await context.bot.get_sticker_set(packname)
            if len(stickerset.stickers) >= max_stickers:
                packnum += 1
                packname = (
                    "a"
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
    kangsticker = f"kangsticker_{user.id}.png"
    is_animated = False
    is_video = False
    is_gif = False
    file_id = ""

    if msg.reply_to_message and not msg.reply_to_message.forum_topic_created:
        if msg.reply_to_message.sticker:
            if msg.reply_to_message.sticker.is_animated:
                is_animated = True
            elif msg.reply_to_message.sticker.is_video:
                is_video = True
            file_id = msg.reply_to_message.sticker.file_id

        elif msg.reply_to_message.photo:
            file_id = msg.reply_to_message.photo[-1].file_id
        elif msg.reply_to_message.document == "video/mp4":
            file_id = msg.reply_to_message.document.file_id
        elif msg.reply_to_message.animation:
            file_id = msg.reply_to_message.animation.file_id
            is_gif = True
        else:
            await msg.reply_text("ʏᴇᴀ, ɪ ᴄᴀɴ'ᴛ ᴋᴀɴɢ ᴛʜᴀᴛ .")

        kang_file = await context.bot.get_file(file_id)
        if not is_animated and not (is_video or is_gif):
            await kang_file.download_to_drive(f"kangsticker_{user.id}.png")
        elif is_animated:
            await kang_file.download_to_drive(f"kangsticker_{user.id}.tgs")
        elif is_video and not is_gif:
            await kang_file.download_to_drive(f"kangsticker_{user.id}.webm")
        elif is_gif:
            await kang_file.download_to_drive(f"kang_{user.id}.mp4")
            convert_gif(f"kang_{user.id}.mp4")

        if args:
            sticker_emoji = str(args[0])
        elif msg.reply_to_message.sticker and msg.reply_to_message.sticker.emoji:
            sticker_emoji = msg.reply_to_message.sticker.emoji
        else:
            sticker_emoji = "🤗"

        if not is_animated and not (is_video or is_gif):
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
                await context.bot.add_sticker_to_set(
                    user_id=user.id,
                    name=packname,
                    png_sticker=open(f"kangsticker_{user.id}.png", "rb"),
                    emojis=sticker_emoji,
                )
                await msg.reply_text(
                    f"sᴛɪᴄᴋᴇʀ sᴜᴄᴄᴇssғᴜʟʟʏ ᴀᴅᴅᴇᴅ ᴛᴏ [pack](t.me/addstickers/{packname})"
                    + f"\nᴇᴍᴏᴊɪ ɪs: {sticker_emoji}",
                    parse_mode=ParseMode.MARKDOWN,
                )

            except OSError as e:
                await msg.reply_text("I ᴄᴀɴ ᴏɴʟʏ ᴋᴀɴɢ ɪᴍᴀɢᴇs ᴍ8.")
                LOGGER.error(e)
                return

            except TelegramError as e:
                if e.message == "Stickerset_invalid":
                    await makepack_internal(
                        update,
                        context,
                        msg,
                        user,
                        sticker_emoji,
                        packname,
                        packnum,
                        png_sticker=open(f"kangsticker_{user.id}.png", "rb"),
                    )
                elif e.message == "Sticker_png_dimensions":
                    im.save(kangsticker, "PNG")
                    await context.bot.add_sticker_to_set(
                        user_id=user.id,
                        name=packname,
                        png_sticker=open(f"kangsticker_{user.id}.png", "rb"),
                        emojis=sticker_emoji,
                    )
                    await msg.reply_text(
                        f"sᴛɪᴄᴋᴇʀ sᴜᴄᴄᴇssғᴜʟʟʏ ᴀᴅᴅᴇᴅ ᴛᴏ [ᴘᴀᴄᴋ](t.me/addstickers/{packname})"
                        + f"\nᴇᴍᴏᴊɪ ɪs: {sticker_emoji}",
                        parse_mode=ParseMode.MARKDOWN,
                    )
                elif e.message == "Invalid sticker emojis":
                    await msg.reply_text("ɪɴᴠᴀʟɪᴅ ᴇᴍᴏᴊɪ(s).")
                elif e.message == "Stickers_too_much":
                    await msg.reply_text(
                        "ᴍᴀx ᴘᴀᴄᴋsɪᴢᴇ ʀᴇᴀᴄʜᴇᴅ. ᴘʀᴇss ғ ᴛᴏ ᴘᴀʏ ʀᴇsᴘᴇᴄᴄ."
                    )
                elif e.message == "Internal Server Error: sticker set not found (500)":
                    await msg.reply_text(
                        "sᴛɪᴄᴋᴇʀ sᴜᴄᴄᴇssғᴜʟʟʏ ᴀᴅᴅᴇᴅ ᴛᴏ [ᴘᴀᴄᴋ](t.me/addstickers/%s)"
                        % packname
                        + "\n"
                        "ᴇᴍᴏᴊɪ ɪs:" + " " + sticker_emoji,
                        parse_mode=ParseMode.MARKDOWN,
                    )
                LOGGER.error(e)

        elif is_animated:
            packname = "ᴀɴɪᴍᴀᴛᴇᴅ" + str(user.id) + "_ʙʏ_" + context.bot.username
            packname_found = 0
            max_stickers = 50
            while packname_found == 0:
                try:
                    stickerset = await context.bot.get_sticker_set(packname)
                    if len(stickerset.stickers) >= max_stickers:
                        packnum += 1
                        packname = (
                            "animated"
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
                await context.bot.add_sticker_to_set(
                    user_id=user.id,
                    name=packname,
                    tgs_sticker=open(f"kangsticker_{user.id}.tgs", "rb"),
                    emojis=sticker_emoji,
                )
                await msg.reply_text(
                    f"sᴛɪᴄᴋᴇʀ sᴜᴄᴄᴇssғᴜʟʟʏ ᴀᴅᴅᴇᴅ ᴛᴏ [ᴘᴀᴄᴋ](t.me/addstickers/{packname})"
                    + f"\nᴇᴍᴏᴊɪ ɪs: {sticker_emoji}",
                    parse_mode=ParseMode.MARKDOWN,
                )
            except TelegramError as e:
                if e.message == "Stickerset_invalid":
                    await makepack_internal(
                        update,
                        context,
                        msg,
                        user,
                        sticker_emoji,
                        packname,
                        packnum,
                        tgs_sticker=open(f"kangsticker_{user.id}.tgs", "rb"),
                    )
                elif e.message == "Invalid sticker emojis":
                    await msg.reply_text("Invalid emoji(s).")
                elif e.message == "ɪɴᴛᴇʀɴᴀʟ sᴇʀᴠᴇʀ ᴇʀʀᴏʀ: sᴛɪᴄᴋᴇʀ sᴇᴛ ɴᴏᴛ ғᴏᴜɴᴅ (500)":
                    await msg.reply_text(
                        "sᴛɪᴄᴋᴇʀ sᴜᴄᴄᴇssғᴜʟʟʏ ᴀᴅᴅᴇᴅ ᴛᴏ [ᴘᴀᴄᴋ](t.me/addstickers/%s)"
                        % packname
                        + "\n"
                        "ᴇᴍᴏᴊɪ ɪs:" + " " + sticker_emoji,
                        parse_mode=ParseMode.MARKDOWN,
                    )
                LOGGER.error(e)

        elif is_video or is_gif:
            packname = "ᴠɪᴅᴇᴏ" + str(user.id) + "_ʙʏ_" + context.bot.username
            packname_found = 0
            max_stickers = 120

            while packname_found == 0:
                try:
                    stickerset = await context.bot.get_sticker_set(packname)
                    if len(stickerset.stickers) >= max_stickers:
                        packnum += 1
                        packname = (
                            "ᴀɴɪᴍᴀᴛᴇᴅ"
                            + str(packnum)
                            + "_"
                            + str(user.id)
                            + "_ʙʏ_"
                            + context.bot.username
                        )

                    else:
                        packname_found = 1
                except TelegramError as e:
                    if e.message == "Stickerset_invalid":
                        packname_found = 1

            try:
                await context.bot.add_sticker_to_set(
                    user_id=user.id,
                    name=packname,
                    webm_sticker=open(f"kangsticker_{user.id}.webm", "rb"),
                    emojis=sticker_emoji,
                )
                await msg.reply_text(
                    f"sᴛɪᴄᴋᴇʀ sᴜᴄᴄᴇssғᴜʟʟʏ ᴀᴅᴅᴇᴅ ᴛᴏ [ᴘᴀᴄᴋ](t.me/addstickers/{packname})"
                    + f"\nᴇᴍᴏᴊɪ ɪs: {sticker_emoji}",
                    parse_mode=ParseMode.MARKDOWN,
                )

            except TelegramError as e:
                if e.message == "Stickerset_invalid":
                    await makepack_internal(
                        update,
                        context,
                        msg,
                        user,
                        sticker_emoji,
                        packname,
                        packnum,
                        webm_sticker=open(f"kangsticker_{user.id}.webm", "rb"),
                    )
                elif e.message == "Invalid sticker emojis":
                    await msg.reply_text("ɪɴᴠᴀʟɪᴅ ᴇᴍᴏᴊɪ(s)")
                elif e.message == "ɪɴᴛᴇʀɴᴀʟ sᴇʀᴠᴇʀ ᴇʀʀᴏʀ: sᴛɪᴄᴋᴇʀ sᴇᴛ ɴᴏᴛ ғᴏᴜɴᴅ (500)":
                    await msg.reply_text(
                        f"sᴛɪᴄᴋᴇʀ sᴜᴄᴄᴇssғᴜʟʟʏ ᴀᴅᴅᴇᴅ ᴛᴏ [ᴘᴀᴄᴋ](t.me/addsticker/{packname})",
                        +"\n" f"ᴇᴍᴏᴊɪ ɪs: {sticker_emoji}",
                        parse_mode=ParseMode.MARKDOWN,
                    )

    elif args:
        try:
            try:
                urlemoji = msg.text.split(" ")
                png_sticker = urlemoji[1]
                sticker_emoji = urlemoji[2]
            except IndexError:
                sticker_emoji = "🃏"
            try:
                urllib.urlretrieve(png_sticker, kangsticker)
            except ValueError:
                msg.reply_text("ᴘʟᴇᴀsᴇ ᴘʀᴏᴠɪᴅᴇ ᴠᴀʟɪᴅ ɪᴍᴀɢᴇ ᴜʀʟ.")
                return
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
            await msg.reply_photo(photo=open(f"kangsticker_{user.id}.png", "rb"))
            await context.bot.add_sticker_to_set(
                user_id=user.id,
                name=packname,
                png_sticker=open(f"kangsticker_{user.id}.png", "rb"),
                emojis=sticker_emoji,
            )
            await msg.reply_text(
                f"sᴛɪᴄᴋᴇʀ sᴜᴄᴄᴇssғᴜʟʟʏ ᴀᴅᴅᴇᴅ ᴛᴏ [ᴘᴀᴄᴋ](t.me/addstickers/{packname})"
                + f"\nᴇᴍᴏᴊɪ ɪs: {sticker_emoji}",
                parse_mode=ParseMode.MARKDOWN,
            )
        except OSError as e:
            await msg.reply_text("I ᴄᴀɴ ᴏɴʟʏ ᴋᴀɴɢ ɪᴍᴀɢᴇs m8.")
            LOGGER.error(e)
            return
        except TelegramError as e:
            if e.message == "Stickerset_invalid":
                await makepack_internal(
                    update,
                    context,
                    msg,
                    user,
                    sticker_emoji,
                    packname,
                    packnum,
                    png_sticker=open(f"kangsticker_{user.id}.png", "rb"),
                )
            elif e.message == "Sticker_png_dimensions":
                im.save(kangsticker, "PNG")
                await context.bot.add_sticker_to_set(
                    user_id=user.id,
                    name=packname,
                    png_sticker=open(f"kangsticker_{user.id}.png", "rb"),
                    emojis=sticker_emoji,
                )
                await msg.reply_text(
                    "sᴛɪᴄᴋᴇʀ sᴜᴄᴄᴇssғᴜʟʟʏ ᴀᴅᴅᴇᴅ ᴛᴏ [ᴘᴀᴄᴋ](t.me/addstickers/%s)"
                    % packname
                    + "\n"
                    + "ᴇᴍᴏᴊɪ ɪs:"
                    + " "
                    + sticker_emoji,
                    parse_mode=ParseMode.MARKDOWN,
                )
            elif e.message == "Invalid sticker emojis":
                await msg.reply_text("ɪɴᴠᴀʟɪᴅ ᴇᴍᴏᴊɪ(s).")
            elif e.message == "Stickers_too_much":
                await msg.reply_text("ᴍᴀx ᴘᴀᴄᴋsɪᴢᴇ ʀᴇᴀᴄʜᴇᴅ. ᴘʀᴇss F ᴛᴏ ᴘᴀʏ ʀᴇsᴘᴇᴄᴛ.")
            elif e.message == "ɪɴᴛᴇʀɴᴀʟ sᴇʀᴠᴇʀ ᴇʀʀᴏʀ: sᴛɪᴄᴋᴇʀ sᴇᴛ ɴᴏᴛ ғᴏᴜɴᴅ (500)":
                await msg.reply_text(
                    "sᴛɪᴄᴋᴇʀ sᴜᴄᴄᴇssғᴜʟʟʏ ᴀᴅᴅᴇᴅ ᴛᴏ [ᴘᴀᴄᴋ](t.me/addstickers/%s)"
                    % packname
                    + "\n"
                    "ᴇᴍᴏᴊɪ is:" + " " + sticker_emoji,
                    parse_mode=ParseMode.MARKDOWN,
                )
            LOGGER.error(e)
    else:
        packs = "ᴘʟᴇᴀsᴇ ʀᴇᴘʟʏ ᴛᴏ ᴀ sᴛɪᴄᴋᴇʀ, ᴏʀ ɪᴍᴀɢᴇ or ɢɪғ ᴛᴏ ᴋᴀɴɢ ɪᴛ!\nᴏʜ, ʙʏ ᴛʜᴇ ᴡᴀʏ. ʜᴇʀᴇ ᴀʀᴇ ʏᴏᴜʀ ᴘᴀᴄᴋs:\n"
        if packnum > 0:
            firstpackname = "a" + str(user.id) + "_ʙʏ_" + context.bot.username
            for i in range(0, packnum + 1):
                if i == 0:
                    packs += f"[ᴘᴀᴄᴋ](t.me/addstickers/{firstpackname})\n"
                else:
                    packs += f"[ᴘᴀᴄᴋ{i}](t.me/addstickers/{packname})\n"
        else:
            packs += f"[ᴘᴀᴄᴋ](t.me/addstickers/{packname})"
        await msg.reply_text(packs, parse_mode=ParseMode.MARKDOWN)
    try:
        if os.path.isfile(f"kangsticker_{user.id}.png"):
            os.remove(f"kangsticker_{user.id}.png")
        elif os.path.isfile(f"kangsticker_{user.id}.tgs"):
            os.remove(f"kangsticker_{user.id}.tgs")
        elif os.path.isfile(f"kangsticker_{user.id}.webm"):
            os.remove(f"kangsticker_{user.id}.webm")
        elif os.path.isfile(f"kang_{user.id}.mp4"):
            os.remove(f"kang_{user.id}.mp4")
    except:
        pass


async def delsticker(update: Update, context: ContextTypes.DEFAULT_TYPE):

    check = "_ʙʏ_" + context.bot.username

    if update.effective_message.reply_to_message is None:
        await update.effective_message.reply_text(
            "sᴏʀʀʏ ʙᴜᴛ ʏᴏᴜ ʜᴀᴠᴇ ᴛᴏ ʀᴇᴘʟʏ ᴛᴏ ᴀ sᴛɪᴄᴋᴇʀ ᴛᴏ ᴅᴇʟᴇᴛᴇ."
        )
        return
    elif update.effective_message.reply_to_message:
        if update.effective_message.reply_to_message.forum_topic_created:
            await update.effective_message.reply_text(
                "sᴏʀʀʏ ʙᴜᴛ ʏᴏᴜ ʜᴀᴠᴇ ᴛᴏ ʀᴇᴘʟʏ ᴛᴏ ᴀ sᴛɪᴄᴋᴇʀ ᴛᴏ ᴅᴇʟᴇᴛᴇ."
            )
            return

    sticker = update.effective_message.reply_to_message.sticker

    if sticker.set_name.endswith(check):  # check if the sticker set made by this bot
        try:
            await context.bot.delete_sticker_from_set(sticker.file_id)
        except BadRequest as e:
            if e.message == "Stickerset_not_modified":
                await update.effective_message.reply_text(
                    "I ᴡᴏɴᴅᴇʀ ʜᴏᴡ ʏᴏᴜ ᴄᴀɴ ᴜsᴇ ᴛʜᴀᴛ sᴛɪᴄᴋᴇʀ,\nI ᴄᴀɴ'ᴛ sᴇᴇᴍ ᴛᴏ ғɪɴᴅ ᴛʜᴀᴛ ᴏɴᴇ ɪɴ ᴛʜᴇ ᴘᴀᴄᴋ"
                )
            return
        await update.effective_message.reply_text("ᴅᴏɴᴇ ʙᴀʙʏ !")
        return

    else:
        await update.effective_message.reply_text(
            "I ᴄᴀɴ'ᴛ ᴅᴇʟᴇᴛᴇ ᴛʜᴀᴛ sᴛɪᴄᴋᴇʀ sɪɴᴄᴇ I ᴅɪᴅɴ'ᴛ ᴍᴀᴋᴇ ᴛʜᴀᴛ ᴏɴᴇ..."
        )
        return


async def makepack_internal(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    msg: Message,
    user: User,
    emoji,
    packname,
    packnum,
    png_sticker=None,
    tgs_sticker=None,
    webm_sticker=None,
):
    name = user.first_name
    name = name[:50]
    try:
        extra_version = ""
        if packnum > 0:
            extra_version = " " + str(packnum)
        if png_sticker:
            success = await context.bot.create_new_sticker_set(
                user.id,
                packname,
                f"{name}s ᴘᴀᴄᴋ" + extra_version,
                png_sticker=png_sticker,
                emojis=emoji,
            )
        if tgs_sticker:
            success = await context.bot.create_new_sticker_set(
                user.id,
                packname,
                f"{name}s ᴀɴɪᴍᴀᴛᴇᴅ ᴘᴀᴄᴋ" + extra_version,
                tgs_sticker=tgs_sticker,
                emojis=emoji,
            )
        if webm_sticker:
            success = await context.bot.create_new_sticker_set(
                user.id,
                packname,
                f"{name}s ᴠɪᴅᴇᴏ ᴘᴀᴄᴋ" + extra_version,
                webm_sticker=webm_sticker,
                emojis=emoji,
            )

    except TelegramError as e:
        LOGGER.error(e)
        if e.message == "sᴛɪᴄᴋᴇʀ sᴇᴛ ɴᴀᴍᴇ ɪs ᴀʟʀᴇᴀᴅʏ ᴏᴄᴄᴜᴘɪᴇᴅ ":
            await msg.reply_text(
                "ʏᴏᴜʀ ᴘᴀᴄᴋ ᴄᴀɴ ʙᴇ ғᴏᴜɴᴅ [ʜᴇʀᴇ](t.me/addstickers/%s)" % packname,
                parse_mode=ParseMode.MARKDOWN,
            )
        elif e.message in ("Peer_id_invalid", "ʙᴏᴛ ᴡᴀs ʙʟᴏᴄᴋᴇᴅ ʙʏ ᴛʜᴇ ᴜsᴇʀ"):
            await msg.reply_text(
                "ᴄᴏɴᴛᴀᴄᴛ ᴍᴇ ɪɴ ᴘᴍ ғɪʀsᴛ.",
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                text="sᴛᴀʀᴛ",
                                url=f"t.me/{context.bot.username}",
                            ),
                        ],
                    ],
                ),
            )
        elif e.message == "ɪɴᴛᴇʀɴᴀʟ sᴇʀᴠᴇʀ ᴇʀʀᴏʀ: ᴄʀᴇᴀᴛᴇᴅ sᴛɪᴄᴋᴇʀ sᴇᴛ ɴᴏᴛ ғᴏᴜɴᴅ (500)":
            await msg.reply_text(
                "sᴛɪᴄᴋᴇʀ ᴘᴀᴄᴋ sᴜᴄᴄᴇssғᴜʟʟʏ ᴄʀᴇᴀᴛᴇᴅ. ɢᴇᴛ ɪᴛ [ʜᴇʀᴇ](t.me/addstickers/%s)"
                % packname,
                parse_mode=ParseMode.MARKDOWN,
            )
        return

    if success:
        await msg.reply_text(
            "sᴛɪᴄᴋᴇʀ ᴘᴀᴄᴋ sᴜᴄᴄᴇssғᴜʟʟʏ ᴄʀᴇᴀᴛᴇᴅ. ɢᴇᴛ ɪᴛ [ʜᴇʀᴇ](t.me/addstickers/%s)"
            % packname,
            parse_mode=ParseMode.MARKDOWN,
        )
    else:
        await msg.reply_text(
            "ғᴀɪʟᴇᴅ ᴛᴏ ᴄʀᴇᴀᴛᴇ sᴛɪᴄᴋᴇʀ ᴘᴀᴄᴋ. ᴘᴏssɪʙʟʏ ᴅᴜᴇ ᴛᴏ ʙʟᴇᴋ ᴍᴇᴊɪᴋ."
        )


__help__ = """
• /stickerid*:* ʀᴇᴘʟʏ ᴛᴏ ᴀ sᴛɪᴄᴋᴇʀ ᴛᴏ ᴍᴇ ᴛᴏ ᴛᴇʟʟ ʏᴏᴜ ɪᴛs ғɪʟᴇ ID.
• /getsticker*:* ʀᴇᴘʟʏ ᴛᴏ ᴀ sᴛɪᴄᴋᴇʀ ᴛᴏ ᴍᴇ ᴛᴏ ᴜᴘʟᴏᴀᴅ ɪᴛs ʀᴀᴡ PNG ғɪʟᴇ.
• /delstcker*:* ʀᴇᴘʟʏ ᴛᴏ ᴀ sᴛɪᴄᴋᴇʀ ᴛᴏ ᴅᴇʟᴇᴛᴇ ɪᴛ ғʀᴏᴍ ᴛʜᴇ ᴘᴀᴄᴋ, I ᴄᴀɴ ᴅᴇʟᴇᴛᴇ ᴡʜᴀᴛ I ᴍᴀᴅᴇ ᴏɴʟʏ.
• /kang*:* ʀᴇᴘʟʏ ᴛᴏ sᴛɪᴄᴋᴇʀ (ᴀɴɪᴍᴀᴛᴇᴅ/sᴛᴀᴛɪᴄ/ᴠɪᴅᴇᴏ) ᴏʀ ɪᴍᴀɢᴇ ᴏʀ ɢɪғ ᴛᴏ ᴋᴀɴɢ ɪɴᴛᴏ *ʏᴏᴜʀ ᴏᴡɴ* ᴘᴀᴄᴋ.
• /stickers*:* ғɪɴᴅ sᴛɪᴄᴋᴇʀs ғᴏʀ ɢɪᴠᴇɴ ᴛᴇʀᴍ ᴏɴ ᴄᴏᴍʙᴏᴛ sᴛɪᴄᴋᴇʀ ᴄᴀᴛᴀʟᴏɢᴜᴇ
"""

__mod_name__ = "𝐒ᴛɪᴄᴋᴇʀs"

STICKERID_HANDLER = DisableAbleCommandHandler("stickerid", stickerid, block=False)
GETSTICKER_HANDLER = DisableAbleCommandHandler("getsticker", getsticker, block=False)
KANG_HANDLER = DisableAbleCommandHandler("kang", kang, admin_ok=True, block=False)
STICKERS_HANDLER = DisableAbleCommandHandler("stickers", cb_sticker, block=False)
DELSTICKER_HANDLER = DisableAbleCommandHandler("delsticker", delsticker, block=False)

application.add_handler(STICKERS_HANDLER)
application.add_handler(STICKERID_HANDLER)
application.add_handler(GETSTICKER_HANDLER)
application.add_handler(KANG_HANDLER)
application.add_handler(DELSTICKER_HANDLER)
