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
