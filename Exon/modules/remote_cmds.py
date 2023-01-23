from telegram import (
    ChatMemberAdministrator,
    ChatMemberRestricted,
    ChatPermissions,
    Update,
)
from telegram.error import BadRequest
from telegram.ext import CommandHandler, ContextTypes, filters

from Exon import DRAGONS, LOGGER, exon
from Exon.modules.helper_funcs.chat_status import (
    is_bot_admin,
    is_user_ban_protected,
    is_user_in_chat,
)
from Exon.modules.helper_funcs.extraction import extract_user_and_text

RBAN_ERRORS = {
    "ᴜsᴇʀ ɪs ᴀɴ ᴀᴅᴍɪɴɪsᴛʀᴀᴛᴏʀ ᴏғ ᴛʜᴇ ᴄʜᴀᴛ",
    "ᴄʜᴀᴛ ɴᴏᴛ ғᴏᴜɴᴅ",
    "ɴᴏᴛ ᴇɴᴏᴜɢʜ ʀɪɢʜᴛs ᴛᴏ ʀᴇsᴛʀɪᴄᴛ/ᴜɴʀᴇsᴛʀɪᴄᴛ ᴄʜᴀᴛ ᴍᴇᴍʙᴇʀ",
    "ᴜsᴇʀ_ɴᴏᴛ_ᴘᴀʀᴛɪᴄɪᴘᴀɴᴛ",
    "ᴘᴇᴇʀ_ɪᴅ_ɪɴᴠᴀʟɪᴅ",
    "ɢʀᴏᴜᴘ ᴄʜᴀᴛ ᴡᴀs ᴅᴇᴀᴄᴛɪᴠᴀᴛᴇᴅ",
    "ɴᴇᴇᴅ ᴛᴏ ʙᴇ ɪɴᴠɪᴛᴇʀ ᴏғ ᴀ ᴜsᴇʀ ᴛᴏ ᴋɪᴄᴋ ɪᴛ ғʀᴏᴍ ᴀ ʙᴀsɪᴄ ɢʀᴏᴜᴘ",
    "ᴄʜᴀᴛ_ᴀᴅᴍɪɴ_ʀᴇǫᴜɪʀᴇᴅ",
    "ᴏɴʟʏ ᴛʜᴇ ᴄʀᴇᴀᴛᴏʀ ᴏғ ᴀ ʙᴀsɪᴄ ɢʀᴏᴜᴘ ᴄᴀɴ ᴋɪᴄᴋ ɢʀᴏᴜᴘ ᴀᴅᴍɪɴɪsᴛʀᴀᴛᴏʀs",
    "ᴄʜᴀɴɴᴇʟ_ᴘʀɪᴠᴀᴛᴇ",
    "ɴᴏᴛ ɪɴ ᴛʜᴇ ᴄʜᴀᴛ",
}

RUNBAN_ERRORS = {
    "ᴜsᴇʀ ɪs ᴀɴ ᴀᴅᴍɪɴɪsᴛʀᴀᴛᴏʀ ᴏғ ᴛʜᴇ ᴄʜᴀᴛ",
    "ᴄʜᴀᴛ ɴᴏᴛ ғᴏᴜɴᴅ",
    "ɴᴏᴛ ᴇɴᴏᴜɢʜ ʀɪɢʜᴛs ᴛᴏ ʀᴇsᴛʀɪᴄᴛ/ʀᴇsᴛʀɪᴄ ᴄʜᴀᴛ ᴍᴇᴍʙᴇʀ",
    "ᴜsᴇʀ_ɴᴏᴛ_ᴘᴀʀᴛɪᴄɪᴘᴀɴᴛ",
    "ᴘᴇᴇʀ_ɪᴅ_ɪɴᴠᴀʟɪᴅ",
    "ɢʀᴏᴜᴘ ᴄʜᴀᴛ ᴡᴀs ᴅᴇᴀᴄᴛɪᴠᴀᴛᴇᴅ",
    "ɴᴇᴇᴅ ᴛᴏ ʙᴇ ɪɴᴠɪᴛᴇʀ ᴏғ ᴀ ᴜsᴇʀ ᴛᴏ ᴋɪᴄᴋ ɪᴛ ғʀᴏᴍ ᴀ ʙᴀsɪᴄ ɢʀᴏᴜᴘ",
    "ᴄʜᴀᴛ_ᴀᴅᴍɪɴ_ʀᴇǫᴜɪʀᴇᴅ",
    "ᴏɴʟʏ ᴛʜᴇ ᴄʀᴇᴀᴛᴏʀ ᴏғ ᴀ ʙᴀsɪᴄ ɢʀᴏᴜᴘ ᴄᴀɴ ᴋɪᴄᴋ ɢʀᴏᴜᴘ ᴀᴅᴍɪɴɪsᴛʀᴀᴛᴏʀs",
    "ᴄʜᴀɴɴᴇʟ_ᴘʀɪᴠᴀᴛᴇ",
    "ɴᴏᴛ ɪɴ ᴛʜᴇ ᴄʜᴀᴛ",
}

