import os
import re
from html import escape

from telegram import ChatMemberAdministrator, Update
from telegram.constants import ChatID, ChatType, ParseMode
from telegram.error import BadRequest
from telegram.ext import CommandHandler, ContextTypes
from telegram.helpers import mention_html
from telethon import events
from telethon.tl.functions.channels import GetFullChannelRequest
from telethon.tl.types import ChannelParticipantsAdmins

from Exon import DEV_USERS, DRAGONS, OWNER_ID, exon, telethn
from Exon.__main__ import STATS, USER_INFO
from Exon.modules.disable import DisableAbleCommandHandler
from Exon.modules.helper_funcs.chat_status import check_admin
from Exon.modules.helper_funcs.extraction import extract_user
from Exon.modules.sql.approve_sql import is_approved
from Exon.modules.users import get_user_id

INFOPIC = True


async def get_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bot, args = context.bot, context.args
    chat = update.effective_chat
    message = update.effective_message
    user_id = await extract_user(message, context, args)

    if message.reply_to_message:
        if chat.is_forum and message.reply_to_message.forum_topic_created:
            await message.reply_text(
                f"ᴛʜɪs ɢʀᴏᴜᴘ's ɪᴅ ɪs <code>:{chat.id}</code> \nᴛʜɪs ᴛᴏᴘɪᴄ's ɪᴅ ɪs <code>{message.message_thread_id}</code>",
                parse_mode=ParseMode.HTML,
            )
            return
    else:
        pass

    if message.reply_to_message and message.reply_to_message.forward_from:

        user1 = message.reply_to_message.from_user
        user2 = message.reply_to_message.forward_from

        await message.reply_text(
            f"<b>ᴛᴇʟᴇɢʀᴀᴍ ɪᴅ:</b>,\n"
            f"• {html.escape(user2.first_name)} - <code>{user2.id}</code>.\n"
            f"• {html.escape(user1.first_name)} - <code>{user1.id}</code>.",
            parse_mode=ParseMode.HTML,
        )
    elif len(args) >= 1 or message.reply_to_message:
        user = await bot.get_chat(user_id)
        await message.reply_text(
            f"{html.escape(user.first_name)}'s ɪᴅ ɪs <code>{user.id}</code>.",
            parse_mode=ParseMode.HTML,
        )
    elif chat.type == "private":
        await message.reply_text(
            f"ʏᴏᴜʀ ɪᴅ ɪs <code>{chat.id}</code>.",
            parse_mode=ParseMode.HTML,
        )
    else:
        await message.reply_text(
            f"ᴛʜɪs ɢʀᴏᴜᴘ's ɪᴅ ɪs <code>{chat.id}</code>.",
            parse_mode=ParseMode.HTML,
        )
    return


