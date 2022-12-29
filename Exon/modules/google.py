from GoogleSearch import Search
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.error import BadRequest
from telegram.ext import ContextTypes

from Exon import application
from Exon.modules.disable import DisableAbleCommandHandler


async def reverse(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.effective_message
    args = context.args

    if args:
        if len(args) <= 1:
            url = args[0]
            if url.startswith(("https://", "http://")):
                msg = await message.reply_text("ᴜᴘʟᴏᴀᴅɪɴɢ ᴜʀʟ ᴛᴏ ɢᴏᴏɢʟᴇ..")

                result = Search(url=url)
                name = result["output"]
                link = result["similar"]

                await msg.edit_text("ᴜᴘʟᴏᴀᴅᴇᴅ ᴛᴏ ɢᴏᴏɢʟᴇ, ғᴇᴛᴄʜɪɴɢ ʀᴇsᴜʟᴛs...")
                await msg.edit_text(
                    text=f"{name}",
                    reply_markup=InlineKeyboardMarkup(
                        [
                            [
                                InlineKeyboardButton(
                                    text="sɪᴍɪʟᴀʀ",
                                    url=link,
                                ),
                            ],
                        ],
                    ),
                )
                return
        else:
            await message.reply_text(
                "ᴄᴏᴍᴍᴀɴᴅ ᴍᴜsᴛ ʙᴇ ᴜsᴇᴅ ᴡɪᴛʜ ᴀ ʀᴇᴘʟʏ ᴛᴏ ᴀɴ ɪᴍᴀɢᴇ ᴏʀ sʜᴏᴜʟᴅ ɢɪᴠᴇ ᴜʀʟ"
            )

    elif message.reply_to_message and message.reply_to_message.photo:
        try:
            edit = await message.reply_text("ᴅᴏᴡɴʟᴏᴀᴅɪɴɢ ɪᴍᴀɢᴇ")
        except BadRequest:
            return

        photo = message.reply_to_message.photo[-1]
        file = await context.bot.get_file(photo.file_id)
        await file.download_to_drive("reverse.jpg")

        await edit.edit_text("ᴅᴏᴡɴʟᴏᴀᴅᴇᴅ ɪᴍᴀɢᴇ, ᴜᴘʟᴏᴀᴅɪɴɢ ᴛᴏ ɢᴏᴏɢʟᴇ...")

        result = Search(file_path="reverse.jpg")
        await edit.edit_text("ᴜᴘʟᴏᴀᴅᴇᴅ ᴛᴏ ɢᴏᴏɢʟᴇ, ғᴇᴛᴄʜɪɴɢ ʀᴇsᴜʟᴛs...")
        name = result["output"]
        link = result["similar"]

        await edit.edit_text(
            text=f"{name}",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text="sɪᴍɪʟᴀʀ",
                            url=link,
                        ),
                    ],
                ],
            ),
        )
        return
    else:
        await message.reply_text(
            "ᴄᴏᴍᴍᴀɴᴅ sʜᴏᴜʟᴅ ʙᴇ ᴜsᴇᴅ ᴡɪᴛʜ ʀᴇᴘʟʏɪɴɢ ᴛᴏ ᴀɴ ɪᴍᴀɢᴇ ᴏʀ ᴜʀʟ sʜᴏᴜʟᴅ ɢɪᴠᴇɴ."
        )


REVERSE_HANDLER = DisableAbleCommandHandler(["reverse", "pp"], reverse, block=False)
application.add_handler(REVERSE_HANDLER)

__help__ = """
ʀᴇᴠᴇʀsᴇ sᴇᴀʀᴄʜ ᴀɴʏ ɪᴍᴀɢᴇ ᴜsɪɴɢ ɢᴏᴏɢʟᴇ ɪᴍᴀɢᴇ sᴇᴀʀᴄʜ.

*ᴜsᴀɢᴇ:*
• sᴇɴᴅɪɴɢ /reverse ʙʏ ʀᴇᴘʟʏɪɴɢ ᴛᴏ ᴀɴʏ ɪᴍᴀɢᴇ
• /reverse ᴛʜᴇɴ ᴜʀʟ 
"""

__mod_name__ = "𝐆ᴏᴏɢʟᴇ"