RKICK_ERRORS = {
    "ᴜsᴇʀ ɪs ᴀɴ ᴀᴅᴍɪɴɪsᴛʀᴀᴛᴏʀ ᴏғ ᴛʜᴇ ᴄʜᴀᴛ",
    "ᴄʜᴀᴛ ɴᴏᴛ ғᴏᴜɴᴅ",
    "ɴᴏᴛ ᴇɴᴏᴜɢʜ ʀɪɢʜᴛs ᴛᴏ ʀᴇsᴛʀɪᴄᴛ/ᴜɴʀᴇsᴛʀɪᴄᴛ ᴄʜᴀᴛ ᴍᴇᴍʙᴇʀ",
    "ᴜsᴇʀ_ɴᴏᴛ_ᴘᴀʀᴛɪᴄɪᴘᴀɴᴛ",
    "ᴘᴇᴇʀ_ɪᴅ_ɪɴᴠᴀʟɪᴅ",
    "ɢʀᴏᴜᴘ ᴄʜᴀᴛ ᴡᴀs ᴅᴇᴀᴄᴛɪᴠᴀᴛᴇᴅ",
    "ɴᴇᴇᴅ ᴛᴏ ʙᴇ ɪɴᴠɪᴛᴇʀ ᴏғ ᴀ ᴜsᴇʀ ᴛᴏ ᴋɪᴄᴋ ɪᴛ ғʀᴏᴍ ᴀ ʙᴀsɪᴄ ɢʀᴏᴜᴘ",
    "ᴄʜᴀᴛ_ᴀᴅᴍɪɴ_ʀᴇǫᴜɪʀᴇᴅ",
    "ᴏɴʟʏ ᴛʜᴇ ᴄʀᴇᴀᴛᴏʀ ᴏғ ᴀ ʙᴀsɪᴄ ɢʀᴏᴜᴘ ᴄᴀɴ ᴋɪᴄᴋ ɢʀᴏᴜᴘ ᴀᴅᴍɪɴɪsᴛʀᴀᴛᴏʀs",
    "ᴄʜᴀɴɴᴇʟ_ᴘʀɪᴠᴀᴛᴇ",
    "ɴᴏᴛ ɪɴ ᴛʜᴇ ᴄʜᴀᴛ",
}

RMUTE_ERRORS = {
    "ᴜsᴇʀ ɪs ᴀɴ ᴀᴅᴍɪɴɪsᴛʀᴀᴛᴏʀ ᴏғ ᴛʜᴇ ᴄʜᴀᴛ",
    "ᴄʜᴀᴛ ɴᴏᴛ ғᴏᴜɴᴅ",
    "ɴᴏᴛ ᴇɴᴏᴜɢʜ ʀɪɢʜᴛs ᴛᴏ ʀᴇsᴛʀɪᴄᴛ/ᴜɴʀᴇsᴛʀɪᴄᴛ ᴄʜᴀᴛ ᴍᴇᴍʙᴇʀ",
    "ᴜsᴇʀ_ɴᴏᴛ_ᴘᴀʀᴛɪᴄɪᴘᴀɴᴛ",
    "ᴘᴇᴇʀ_ɪᴅ_ɪɴᴠᴀʟɪᴅ",
    "ɢʀᴏᴜᴘ ᴄʜᴀᴛ ᴡᴀs ᴅᴇᴀᴄᴛɪᴠᴀᴛᴇᴅ",
    "ɴᴇᴇᴅ ᴛᴏ ʙᴇ ɪɴᴠɪᴛᴇʀ ᴏғ ᴀ ᴜsᴇʀ ᴛᴏ ᴋɪᴄᴋ ɪᴛ ғʀᴏᴍ ᴀ ʙᴀsɪᴄ ɢʀᴏᴜᴘ",
    "ᴄʜᴀᴛ_ᴀᴅᴍɪɴ_ʀᴇǫᴜɪʀᴇᴅ",
    "ᴏɴʟʏ ᴛʜᴇ ᴄʀᴇᴀᴛᴏʀ ᴏғ ᴀ ʙᴀsɪᴄ ɢʀᴏᴜᴘ ᴄᴀɴ ᴋɪᴄᴋ ɢʀᴏᴜᴘ ᴀᴅᴍɪɴɪsᴛʀᴀᴛᴏʀs",
    "ᴄʜᴀɴɴᴇʟ_ᴘʀɪᴠᴀᴛᴇ",
    "ɴᴏᴛ ɪɴ ᴛʜᴇ ᴄʜᴀᴛ",
}