@telethn.on(
    events.NewMessage(
        pattern="/ginfo ",
        from_users=(DRAGONS or []),
    ),
)
async def group_info(event) -> None:
    chat = event.text.split(" ", 1)[1]
    try:
        entity = await event.client.get_entity(chat)
        totallist = await event.client.get_participants(
            entity,
            filter=ChannelParticipantsAdmins,
        )
        ch_full = await event.client(GetFullChannelRequest(channel=entity))
    except:
        await event.reply(
            "ᴄᴀɴ'ᴛ ғᴏʀ sᴏᴍᴇ ʀᴇᴀsᴏɴ, ᴍᴀʏʙᴇ ɪᴛ ɪs ᴀ ᴘʀɪᴠᴀᴛᴇ ᴏɴᴇ ᴏʀ ᴛʜᴀᴛ I ᴀᴍ ʙᴀɴɴᴇᴅ ᴛʜᴇʀᴇ.",
        )
        return
    msg = f"**ɪᴅ**: `{entity.id}`"
    msg += f"\n**ᴛɪᴛʟᴇ**: `{entity.title}`"
    try:
        msg += f"\n**ᴅᴀᴛᴀᴄᴇɴᴛᴇʀ**: `{entity.photo.dc_id}`"
        msg += f"\n**ᴠɪᴅᴇᴏ ᴘғᴘ**: `{entity.photo.has_video}`"
    except:
        pass
    msg += f"\n**sᴜᴘᴇʀɢʀᴏᴜᴘ**: `{entity.megagroup}`"
    msg += f"\n**ʀᴇsᴛʀɪᴄᴛᴇᴅ**: `{entity.restricted}`"
    msg += f"\n**sᴄᴀᴍ**: `{entity.scam}`"
    msg += f"\n**sʟᴏᴡᴍᴏᴅᴇ**: `{entity.slowmode_enabled}`"
    if entity.username:
        msg += f"\n**ᴜsᴇʀɴᴀᴍᴇ**: {entity.username}"
    msg += "\n\n**ᴍᴇᴍʙᴇʀ sᴛᴀᴛs:**"
    msg += f"\n`ᴀᴅᴍɪɴs:` `{len(totallist)}`"
    msg += f"\n`ᴜsᴇʀs`: `{totallist.total}`"
    msg += "\n\n**ᴀᴅᴍɪɴs ʟɪsᴛ:**"
    for x in totallist:
        msg += f"\n• [{x.id}](tg://user?id={x.id})"
    msg += f"\n\n**ᴅᴇsᴄʀɪᴘᴛɪᴏɴ**:\n`{ch_full.full_chat.about}`"
    await event.reply(msg)


async def gifid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.effective_message
    if (
        msg.reply_to_message
        and msg.reply_to_message.animation
        and not msg.reply_to_message.forum_topic_created
    ):
        await update.effective_message.reply_text(
            f"ɢɪғ ɪᴅ:\n<code>{msg.reply_to_message.animation.file_id}</code>",
            parse_mode=ParseMode.HTML,
        )
    else:
        await update.effective_message.reply_text(
            "ᴘʟᴇᴀsᴇ ʀᴇᴘʟʏ ᴛᴏ ᴀ ɢɪғ ᴛᴏ ɢᴇᴛ ɪᴛs ɪᴅ."
        )


