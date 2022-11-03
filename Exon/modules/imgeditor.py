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

from pyrogram import filters
from pyrogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)

from Exon import BOT_NAME, pgram

# By @AbishnoMF
from Exon.utils.resources.ImageEditor.edit_1 import (  # pylint:disable=import-error
    black_white,
    box_blur,
    bright,
    g_blur,
    mix,
    normal_blur,
)
from Exon.utils.resources.ImageEditor.edit_2 import (  # pylint:disable=import-error
    cartoon,
    circle_with_bg,
    circle_without_bg,
    contrast,
    edge_curved,
    pencil,
    sepia_mode,
    sticker,
)
from Exon.utils.resources.ImageEditor.edit_3 import (  # pylint:disable=import-error
    black_border,
    blue_border,
    green_border,
    red_border,
)
from Exon.utils.resources.ImageEditor.edit_4 import (  # pylint:disable=import-error
    inverted,
    removebg_plain,
    removebg_sticker,
    removebg_white,
    rotate_90,
    rotate_180,
    rotate_270,
    round_sticker,
)
from Exon.utils.resources.ImageEditor.edit_5 import (  # pylint:disable=import-error
    normalglitch_1,
    normalglitch_2,
    normalglitch_3,
    normalglitch_4,
    normalglitch_5,
    scanlineglitch_1,
    scanlineglitch_2,
    scanlineglitch_3,
    scanlineglitch_4,
    scanlineglitch_5,
)

lel = 00000000
# pylint:disable=import-error
@pgram.on_message(filters.command(["edit", "editor"]))
async def photo(client: pgram, message: Message):
    try:
        if not message.reply_to_message.photo:
            await client.send_message(message.chat.id, "ʀᴇᴘʟʏ ᴛᴏ ᴀɴ ɪᴍᴀɢᴇ ᴍᴀɴ!")
            return
    except:
        return
    global lel
    try:
        lel = message.from_user.id
    except:
        return
    try:
        await client.send_message(
            chat_id=message.chat.id,
            text="sᴇʟᴇᴄᴛ ʏᴏᴜʀ ʀᴇǫᴜɪʀᴇᴅ ᴍᴏᴅᴇ ғʀᴏᴍ ʙᴇʟᴏᴡ!ㅤㅤ",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(text="ʙʀɪɢʜᴛᴇɴ", callback_data="bright"),
                        InlineKeyboardButton(text="ᴍɪxᴇᴅ", callback_data="mix"),
                        InlineKeyboardButton(text="ʙ&ᴡ", callback_data="b|w"),
                    ],
                    [
                        InlineKeyboardButton(text="ᴄɪʀᴄʟᴇ", callback_data="circle"),
                        InlineKeyboardButton(text="ʙʟᴜʀ", callback_data="blur"),
                        InlineKeyboardButton(text="ʙᴏʀᴅᴇʀ", callback_data="border"),
                    ],
                    [
                        InlineKeyboardButton(text="sᴛɪᴄᴋᴇʀ", callback_data="stick"),
                        InlineKeyboardButton(text="ʀᴏᴛᴀᴛᴇ", callback_data="rotate"),
                        InlineKeyboardButton(text="ᴄᴏɴᴛʀᴀsᴛ", callback_data="contrast"),
                    ],
                    [
                        InlineKeyboardButton(text="sᴇᴘɪᴀ", callback_data="sepia"),
                        InlineKeyboardButton(text="ᴘᴇɴᴄɪʟ", callback_data="pencil"),
                        InlineKeyboardButton(text="ᴄᴀʀᴛᴏᴏɴ", callback_data="cartoon"),
                    ],
                    [
                        InlineKeyboardButton(text="ɪɴᴠᴇʀᴛ", callback_data="inverted"),
                        InlineKeyboardButton(text="ɢʟɪᴛᴄʜ", callback_data="glitch"),
                        InlineKeyboardButton(
                            text="ʀᴇᴍᴏᴠᴇ ʙɢ", callback_data="removebg"
                        ),
                    ],
                    [
                        InlineKeyboardButton(text="ᴄʟᴏsᴇ", callback_data="close_e"),
                    ],
                ]
            ),
            reply_to_message_id=message.reply_to_message.message_id,
        )
    except Exception as e:
        print(f"photomarkup error - {str(e)}")
        if "USER_IS_BLOCKED" in str(e):
            return
        try:
            await message.reply_text("sᴏᴍᴇᴛʜɪɴɢ ᴡᴇɴᴛ ᴡʀᴏɴɢ!", quote=True)
        except Exception:
            return


