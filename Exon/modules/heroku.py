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

import asyncio
import math
import os

import heroku3
import requests

from Exon import HEROKU_API_KEY, HEROKU_APP_NAME, OWNER_ID
from Exon.events import register

heroku_api = "https://api.heroku.com"
Heroku = heroku3.from_key(HEROKU_API_KEY)


@register(pattern="^/usage$")
async def dyno_usage(dyno):
    if dyno.fwd_from:
        return
    if dyno.sender_id != OWNER_ID:
        return
    """
    Get your account Dyno Usage
    """
    die = await dyno.reply("`Processing...`")
    useragent = (
        "Mozilla/5.0 (Linux; Android 10; SM-G975F) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/80.0.3987.149 Mobile Safari/537.36"
    )
    user_id = Heroku.account().id
    headers = {
        "User-Agent": useragent,
        "Authorization": f"Bearer {HEROKU_API_KEY}",
        "Accept": "application/vnd.heroku+json; version=3.account-quotas",
    }
    path = f"/accounts/{user_id}/actions/get-quota"
    r = requests.get(heroku_api + path, headers=headers)
    if r.status_code != 200:
        return await die.edit("`ᴇʀʀᴏʀ: sᴏᴍᴇᴛʜɪɴɢ ʙᴀᴅ happened`\n\n" f">.`{r.reason}`\n")
    result = r.json()
    quota = result["account_quota"]
    quota_used = result["quota_used"]

    """ - Used - """
    remaining_quota = quota - quota_used
    percentage = math.floor(remaining_quota / quota * 100)
    minutes_remaining = remaining_quota / 60
    hours = math.floor(minutes_remaining / 60)
    minutes = math.floor(minutes_remaining % 60)
    day = math.floor(hours / 24)

    """ - Current - """
    App = result["apps"]
    try:
        App[0]["quota_used"]
    except IndexError:
        AppQuotaUsed = 0
        AppPercentage = 0
    else:
        AppQuotaUsed = App[0]["quota_used"] / 60
        AppPercentage = math.floor(App[0]["quota_used"] * 100 / quota)
    AppHours = math.floor(AppQuotaUsed / 60)
    AppMinutes = math.floor(AppQuotaUsed % 60)
    await asyncio.sleep(1.5)

    return await die.edit(
        " **ᴅʏɴᴏ ᴜsᴀɢᴇ **:\n\n"
        f" » ᴅʏɴᴏ ᴜsᴀɢᴇ ғᴏʀ **{HEROKU_APP_NAME}**:\n"
        f"      •  `{AppHours}`**h**  `{AppMinutes}`**m**  "
        f"**|**  [`{AppPercentage}`**%**]"
        "\n\n"
        "  » ᴅʏɴᴏ ʜᴏᴜʀs ǫᴜᴏᴛᴀ ʀᴇᴍᴀɪɴɪɴɢ ᴛʜɪs ᴍᴏɴᴛʜ:\n"
        f"      •  `{hours}`**h**  `{minutes}`**m**  "
        f"**|**  [`{percentage}`**%**]"
        f"\n\n  » ᴅʏɴᴏs ʜᴇʀᴏᴋᴜ {day} ᴅᴀʏs ʟᴇғᴛ"
    )


@register(pattern="^/logs$")
async def _(dyno):
    if dyno.fwd_from:
        return
    if dyno.sender_id != OWNER_ID:
        return
    try:
        Heroku = heroku3.from_key(HEROKU_API_KEY)
        app = Heroku.app(HEROKU_APP_NAME)
    except:
        return await dyno.reply(
            " ᴘʟᴇᴀsᴇ ᴍᴀᴋᴇ sᴜʀᴇ ʏᴏᴜʀ ʜᴇʀᴏᴋᴜ ᴀᴘɪ ᴋᴇʏ, ʏᴏᴜʀ ᴀᴘᴘ ɴᴀᴍᴇ ᴀʀᴇ ᴄᴏɴғɪɢᴜʀᴇᴅ ᴄᴏʀʀᴇᴄᴛʟʏ ɪɴ ᴛʜᴇ ʜᴇʀᴏᴋᴜ"
        )
    v = await dyno.reply("ɢᴇᴛᴛɪɴɢ ʟᴏɢs.......")
    with open("logs.txt", "w") as log:
        log.write(app.get_log())
    await v.edit("ɢᴏᴛ ᴛʜᴇ ʟᴏɢs ᴡᴀɪᴛ ᴀ sᴇᴄ")
    await dyno.client.send_file(
        dyno.chat_id,
        "logs.txt",
        reply_to=dyno.id,
        caption="ᴇxᴏɴ ʟᴏɢs.",
    )

    await asyncio.sleep(5)
    await v.delete()
    return os.remove("logs.txt")


def prettyjson(obj, indent=2, maxlinelength=80):
    """Renders JSON content with indentation and line splits/concatenations to fit maxlinelength.
    Only dicts, lists and basic types are supported"""

    items, _ = getsubitems(
        obj,
        itemkey="",
        islast=True,
        maxlinelength=maxlinelength - indent,
        indent=indent,
    )
    return indentitems(items, indent, level=0)
