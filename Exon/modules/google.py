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

import glob
import re
import urllib
import urllib.request

from bing_image_downloader import downloader
from bs4 import BeautifulSoup
from telethon import *
from telethon.tl.types import *

from Exon import telethn
from Exon.events import register


@register(pattern="^/img (.*)")
async def img_sampler(event):
    if event.fwd_from:
        return

    query = event.pattern_match.group(1)
    jit = f'"{query}"'
    downloader.download(
        jit,
        limit=4,
        output_dir="store",
        adult_filter_off=False,
        force_replace=False,
        timeout=60,
    )
    os.chdir(f'./store/"{query}"')
    types = ("*.png", "*.jpeg", "*.jpg")  # the tuple of file types
    files_grabbed = []
    for files in types:
        files_grabbed.extend(glob.glob(files))
    await telethn.send_file(event.chat_id, files_grabbed, reply_to=event.id)
    os.chdir("/app")
    os.system("rm -rf store")


opener = urllib.request.build_opener()
useragent = "Mozilla/5.0 (Linux; Android 9; SM-G960F Build/PPR1.180610.011; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/74.0.3729.157 Mobile Safari/537.36"
opener.addheaders = [("User-agent", useragent)]


async def ParseSauce(googleurl):
    """Parse/Scrape the HTML code for the info we want."""

    source = opener.open(googleurl).read()
    soup = BeautifulSoup(source, "html.parser")

    results = {"similar_images": "", "best_guess": ""}

    try:
        for similar_image in soup.findAll("input", {"class": "gLFyf"}):
            url = "https://www.google.com/search?tbm=isch&q=" + urllib.parse.quote_plus(
                similar_image.get("value")
            )
            results["similar_images"] = url
    except BaseException:
        pass

    for best_guess in soup.findAll("div", attrs={"class": "r5a77d"}):
        results["best_guess"] = best_guess.get_text()

    return results


async def scam(results, lim):

    single = opener.open(results["similar_images"]).read()
    decoded = single.decode("utf-8")

    imglinks = []
    counter = 0

    pattern = r"^,\[\"(.*[.png|.jpg|.jpeg])\",[0-9]+,[0-9]+\]$"
    oboi = re.findall(pattern, decoded, re.I | re.M)

    for imglink in oboi:
        counter += 1
        if counter < int(lim):
            imglinks.append(imglink)
        else:
            break

    return imglinks


async def is_register_admin(chat, user):
    if isinstance(chat, (types.InputPeerChannel, types.InputChannel)):

        return isinstance(
            (
                await telethn(functions.channels.GetParticipantRequest(chat, user))
            ).participant,
            (types.ChannelParticipantAdmin, types.ChannelParticipantCreator),
        )
    if isinstance(chat, types.InputPeerChat):

        ui = await telethn.get_peer_id(user)
        ps = (
            await telethn(functions.messages.GetFullChatRequest(chat.chat_id))
        ).full_chat.participants.participants
        return isinstance(
            next((p for p in ps if p.user_id == ui), None),
            (types.ChatParticipantAdmin, types.ChatParticipantCreator),
        )
    return None


__mod_name__ = "𝚃ᴏᴏʟs"

__help__ = """
⍟ /img <text> :- `sᴇᴀʀᴄʜ ɢᴏᴏɢʟᴇ ғᴏʀ ɪᴍᴀɢᴇs ᴀɴᴅ ʀᴇᴛᴜʀɴs ᴛʜᴇᴍ ғᴏʀ ɢʀᴇᴀᴛᴇʀ ɴᴏ. ᴏғ ʀᴇsᴜʟᴛs sᴘᴇᴄɪғʏ ʟɪᴍ, ғᴏʀ`

ᴇɢ: `/img hello lim=10`

⍟ /reverse :- `ʀᴇᴘʟʏ ᴛᴏ ᴀ sᴛɪᴄᴋᴇʀ, or ᴏʀ ɪᴍᴀɢᴇ ᴛᴏ sᴇᴀʀᴄʜ ɪᴛ `

  ᴅᴏ ʏᴏᴜ ᴋɴᴏᴡ that ʏᴏᴜ ᴄᴀɴ search ᴀɴ ɪᴍᴀɢᴇ ᴡɪᴛʜ ᴀ ʟɪɴᴋ ᴛᴏᴏ?
   /reverse picturelink <amount>.
  
⍟ /git <ɢɪᴛʜᴜʙ ᴜsᴇʀɴᴀᴍᴇ> :-`ɢᴇᴛ ɪɴғᴏ ᴏғ ᴀɴʏ ɢɪᴛʜᴜʙ ᴘʀᴏғɪʟᴇ`

⍟ /webss <ᴡᴇʙɴᴀᴍᴇ.ᴄᴏᴍ> :- `ɢᴇᴛ sᴄʀᴇᴇɴ sʜᴏᴛ ᴏғ ᴀɴʏ ᴡᴇʙsɪᴛᴇ ʏᴏᴜ ᴡᴀɴᴛ `.
"""