RUNMUTE_ERRORS = {
    "ᴜsᴇʀ ɪs ᴀɴ ᴀᴅᴍɪɴɪsᴛʀᴀᴛᴏʀ ᴏғ ᴛʜᴇ ᴄʜᴀᴛ",
    "ᴄʜᴀᴛ ɴᴏᴛ ғᴏᴜɴᴅ",
    "ɴᴏᴛ ᴇɴᴏᴜɢʜ ʀɪɢʜᴛs ᴛᴏ ʀᴇsᴛʀɪᴄᴛ/ᴜɴʀᴇsᴛʀɪᴄᴛ ᴄʜᴀᴛ ᴍᴇᴍʙᴇʀ",
    "ᴜsᴇʀ_ɴᴏᴛ_ᴘᴀʀᴛɪᴄɪᴘᴀɴᴛ",
    "ᴘᴇᴇʀ_ɪᴅ_ɪɴᴠᴀʟɪᴅ",
    "ɢʀᴏᴜᴘ ᴄʜᴀᴛ ᴡᴀs ᴅᴇᴀᴄᴛɪᴠᴀᴛᴇᴅ",
    "ɴᴇᴇᴅ ᴛᴏ ʙᴇ ɪɴᴠɪᴛᴇʀ ᴏғ ᴀ ᴜsᴇʀ ᴛᴏ ᴋɪᴄᴋ ɪᴛ ғʀᴏᴍ ᴀ ʙᴀsɪᴄ ɢʀᴏᴜᴘ",
    "ᴄʜᴀᴛ_ᴀᴅᴍɪɴ_ʀᴇǫᴜɪʀᴇᴅ",
    "ᴏɴʟʏ ᴛʜᴇ ᴄʀᴇᴀᴛᴏʀ of ᴀ ʙᴀsɪᴄ ɢʀᴏᴜᴘ ᴄᴀɴ ᴋɪᴄᴋ ɢʀᴏᴜᴘ ᴀᴅᴍɪɴɪsᴛʀᴀᴛᴏʀs",
    "ᴄʜᴀɴɴᴇʟ_ᴘʀɪᴠᴀᴛᴇ",
    "ɴᴏᴛ ɪɴ ᴛʜᴇ ᴄʜᴀᴛ",
}


async def rban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bot, args = context.bot, context.args
    message = update.effective_message

    if not args:
        await message.reply_text("ʏᴏᴜ ᴅᴏɴ'ᴛ sᴇᴇᴍ ᴛᴏ ʙᴇ ʀᴇғᴇʀʀɪɴɢ ᴛᴏ ᴀ ᴄʜᴀᴛ/ᴜsᴇʀ.")
        return

    user_id, chat_id = await extract_user_and_text(message, context, args)

    if not user_id:
        await message.reply_text(
            "ʏᴏᴜ ᴅᴏɴ'ᴛ sᴇᴇᴍ ᴛᴏ ʙᴇ ʀᴇғᴇʀʀɪɴɢ ᴛᴏ ᴀ ᴜsᴇʀ ᴏʀ ᴛʜᴇ ID sᴘᴇᴄɪғɪᴇᴅ ɪs ɪɴᴄᴏʀʀᴇᴄᴛ..",
        )
        return
    elif not chat_id:
        await message.reply_text("ʏᴏᴜ ᴅᴏɴ'ᴛ sᴇᴇᴍ ᴛᴏ ʙᴇ ʀᴇғᴇʀʀɪɴɢ ᴛᴏ ᴀ ᴄʜᴀᴛ.")
        return

    try:
        chat = await bot.get_chat(chat_id.split()[0])
    except BadRequest as excp:
        if excp.message == "Chat not found":
            await message.reply_text(
                "ᴄʜᴀᴛ ɴᴏᴛ ғᴏᴜɴᴅ! ᴍᴀᴋᴇ sᴜʀᴇ ʏᴏᴜ ᴇɴᴛᴇʀᴇᴅ ᴀ ᴠᴀʟɪᴅ ᴄʜᴀᴛ ɪᴅ ᴀɴᴅ I'ᴍ ᴘᴀʀᴛ ᴏғ ᴛʜᴀᴛ ᴄʜᴀᴛ.",
            )
            return
        else:
            raise

    if chat.type == "private":
        await message.reply_text("ɪ'ᴍ sᴏʀʀʏ, ʙᴜᴛ ᴛʜᴀᴛ's ᴀ ᴘʀɪᴠᴀᴛᴇ ᴄʜᴀᴛ!")
        return

    bot_member = await chat.get_member(bot.id)

    if isinstance(bot_member, ChatMemberAdministrator):
        bot_can_restrict_members = bot_member.can_restrict_members

        if not is_bot_admin(chat, bot.id) or not bot_can_restrict_members:
            await message.reply_text(
                "I ᴄᴀɴ'ᴛ ʀᴇsᴛʀɪᴄᴛ ᴘᴇᴏᴘʟᴇ ᴛʜᴇʀᴇ! ᴍᴀᴋᴇ sᴜʀᴇ ɪ'ᴍ ᴀᴅᴍɪɴ ᴀɴᴅ ᴄᴀɴ ʙᴀɴ ᴜsᴇʀs.",
            )
            return

    try:
        member = await chat.get_member(user_id)
    except BadRequest as excp:
        if excp.message == "User not found":
            await message.reply_text("I ᴄᴀɴ'ᴛ sᴇᴇᴍ ᴛᴏ ғɪɴᴅ ᴛʜɪs ᴜsᴇʀ")
            return
        else:
            raise

    if await is_user_ban_protected(chat, user_id, member):
        await message.reply_text("I ʀᴇᴀʟʟʏ ᴡɪsʜ ɪ ᴄᴏᴜʟᴅ ʙᴀɴ ᴀᴅᴍɪɴs...")
        return

    if user_id == bot.id:
        await message.reply_text("I'ᴍ ɴᴏᴛ ɢᴏɴɴᴀ BAN ᴍʏsᴇʟғ, ᴀʀᴇ ʏᴏᴜ ᴄʀᴀᴢʏ?")
        return

    try:
        await chat.ban_member(user_id)
        await message.reply_text("ʙᴀɴɴᴇᴅ ғʀᴏᴍ ᴄʜᴀᴛ!")
    except BadRequest as excp:
        if excp.message == "ʀᴇᴘʟʏ ᴍᴇssᴀɢᴇ ɴᴏᴛ ғᴏᴜɴᴅ":
            # Do not reply
            await message.reply_text("ʙᴀɴɴᴇᴅ!", quote=False)
        elif excp.message in RBAN_ERRORS:
            await message.reply_text(excp.message)
        else:
            LOGGER.warning(update)
            LOGGER.exception(
                "ᴇʀʀᴏʀ ʙᴀɴɴɪɴɢ ᴜsᴇʀ %s ɪɴ ᴄʜᴀᴛ %s (%s) ᴅᴜᴇ ᴛᴏ %s",
                user_id,
                chat.title,
                chat.id,
                excp.message,
            )
            await message.reply_text("ᴡᴇʟʟ ᴅᴀᴍɴ, I ᴄᴀɴ'ᴛ ʙᴀɴ ᴛʜᴀᴛ ᴜsᴇʀ.")