async def info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    message = update.effective_message
    args = context.args
    bot = context.bot

    head = ""
    premium = False

    reply = await message.reply_text(
        "<code>ɢᴇᴛᴛɪɴɢ ɪɴғᴏʀᴍᴀᴛɪᴏɴ...</code>", parse_mode=ParseMode.HTML
    )

    if len(args) >= 1 and args[0][0] == "@":
        user_name = args[0]
        user_id = await get_user_id(user_name)

        if not user_id:
            try:
                chat_obj = await bot.get_chat(user_name)
            except BadRequest:
                await reply.edit_text(
                    "I ᴄᴀɴ'ᴛ ɢᴇᴛ ɪɴғᴏʀᴍᴀᴛɪᴏɴ ᴀʙᴏᴜᴛ ᴛʜɪs ᴜsᴇʀ/ᴄʜᴀɴɴᴇʟ/ɢʀᴏᴜᴘ."
                )
                return
            userid = chat_obj.id
        else:
            userid = user_id
    elif len(args) >= 1 and args[0].lstrip("-").isdigit():
        userid = int(args[0])
    elif message.reply_to_message and not message.reply_to_message.forum_topic_created:
        if message.reply_to_message.sender_chat:
            userid = message.reply_to_message.sender_chat.id
        elif message.reply_to_message.from_user:
            if message.reply_to_message.from_user.id == ChatID.FAKE_CHANNEL:
                userid = message.reply_to_message.chat.id
            else:
                userid = message.reply_to_message.from_user.id
                premium = message.reply_to_message.from_user.is_premium
    elif not message.reply_to_message and not args:
        if message.from_user.id == ChatID.FAKE_CHANNEL:
            userid = message.sender_chat.id
        else:
            userid = message.from_user.id
            premium = message.from_user.is_premium

    try:
        chat_obj = await bot.get_chat(userid)
    except (BadRequest, UnboundLocalError):
        await reply.edit_text("I ᴄᴀɴ'ᴛ ɢᴇᴛ ɪɴғᴏʀᴍᴀᴛɪᴏɴ ᴀʙᴏᴜᴛ ᴛʜɪs ᴜsᴇʀ/ᴄʜᴀɴɴᴇʟ/ɢʀᴏᴜᴘ.")
        return

    if chat_obj.type == ChatType.PRIVATE:
        if not chat_obj.username:
            head = f"╒═══「<b> ᴜsᴇʀ ɪɴғᴏʀᴍᴀᴛɪᴏɴ:</b> 」\n"
            await reply.edit_text("ғᴏᴜɴᴅ ᴜsᴇʀ, ɢᴇᴛᴛɪɴɢ ɪɴғᴏʀᴍᴀᴛɪᴏɴ...")
        elif chat_obj.username and chat_obj.username.endswith("bot"):
            head = f"╒═══「<b> ʙᴏᴛ ɪɴғᴏʀᴍᴀᴛɪᴏɴ:</b> 」\n"
            await reply.edit_text("ғᴏᴜɴᴅ ʙᴏᴛ, ɢᴇᴛᴛɪɴɢ ɪɴғᴏʀᴍᴀᴛɪᴏɴ...")
        else:
            head = f"╒═══「<b> ᴜsᴇʀ ɪɴғᴏʀᴍᴀᴛɪᴏɴ:</b> 」\n"
            await reply.edit_text("ғᴏᴜɴᴅ ᴜsᴇʀ, ɢᴇᴛᴛɪɴɢ ɪɴғᴏʀᴍᴀᴛɪᴏɴ...")
        head += f"<b>\nɪᴅ:</b> <code>{chat_obj.id}</code>"
        head += f"<b>\nғɪʀsᴛ ɴᴀᴍᴇ:</b> {chat_obj.first_name}"
        if chat_obj.last_name:
            head += f"<b>\nʟᴀsᴛ ɴᴀᴍᴇ:</b> {chat_obj.last_name}"
        if chat_obj.username:
            head += f"<b>\nᴜsᴇʀɴᴀᴍᴇ:</b> @{chat_obj.username}"
        head += f"\nᴘᴇʀᴍᴀʟɪɴᴋ: {mention_html(chat_obj.id, 'link')}"
        if chat_obj.username and not chat_obj.username.endswith("bot"):
            head += f"<b>\nᴘʀᴇᴍɪᴜᴍ ᴜsᴇʀ:</b> {premium}"
        if chat_obj.bio:
            head += f"<b>\n\nʙɪᴏ:</b> {chat_obj.bio}"

            chat_member = await chat.get_member(chat_obj.id)
            if isinstance(chat_member, ChatMemberAdministrator):
                head += f"<b>\nᴘʀᴇsᴇɴᴄᴇ:</b> {chat_member.status}"
                if chat_member.custom_title:
                    head += f"<b>\nᴀᴅᴍɪɴ ᴛɪᴛʟᴇ:</b> {chat_member.custom_title}"
            else:
                head += f"<b>\nᴘʀᴇsᴇɴᴄᴇ:</b> {chat_member.status}"

            if is_approved(chat.id, chat_obj.id):
                head += f"<b>\nᴀᴘᴘʀᴏᴠᴇᴅ:</b> ᴛʜɪs ᴜsᴇʀ ɪs ᴀᴘᴘʀᴏᴠᴇᴅ ɪɴ ᴛʜɪs ᴄʜᴀᴛ."

        disaster_level_present = False

        if chat_obj.id == OWNER_ID:
            head += "\n\nᴛʜᴇ ᴅɪsᴀsᴛᴇʀ ʟᴇᴠᴇʟ ᴏғ ᴛʜɪs ᴘᴇʀsᴏɴ ɪs 'ᴍʏ ᴏᴡɴᴇʀ."
            disaster_level_present = True
        elif chat_obj.id in DEV_USERS:
            head += "\n\nᴛʜɪs ᴜsᴇʀ ɪs ᴍᴇᴍʙᴇʀ ᴏғ 'ᴛᴇᴀᴍ ᴀʙɪsʜɴᴏɪ."
            disaster_level_present = True
        elif chat_obj.id in DRAGONS:
            head += "\n\nᴛʜᴇ ᴅɪsᴀsᴛᴇʀ ʟᴇᴠᴇʟ ᴏғ ᴛʜɪs ᴘᴇʀsᴏɴ ɪs 'ᴅʀᴀɢᴏɴ."
            disaster_level_present = True
        if disaster_level_present:
            head += ' [<a href="https://t.me/Abishnoi_bots/54">?</a>]'.format(
                bot.username,
            )

        for mod in USER_INFO:
            try:
                mod_info = mod.__user_info__(chat_obj.id).strip()
            except TypeError:
                mod_info = mod.__user_info__(chat_obj.id, chat.id).strip()

            head += "\n\n" + mod_info if mod_info else ""

    if chat_obj.type == ChatType.SENDER:
        head = f"╒═══「<b>sᴇɴᴅᴇʀ ᴄʜᴀᴛ ɪɴғᴏʀᴍᴀᴛɪᴏɴ:</b> 」\n"
        await reply.edit_text("ғᴏᴜɴᴅ sᴇɴᴅᴇʀ ᴄʜᴀᴛ, ɢᴇᴛᴛɪɴɢ ɪɴғᴏʀᴍᴀᴛɪᴏɴ...")
        head += f"<b>\nɪᴅ:</b> <code>{chat_obj.id}</code>"
        if chat_obj.title:
            head += f"<b>\nᴛɪᴛʟᴇ:</b> {chat_obj.title}"
        if chat_obj.username:
            head += f"<b>\nᴜsᴇʀɴᴀᴍᴇ:</b> @{chat_obj.username}"
        head += f"\nᴘᴇʀᴍᴀʟɪɴᴋ: {mention_html(chat_obj.id, 'link')}"
        if chat_obj.description:
            head += f"<b>\n\nᴅᴇsᴄʀɪᴘᴛɪᴏɴ:</b> {chat_obj.description}"

    elif chat_obj.type == ChatType.CHANNEL:
        head = f"╒═══「<b> ᴄʜᴀɴɴᴇʟ ɪɴғᴏʀᴍᴀᴛɪᴏɴ:</b> 」\n"
        await reply.edit_text("ғᴏᴜɴᴅᴇᴅ ᴄʜᴀɴɴᴇʟ, ɢᴇᴛᴛɪɴɢ ɪɴғᴏʀᴍᴀᴛɪᴏɴ...")
        head += f"<b>\nɪᴅ:</b> <code>{chat_obj.id}</code>"
        if chat_obj.title:
            head += f"<b>\nᴛɪᴛʟᴇ:</b> {chat_obj.title}"
        if chat_obj.username:
            head += f"<b>\nᴜsᴇʀɴᴀᴍᴇ:</b> @{chat_obj.username}"
        head += f"\nᴘᴇʀᴍᴀʟɪɴᴋ: {mention_html(chat_obj.id, 'link')}"
        if chat_obj.description:
            head += f"<b>\n\nᴅᴇsᴄʀɪᴘᴛɪᴏɴ:</b> {chat_obj.description}"
        if chat_obj.linked_chat_id:
            head += f"<b>\nʟɪɴᴋᴇᴅ ᴄʜᴀᴛ ɪᴅ:</b> <code>{chat_obj.linked_chat_id}</code>"

    elif chat_obj.type in [ChatType.GROUP, ChatType.SUPERGROUP]:
        head = f"╒═══「<b> ɢʀᴏᴜᴘ ɪɴғᴏʀᴍᴀᴛɪᴏɴ:</b> 」\n"
        await reply.edit_text("ғᴏᴜɴᴅ ɢʀᴏᴜᴘ, ɢᴇᴛᴛɪɴɢ ɪɴғᴏʀᴍᴀᴛɪᴏɴ...")
        head += f"<b>\nɪᴅ:</b> <code>{chat_obj.id}</code>"
        if chat_obj.title:
            head += f"<b>\nᴛɪᴛʟᴇ:</b> {chat_obj.title}"
        if chat_obj.username:
            head += f"<b>\nᴜsᴇʀɴᴀᴍᴇ:</b> @{chat_obj.username}"
        head += f"\nᴘᴇʀᴍᴀʟɪɴᴋ: {mention_html(chat_obj.id, 'link')}"
        if chat_obj.description:
            head += f"<b>\n\nᴅᴇsᴄʀɪᴘᴛɪᴏɴ:</b> {chat_obj.description}"

    if INFOPIC:
        try:
            if chat_obj.photo:
                _file = await chat_obj.photo.get_big_file()
                # _file = await bot.get_file(file_id)
                await _file.download_to_drive(f"{chat_obj.id}.png")

                await message.reply_photo(
                    photo=open(f"{chat_obj.id}.png", "rb"),
                    caption=(head),
                    parse_mode=ParseMode.HTML,
                )
                await reply.delete()
                os.remove(f"{chat_obj.id}.png")
            else:
                await reply.edit_text(
                    escape(head),
                    parse_mode=ParseMode.HTML,
                    disable_web_page_preview=True,
                )

        except:
            await reply.edit_text(
                escape(head),
                parse_mode=ParseMode.HTML,
                disable_web_page_preview=True,
            )


