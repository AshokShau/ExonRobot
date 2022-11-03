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
from datetime import datetime

from PIL import Image
from telegraph import Telegraph, exceptions, upload_file

from Exon import telethn
from Exon.events import register

TMP_DOWNLOAD_DIRECTORY = "tg-File/"
babe = "ExonRobot"  # ᴅᴏɴ'ᴛ ᴇᴅɪᴛ ᴛʜɪᴀ ʟɪɴᴇ
telegraph = Telegraph()
r = telegraph.create_account(short_name=babe)
auth_url = r["auth_url"]


@register(pattern="^/t(gm|gt) ?(.*)")
async def _(event):
    if event.fwd_from:
        return
    optional_title = event.pattern_match.group(2)
    if event.reply_to_msg_id:
        start = datetime.now()
        r_message = await event.get_reply_message()
        input_str = event.pattern_match.group(1)
        if input_str == "gm":
            downloaded_file_name = await telethn.download_media(
                r_message, TMP_DOWNLOAD_DIRECTORY
            )
            end = datetime.now()
            ms = (end - start).seconds
            h = await event.reply(
                "ᴅᴏᴡɴʟᴏᴀᴅᴇᴅ ᴛᴏ {} in {} sᴇᴄᴏɴᴅs.".format(downloaded_file_name, ms)
            )
            if downloaded_file_name.endswith((".webp")):
                resize_image(downloaded_file_name)
            try:
                start = datetime.now()
                media_urls = upload_file(downloaded_file_name)
            except exceptions.TelegraphException as exc:
                await h.edit("ᴇʀʀᴏʀ: " + str(exc))
                os.remove(downloaded_file_name)
            else:
                end = datetime.now()
                ms_two = (end - start).seconds
                os.remove(downloaded_file_name)
                await h.edit(
                    "ᴜᴘʟᴏᴀᴅᴇᴅ ᴛᴏ [ᴛᴇʟᴇɢʀᴀᴘʜ](https://telegra.ph{}) ɪɴ {} sᴇᴄᴏɴᴅs.".format(
                        media_urls[0], (ms + ms_two)
                    ),
                    link_preview=True,
                )
        elif input_str == "gt":
            user_object = await telethn.get_entity(r_message.sender_id)
            title_of_page = user_object.first_name  # + " " + user_object.last_name
            # apparently, all Users do not have last_name field
            if optional_title:
                title_of_page = optional_title
            page_content = r_message.message
            if r_message.media:
                if page_content != "":
                    title_of_page = page_content
                downloaded_file_name = await telethn.download_media(
                    r_message, TMP_DOWNLOAD_DIRECTORY
                )
                m_list = None
                with open(downloaded_file_name, "rb") as fd:
                    m_list = fd.readlines()
                for m in m_list:
                    page_content += m.decode("UTF-8") + "\n"
                os.remove(downloaded_file_name)
            page_content = page_content.replace("\n", "<br>")
            response = telegraph.create_page(title_of_page, html_content=page_content)
            end = datetime.now()
            ms = (end - start).seconds
            await event.reply(
                "ᴘᴀsᴛᴇᴅ ᴛᴏ [ᴛᴇʟᴇɢʀᴀᴘʜ](https://telegra.ph/{}) ɪɴ {} sᴇᴄᴏɴᴅs.".format(
                    response["path"], ms
                ),
                link_preview=True,
            )
    else:
        await event.reply("ʀᴇᴘʟʏ ᴛᴏ a ᴍᴇssᴀɢᴇ ᴛᴏ ɢᴇᴛ ᴀ ᴘᴇʀᴍᴀɴᴇɴᴛ telegra.ph ʟɪɴᴋ.")


def resize_image(image):
    im = Image.open(image)
    im.save(image, "PNG")


file_help = os.path.basename(__file__)
file_help = file_help.replace(".py", "")
file_helpo = file_help.replace("_", " ")


__help__ = """ 
ᴛᴇʟᴇɢʀᴀᴘʜ:

⍟ /tgm*:* `ɢᴇᴛ ᴛᴇʟᴇɢʀᴀᴘʜ ʟɪɴᴋ ᴏғ ʀᴇᴘʟɪᴇᴅ ᴍᴇᴅɪᴀ `

⍟ /tgt*:* `ɢᴇᴛ ᴛᴇʟᴇɢʀᴀᴘʜ Link ᴏғ ʀᴇᴘʟɪᴇᴅ ᴛᴇxᴛ ` 
 """

__mod_name__ = "𝚃ᴇʟᴇɢʀᴀᴘʜ"
