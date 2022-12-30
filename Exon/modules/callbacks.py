from pyrogram import filters
from pyrogram.types import CallbackQuery
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.constants import ParseMode
from telegram.ext import CallbackQueryHandler, ContextTypes
from telegram.helpers import escape_markdown

from Exon import BOT_NAME, BOT_USERNAME, OWNER_ID, SUPPORT_CHAT, app, application
from Exon.__main__ import buttons


@app.on_callback_query(filters.regex("close_"))
async def close(_, cb: CallbackQuery):
    await cb.answer()
    await cb.message.delete()


async def EXON_about_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query.data == "EXON_":
        await query.message.edit_caption(
            f"๏ ɪ'ᴍ {BOT_NAME}, ᴀ ᴘᴏᴡᴇʀғᴜʟ ɢʀᴏᴜᴘ ᴍᴀɴᴀɢᴇᴍᴇɴᴛ ʙᴏᴛ ʙᴜɪʟᴛ ᴛᴏ ʜᴇʟᴘ ʏᴏᴜ ᴍᴀɴᴀɢᴇ ʏᴏᴜʀ ɢʀᴏᴜᴘ ᴇᴀsɪʟʏ."
            "\n• I scan ʀᴇsᴛʀɪᴄᴛ ᴜsᴇʀs."
            "\n• ɪ ᴄᴀɴ ɢʀᴇᴇᴛ ᴜsᴇʀs ᴡɪsh ᴄᴜsᴛᴏᴍɪᴢᴀʙʟᴇ ᴡᴇʟᴄᴏᴍᴇ ᴍᴇssᴀɢᴇs ᴀɴᴅ ᴇᴠᴇɴ sᴇᴛ ᴀ ɢʀᴏᴜᴘ's ʀᴜʟᴇs."
            "\n• ɪ ʜᴀᴠᴇ ᴀɴ ᴀᴅᴠᴀɴᴄᴇᴅ ᴀɴᴛɪ-ғʟᴏᴏᴅ sʏsᴛᴇᴍ."
            "\n• ɪ ᴄᴀɴ ᴡᴀʀɴ ᴜsᴇʀs ᴜɴsɪʟ ᴛʜᴇʏ ʀᴇᴀᴄʜ ᴍᴀx ᴡᴀʀɴx, ᴡɪᴛʜ ᴇᴀᴄʜ ᴘʀᴇᴅᴇғɪɴᴇᴅ ᴀᴄᴛɪᴏɴs sᴜᴄʜ ᴀs ʙᴀɴ, ᴍᴜᴛᴇ, ᴋɪᴄᴋ, ᴇᴛᴄ."
            "\n• ɪ ʜᴀᴠᴇ ᴀ ɴᴏᴛᴇ ᴋᴇᴇᴘɪɴɢ sʏsᴛᴇᴍ, ʙʟᴀᴄᴋʟɪsᴛs, ᴀɴᴅ ᴇᴠᴇɴ ᴘʀᴇᴅᴇᴛᴇʀᴍɪɴᴇᴅ ʀᴇᴘʟɪᴇs ᴏɴ ᴄᴇʀᴛᴀɪɴ ᴋᴇʏᴡᴏʀᴅs."
            "\n• ɪ ᴄʜᴇᴄᴋ ғᴏʀ ᴀᴅᴍɪɴs ᴘᴇʀᴍɪssɪᴏɴs ʙᴇғᴏʀᴇ ᴇxᴇᴄᴜᴛɪɴɢ ᴀɴʏ ᴄᴏᴍᴍᴀɴᴅ ᴀɴᴅ ᴍᴏʀᴇ sᴛᴜғғs"
            "\n\n_Exᴏɴ ʟɪᴄᴇɴsᴇᴅ ᴜɴᴅᴇʀ ᴛʜᴇ GNU ɢᴇɴᴇʀᴀʟ ᴘᴜʙʟɪᴄ ʟɪᴄᴇɴsᴇ v3.0_"
            f"\n\n*ᴄʟɪᴄᴋ ᴏɴ ʙᴜᴛᴛᴏɴ ʙᴇʟʟᴏᴡ ᴛᴏ ɢᴇᴛ ʙᴀsɪᴄ ʜᴇʟᴘ ғᴏʀ {BOT_NAME} *.",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(text="ᴀᴅᴍɪɴs", callback_data="EXON_ADMIN"),
                        InlineKeyboardButton(text="ɴᴏᴛᴇs", callback_data="EXON_notes"),
                    ],
                    [
                        InlineKeyboardButton(
                            text="sᴜᴘᴘᴏʀᴛ", callback_data="EXON_SUPPORT"
                        ),
                        InlineKeyboardButton(
                            text="ᴄʀᴇᴅɪᴛs", callback_data="EXON_CREDIT"
                        ),
                    ],
                    [
                        InlineKeyboardButton(
                            text="sᴏᴜʀᴄᴇ",
                            callback_data="EXON_SOURCE",
                        ),
                    ],
                    [
                        InlineKeyboardButton(
                            text="ɢᴏ ʙᴀᴄᴋ", callback_data="start_back"
                        ),
                    ],
                ]
            ),
        )

    elif query.data == "EXON_ADMIN":
        await query.message.edit_caption(
            f"━━━━━━━ *ᴀᴅᴍɪɴs* ━━━━━━━\n",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(text="🏡", callback_data="start_back"),
                        InlineKeyboardButton(text="🛡️", callback_data="EXON_ADMIN"),
                        InlineKeyboardButton(text="💳", callback_data="EXON_CREDIT"),
                        InlineKeyboardButton(text="🕹️", callback_data="EXON_SOURCE"),
                        InlineKeyboardButton(text="🖥️", url=f"http://t.me/{BOT_USERNAME}?start=help"),
                    ]
                ]
            ),
        )

    elif query.data == "EXON_notes":
        await query.message.edit_caption(
            f"<b>๏ sᴇᴛᴛɪɴɢ ᴜᴘ ɴᴏᴛᴇs</b>"
            f"\nʏᴏᴜ ᴄᴀɴ sᴀᴠᴇ ᴍᴇssᴀɢᴇ/ᴍᴇᴅɪᴀ/ᴀᴜᴅɪᴏ ᴏʀ ᴀɴʏᴛʜɪɴɢ ᴀs ɴᴏᴛᴇs"
            f"\nᴛᴏ ɢᴇᴛ ᴀ ɴᴏᴛᴇ sɪᴍᴘʟʏ ᴜsᴇ # ᴀᴛ ᴛʜᴇ ʙᴇɢɪɴɴɪɴɢ ᴏғ ᴀ ᴡᴏʀᴅ"
            f"\n\nʏᴏᴜ ᴄᴀɴ ᴀʟsᴏ sᴇᴛ ʙᴜᴛᴛᴏɴs ғᴏʀ ɴᴏᴛᴇs ᴀɴᴅ ғɪʟᴛᴇʀs (ʀᴇғᴇʀ ʜᴇʟᴘ ᴍᴇɴᴜ)",
            parse_mode=ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton(text="ɢᴏ ʙᴀᴄᴋ", callback_data="EXON_")]]
            ),
        )
    elif query.data == "EXON_SUPPORT":
        await query.message.edit_caption(
            f"*๏ ᴇxᴏɴ sᴜᴘᴘᴏʀᴛ ᴄʜᴀᴛs*"
            f"\nᴊᴏɪɴ ᴍʏ sᴜᴘᴘᴏʀᴛ ɢʀᴏᴜᴘ/ᴄʜᴀɴɴᴇʟ ғᴏʀ sᴇᴇ ᴏʀ ʀᴇᴘᴏʀᴛ ᴀ ᴘʀᴏʙʟᴇᴍ ᴏɴ {BOT_NAME}",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text="sᴜᴘᴘᴏʀᴛ", url=f"t.me/{SUPPORT_CHAT}"
                        ),
                        InlineKeyboardButton(
                            text="ᴜᴘᴅᴀᴛᴇs", url="https://t.me/Abishnoi_bots"
                        ),
                    ],
                    [
                        InlineKeyboardButton(text="ɢᴏ ʙᴀᴄᴋ", callback_data="EXON_"),
                    ],
                ]
            ),
        )

    elif query.data == "EXON_CREDIT":  # ᴄʀᴇᴅɪᴛ  i ʜᴏᴘᴇ ᴇᴅɪᴛ ɴᴀɪ ʜᴏɢᴀ
        await query.message.edit_caption(
            f"━━━━━━━ *ᴄʀᴇᴅɪᴛ* ━━━━━━━"
            "\n🛡️ *ᴄʀᴇᴅɪᴛ ꜰᴏʀ ᴇxᴏɴ ʀᴏʙᴏᴛ* 🛡️"
            "\n\nʜᴇʀᴇ ɪꜱ ᴛʜᴇ ᴅᴇᴠᴇʟᴏᴘᴇʀ ᴀɴᴅ"
            f"\nꜱᴘᴏɴꜱᴏʀ ᴏꜰ [{BOT_NAME}](t.me/{BOT_USERNAME})"
            "\n\nʜᴇ ꜱᴘᴇɴᴛ ᴀ ʟᴏᴛ ᴏꜰ ᴛɪᴍᴇ ꜰᴏʀ"
            f"\nᴍᴀᴋɪɴɢ [{BOT_NAME}](t.me/Abishnoi1M)"
            "\nꜱᴜᴘᴇʀ ɢʀᴏᴜᴘ ᴍᴀɴᴀɢᴇᴍᴇɴᴛ ʙᴏᴛ",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(text="🏡", callback_data="start_back"),
                        InlineKeyboardButton(text="🛡️", callback_data="EXON_ADMIN"),
                        InlineKeyboardButton(text="💳", callback_data="EXON_CREDIT"),
                        InlineKeyboardButton(text="⚔️", callback_data="EXON_SOURCE"),
                        InlineKeyboardButton(text="🖥️", url=f"http://t.me/{BOT_USERNAME}?start=help"),
                    ],
                    [
                        InlineKeyboardButton(
                            text="ᴀʙɪsʜɴᴏɪ",
                            url="https://t.me/Abishnoi1M",  # ᴄʀᴇᴅɪᴛ ( ɪ ʜᴏᴘᴇ ɴᴏ ᴄʜᴀɴɢᴇ )
                        ),
                        InlineKeyboardButton(
                            text="ᴄʜᴀᴛ", url=f"https://t.me/{SUPPORT_CHAT}"
                        ),
                    ],
                ]
            ),
        )
    elif query.data == "EXON_SOURCE":
        await query.message.edit_caption(
            caption=f"""
*ʜᴇʏ,
 ᴛʜɪs ɪs {BOT_NAME} ,
ᴀɴ ᴏᴩᴇɴ sᴏᴜʀᴄᴇ ᴛᴇʟᴇɢʀᴀᴍ ɢʀᴏᴜᴩ ᴍᴀɴᴀɢᴇᴍᴇɴᴛ ʙᴏᴛ.*

ᴡʀɪᴛᴛᴇɴ ɪɴ ᴩʏᴛʜᴏɴ ᴡɪᴛʜ ᴛʜᴇ ʜᴇʟᴩ ᴏғ : [ᴛᴇʟᴇᴛʜᴏɴ](https://github.com/LonamiWebs/Telethon), 
[ᴩʏʀᴏɢʀᴀᴍ](https://github.com/pyrogram/pyrogram), 
[ᴩʏᴛʜᴏɴ-ᴛᴇʟᴇɢʀᴀᴍ-ʙᴏᴛ](https://github.com/python-telegram-bot/python-telegram-bot), 
ᴀɴᴅ ᴜsɪɴɢ [sǫʟᴀʟᴄʜᴇᴍʏ](https://www.sqlalchemy.org) ᴀɴᴅ [ᴍᴏɴɢᴏ](https://cloud.mongodb.com) ᴀs ᴅᴀᴛᴀʙᴀsᴇ.

*ʜᴇʀᴇ ɪs ᴍʏ sᴏᴜʀᴄᴇ ᴄᴏᴅᴇ :* [{BOT_NAME}](https://github.com/Abishnoi69/ExonRobot)


ᴇxᴏɴ ʀᴏʙᴏᴛ ɪs ʟɪᴄᴇɴsᴇᴅ ᴜɴᴅᴇʀ ᴛʜᴇ [ᴍɪᴛ ʟɪᴄᴇɴsᴇ](https://github.com/Abishnoi69/ExonRobot/blob/main/LICENSE).
© 2022 - 2023 [@ᴀʙɪsʜɴᴏɪᴍғ](https://t.me/AbishnoiMF), ᴀʟʟ ʀɪɢʜᴛs ʀᴇsᴇʀᴠᴇᴅ.
""",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(text="🏡", callback_data="start_back"),
                        InlineKeyboardButton(text="🛡️", callback_data="EXON_ADMIN"),
                        InlineKeyboardButton(text="💳", callback_data="EXON_CREDIT"),
                        InlineKeyboardButton(text="🧑‍", url=f"tg://user?id={OWNER_ID}"),
                        InlineKeyboardButton(text="🖥️", url=f"http://t.me/{BOT_USERNAME}?start=help"),
                    ],
                    [
                        InlineKeyboardButton(
                            text="ꜱᴏᴜʀᴄᴇ",
                            url="https://github.com/Abishnoi69/ExonRobot",
                        ),
                    ],
                ]
            ),
        )


async def EXON_back_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query.data == "start_back":
        first_name = update.effective_user.first_name
        await query.message.edit_caption(
            escape_markdown(
                f"""ʜҽʏ ᴛʜᴇʀᴇ {first_name}.\
                \nɪ'ᴍ ʜᴇʀᴇ ᴛᴏ ʜᴇʟᴘ ʏᴏᴜ ᴍᴀɴᴀɢᴇ ʏᴏᴜʀ ɢʀᴏᴜᴘs!
                \nʜɪᴛ /help ᴛᴏ ғɪɴᴅ ᴏᴜᴛ ᴍᴏʀᴇ ᴀʙᴏᴜᴛ ʜᴏᴡ ᴛᴏ ᴜsᴇ ᴍᴇ ᴛᴏ ᴍʏ ғᴜʟʟ ᴘᴏᴛᴇɴᴛɪᴀʟ."""
            ),
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup(buttons),
        )


about_callback_handler = CallbackQueryHandler(
    EXON_about_callback, pattern=r"EXON_", block=False
)
back_callback_handler = CallbackQueryHandler(
    EXON_back_callback, pattern="start_back", block=False
)

application.add_handler(about_callback_handler)
application.add_handler(back_callback_handler)
