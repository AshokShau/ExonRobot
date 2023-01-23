from telethon import *
from telethon.tl import *

# @Abishnoi1M
from Exon import BOT_ID, mdb, register
from Exon import telethn as Abishnoi

approved_users = mdb.approve

poll_id = mdb.pollid


async def is_register_admin(chat, user):
    if isinstance(chat, (types.InputPeerChannel, types.InputChannel)):
        return isinstance(
            (
                await Abishnoi(functions.channels.GetParticipantRequest(chat, user))
            ).participant,
            (types.ChannelParticipantAdmin, types.ChannelParticipantCreator),
        )
    if isinstance(chat, types.InputPeerChat):
        ui = await Abishnoi.get_peer_id(user)
        ps = (
            await Abishnoi(functions.messages.GetFullChatRequest(chat.chat_id))
        ).full_chat.participants.participants
        return isinstance(
            next((p for p in ps if p.user_id == ui), None),
            (types.ChatParticipantAdmin, types.ChatParticipantCreator),
        )
    return None


@register(pattern="^/poll (.*)")
async def _(event):
    approved_userss = approved_users.find({})
    for ch in approved_userss:
        iid = ch["id"]
        userss = ch["user"]
    if event.is_group:
        if await is_register_admin(event.input_chat, event.message.sender_id):
            pass
        elif event.chat_id == iid and event.sender_id == userss:
            pass
        else:
            return
    try:
        quew = event.pattern_match.group(1)
    except Exception:
        await event.reply("ᴡʜᴇʀᴇ is ᴛʜᴇ ǫᴜᴇsᴛɪᴏɴ ?")
        return
    if "|" in quew:
        secrets, quess, options = quew.split("|")
    secret = secrets.strip()

    if not secret:
        await event.reply("ɪ ɴᴇᴇᴅ ᴀ ᴘᴏʟʟ ɪᴅ ᴏғ 5 ᴅɪɢɪᴛs ᴛᴏ ᴍᴀᴋᴇ ᴀ ᴘᴏʟʟ")
        return

    try:
        secret = str(secret)
    except ValueError:
        await event.reply("ᴘᴏʟʟ ɪᴅ sʜᴏᴜʟᴅ ᴄᴏɴᴛᴀɪɴ ᴏɴʟʏ ɴᴜᴍʙᴇʀs")
        return

    # print(secret)

    if len(secret) != 5:
        await event.reply("ᴘᴏʟʟ ɪᴅ sʜᴏᴜʟᴅ ʙᴇ ᴀɴ ɪɴᴛᴇɢᴇʀ ᴏғ 5 ᴅɪɢɪᴛs")
        return

    allpoll = poll_id.find({})
    # print(secret)
    for c in allpoll:
        if event.sender_id == c["user"]:
            await event.reply(
                "ᴘʟᴇᴀsᴇ sᴛᴏᴘ ᴛʜᴇ ᴘʀᴇᴠɪᴏᴜs ᴘᴏʟʟ ʙᴇғᴏʀᴇ ᴄʀᴇᴀᴛɪɴɢ ᴀ ɴᴇᴡ ᴏɴᴇ !"
            )
            return
    poll_id.insert_one({"user": event.sender_id, "pollid": secret})

    ques = quess.strip()
    option = options.strip()
    quiz = option.split(" ")[1 - 1]
    if "True" in quiz:
        quizy = True
        if "@" in quiz:
            one, two = quiz.split("@")
            rightone = two.strip()
        else:
            await event.reply(
                "ʏᴏᴜ ɴᴇᴇᴅ ᴛᴏ sᴇʟᴇᴄᴛ ᴛʜᴇ ʀɪɢʜᴛ ᴀɴsᴡᴇʀ ᴡɪᴛʜ ǫᴜᴇsᴛɪᴏɴ ɴᴜᴍʙᴇʀ ʟɪᴋᴇ True@1, True@3 ᴇᴛᴄ.."
            )
            return

        quizoptionss = []
        try:
            ab = option.split(" ")[4 - 1]
            cd = option.split(" ")[5 - 1]
            quizoptionss.append(types.PollAnswer(ab, b"1"))
            quizoptionss.append(types.PollAnswer(cd, b"2"))
        except Exception:
            await event.reply("ᴀᴛ ʟᴇᴀsᴛ ɴᴇᴇᴅ ᴛᴡᴏ ᴏᴘᴛɪᴏɴs ᴛᴏ ᴄʀᴇᴀᴛᴇ ᴀ ᴘᴏʟʟ")
            return
        try:
            ef = option.split(" ")[6 - 1]
            quizoptionss.append(types.PollAnswer(ef, b"3"))
        except Exception:
            ef = None
        try:
            gh = option.split(" ")[7 - 1]
            quizoptionss.append(types.PollAnswer(gh, b"4"))
        except Exception:
            gh = None
        try:
            ij = option.split(" ")[8 - 1]
            quizoptionss.append(types.PollAnswer(ij, b"5"))
        except Exception:
            ij = None
        try:
            kl = option.split(" ")[9 - 1]
            quizoptionss.append(types.PollAnswer(kl, b"6"))
        except Exception:
            kl = None
        try:
            mn = option.split(" ")[10 - 1]
            quizoptionss.append(types.PollAnswer(mn, b"7"))
        except Exception:
            mn = None
        try:
            op = option.split(" ")[11 - 1]
            quizoptionss.append(types.PollAnswer(op, b"8"))
        except Exception:
            op = None
        try:
            qr = option.split(" ")[12 - 1]
            quizoptionss.append(types.PollAnswer(qr, b"9"))
        except Exception:
            qr = None
        try:
            st = option.split(" ")[13 - 1]
            quizoptionss.append(types.PollAnswer(st, b"10"))
        except Exception:
            st = None

    elif "False" in quiz:
        quizy = False
    else:
        await event.reply("ᴡʀᴏɴɢ ᴀʀɢᴜᴍᴇɴᴛs ᴘʀᴏᴠɪᴅᴇᴅ !")
        return

    pvote = option.split(" ")[2 - 1]
    if "True" in pvote:
        pvoty = True
    elif "False" in pvote:
        pvoty = False
    else:
        await event.reply("ᴡʀᴏɴɢ ᴀʀɢᴜᴍᴇɴᴛs ᴘʀᴏᴠɪᴅᴇᴅ !")
        return
    mchoice = option.split(" ")[3 - 1]
    if "True" in mchoice:
        mchoicee = True
    elif "False" in mchoice:
        mchoicee = False
    else:
        await event.reply("ᴡʀᴏɴɢ ᴀʀɢᴜᴍᴇɴᴛs ᴘʀᴏᴠɪᴅᴇᴅ !")
        return
    optionss = []
    try:
        ab = option.split(" ")[4 - 1]
        cd = option.split(" ")[5 - 1]
        optionss.append(types.PollAnswer(ab, b"1"))
        optionss.append(types.PollAnswer(cd, b"2"))
    except Exception:
        await event.reply("ᴀᴛ ʟᴇᴀsᴛ ɴᴇᴇᴅ ᴛᴡᴏ ᴏᴘᴛɪᴏɴs ᴛᴏ ᴄʀᴇᴀᴛᴇ ᴀ ᴘᴏʟʟ")
        return
    try:
        ef = option.split(" ")[6 - 1]
        optionss.append(types.PollAnswer(ef, b"3"))
    except Exception:
        ef = None
    try:
        gh = option.split(" ")[7 - 1]
        optionss.append(types.PollAnswer(gh, b"4"))
    except Exception:
        gh = None
    try:
        ij = option.split(" ")[8 - 1]
        optionss.append(types.PollAnswer(ij, b"5"))
    except Exception:
        ij = None
    try:
        kl = option.split(" ")[9 - 1]
        optionss.append(types.PollAnswer(kl, b"6"))
    except Exception:
        kl = None
    try:
        mn = option.split(" ")[10 - 1]
        optionss.append(types.PollAnswer(mn, b"7"))
    except Exception:
        mn = None
    try:
        op = option.split(" ")[11 - 1]
        optionss.append(types.PollAnswer(op, b"8"))
    except Exception:
        op = None
    try:
        qr = option.split(" ")[12 - 1]
        optionss.append(types.PollAnswer(qr, b"9"))
    except Exception:
        qr = None
    try:
        st = option.split(" ")[13 - 1]
        optionss.append(types.PollAnswer(st, b"10"))
    except Exception:
        st = None

    if pvoty is False and quizy is False and mchoicee is False:
        await Abishnoi.send_file(
            event.chat_id,
            types.InputMediaPoll(
                poll=types.Poll(id=12345, question=ques, answers=optionss, quiz=False)
            ),
        )

    if pvoty is True and quizy is False and mchoicee is True:
        await Abishnoi.send_file(
            event.chat_id,
            types.InputMediaPoll(
                poll=types.Poll(
                    id=12345,
                    question=ques,
                    answers=optionss,
                    quiz=False,
                    multiple_choice=True,
                    public_voters=True,
                )
            ),
        )

    if pvoty is False and quizy is False and mchoicee is True:
        await Abishnoi.send_file(
            event.chat_id,
            types.InputMediaPoll(
                poll=types.Poll(
                    id=12345,
                    question=ques,
                    answers=optionss,
                    quiz=False,
                    multiple_choice=True,
                    public_voters=False,
                )
            ),
        )

    if pvoty is True and quizy is False and mchoicee is False:
        await Abishnoi.send_file(
            event.chat_id,
            types.InputMediaPoll(
                poll=types.Poll(
                    id=12345,
                    question=ques,
                    answers=optionss,
                    quiz=False,
                    multiple_choice=False,
                    public_voters=True,
                )
            ),
        )

    if pvoty is False and quizy is True and mchoicee is False:
        await Abishnoi.send_file(
            event.chat_id,
            types.InputMediaPoll(
                poll=types.Poll(
                    id=12345, question=ques, answers=quizoptionss, quiz=True
                ),
                correct_answers=[f"{rightone}"],
            ),
        )

    if pvoty is True and quizy is True and mchoicee is False:
        await Abishnoi.send_file(
            event.chat_id,
            types.InputMediaPoll(
                poll=types.Poll(
                    id=12345,
                    question=ques,
                    answers=quizoptionss,
                    quiz=True,
                    public_voters=True,
                ),
                correct_answers=[f"{rightone}"],
            ),
        )

    if pvoty is True and quizy is True and mchoicee is True:
        await event.reply("ʏᴏᴜ ᴄᴀɴ'ᴛ ᴜsᴇ ᴍᴜʟᴛɪᴘʟᴇ ᴠᴏᴛɪɴɢ ᴡɪᴛʜ ǫᴜɪᴢ ᴍᴏᴅᴇ")
        return
    if pvoty is False and quizy is True and mchoicee is True:
        await event.reply("ʏᴏᴜ ᴄᴀɴ'ᴛ ᴜsᴇ ᴍᴜʟᴛɪᴘʟᴇ ᴠᴏᴛɪɴɢ ᴡɪᴛʜ ǫᴜɪᴢ ᴍᴏᴅᴇ")
        return