@pgram.on_callback_query()
async def cb_handler(client: pgram, query: CallbackQuery):
    user_id = query.from_user.id
    if lel == user_id:
        if query.data == "removebg":
            await query.message.edit_text(
                "**sᴇʟᴇᴄᴛ ʀᴇǫᴜɪʀᴇᴅ ᴍᴏᴅᴇ**ㅤㅤㅤㅤ",
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                text="ᴡɪᴛʜ ᴡʜɪᴛᴇ ʙɢ", callback_data="rmbgwhite"
                            ),
                            InlineKeyboardButton(
                                text="ᴡɪᴛʜᴏᴜᴛ ʙɢ", callback_data="rmbgplain"
                            ),
                        ],
                        [
                            InlineKeyboardButton(
                                text="sᴛɪᴄᴋᴇʀ", callback_data="rmbgsticker"
                            )
                        ],
                    ]
                ),
            )
        elif query.data == "stick":
            await query.message.edit(
                "**sᴇʟᴇᴄᴛ ᴀ ᴛʏᴘᴇ**",
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(text="ɴᴏʀᴍᴀʟ", callback_data="stkr"),
                            InlineKeyboardButton(
                                text="ᴇᴅɢᴇ ᴄᴜʀᴠᴇᴅ", callback_data="cur_ved"
                            ),
                        ],
                        [
                            InlineKeyboardButton(
                                text="ᴄɪʀᴄʟᴇ", callback_data="circle_sticker"
                            )
                        ],
                    ]
                ),
            )
        elif query.data == "rotate":
            await query.message.edit_text(
                "**sᴇʟᴇᴄᴛ ᴛʜᴇ ᴅᴇɢʀᴇᴇ**",
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(text="180", callback_data="180"),
                            InlineKeyboardButton(text="90", callback_data="90"),
                        ],
                        [InlineKeyboardButton(text="270", callback_data="270")],
                    ]
                ),
            )

        elif query.data == "glitch":
            await query.message.edit_text(
                "**sᴇʟᴇᴄᴛ ʀᴇǫᴜɪʀᴇᴅ ᴍᴏᴅᴇ**ㅤㅤㅤㅤ",
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                text="ɴᴏʀᴍᴀʟ", callback_data="normalglitch"
                            ),
                            InlineKeyboardButton(
                                text="sᴄᴀɴ ʟɪɴᴇs", callback_data="scanlineglitch"
                            ),
                        ]
                    ]
                ),
            )
        elif query.data == "normalglitch":
            await query.message.edit_text(
                "**sᴇʟᴇᴄᴛ ɢʟɪᴛᴄʜ ᴘᴏᴡᴇʀ ʟᴇᴠᴇʟ**",
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                text="1", callback_data="normalglitch1"
                            ),
                            InlineKeyboardButton(
                                text="2", callback_data="normalglitch2"
                            ),
                            InlineKeyboardButton(
                                text="3", callback_data="normalglitch3"
                            ),
                        ],
                        [
                            InlineKeyboardButton(
                                text="4", callback_data="normalglitch4"
                            ),
                            InlineKeyboardButton(
                                text="5", callback_data="normalglitch5"
                            ),
                        ],
                    ]
                ),
            )
        elif query.data == "scanlineglitch":
            await query.message.edit_text(
                "**sᴇʟᴇᴄᴛ ɢʟɪᴛᴄʜ ᴘᴏᴡᴇʀ ʟᴇᴠᴇʟ**",
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                text="1", callback_data="scanlineglitch1"
                            ),
                            InlineKeyboardButton(
                                text="2", callback_data="scanlineglitch2"
                            ),
                            InlineKeyboardButton(
                                text="3", callback_data="scanlineglitch3"
                            ),
                        ],
                        [
                            InlineKeyboardButton(
                                text="4", callback_data="scanlineglitch4"
                            ),
                            InlineKeyboardButton(
                                text="5", callback_data="scanlineglitch5"
                            ),
                        ],
                    ]
                ),
            )
        elif query.data == "blur":
            await query.message.edit(
                "**sᴇʟᴇᴄᴛ ᴀ ᴛʏᴘᴇ**",
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(text="ʙᴏx", callback_data="box"),
                            InlineKeyboardButton(text="ɴᴏʀᴍᴀʟ", callback_data="normal"),
                        ],
                        [InlineKeyboardButton(text="ɢᴀᴜssɪᴀɴ", callback_data="gas")],
                    ]
                ),
            )
        elif query.data == "circle":
            await query.message.edit_text(
                "**sᴇʟᴇᴄᴛ ʀᴇǫᴜɪʀᴇᴅ ᴍᴏᴅᴇ**",
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                text="ᴡɪᴛʜ ʙɢ", callback_data="circlewithbg"
                            ),
                            InlineKeyboardButton(
                                text="ᴡɪᴛʜᴏᴜᴛ ʙɢ", callback_data="circlewithoutbg"
                            ),
                        ]
                    ]
                ),
            )
        elif query.data == "border":
            await query.message.edit(
                "**sᴇʟᴇᴄᴛ ʙᴏʀᴅᴇʀ ᴄᴏʟᴏᴜʀ**",
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(text="ʀᴇᴅ", callback_data="red"),
                            InlineKeyboardButton(text="ɢʀᴇᴇɴ", callback_data="green"),
                        ],
                        [
                            InlineKeyboardButton(text="ʙʟᴀᴄᴋ", callback_data="black"),
                            InlineKeyboardButton(text="ʙʟᴜᴇ", callback_data="blue"),
                        ],
                    ]
                ),
            )

        elif query.data == "bright":
            await query.message.delete()
            await bright(client, query.message)

        elif query.data == "close_e":
            await query.message.delete()

        elif query.data == "mix":
            await query.message.delete()
            await mix(client, query.message)

        elif query.data == "b|w":
            await query.message.delete()
            await black_white(client, query.message)

        elif query.data == "circlewithbg":
            await query.message.delete()
            await circle_with_bg(client, query.message)

        elif query.data == "circlewithoutbg":
            await query.message.delete()
            await circle_without_bg(client, query.message)

        elif query.data == "green":
            await query.message.delete()
            await green_border(client, query.message)

        elif query.data == "blue":
            await query.message.delete()
            await blue_border(client, query.message)

        elif query.data == "red":
            await query.message.delete()
            await red_border(client, query.message)
        # AbishnoiMF
        elif query.data == "black":
            await query.message.delete()
            await black_border(client, query.message)

        elif query.data == "circle_sticker":
            await query.message.delete()
            await round_sticker(client, query.message)

        elif query.data == "inverted":
            await query.message.delete()
            await inverted(client, query.message)

        elif query.data == "stkr":
            await query.message.delete()
            await sticker(client, query.message)

        elif query.data == "cur_ved":
            await query.message.delete()
            await edge_curved(client, query.message)

        elif query.data == "90":
            await query.message.delete()
            await rotate_90(client, query.message)

        elif query.data == "180":
            await query.message.delete()
            await rotate_180(client, query.message)

        elif query.data == "270":
            await query.message.delete()
            await rotate_270(client, query.message)

        elif query.data == "contrast":
            await query.message.delete()
            await contrast(client, query.message)

        elif query.data == "box":
            await query.message.delete()
            await box_blur(client, query.message)

        elif query.data == "gas":
            await query.message.delete()
            await g_blur(client, query.message)

        elif query.data == "normal":
            await query.message.delete()
            await normal_blur(client, query.message)

        elif query.data == "sepia":
            await query.message.delete()
            await sepia_mode(client, query.message)

        elif query.data == "pencil":
            await query.message.delete()
            await pencil(client, query.message)

        elif query.data == "cartoon":
            await query.message.delete()
            await cartoon(client, query.message)

        elif query.data == "normalglitch1":
            await query.message.delete()
            await normalglitch_1(client, query.message)

        elif query.data == "normalglitch2":
            await query.message.delete()
            await normalglitch_2(client, query.message)

        elif query.data == "normalglitch3":
            await normalglitch_3(client, query.message)

        elif query.data == "normalglitch4":
            await query.message.delete()
            await normalglitch_4(client, query.message)

        elif query.data == "normalglitch5":
            await query.message.delete()
            await normalglitch_5(client, query.message)

        elif query.data == "scanlineglitch1":
            await query.message.delete()
            await scanlineglitch_1(client, query.message)

        elif query.data == "scanlineglitch2":
            await query.message.delete()
            await scanlineglitch_2(client, query.message)

        elif query.data == "scanlineglitch3":
            await query.message.delete()
            await scanlineglitch_3(client, query.message)

        elif query.data == "scanlineglitch4":
            await query.message.delete()
            await scanlineglitch_4(client, query.message)

        elif query.data == "scanlineglitch5":
            await query.message.delete()
            await scanlineglitch_5(client, query.message)

        elif query.data == "rmbgwhite":
            await query.message.delete()
            await removebg_white(client, query.message)

        elif query.data == "rmbgplain":
            await query.message.delete()
            await removebg_plain(client, query.message)

        elif query.data == "rmbgsticker":
            await removebg_sticker(client, query.message)


__mod_name__ = "𝙴ᴅɪᴛᴏʀ"
__help__ = f"""
{BOT_NAME} ʜᴀᴠᴇ sᴏᴍᴇ ᴀᴅᴠᴀɴᴄᴇᴅ ɪᴍᴀɢᴇ ᴇᴅɪᴛɪɴɢ ᴛᴏᴏʟs ɪɴʙᴜɪʟᴛ

ʙʀɪɢʜᴛ, ᴄɪʀᴄʟᴇ, ʀᴇᴍʙɢ, ʙʟᴜʀ, ʙᴏʀᴅᴇʀ, ғʟɪᴘ, ɢʟɪᴛᴄʜ, sᴛɪᴄᴋᴇʀ ᴍᴀᴋᴇʀ ᴀɴᴅ ᴍᴏʀᴇ


⍟ /edit [reply to image]*:* `ᴏᴘᴇɴ ᴛʜᴇ ɪᴍᴀɢᴇ ᴇᴅɪᴛᴏʀ `

⍟ /rmbg [REPLY]*:* `ʀᴇᴍᴏᴠᴇ BG ᴏғ ʀᴇᴘʟɪᴇᴅ ɪᴍᴀɢᴇ/sᴛɪᴄᴋᴇʀ `.
"""
