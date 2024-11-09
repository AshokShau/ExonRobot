from ptbmod import Admins
from ptbmod.decorator.cache import load_admin_cache
from telegram import Update
from telegram.constants import ChatMemberStatus
from telegram.ext import ContextTypes

from .. import Cmd


@Cmd(command="adminList")
async def adminList(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat = update.effective_chat
    _, admins = await load_admin_cache(context.bot, chat.id)

    admin_list_text = "<b>Admins in this chat:</b>\n\n"
    owner_text = ""
    admin_texts = []

    for admin in admins.user_info:
        user = admin.user
        name = f"{user.full_name} (@{user.username})" if user.username else user.full_name
        role = "Owner" if admin.status == ChatMemberStatus.OWNER else (admin.custom_title or "Admin")

        if role == "Owner":
            owner_text = f"<b>Owner:</b> {name}\n\n"
        else:
            admin_texts.append(f"• {name} - <i>{role}</i>")

    admin_list_text += owner_text + "<b>Admins:</b>\n" + "\n".join(admin_texts)

    await update.effective_message.reply_text(admin_list_text)


@Cmd(command="promote")
@Admins(permissions="can_promote_members")
async def promote(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    pass