@register(pattern="^/stoppoll(?: |$)(.*)")
async def stop(event):
    secret = event.pattern_match.group(1)
    # print(secret)
    approved_userss = approved_users.find({})
    for ch in approved_userss:
        iid = ch["id"]
        userss = ch["user"]
    if event.is_group:
        if await is_register_admin(event.input_chat, event.message.sender_id):
            pass
        elif event.chat_id == iid and event.sender_id == userss:
            pass
        else:
            return

    if not event.reply_to_msg_id:
        await event.reply("ᴘʟᴇᴀsᴇ ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴘᴏʟʟ ᴛᴏ sᴛᴏᴘ ɪᴛ")
        return

    if input is None:
        await event.reply("ᴡʜᴇʀᴇ ɪs ᴛʜᴇ ᴘᴏʟʟ ɪᴅ ?")
        return

    try:
        secret = str(secret)
    except ValueError:
        await event.reply("ᴘᴏʟʟ ɪᴅ sʜᴏᴜʟᴅ ᴄᴏɴᴛᴀɪɴ ᴏɴʟʏ ɴᴜᴍʙᴇʀs")
        return

    if len(secret) != 5:
        await event.reply("ᴘᴏʟʟ ɪᴅ sʜᴏᴜʟᴅ ʙᴇ ᴀɴ ɪɴᴛᴇɢᴇʀ ᴏғ 5 ᴅɪɢɪᴛs")
        return

    msg = await event.get_reply_message()

    if str(msg.sender_id) != str(BOT_ID):
        await event.reply(
            "I ᴄᴀɴ'ᴛ ᴅᴏ ᴛʜɪs ᴏᴘᴇʀᴀᴛɪᴏɴ ᴏɴ ᴛʜɪs ᴘᴏʟʟ.\nᴘʀᴏʙᴀʙʟʏ ɪᴛ's ɴᴏᴛ ᴄʀᴇᴀᴛᴇᴅ ʙʏ ᴍᴇ"
        )
        return
    print(secret)
    if msg.poll:
        allpoll = poll_id.find({})
        for c in allpoll:
            if not event.sender_id == c["user"] and not secret == c["pollid"]:
                await event.reply(
                    "ᴏᴏᴘs, ᴇɪᴛʜᴇʀ ʏᴏᴜ ʜᴀᴠᴇɴ'ᴛ ᴄʀᴇᴀᴛᴇᴅ ᴛʜɪs ᴘᴏʟʟ ᴏʀ ʏᴏᴜ ʜᴀᴠᴇ ɢɪᴠᴇɴ ᴡʀᴏɴɢ ᴘᴏʟʟ ɪᴅ"
                )
                return
        if msg.poll.poll.closed:
            await event.reply("ᴏᴏᴘs, ᴛʜᴇ ᴘᴏʟʟ ɪs ᴀʟʀᴇᴀᴅʏ ᴄʟᴏsᴇᴅ.")
            return
        poll_id.delete_one({"user": event.sender_id})
        pollid = msg.poll.poll.id
        await msg.edit(
            file=types.InputMediaPoll(
                poll=types.Poll(id=pollid, question="", answers=[], closed=True)
            )
        )
        await event.reply("sᴜᴄᴄᴇssғᴜʟʟʏ sᴛᴏᴘᴘᴇᴅ ᴛʜᴇ ᴘᴏʟʟ")
    else:
        await event.reply("ᴛʜɪs ɪsɴ'ᴛ ᴀ ᴘᴏʟʟ")


