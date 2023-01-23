import httpx
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import CommandHandler, ContextTypes

from Exon import exon


async def convert(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = update.effective_message.text.split(" ")

    if len(args) == 4:
        try:
            orig_cur_amount = int(args[1])

        except ValueError:
            await update.effective_message.reply_text("ɪɴᴠᴀʟɪᴅ ᴀᴍᴏᴜɴᴛ ᴏғ ᴄᴜʀʀᴇɴᴄʏ")
            return

        orig_cur = args[2].lower()
        new_cur = args[3].lower()

        request_url = f"https://cdn.jsdelivr.net/gh/fawazahmed0/currency-api@1/latest/currencies/{orig_cur}.json"
        async with httpx.AsyncClient() as client:
            r = await client.get(request_url)
        data = r.json()

        for curr_name in data[orig_cur]:
            if new_cur == curr_name:
                current_rate = data[orig_cur][curr_name]

        new_cur_amount = round(orig_cur_amount * current_rate, 5)
        await update.effective_message.reply_text(
            f"{orig_cur_amount} {orig_cur.upper()} = {new_cur_amount} {new_cur.upper()}",
        )

    elif len(args) == 1:
        await update.effective_message.reply_text(help, parse_mode=ParseMode.MARKDOWN)

    else:
        await update.effective_message.reply_text(
            f"*ɪɴᴠᴀʟɪᴅ ᴀʀɢs!!:* ʀᴇǫᴜɪʀᴇᴅ 3 ʙᴜᴛ ᴘᴀssᴇᴅ {len(args) -1}",
            parse_mode=ParseMode.MARKDOWN,
        )


help = """
*ᴄᴏɴᴠᴇʀᴛs ᴍᴏɴᴇʏ ғʀᴏᴍ ᴏɴᴇ ᴇxᴄʜᴀɴɢᴇ ᴛᴏ ᴀɴᴏᴛʜᴇʀ*

*ɴᴏᴛᴇ:* sᴜᴘᴘᴏʀᴛs ᴄʀʏᴘᴛᴏᴄᴜʀʀᴇɴᴄɪᴇs ᴛᴏᴏ
.
ᴜsᴀɢᴇ: /cash ᴀᴍᴏᴜɴᴛ ғʀᴏᴍ ᴛᴏ
ᴇxᴀᴍᴘʟᴇ: `/cash 20 USD INR`"""

CONVERTER_HANDLER = CommandHandler("cash", convert)

exon.add_handler(CONVERTER_HANDLER)

__command_list__ = ["cash"]
__handlers__ = [CONVERTER_HANDLER]
