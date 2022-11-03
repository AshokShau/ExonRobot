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

import os
import re
import urllib
import urllib.parse
import urllib.request
from urllib.error import HTTPError, URLError

import requests
from bs4 import BeautifulSoup
from telegram import InputMediaPhoto, TelegramError, Update
from telegram.ext import CallbackContext

from Exon import dispatcher
from Exon.modules.disable import DisableAbleCommandHandler

opener = urllib.request.build_opener()
useragent = "Mozilla/5.0 (Linux; Android 6.0.1; SM-G920V Build/MMB29K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.98 Mobile Safari/537.36"
opener.addheaders = [("User-agent", useragent)]


def reverse(update: Update, context: CallbackContext):
    if os.path.isfile("okgoogle.png"):
        os.remove("okgoogle.png")

    msg = update.effective_message
    chat_id = update.effective_chat.id
    bot, args = context.bot, context.args
    rtmid = msg.message_id
    imagename = "okgoogle.png"

    if reply := msg.reply_to_message:
        if reply.sticker:
            file_id = reply.sticker.file_id
        elif reply.photo:
            file_id = reply.photo[-1].file_id
        elif reply.document:
            file_id = reply.document.file_id
        else:
            msg.reply_text("ʀᴇᴘʟʏ ᴛᴏ ᴀɴ ɪᴍᴀɢᴇ ᴏʀ sᴛɪᴄᴋᴇʀ ᴛᴏ ʟᴏᴏᴋᴜᴘ.")
            return
        image_file = bot.get_file(file_id)
        image_file.download(imagename)
        if args:
            txt = args[0]
            try:
                lim = int(txt)
            except:
                lim = 2
        else:
            lim = 2
    elif args:
        splatargs = msg.text.split(" ")
        if len(splatargs) == 3:
            img_link = splatargs[1]
            try:
                lim = int(splatargs[2])
            except:
                lim = 2
        elif len(splatargs) == 2:
            img_link = splatargs[1]
            lim = 2
        else:
            msg.reply_text("/reverse <link> <amount ᴏғ ɪᴍᴀɢᴇs ᴛᴏ ʀᴇᴛᴜʀɴ.>")
            return
        try:
            urllib.request.urlretrieve(img_link, imagename)
        except HTTPError as HE:
            if HE.reason == "Not Found":
                msg.reply_text("ɪᴍᴀɢᴇ ɴᴏᴛ ғᴏᴜɴᴅ.")
                return
            if HE.reason == "Forbidden":
                msg.reply_text(
                    "ᴄᴏᴜʟᴅɴ'ᴛ ᴀᴄᴄᴇss ᴛʜᴇ ᴘʀᴏᴠɪᴅᴇᴅ ʟɪɴᴋ, ᴛʜᴇ ᴡᴇʙsɪᴛᴇ ᴍɪɢʜᴛ ʜᴀᴠᴇ ʙʟᴏᴄᴋᴇᴅ ᴀᴄᴄᴇssɪɴɢ ᴛᴏ ᴛʜᴇ website ʙʏ ʙᴏᴛ ᴏʀ ᴛʜᴇ ᴡᴇʙsɪᴛᴇ ᴅᴏᴇs ɴᴏᴛ ᴇxɪsᴛᴇᴅ."
                )
                return
        except URLError as UE:
            msg.reply_text(f"{UE.reason}")
            return
        except ValueError as VE:
            msg.reply_text(f"{VE}\nᴘʟᴇᴀsᴇ ᴛʀʏ ᴀɢᴀɪɴ ᴜsɪɴɢ ʜᴛᴛᴘ ᴏʀ ʜᴛᴛᴘs ᴘʀᴏᴛᴏᴄᴏʟ.")
            return
    else:
        msg.reply_markdown(
            "ᴘʟᴇᴀsᴇ ʀᴇᴘʟʏ ᴛᴏ ᴀ sᴛɪᴄᴋᴇʀ, ᴏʀ ᴀɴ ɪᴍᴀɢᴇ to sᴇᴀʀᴄʜ it!\nᴅᴏ ʏᴏᴜ ᴋɴᴏᴡ ᴛʜᴀᴛ ʏᴏᴜ ᴄᴀɴ sᴇᴀʀᴄʜ ᴀɴ ɪᴍᴀɢᴇ ᴡɪᴛʜ a ʟɪɴᴋ ᴛᴏᴏ? `/reverse [ᴘɪᴄᴛᴜʀᴇʟɪɴᴋ] <ᴀᴍᴏᴜɴᴛ>`."
        )
        return

    try:
        searchUrl = "https://www.google.com/searchbyimage/upload"
        multipart = {
            "encoded_image": (imagename, open(imagename, "rb")),
            "image_content": "",
        }
        response = requests.post(searchUrl, files=multipart, allow_redirects=False)
        fetchUrl = response.headers["Location"]

        if response != 400:
            xx = bot.send_message(
                chat_id,
                "ɪᴍᴀɢᴇ ᴡᴀs sᴜᴄᴄᴇssғᴜʟʟʏ ᴜᴘʟᴏᴀᴅᴇᴅ ᴛᴏ ɢᴏᴏɢʟᴇ." "\n ᴘʟᴇᴀsᴇ ᴡᴀɪᴛ ʙᴀʙʏ...",
                reply_to_message_id=rtmid,
            )
        else:
            xx = bot.send_message(
                chat_id,
                "ɢᴏᴏɢʟᴇ ᴛᴏʟᴅ ᴍᴇ ᴛᴏ ғᴜᴄᴋ ʏᴏᴜ ᴛʜɪs ɢᴀʏ",
                reply_to_message_id=rtmid,
            )
            return

        os.remove(imagename)
        match = ParseSauce(f"{fetchUrl}&hl=en")
        guess = match["best_guess"]
        if match["override"] and match["override"] != "":
            imgspage = match["override"]
        else:
            imgspage = match["similar_images"]

        if guess and imgspage:
            xx.edit_text(
                f"[{guess}]({fetchUrl})\nWaito...",
                parse_mode="Markdown",
                disable_web_page_preview=True,
            )
        else:
            xx.edit_text("ᴄᴏᴜʟᴅɴ'ᴛ ғɪɴᴅ ᴀɴʏᴛʜɪɴɢ.")
            return

        images = scam(imgspage, lim)
        if len(images) == 0:
            xx.edit_text(
                f"[{guess}]({fetchUrl})[.]({imgspage})",
                parse_mode="Markdown",
                disable_web_page_preview=True,
            )
            return

        imglinks = []
        for link in images:
            lmao = InputMediaPhoto(media=str(link))
            imglinks.append(lmao)

        bot.send_media_group(chat_id=chat_id, media=imglinks, reply_to_message_id=rtmid)
        xx.edit_text(
            f"[{guess}]({fetchUrl})[.]({imgspage})",
            parse_mode="Markdown",
            disable_web_page_preview=True,
        )
    except TelegramError as e:
        print(e)
    except Exception as exception:
        print(exception)