@register(pattern="^/forgotpollid$")
async def stop(event):
    approved_userss = approved_users.find({})
    for ch in approved_userss:
        iid = ch["id"]
        userss = ch["user"]
    if event.is_group:
        if await is_register_admin(event.input_chat, event.message.sender_id):
            pass
        elif event.chat_id == iid and event.sender_id == userss:
            pass
        else:
            return
    allpoll = poll_id.find({})
    for c in allpoll:
        if event.sender_id == c["user"]:
            try:
                poll_id.delete_one({"user": event.sender_id})
                await event.reply("ᴅᴏɴᴇ ʏᴏᴜ ᴄᴀɴ ɴᴏᴡ ᴄʀᴇᴀᴛᴇ ᴀ ɴᴇᴡ ᴘᴏʟʟ.")
            except Exception:
                await event.reply("sᴇᴇᴍs ʟɪᴋᴇ ʏᴏᴜ ʜᴀᴠᴇɴ'ᴛ ᴄʀᴇᴀᴛᴇᴅ ᴀɴʏ ᴘᴏʟʟ ʏᴇᴛ !")


__help__ = """
*ʏᴏᴜ ᴄᴀɴ ɴᴏᴡ ꜱᴇɴᴅ ᴘᴏʟʟꜱ ᴀɴᴏɴʏᴍᴏᴜꜱʟʏ*
*ᴘᴀʀᴀᴍᴇᴛᴇʀꜱ* -
 ❍ poll-id - ᴀ ᴘᴏʟʟ ɪᴅ ᴄᴏɴꜱɪꜱᴛꜱ of ᴀɴ 5 ᴅɪɢɪᴛ ʀᴀɴᴅᴏᴍ ɪɴᴛᴇɢᴇʀ, ᴛʜɪꜱ ɪᴅ ɪꜱ ᴀᴜᴛᴏᴍᴀᴛɪᴄᴀʟʟʏ ʀᴇᴍᴏᴠᴇᴅ ғʀᴏᴍ ᴛʜᴇ ꜱʏꜱᴛᴇᴍ ᴡʜᴇɴ ʏᴏᴜ ꜱᴛᴏᴘ ʏᴏᴜʀ ᴘʀᴇᴠɪᴏᴜꜱ ᴘᴏʟʟ
 ❍ question - ᴛʜᴇ ϙᴜᴇꜱᴛɪᴏɴ ʏᴏᴜ ᴡᴀɴɴᴀ ᴀꜱᴋ
 
 ❍ <True@optionnumber/False>(1) :- ϙᴜɪᴢ ᴍᴏᴅᴇ, ʏᴏᴜ ᴍᴜꜱᴛ ꜱᴛᴀᴛᴇ ᴛʜᴇ ᴄᴏʀʀᴇᴄᴛ ᴀɴꜱᴡᴇʀ ᴡɪᴛʜ `@` ᴇx -: `True@1` ᴏʀ `True@2`
 ❍ <True/False>(2) - ᴘᴜʙʟɪᴄ ᴠᴏᴛᴇꜱ 
 ❍ <True/False>(3) - ᴍᴜʟᴛɪᴘʟᴇ ᴄʜᴏɪᴄᴇ
*ꜱʏɴᴛᴀx* -
➥ /poll <poll-id> <question> | <True@optionnumber/False> <True/False> <True/False> <option1> <option2> ... upto <option10>
*ᴇxᴀᴍᴘʟᴇꜱ* -
➥ `/poll 12345 | ᴀᴍ ɪ ᴄᴏᴏʟ ? | False False False yes no`
➥ `/poll 12345 | ᴀᴍ ɪ ᴄᴏᴏʟ ? | True@1 False False yes no`
ʀᴇᴘʟʏ ᴛᴏ ᴛʜᴇ ᴘᴏʟʟ ᴡɪᴛʜ `/stoppoll <poll-id>` ᴛᴏ ꜱᴛᴏᴘ ᴛʜᴇ ᴘᴏʟʟ
*ɴᴏᴛᴇ* : ɪғ ʏᴏᴜ ʜᴀᴠᴇ ғᴏʀɢᴏᴛᴛᴇɴ ʏᴏᴜʀ ᴘᴏʟʟ ɪᴅ ᴏʀ ᴅᴇʟᴇᴛᴇᴅ ᴛʜᴇ ᴘᴏʟʟ ꜱᴏ ᴛʜᴀᴛ ʏᴏᴜ ᴄᴀɴ'ᴛ ꜱᴛᴏᴘ ᴛʜᴇ ᴘʀᴇᴠɪᴏᴜꜱ ᴘᴏʟʟ ᴛʏᴘᴇ `/forgotpollid`, ᴛʜɪꜱ ᴡɪʟʟ ʀᴇꜱᴇᴛ ᴛʜᴇ ᴘᴏʟʟ ɪᴅ, ʏᴏᴜ ᴡɪʟʟ ʜᴀᴠᴇ ɴᴏ ᴀᴄᴄᴇꜱꜱ ᴛᴏ ᴛʜᴇ ᴘʀᴇᴠɪᴏᴜꜱ ᴘᴏʟʟ !
"""


__mod_name__ = "𝐏ᴏʟʟɪɴɢ"
