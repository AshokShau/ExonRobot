"""
MIT License

Copyright (c) 2022 ABISHNOI

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
# TG :- @Abishnoi1M
#     MY ALL BOTS :- Abishnoi_bots
#     GITHUB :- KingAbishnoi ""


import os

from gtts import gTTS, gTTSError

from Exon import telethn as tbot
from Exon.events import register


@register(pattern="^/tts (.*)")
async def _(event):
    if event.fwd_from:
        return
    input_str = event.pattern_match.group(1)
    reply_to_id = event.message.id
    if event.reply_to_msg_id:
        previous_message = await event.get_reply_message()
        text = previous_message.message
        lan = input_str
    elif "|" in input_str:
        lan, text = input_str.split("|")
    else:
        await event.reply("ɪɴᴠᴀʟɪᴅ ꜱʏɴᴛᴀx\nғᴏʀ eg: `/tts en | hello`")
        return
    text = text.strip()
    lan = lan.strip()
    try:
        tts = gTTS(text, tld="com", lang=lan)
        tts.save("k.mp3")
    except AssertionError:
        await event.reply(
            "ᴛʜᴇ ᴛᴇxᴛ ɪs ᴇᴍᴘᴛʏ.\n"
            "ɴᴏᴛʜɪɴɢ ʟᴇғᴛ ᴛᴏ sᴘᴇᴀᴋ ᴀғᴛᴇʀ ᴘʀᴇ-ᴘʀᴇᴄᴇssɪɴɢ, "
            "ᴛᴏᴋᴇɴɪᴢɪɴɢ ᴀɴᴅ ᴄʟᴇᴀɴɪɴɢ."
        )
        return
    except ValueError:
        await event.reply("ʟᴀɴɢᴜᴀɢᴇ ɪs ɴᴏᴛ sᴜᴘᴘᴏʀᴛᴇᴅ.")
        return
    except RuntimeError:
        await event.reply("ᴇʀʀᴏʀ ʟᴏᴀᴅɪɴɢ ᴛʜᴇ ʟᴀɴɢᴜᴀɢᴇs ᴅɪᴄᴛɪᴏɴᴀʀʏ.")
        return
    except gTTSError:
        await event.reply("ᴇʀʀᴏʀ ɪɴ ɢᴏᴏɢʟᴇ ᴛᴇxᴛ-ᴛᴏ-sᴘᴇᴇᴄʜ ᴀᴘɪ ʀᴇǫᴜᴇsᴛ !")
        return
    with open("k.mp3", "r"):
        await tbot.send_file(
            event.chat_id, "k.mp3", voice_note=True, reply_to=reply_to_id
        )
        os.remove("k.mp3")


__help__ = """

⍟ /tts hi|hello  *:* `ᴛᴇxᴛ ᴛᴏ sᴘᴇᴇᴄʜ `


"""

__mod_name__ = "𝚃ᴛs"