def ParseSauce(googleurl):
    """Parse/Scrape the HTML code for the info we want."""

    source = opener.open(googleurl).read()
    soup = BeautifulSoup(source, "html.parser")

    results = {"similar_images": "", "override": "", "best_guess": ""}

    try:
        for bess in soup.findAll("a", {"class": "PBorbe"}):
            url = "https://www.google.com" + bess.get("href")
            results["override"] = url
    except:
        pass

    for similar_image in soup.findAll("input", {"class": "gLFyf"}):
        url = "https://www.google.com/search?tbm=isch&q=" + urllib.parse.quote_plus(
            similar_image.get("value")
        )
        results["similar_images"] = url

    for best_guess in soup.findAll("div", attrs={"class": "r5a77d"}):
        results["best_guess"] = best_guess.get_text()

    return results


def scam(imgspage, lim):
    """Parse/Scrape the HTML code for the info we want."""

    single = opener.open(imgspage).read()
    decoded = single.decode("utf-8")
    if int(lim) > 10:
        lim = 10

    imglinks = []
    counter = 0

    pattern = r"^,\[\"(.*[.png|.jpg|.jpeg])\",[0-9]+,[0-9]+\]$"
    oboi = re.findall(pattern, decoded, re.I | re.M)

    for imglink in oboi:
        counter += 1
        imglinks.append(imglink)
        if counter >= int(lim):
            break

    return imglinks


REVERSE_HANDLER = DisableAbleCommandHandler(
    ["grs", "reverse", "pp"], reverse, pass_args=True, run_async=True
)

dispatcher.add_handler(REVERSE_HANDLER)

__mod_name__ = "𝚁ᴇᴠᴇʀsᴇ"