@check_admin(only_sudo=True)
async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    stats = "<b>📊 ᴄᴜʀʀᴇɴᴛ sᴛᴀᴛs:</b>\n" + "\n".join([mod.__stats__() for mod in STATS])
    result = re.sub(r"(\d+)", r"<code>\1</code>", stats)
    await update.effective_message.reply_text(result, parse_mode=ParseMode.HTML)


__help__ = """
*ɪᴅ:*
• /id*:* ɢᴇᴛ ᴛʜᴇ ᴄᴜʀʀᴇɴᴛ ɢʀᴏᴜᴘ ɪᴅ. ɪғ ᴜsᴇᴅ ʙʏ ʀᴇᴘʟʏɪɴɢ ᴛᴏ ᴀ ᴍᴇssᴀɢᴇ, ɢᴇᴛs ᴛʜᴀᴛ ᴜsᴇʀ's ɪᴅ.
• /gifid*:* ʀᴇᴘʟʏ ᴛᴏ ᴀ ɢɪғ ᴛᴏ ᴍᴇ ᴛᴏ ᴛᴇʟʟ ʏᴏᴜ ɪᴛs ғɪʟᴇ ɪᴅ.

*ᴏᴠᴇʀᴀʟʟ ɪɴғᴏʀᴍᴀᴛɪᴏɴ ᴀʙᴏᴜᴛ ʏᴏᴜ:*
• /info*:* ɢᴇᴛ ɪɴғᴏʀᴍᴀᴛɪᴏɴ ᴀʙᴏᴜᴛ ᴀ ᴜsᴇʀ.
"""


STATS_HANDLER = CommandHandler(["stats", "gstats"], stats)
ID_HANDLER = DisableAbleCommandHandler("id", get_id)
GIFID_HANDLER = DisableAbleCommandHandler("gifid", gifid)
INFO_HANDLER = DisableAbleCommandHandler(("info", "book"), info)


exon.add_handler(STATS_HANDLER)
exon.add_handler(ID_HANDLER)
exon.add_handler(GIFID_HANDLER)
exon.add_handler(INFO_HANDLER)


__mod_name__ = "𝐈ɴғᴏ"
__command_list__ = ["info"]
__handlers__ = [
    GIFID_HANDLER,
    INFO_HANDLER,
    STATS_HANDLER,
]
