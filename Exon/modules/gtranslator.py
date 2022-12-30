from gpytranslate import SyncTranslator
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.constants import ParseMode
from telegram.ext import CallbackContext

from Exon import application
from Exon.modules.disable import DisableAbleCommandHandler

trans = SyncTranslator()


def translate(update: Update, context: CallbackContext) -> None:
    bot = context.bot
    message = update.effective_message
    reply_msg = message.reply_to_message
    if not reply_msg:
        message.reply_text("ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴍᴇssᴀɢᴇ ᴛᴏ ᴛʀᴀɴsʟᴀᴛᴇ ɪᴛ!")
        return
    if reply_msg.caption:
        to_translate = reply_msg.caption
    else:
        to_translate = reply_msg.text
    try:
        args = message.text.split()[1].lower()
        if "//" in args:
            source = args.split("//")[0]
            dest = args.split("//")[1]
        else:
            source = trans.detect(to_translate)
            dest = args
    except IndexError:
        source = trans.detect(to_translate)
        dest = "en"
    translation = trans(to_translate, sourcelang=source, targetlang=dest)
    reply = (
        f"<b>ʟᴀɴɢᴜᴀɢᴇ: {source} -> {dest}</b>:\n\n"
        f"ᴛʀᴀɴsʟᴀᴛɪᴏɴ: <code>{translation.text}</code>"
    )

    bot.send_message(text=reply, chat_id=message.chat.id, parse_mode=ParseMode.HTML)


def languages(update: Update, context: CallbackContext) -> None:
    update.effective_message.reply_text(
        "ᴄʟɪᴄᴋ ᴏɴ ᴛʜᴇ ʙᴜᴛᴛᴏɴ ʙᴇʟᴏᴡ ᴛᴏ sᴇᴇ ᴛʜᴇ ʟɪsᴛ ᴏғ sᴜᴘᴘᴏʀᴛᴇᴅ ʟᴀɴɢᴜᴀɢᴇ ᴄᴏᴅᴇs.",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text="ʟᴀɴɢᴜᴀɢᴇ ᴄᴏᴅᴇs",
                        url="https://telegra.ph/ɪᴛs-ᴍᴇ-𒆜-Aʙɪsʜɴᴏɪ-07-30-2",
                    ),
                ],
            ],
            disable_web_page_preview=True,
        ),
    )


application.add_handler(
    DisableAbleCommandHandler(["tr", "tl"], translate, pass_args=True, block=False)
)
application.add_handler(
    DisableAbleCommandHandler(["langs", "lang"], languages, block=False)
)


__command_list__ = ["tr", "tl", "lang", "langs"]

__mod_name__ = "𝐓ʀᴀɴsʟᴀᴛᴏʀ"
