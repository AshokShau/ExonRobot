import io

import aiohttp
import httpx
from pyrogram import Client, filters
from pyrogram.types import Message
from telethon.tl import functions, types

from Exon import app as abishnoi
from Exon import register
from Exon import telethn as tbot

timeout = httpx.Timeout(40, pool=None)

http = httpx.AsyncClient(http2=True, timeout=timeout)


# Api key used in weather.com's mobile app. @Abishnoi1M

weather_apikey = "8de2d8b3a93542c9a2d8b3a935a2c909"

get_coords = "https://api.weather.com/v3/location/search"
url = "https://api.weather.com/v3/aggcommon/v3-wx-observations-current"

headers = {
    "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 12; M2012K11AG Build/SQ1D.211205.017)"
}


@abishnoi.on_message(filters.command("weather"))
async def weather(c: Client, m: Message):
    if len(m.command) == 1:
        return await m.reply_text(
            "<b>ᴜsᴀɢᴇ:</b> <code>/weather location ᴏʀ city</code> - ɢᴇᴛ ɪɴғᴏʀᴍᴀᴛɪᴏɴ ᴀʙᴏᴜᴛ ᴛʜᴇ ᴡᴇᴀᴛʜᴇʀ ɪɴ <i>ʟᴏᴄᴀᴛɪᴏɴ ᴏʀ ᴄɪᴛʏ</i>"
        )

    r = await http.get(
        get_coords,
        headers=headers,
        params=dict(
            apiKey=weather_apikey,
            format="json",
            language="en",
            query=m.text.split(maxsplit=1)[1],
        ),
    )
    loc_json = r.json()

    if not loc_json.get("location"):
        await m.reply_text("ʟᴏᴄᴀᴛɪᴏɴ ɴᴏᴛ ғᴏᴜɴᴅ")
    else:
        pos = f"{loc_json['location']['latitude'][0]},{loc_json['location']['longitude'][0]}"
        r = await http.get(
            url,
            headers=headers,
            params=dict(
                apiKey=weather_apikey,
                format="json",
                language="en",
                geocode=pos,
                units="m",
            ),
        )
        res_json = r.json()

        obs_dict = res_json["v3-wx-observations-current"]

        res = "<b>{location}</b>:\n\nᴛᴇᴍᴘᴇʀᴀᴛᴜʀᴇ: <code>{temperature} °C</code>\nᴛᴇᴍᴘᴇʀᴀᴛᴜʀᴇ ғᴇᴇʟs ʟɪᴋᴇ: <code>{feels_like} °C</code>\nᴀɪʀ ʜᴜᴍɪᴅɪᴛʏ: <code>{air_humidity}%</code>\nᴡɪɴᴅ sᴘᴇᴇᴅ: <code>{wind_speed} km/h</code>\n\n- <i>{overview}</i>".format(
            location=loc_json["location"]["address"][0],
            temperature=obs_dict["temperature"],
            feels_like=obs_dict["temperatureFeelsLike"],
            air_humidity=obs_dict["relativeHumidity"],
            wind_speed=obs_dict["windSpeed"],
            overview=obs_dict["wxPhraseLong"],
        )

        await m.reply_text(res)


async def is_register_admin(chat, user):
    if isinstance(chat, (types.InputPeerChannel, types.InputChannel)):
        return isinstance(
            (
                await tbot(functions.channels.GetParticipantRequest(chat, user))
            ).participant,
            (types.ChannelParticipantAdmin, types.ChannelParticipantCreator),
        )
    if isinstance(chat, types.InputPeerUser):
        return True


@register(pattern="^/mosam (.*)")
async def _(event):
    if event.fwd_from:
        return

    sample_url = "https://wttr.in/{}.png"
    input_str = event.pattern_match.group(1)
    async with aiohttp.ClientSession() as session:
        response_api_zero = await session.get(sample_url.format(input_str))
        response_api = await response_api_zero.read()
        with io.BytesIO(response_api) as out_file:
            await event.reply(file=out_file)


__help__ = """
*ɪ ᴄᴀɴ ғɪɴᴅ ᴡᴇᴀᴛʜᴇʀ ᴏғ ᴀʟʟ ᴄɪᴛɪᴇs*
❍ /weather*:*  ɢᴇᴛ ɪɴғᴏʀᴍᴀᴛɪᴏɴ ᴀʙᴏᴜᴛ ᴛʜᴇ ᴡᴇᴀᴛʜᴇʀ 
❍ /mosam <ᴄɪᴛʏ>*:* ᴀᴅᴠᴀɴᴄᴇᴅ ᴡᴇᴀᴛʜᴇʀ ᴍᴏᴅᴜʟᴇ, ᴜsᴀɢᴇ sᴀᴍᴇ ᴀs /weather
❍ /mosam moon*:* ɢᴇᴛ ᴛʜᴇ ᴄᴜʀʀᴇɴᴛ sᴛᴀᴛᴜs ᴏғ ᴍᴏᴏɴ
"""

__mod_name__ = "𝐖ᴇᴀᴛʜᴇʀ"
