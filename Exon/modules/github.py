import asyncio

from pyrogram import filters
from pyrogram.types import Message
from Exon.modules.helper_funcs import *
from Exon import app as Abishnoi


@Abishnoi.on_message(filters.command(["git", "github"]))
async def github(_, m: Message):
    if len(m.text.split()) == 2:
        username = m.text.split(maxsplit=1)[1]
    else:
        await m.reply_text(
            f"ᴜsᴀɢᴇ: <code> /github Abishnoi69 </code>",
        )
        return
    username = username.split("/")[-1]
    URL = f"https://api.github.com/users/{username}"
    try:
        r = await get(URL, timeout=5)
    except asyncio.TimeoutError:
        return await m.reply_text("ʀᴇǫᴜᴇsᴛ ᴛɪᴍᴇᴏᴜᴛ")
    except Exception as e:
        return await m.reply_text(f"ᴇʀʀᴏʀ: `{e}`")

    avtar = r.get("avatar_url", None)
    url = r.get("html_url", None)
    name = r.get("name", None)
    company = r.get("company", None)
    followers = r.get("followers", 0)
    following = r.get("following", 0)
    public_repos = r.get("public_repos", 0)
    bio = r.get("bio", None)
    created_at = r.get("created_at", "ɴᴏᴛ ғᴏᴜɴᴅ")
    location = r.get("location", None)
    email = r.get("email", None)
    updated_at = r.get("updated_at", "ɴᴏᴛ ғᴏᴜɴᴅ")
    blog = r.get("blog", None)
    twitter = r.get("twitter_username", None)

    ABG = ""
    if name:
        ABG += f"<b>🧑‍💻 ɢɪᴛʜᴜʙ ɪɴғᴏ ᴏғ {name}:</b>"
    if url:
        ABG += f"\n<b>📎 ᴜʀʟ:</b> <a href='{url}'>{username}</a>"
    ABG += f"\n<b>🔑 ᴘᴜʙʟɪᴄ ʀᴇᴘᴏs:</b> {public_repos}"
    ABG += f"\n<b>🧲 ғᴏʟʟᴏᴡᴇʀs:</b> {followers}"
    ABG += f"\n<b>✨ ғᴏʟʟᴏᴡɪɴɢ:</b> {following}"
    if email:
        ABG += f"\n<b>✉️ ᴇᴍᴀɪʟ:</b> <code>{email}</code>"
    if company:
        org_url = company.strip("@")
        ABG += f"\n<b>™️ ᴏʀɢᴀɴɪᴢᴀᴛɪᴏɴ:</b> <a href='https://github.com/{org_url}'>{company}</a>"
    if blog:
        bname = blog.split(".")[-2]
        bname = bname.split("/")[-1]
        ABG += f"\n<b>📝 ʙʟᴏɢ:</b> <a href={blog}>{bname}</a>"
    if twitter:
        ABG += f"\n<b>⚜️ ᴛᴡɪᴛᴛᴇʀ:</b> <a href='https://twitter.com/{twitter}'>{twitter}</a>"
    if location:
        ABG += f"\n<b>🚀 ʟᴏᴄᴀᴛɪᴏɴ:</b> <code>{location}</code>"
    ABG += f"\n<b>💫 ᴄʀᴇᴀᴛᴇᴅ at:</b> <code>{created_at}</code>"
    ABG += f"\n<b>⌚️ ᴜᴘᴅᴀᴛᴇᴅ at:</b> <code>{updated_at}</code>"
    if bio:
        ABG += f"\n\n<b>🎯 ʙɪᴏ:</b> <code>{bio}</code>"

    if avtar:
        return await m.reply_photo(photo=f"{avtar}", caption=ABG)
    await m.reply_text(ABG)
    return


__mod_name__ = "𝐆ɪᴛʜᴜʙ"

__help__ = """
*ɪ ᴡɪʟʟ ɢɪᴠᴇ ɪɴғᴏʀᴍᴀᴛɪᴏɴ ᴀʙᴏᴜᴛ ɢɪᴛʜᴜʙ ᴘʀᴏғɪʟᴇ* 

❍ /github <ᴜsᴇʀɴᴀᴍᴇ>*:* ɢᴇᴛ ɪɴғᴏʀᴍᴀᴛɪᴏɴ ᴀʙᴏᴜᴛ ᴀ ɢɪᴛʜᴜʙ ᴜsᴇʀ.
"""