async def runban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bot, args = context.bot, context.args
    message = update.effective_message

    if not args:
        await message.reply_text("ʏᴏᴜ ᴅᴏɴ'ᴛ sᴇᴇᴍ ᴛᴏ ʙᴇ ʀᴇғᴇʀʀɪɴɢ ᴛᴏ ᴀ ᴄʜᴀᴛ/ᴜsᴇʀ.")
        return

    user_id, chat_id = await extract_user_and_text(message, context, args)

    if not user_id:
        await message.reply_text(
            "ʏᴏᴜ ᴅᴏɴ'ᴛ sᴇᴇᴍ ᴛᴏ ʙᴇ ʀᴇғᴇʀʀɪɴɢ ᴛᴏ ᴀ ᴜsᴇʀ ᴏʀ ᴛʜᴇ ID sᴘᴇᴄɪғɪᴇᴅ ɪs ɪɴᴄᴏʀʀᴇᴄᴛ..",
        )
        return
    elif not chat_id:
        await message.reply_text("ʏᴏᴜ ᴅᴏɴ'ᴛ sᴇᴇᴍ ᴛᴏ ʙᴇ ʀᴇғᴇʀʀɪɴɢ ᴛᴏ ᴀ ᴄʜᴀᴛ.")
        return

    try:
        chat = await bot.get_chat(chat_id.split()[0])
    except BadRequest as excp:
        if excp.message == "Chat not found":
            await message.reply_text(
                "ᴄʜᴀᴛ ɴᴏᴛ ғᴏᴜɴᴅ! ᴍᴀᴋᴇ sᴜʀᴇ ʏᴏᴜ ᴇɴᴛᴇʀᴇᴅ ᴀ ᴠᴀʟɪᴅ ᴄʜᴀᴛ ID ᴀɴᴅ I'ᴍ ᴘᴀʀᴛ ᴏғ ᴛʜᴀᴛ ᴄʜᴀᴛ.",
            )
            return
        else:
            raise

    if chat.type == "private":
        await message.reply_text("I'ᴍ sᴏʀʀʏ, ʙᴜᴛ ᴛʜᴀᴛ's ᴀ ᴘʀɪᴠᴀᴛᴇ ᴄʜᴀᴛ!")
        return

    bot_member = await chat.get_member(bot.id)

    if isinstance(bot_member, ChatMemberAdministrator):
        bot_can_restrict_members = bot_member.can_restrict_members

        if not is_bot_admin(chat, bot.id) or not bot_can_restrict_members:
            await message.reply_text(
                "I ᴄᴀɴ'ᴛ ᴜɴʀᴇsᴛʀɪᴄᴛ ᴘᴇᴏᴘʟᴇ ᴛʜᴇʀᴇ! ᴍᴀᴋᴇ sᴜʀᴇ I'ᴍ ᴀᴅᴍɪɴ ᴀɴᴅ ᴄᴀɴ ᴜɴʙᴀɴ ᴜsᴇʀs.",
            )
            return

    try:
        await chat.get_member(user_id)
    except BadRequest as excp:
        if excp.message == "User not found":
            await message.reply_text("I ᴄᴀɴ'ᴛ sᴇᴇᴍ ᴛᴏ ғɪɴᴅ ᴛʜɪs ᴜsᴇʀ ᴛʜᴇʀᴇ")
            return
        else:
            raise

    if await is_user_in_chat(chat, user_id):
        await message.reply_text(
            "ᴡʜʏ ᴀʀᴇ ʏᴏᴜ ᴛʀʏɪɴɢ ᴛᴏ ʀᴇᴍᴏᴛᴇʟʏ ᴜɴʙᴀɴ sᴏᴍᴇᴏɴᴇ ᴛʜᴀᴛ's ᴀʟʀᴇᴀᴅʏ ɪɴ ᴛʜᴀᴛ ᴄʜᴀᴛ?",
        )
        return

    if user_id == bot.id:
        await message.reply_text("I'ᴍ ɴᴏᴛ ɢᴏɴɴᴀ UNBAN ᴍʏsᴇʟғ, ɪ'ᴍ ᴀɴ ᴀᴅᴍɪɴ ᴛʜᴇʀᴇ!")
        return

    try:
        chat.unban_member(user_id)
        await message.reply_text("ʏᴇᴘ, ᴛʜɪs ᴜsᴇʀ ᴄᴀɴ ᴊᴏɪɴ ᴛʜᴀᴛ ᴄʜᴀᴛ!")
    except BadRequest as excp:
        if excp.message == "ʀᴇᴘʟʏ ᴍᴇssᴀɢᴇ ɴᴏᴛ ғᴏᴜɴᴅ":
            # Do not reply
            await message.reply_text("ᴜɴʙᴀɴɴᴇᴅ!", quote=False)
        elif excp.message in RUNBAN_ERRORS:
            await message.reply_text(excp.message)
        else:
            LOGGER.warning(update)
            LOGGER.exception(
                "ERROR ᴜɴʙᴀɴɴɪɴɢ ᴜsᴇʀ %s ɪɴ ᴄʜᴀᴛ %s (%s) ᴅᴜᴇ ᴛᴏ %s",
                user_id,
                chat.title,
                chat.id,
                excp.message,
            )
            await message.reply_text("ᴡᴇʟʟ ᴅᴀᴍɴ, I ᴄᴀɴ'ᴛ ᴜɴʙᴀɴ ᴛʜᴀᴛ ᴜsᴇʀ.")


