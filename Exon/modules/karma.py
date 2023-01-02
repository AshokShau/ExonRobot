import asyncio

from pyrogram import filters

from Exon import app as abishnoi, DRAGONS
from Exon.modules.sql.mongo.karma_db import *
from Exon.modules.helper_funcs import can_change_info


regex_upvote = r"^((?i)\+|\+\+|\+1|\++|\+69|thx|thanx|thanks|🖤|❣️|💝|💖|💕|❤|💘|cool|good|👍|baby|thankyou|love|pro)$"
regex_downvote = r"^(\-|\-\-|\-1|👎|💔|noob|weak|fuck off|nub|gey|kid|shit|mf)$"

karma_positive_group = 3
karma_negative_group = 4


@abishnoi.on_message(
    filters.text
    & filters.group
    & filters.incoming
    & filters.reply
    & filters.regex(regex_upvote)
    & ~filters.via_bot
    & ~filters.bot,
    group=karma_positive_group,
)
async def upvote(_, message):
    if not await is_karma_on(message.chat.id):
        return
    if not message.reply_to_message.from_user:
        return
    if not message.from_user:
        return
    if message.reply_to_message.from_user.id == DRAGONS:
        await message.reply_text(
            "ʜᴏᴡ sᴏ ᴘʀᴏ ?"
        )
        return
    if message.reply_to_message.from_user.id == message.from_user.id:
        return
    chat_id = message.chat.id
    user_id = message.reply_to_message.from_user.id
    user_mention = message.reply_to_message.from_user.mention
    current_karma = await get_karma(chat_id, await int_to_alpha(user_id))
    if current_karma:
        current_karma = current_karma["karma"]
        karma = current_karma + 1
    else:
        karma = 1
    new_karma = {"karma": karma}
    await update_karma(chat_id, await int_to_alpha(user_id), new_karma)
    await message.reply_text(
        f"ɪɴᴄʀᴇᴍᴇɴᴛᴇᴅ ᴋᴀʀᴍᴀ ᴏғ {user_mention} ʙʏ 1.\n**ᴛᴏᴛᴀʟ ᴩᴏɪɴᴛs :** {karma}"
    )


@abishnoi.on_message(
    filters.text
    & filters.group
    & filters.incoming
    & filters.reply
    & filters.regex(regex_downvote)
    & ~filters.via_bot
    & ~filters.bot,
    group=karma_negative_group,
)

async def downvote(_, message):
    if not await is_karma_on(message.chat.id):
        return
    if not message.reply_to_message.from_user:
        return
    if not message.from_user:
        return
    if message.reply_to_message.from_user.id == DRAGONS:
        await message.reply_text(
            "ɪ ᴋɴᴏᴡ ʜɪᴍ, sᴏ ɪ'ᴍ ɴᴏᴛ ɢᴏɴɴᴀ ᴅᴏ ᴛʜᴀᴛ ʙᴀʙʏ."
        )
        return
    if message.reply_to_message.from_user.id == message.from_user.id:
        return
    user_id = message.reply_to_message.from_user.id
    user_mention = message.reply_to_message.from_user.mention
    current_karma = await get_karma(message.chat.id, await int_to_alpha(user_id))
    if current_karma:
        current_karma = current_karma["karma"]
        karma = current_karma - 1
    else:
        karma = 0
    new_karma = {"karma": karma}
    await update_karma(message.chat.id, await int_to_alpha(user_id), new_karma)
    await message.reply_text(
        f"ᴅᴇᴄʀᴇᴍᴇɴᴛᴇᴅ ᴋᴀʀᴍᴀ ᴏғ {user_mention} ʙʏ 1.\n**ᴛᴏᴛᴀʟ ᴩᴏɪɴᴛs :** {karma}"
    )


@abishnoi.on_message(filters.command("karmastat") & filters.group)

async def karma(_, message):
    if not message.reply_to_message:
        m = await message.reply_text("🦋")
        karma = await get_karmas(message.chat.id)
        if not karma:
            await m.edit_text("ɴᴏ ᴋᴀʀᴍᴀ ɪɴ ᴅʙ ғᴏʀ ᴛʜɪs ᴄʜᴀᴛ.")
            return
        msg = f"**ᴋᴀʀᴍᴀ ʟɪsᴛ ᴏғ {message.chat.title} :**\n"
        limit = 0
        karma_dicc = {}
        for i in karma:
            user_id = await alpha_to_int(i)
            user_karma = karma[i]["karma"]
            karma_dicc[str(user_id)] = user_karma
            karma_arranged = dict(
                sorted(karma_dicc.items(), key=lambda item: item[1], reverse=True)
            )
        if not karma_dicc:
            await m.edit_text("ɴᴏ ᴋᴀʀᴍᴀ ɪɴ DB ғᴏʀ ᴛʜɪs ᴄʜᴀᴛ.")
            return
        for user_idd, karma_count in karma_arranged.items():
            if limit > 9:
                break
            try:
                user = await app.get_users(int(user_idd))
                await asyncio.sleep(0.8)
            except Exception:
                continue
            first_name = user.first_name
            if not first_name:
                continue
            msg += f"`{karma_count}`  {(first_name[0:12] + '...') if len(first_name) > 12 else first_name}\n"
            limit += 1
        await m.edit_text(msg)
    else:
        user_id = message.reply_to_message.from_user.id
        karma = await get_karma(message.chat.id, await int_to_alpha(user_id))
        karma = karma["karma"] if karma else 0
        await message.reply_text(f"**ᴛᴏᴛᴀʟ ᴩᴏɪɴᴛs :** {karma}")


@abishnoi.on_message(filters.command("karma") & ~filters.private)
@can_change_info
async def captcha_state(_, message):
    usage = "**ᴜsᴀɢᴇ:**\n/karma [ON|OFF]"
    if len(message.command) != 2:
        return await message.reply_text(usage)
    state = message.text.split(None, 1)[1].strip()
    state = state.lower()
    if state == "on":
        await karma_on(message.chat.id)
        await message.reply_text("ᴇɴᴀʙʟᴇᴅ ᴋᴀʀᴍᴀ sʏsᴛᴇᴍ.")
    elif state == "off":
        await karma_off(message.chat.id)
        await message.reply_text("ᴅɪsᴀʙʟᴇᴅ ᴋᴀʀᴍᴀ sʏsᴛᴇᴍ.")
    else:
        await message.reply_text(usage)
