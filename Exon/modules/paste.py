import base64
import json
import typing
import zlib
from io import BytesIO
from urllib.parse import urljoin, urlparse, urlunparse

import base58
import requests
from Crypto import Hash, Protocol, Random
from Crypto.Cipher import AES
from telegram import Update
from telegram.ext import ContextTypes

from Exon import application
from Exon.modules.disable import DisableAbleCommandHandler


def upload_text(data: str) -> typing.Optional[str]:
    passphrase = Random.get_random_bytes(32)
    salt = Random.get_random_bytes(8)
    key = Protocol.KDF.PBKDF2(
        passphrase, salt, 32, 100000, hmac_hash_module=Hash.SHA256
    )
    compress = zlib.compressobj(wbits=-15)
    paste_blob = (
        compress.compress(json.dumps({"paste": data}, separators=(",", ":")).encode())
        + compress.flush()
    )
    cipher = AES.new(key, AES.MODE_GCM)
    paste_meta = [
        [
            base64.b64encode(cipher.nonce).decode(),
            base64.b64encode(salt).decode(),
            100000,
            256,
            128,
            "aes",
            "gcm",
            "zlib",
        ],
        "syntaxhighlighting",
        0,
        0,
    ]
    cipher.update(json.dumps(paste_meta, separators=(",", ":")).encode())
    ct, tag = cipher.encrypt_and_digest(paste_blob)
    resp = requests.post(
        "https://bin.nixnet.services",
        headers={"X-Requested-With": "JSONHttpRequest"},
        data=json.dumps(
            {
                "v": 2,
                "adata": paste_meta,
                "ct": base64.b64encode(ct + tag).decode(),
                "meta": {"expire": "1week"},
            },
            separators=(",", ":"),
        ),
    )
    data = resp.json()
    url = list(urlparse(urljoin("https://bin.nixnet.services", data["url"])))
    url[5] = base58.b58encode(passphrase).decode()
    return urlunparse(url)


async def paste(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    message = update.effective_message

    if message.reply_to_message:
        data = message.reply_to_message.text or message.reply_to_message.caption
        if message.reply_to_message.document:
            file_info = context.bot.get_file(message.reply_to_message.document.file_id)
            with BytesIO() as file:
                file_info.download(out=file)
                file.seek(0)
                data = file.read().decode()

    elif len(args) >= 1:
        data = message.text.split(None, 1)[1]
    else:
        await message.reply_text("ᴡʜᴀᴛ ᴀᴍ I sᴜᴘᴘᴏsᴇᴅ ᴛᴏ ᴅᴏ ᴡɪᴛʜ ᴛʜɪs?")
        return

    txt = ""
    paste_url = upload_text(data)
    if not paste_url:
        txt = "ғᴀɪʟᴇᴅ ᴛᴏ ᴘᴀsᴛᴇ ᴅᴀᴛᴀ"
    else:
        txt = "sᴜᴄᴄᴇssғᴜʟʟʏ ᴜᴘʟᴏᴀᴅᴇᴅ ᴛᴏ ᴘʀɪᴠᴀᴛᴇʙɪɴ: {}".format(paste_url)

    message.reply_text(txt, disable_web_page_preview=True)


__mod_name__ = "𝐏ᴀsᴛᴇ"
__help__ = """
 *ᴘᴀsᴛᴇs ᴛʜᴇ ɢɪᴠᴇɴ ғɪʟᴇ ᴀɴᴅ sʜᴏᴡs ʏᴏᴜ ᴛʜᴇ ʀᴇsᴜʟᴛ*
 
 ❍ /paste *:* ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴛᴇxᴛ ғɪʟᴇ 
 """


PASTE_HANDLER = DisableAbleCommandHandler("paste", paste, block=False)
application.add_handler(PASTE_HANDLER)

__command_list__ = ["paste"]
__handlers__ = [PASTE_HANDLER]