async def rkick(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bot, args = context.bot, context.args
    message = update.effective_message

    if not args:
        await message.reply_text("ʏᴏᴜ ᴅᴏɴ'ᴛ sᴇᴇᴍ ᴛᴏ ʙᴇ ʀᴇғᴇʀʀɪɴɢ ᴛᴏ ᴀ ᴄʜᴀᴛ/ᴜsᴇʀ.")
        return

    user_id, chat_id = await extract_user_and_text(message, context, args)

    if not user_id:
        await message.reply_text(
            "ʏᴏᴜ ᴅᴏɴ'ᴛ sᴇᴇᴍ ᴛᴏ ʙᴇ ʀᴇғᴇʀʀɪɴɢ ᴛᴏ ᴀ ᴜsᴇʀ ᴏʀ ᴛʜᴇ ID sᴘᴇᴄɪғɪᴇᴅ ɪs ɪɴᴄᴏʀʀᴇᴄᴛ..",
        )
        return
    elif not chat_id:
        await message.reply_text("ʏᴏᴜ ᴅᴏɴ'ᴛ sᴇᴇᴍ ᴛᴏ ʙᴇ ʀᴇғᴇʀʀɪɴɢ ᴛᴏ ᴀ ᴄʜᴀᴛ.")
        return

    try:
        chat = await bot.get_chat(chat_id.split()[0])
    except BadRequest as excp:
        if excp.message == "ᴄʜᴀᴛ ɴᴏᴛ ғᴏᴜɴᴅ":
            await message.reply_text(
                "ᴄʜᴀᴛ ɴᴏᴛ ғᴏᴜɴᴅ! ᴍᴀᴋᴇ sᴜʀᴇ ʏᴏᴜ ᴇɴᴛᴇʀᴇᴅ ᴀ ᴠᴀʟɪᴅ ᴄʜᴀᴛ ɪᴅ ᴀɴᴅ I'ᴍ ᴘᴀʀᴛ ᴏғ ᴛʜᴀᴛ ᴄʜᴀᴛ.",
            )
            return
        else:
            raise

    if chat.type == "private":
        await message.reply_text("ɪ'ᴍ sᴏʀʀʏ, ʙᴜᴛ ᴛʜᴀᴛ's ᴀ ᴘʀɪᴠᴀᴛᴇ ᴄʜᴀᴛ!")
        return

    bot_member = await chat.get_member(bot.id)

    if isinstance(bot_member, ChatMemberAdministrator):
        bot_can_restrict_members = bot_member.can_restrict_members

        if not is_bot_admin(chat, bot.id) or not bot_can_restrict_members:
            await message.reply_text(
                "I ᴄᴀɴ'ᴛ ʀᴇsᴛʀɪᴄᴛ ᴘᴇᴏᴘʟᴇ ᴛʜᴇʀᴇ! ᴍᴀᴋᴇ sᴜʀᴇ I'ᴍ ᴀᴅᴍɪɴ ᴀɴᴅ ᴄᴀɴ ᴋɪᴄᴋ ᴜsᴇʀs.",
            )
            return

    try:
        member = await chat.get_member(user_id)
    except BadRequest as excp:
        if excp.message == "User not found":
            await message.reply_text("I ᴄᴀɴ'ᴛ sᴇᴇᴍ ᴛᴏ ғɪɴᴅ ᴛʜɪs ᴜsᴇʀ")
            return
        else:
            raise

    if await is_user_ban_protected(chat, user_id, member):
        await message.reply_text("I ʀᴇᴀʟʟʏ ᴡɪsʜ I ᴄᴏᴜʟᴅ ᴋɪᴄᴋ ᴀᴅᴍɪɴs...")
        return

    if user_id == bot.id:
        await message.reply_text("I'm ɴᴏᴛ ɢᴏɴɴᴀ ᴋɪᴄᴋ ᴍʏsᴇʟғ, ᴀʀᴇ ʏᴏᴜ ᴄʀᴀᴢʏ?")
        return

    try:
        chat.unban_member(user_id)
        await message.reply_text("ᴋɪᴄᴋᴇᴅ ғʀᴏᴍ ᴄʜᴀᴛ!")
    except BadRequest as excp:
        if excp.message == "ʀᴇᴘʟʏ ᴍᴇssᴀɢᴇ ɴᴏᴛ ғᴏᴜɴᴅ":
            # Do not reply
            await message.reply_text("ᴋɪᴄᴋᴇᴅ!", quote=False)
        elif excp.message in RKICK_ERRORS:
            await message.reply_text(excp.message)
        else:
            LOGGER.warning(update)
            LOGGER.exception(
                "ERROR ᴋɪᴄᴋɪɴɢ ᴜsᴇʀ %s ɪɴ ᴄʜᴀᴛ %s (%s) ᴅᴜᴇ ᴛᴏ %s",
                user_id,
                chat.title,
                chat.id,
                excp.message,
            )
            await message.reply_text("ᴡᴇʟʟ ᴅᴀᴍɴ, I ᴄᴀɴ'ᴛ ᴋɪᴄᴋ ᴛʜᴀᴛ ᴜsᴇʀ.")


async def rmute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bot, args = context.bot, context.args
    message = update.effective_message

    if not args:
        await message.reply_text("ʏᴏᴜ ᴅᴏɴ'ᴛ sᴇᴇᴍ ᴛᴏ ʙᴇ ʀᴇғᴇʀʀɪɴɢ ᴛᴏ ᴀ ᴄʜᴀᴛ/ᴜsᴇʀ.")
        return

    user_id, chat_id = await extract_user_and_text(message, context, args)

    if not user_id:
        await message.reply_text(
            "ʏᴏᴜ ᴅᴏɴ'ᴛ sᴇᴇᴍ ᴛᴏ ʙᴇ ʀᴇғᴇʀʀɪɴɢ ᴛᴏ ᴀ ᴜsᴇʀ ᴏʀ ᴛʜᴇ ID sᴘᴇᴄɪғɪᴇᴅ ɪs ɪɴᴄᴏʀʀᴇᴄᴛ..",
        )
        return
    elif not chat_id:
        await message.reply_text("ʏᴏᴜ ᴅᴏɴ'ᴛ sᴇᴇᴍ ᴛᴏ ʙᴇ ʀᴇғᴇʀʀɪɴɢ ᴛᴏ ᴀ ᴄʜᴀᴛ.")
        return

    try:
        chat = await bot.get_chat(chat_id.split()[0])
    except BadRequest as excp:
        if excp.message == "Chat not found":
            await message.reply_text(
                "ᴄʜᴀᴛ ɴᴏᴛ ғᴏᴜɴᴅ! ᴍᴀᴋᴇ sᴜʀᴇ ʏᴏᴜ ᴇɴᴛᴇʀᴇᴅ ᴀ ᴠᴀʟɪᴅ ᴄʜᴀᴛ ɪᴅ ᴀɴᴅ I'ᴍ ᴘᴀʀᴛ ᴏғ ᴛʜᴀᴛ ᴄʜᴀᴛ.",
            )
            return
        else:
            raise

    if chat.type == "private":
        await message.reply_text("I'ᴍ sᴏʀʀʏ, ʙᴜᴛ ᴛʜᴀᴛ's ᴀ ᴘʀɪᴠᴀᴛᴇ ᴄʜᴀᴛ!")
        return

    bot_member = await chat.get_member(bot.id)

    if isinstance(bot_member, ChatMemberAdministrator):
        bot_can_restrict_members = bot_member.can_restrict_members

        if not is_bot_admin(chat, bot.id) or not bot_can_restrict_members:
            await message.reply_text(
                "I ᴄᴀɴ'ᴛ ʀᴇsᴛʀɪᴄᴛ ᴘᴇᴏᴘʟᴇ ᴛʜᴇʀᴇ! ᴍᴀᴋᴇ sᴜʀᴇ I'ᴍ ᴀᴅᴍɪɴ ᴀɴᴅ ᴄᴀɴ ᴍᴜᴛᴇ ᴜsᴇʀs.",
            )
            return

    try:
        member = await chat.get_member(user_id)
    except BadRequest as excp:
        if excp.message == "User not found":
            await message.reply_text("I ᴄᴀɴ'ᴛ sᴇᴇᴍ ᴛᴏ ғɪɴᴅ ᴛʜɪs ᴜsᴇʀ")
            ʀᴇᴛᴜʀɴ
        else:
            raise

    if await is_user_ban_protected(chat, user_id, member):
        await message.reply_text("I ʀᴇᴀʟʟʏ ᴡɪsʜ I ᴄᴏᴜʟᴅ ᴍᴜᴛᴇ ᴀᴅᴍɪɴs...")
        return

    if user_id == bot.id:
        await message.reply_text("I'ᴍ ɴᴏᴛ ɢᴏɴɴᴀ MUTE ᴍʏsᴇʟғ, ᴀʀᴇ ʏᴏᴜ crazy?")
        return

    try:
        await bot.restrict_chat_member(
            chat.id,
            user_id,
            permissions=ChatPermissions(can_send_messages=False),
        )
        await message.reply_text("ᴍᴜᴛᴇᴅ ғʀᴏᴍ ᴛʜᴇ ᴄʜᴀᴛ!")
    except BadRequest as excp:
        if excp.message == "ʀᴇᴘʟʏ ᴍᴇssᴀɢᴇ ɴᴏᴛ ғᴏᴜɴᴅ":
            # Do not reply
            await message.reply_text("ᴍᴜᴛᴇᴅ!", quote=False)
        elif excp.message in RMUTE_ERRORS:
            await message.reply_text(excp.message)
        else:
            LOGGER.warning(update)
            LOGGER.exception(
                "ERROR ᴍᴜᴛᴇ ᴜsᴇʀ %s ɪɴ ᴄʜᴀᴛ %s (%s) ᴅᴜᴇ ᴛᴏ %s",
                user_id,
                chat.title,
                chat.id,
                excp.message,
            )
            await message.reply_text("ᴡᴇʟʟ ᴅᴀᴍɴ, I ᴄᴀɴ'ᴛ ᴍᴜᴛᴇ ᴛʜᴀᴛ ᴜsᴇʀ.")


async def runmute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bot, args = context.bot, context.args
    message = update.effective_message

    if not args:
        await message.reply_text("ʏᴏᴜ ᴅᴏɴ'ᴛ sᴇᴇᴍ ᴛᴏ ʙᴇ ʀᴇғᴇʀʀɪɴɢ ᴛᴏ ᴀ ᴄʜᴀᴛ/ᴜsᴇʀ.")
        return

    user_id, chat_id = await extract_user_and_text(message, context, args)

    if not user_id:
        await message.reply_text(
            "ʏᴏᴜ ᴅᴏɴ'ᴛ sᴇᴇᴍ ᴛᴏ ʙᴇ ʀᴇғᴇʀʀɪɴɢ ᴛᴏ ᴀ user ᴏʀ ᴛʜᴇ ID sᴘᴇᴄɪғɪᴇᴅ ɪs ɪɴᴄᴏʀʀᴇᴄᴛ..",
        )
        return
    elif not chat_id:
        await message.reply_text("ʏᴏᴜ ᴅᴏɴ'ᴛ sᴇᴇᴍ ᴛᴏ ʙᴇ ʀᴇғᴇʀʀɪɴɢ ᴛᴏ ᴀ ᴄʜᴀᴛ.")
        return

    try:
        chat = await bot.get_chat(chat_id.split()[0])
    except BadRequest as excp:
        if excp.message == "Chat not found":
            await message.reply_text(
                "ᴄʜᴀᴛ ɴᴏᴛ ғᴏᴜɴᴅ! Make sure you entered a valid chat ID and I'm part of that chat.",
            )
            return
        else:
            raise

    if chat.type == "private":
        await message.reply_text("I'ᴍ sᴏʀʀʏ, ʙᴜᴛ ᴛʜᴀᴛ's ᴀ ᴘʀɪᴠᴀᴛᴇ ᴄʜᴀᴛ!")
        return

    bot_member = await chat.get_member(bot.id)

    if isinstance(bot_member, ChatMemberAdministrator):
        bot_can_restrict_members = bot_member.can_restrict_members

        if not is_bot_admin(chat, bot.id) or not bot_can_restrict_members:
            await message.reply_text(
                "I ᴄᴀɴ'ᴛ ᴜɴʀᴇsᴛʀɪᴄᴛ ᴘᴇᴏᴘʟᴇ ᴛʜᴇʀᴇ! ᴍᴀᴋᴇ sᴜʀᴇ I'ᴍ ᴀᴅᴍɪɴ ᴀɴᴅ ᴄᴀɴ ᴜɴʙᴀɴ ᴜsᴇʀs.",
            )
            return

    try:
        member = await chat.get_member(user_id)
    except BadRequest as excp:
        if excp.message == "ᴜsᴇʀ ɴᴏᴛ ғᴏᴜɴᴅ":
            await message.reply_text("I ᴄᴀɴ'ᴛ sᴇᴇᴍ ᴛᴏ ғɪɴᴅ ᴛʜɪs ᴜsᴇʀ ᴛʜᴇʀᴇ")
            return
        else:
            raise

    if await is_user_in_chat(chat, user_id):
        if (
            (
                member.can_send_messages
                and member.can_send_media_messages
                and member.can_send_other_messages
                and member.can_add_web_page_previews
            )
            if isinstance(member, ChatMemberRestricted)
            else None
        ):
            await message.reply_text(
                "ᴛʜɪs ᴜsᴇʀ ᴀʟʀᴇᴀᴅʏ ʜᴀs ᴛʜᴇ ʀɪɢʜᴛ ᴛᴏ sᴘᴇᴀᴋ ɪɴ ᴛʜᴀᴛ ᴄʜᴀᴛ."
            )
            return

    if user_id == bot.id:
        await message.reply_text("I'ᴍ ɴᴏᴛ ɢᴏɴɴᴀ UNMUTE ᴍʏsᴇʟғ, I'ᴍ an ᴀᴅᴍɪɴ ᴛʜᴇʀᴇ!")
        return

    try:
        await bot.restrict_chat_member(
            chat.id,
            int(user_id),
            permissions=ChatPermissions(
                can_send_messages=True,
                can_send_media_messages=True,
                can_send_other_messages=True,
                can_add_web_page_previews=True,
            ),
        )
        await message.reply_text("ʏᴇᴘ, ᴛʜɪs ᴜsᴇʀ can talk in that chat!")
    except BadRequest as excp:
        if excp.message == "ʀᴇᴘʟʏ ᴍᴇssᴀɢᴇ ɴᴏᴛ ғᴏᴜɴᴅ":
            # Do not ʀᴇᴘʟʏ
            await message.reply_text("ᴜɴᴍᴜᴛᴇᴅ!", quote=False)
        elif excp.message in RUNMUTE_ERRORS:
            await message.reply_text(excp.message)
        else:
            LOGGER.warning(update)
            LOGGER.exception(
                "ERROR ᴜɴᴍɴᴜᴛɪɴɢ ᴜsᴇʀ %s ɪɴ ᴄʜᴀᴛ %s (%s) ᴅᴜᴇ ᴛᴏ %s",
                user_id,
                chat.title,
                chat.id,
                excp.message,
            )
            await message.reply_text("ᴡᴇʟʟ ᴅᴀᴍɴ, I ᴄᴀɴ'ᴛ ᴜɴᴍᴜᴛᴇ ᴛʜᴀᴛ ᴜsᴇʀ.")


RBAN_HANDLER = CommandHandler("rban", rban, filters=filters.User(DRAGONS))
RUNBAN_HANDLER = CommandHandler(
    "runban", runban, filters=filters.User(DRAGONS)
)
RKICK_HANDLER = CommandHandler(
    "rkick", rkick, filters=filters.User(DRAGONS)
)
RMUTE_HANDLER = CommandHandler(
    "rmute", rmute, filters=filters.User(DRAGONS)
)
RUNMUTE_HANDLER = CommandHandler(
    "runmute", runmute, filters=filters.User(DRAGONS)
)

exon.add_handler(RBAN_HANDLER)
exon.add_handler(RUNBAN_HANDLER)
exon.add_handler(RKICK_HANDLER)
exon.add_handler(RMUTE_HANDLER)
exon.add_handler(RUNMUTE_HANDLER)
