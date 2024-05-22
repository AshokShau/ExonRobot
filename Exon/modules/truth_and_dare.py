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
# TG :- @Abishnoi1M
#      :- Abishnoi_bots
#     GITHUB :- Abishnoi69 ""


import requests

from Exon import SUPPORT_CHAT
from Exon.events import register as abishnoi


@abishnoi(pattern="[/!]dare")
async def _(asux):
    try:
        ak = requests.get("https://api.truthordarebot.xyz/v1/dare").json()
        results = f"{ak['question']}"
        return await asux.reply(results)
    except Exception:
        await asux.reply(f"ᴇʀʀᴏʀ ʀᴇᴘᴏʀᴛ @{SUPPORT_CHAT}")


@abishnoi(pattern="[/!]truth")
async def _(asux):
    try:
        ak = requests.get("https://api.truthordarebot.xyz/v1/truth").json()
        results = f"{ak['question']}"
        return await asux.reply(results)
    except Exception:
        await asux.reply(f"ᴇʀʀᴏʀ ʀᴇᴘᴏʀᴛ @{SUPPORT_CHAT}")


__mod_name__ = "𝐓ʀᴜᴛʜ-Dᴀʀᴇ"

from Exon.modules.language import gs


def get_help(chat):
    return gs(chat, "td_help")
