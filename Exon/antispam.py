from . import OWNER_ID, dispatcher

Owner = [OWNER_ID]
NoResUser = [OWNER_ID]
AntiSpamValue = 6

GLOBAL_USER_DATA = {}


def antispam_restrict_user(user_id, time):
    # print(GLOBAL_USER_DATA)
    if user_id in NoResUser:
        return True
    if GLOBAL_USER_DATA.get(user_id) and GLOBAL_USER_DATA.get(user_id).get("AntiSpamHard") and GLOBAL_USER_DATA.get(user_id).get("AntiSpamHard").get("restrict"):
        return True
    try:
        number = GLOBAL_USER_DATA["AntiSpam"][user_id]["value"]
        status = GLOBAL_USER_DATA["AntiSpam"][user_id]["status"]
        restime = GLOBAL_USER_DATA["AntiSpam"][user_id]["restrict"]
        level = GLOBAL_USER_DATA["AntiSpam"][user_id]["level"]
    except Exception:
        number = 0
        status = False
        restime = None
        level = 1
    if restime and int(time) <= int(restime):
        if status:
            return False
        number += 1
    if number >= int(AntiSpamValue * level):
        status = True
        restrict_time = int(time) + (60 * (number / AntiSpamValue))
    else:
        status = False
        restrict_time = int(time) + AntiSpamValue
    GLOBAL_USER_DATA["AntiSpam"] = {
        user_id: {
            "status": status,
            "user": user_id,
            "value": number,
            "restrict": restrict_time,
            "level": level,
        }
    }


def antispam_cek_user(user_id, time):
    # print(GLOBAL_USER_DATA)
    try:
        value = GLOBAL_USER_DATA["AntiSpam"]
        if not value.get(user_id):
            return {
                "status": False,
                "user": user_id,
                "value": 0,
                "restrict": None,
                "level": 1,
            }
        value = GLOBAL_USER_DATA["AntiSpam"][user_id]
        if value["restrict"]:
            if int(time) >= int(value["restrict"]):
                if value["status"]:
                    # value['value'] = 0
                    value["status"] = False
                    value["level"] += 1
                    value["restrict"] = 0
                else:
                    value["value"] = 2 * int(value["level"])
            elif value["status"]:
                try:
                    number = GLOBAL_USER_DATA["AntiSpamHard"][user_id]["value"]
                    status = GLOBAL_USER_DATA["AntiSpamHard"][user_id]["status"]
                    restime = GLOBAL_USER_DATA["AntiSpamHard"][user_id][
                        "restrict"
                    ]
                    level = GLOBAL_USER_DATA["AntiSpamHard"][user_id]["level"]
                except Exception:
                    number = 0
                    status = False
                    restime = None
                    level = 1
                if status:
                    dispatcher.bot.sendMessage(
                        Owner,
                        f"⚠ ᴡᴀʀɴɪɴɢ: ᴜsᴇʀ `{user_id}` ᴡᴀs ᴅᴇᴛᴇᴄᴛᴇᴅ sᴘᴀᴍ.",
                        parse_mode="markdown",
                    )
                    GLOBAL_USER_DATA["AntiSpamHard"] = {
                        user_id: {
                            "status": False,
                            "user": user_id,
                            "value": 0,
                            "restrict": restime,
                            "level": level,
                        }
                    }
                    # print(GLOBAL_USER_DATA["AntiSpamHard"])
                    return value
                else:
                    if number >= 5:
                        restrict_time = int(time) + 3600
                        status = True
                        GLOBAL_USER_DATA["AntiSpam"] = {
                            user_id: {
                                "status": status,
                                "user": user_id,
                                "value": GLOBAL_USER_DATA["AntiSpam"][user_id][
                                    "value"
                                ],
                                "restrict": restrict_time,
                                "level": GLOBAL_USER_DATA["AntiSpam"][user_id][
                                    "level"
                                ],
                            }
                        }
                    else:
                        restrict_time = None
                        number += 1
                GLOBAL_USER_DATA["AntiSpamHard"] = {
                    user_id: {
                        "status": status,
                        "user": user_id,
                        "value": number,
                        "restrict": restrict_time,
                        "level": level,
                    }
                }
                                    # print(GLOBAL_USER_DATA["AntiSpamHard"])
        return value
    except KeyError:
        return {
            "status": False,
            "user": user_id,
            "value": 0,
            "restrict": None,
            "level": 1,
        }


def check_user_spam(user_id):
    if GLOBAL_USER_DATA.get("AntiSpam"):
        if GLOBAL_USER_DATA["AntiSpam"].get(user_id):
            status = GLOBAL_USER_DATA["AntiSpam"].get(user_id).get("status")
        else:
            status = False
    else:
        status = False
    if GLOBAL_USER_DATA.get("AntiSpamHard"):
        if GLOBAL_USER_DATA["AntiSpamHard"].get(user_id):
            status_hard = GLOBAL_USER_DATA["AntiSpamHard"].get(user_id).get("status")
        else:
            status_hard = False
    else:
        status_hard = False
    return {"status": status, "status_hard": status_hard}


# This is will detect user
def detect_user(user_id, chat_id, message, parsing_date):
    check_spam = antispam_cek_user(user_id, parsing_date)
    check_user = check_user_spam(user_id)
    if check_spam["status"]:
        if check_user["status_hard"]:
            getbotinfo = dispatcher.bot.getChatMember(chat_id, dispatcher.bot.id)
            try:
                if getbotinfo.status in ("administrator", "creator"):
                    dispatcher.bot.kickChatMember(chat_id, user_id)
                    dispatcher.bot.sendMessage(
                        chat_id,
                        "I'ᴠᴇ ʙᴀɴɴᴇᴅ ᴛʜᴇᴍ!",
                        reply_to_message_id=message.message_id,
                    )
                    return True
            except Exception:
                pass
            if message.chat.type != "private":
                dispatcher.bot.sendMessage(
                    chat_id,
                    "ғʟᴏᴏᴅ ᴍᴇssᴀɢᴇ ᴡᴀs ᴅᴇᴛᴇᴄᴛᴇᴅ!\nI'ᴍ ᴏᴜᴛ, ɪɴᴠɪᴛᴇ ᴍᴇ ᴀɢᴀɪɴ ɪғ ᴛʜᴇ ғʟᴏᴏᴅ ʜᴀs sᴛᴏᴘᴘᴇᴅ 🙂\n\nᴛʜᴀɴᴋs",
                )
                dispatcher.bot.leaveChat(chat_id)
                return True
        dispatcher.bot.sendMessage(
            chat_id,
            "ʜᴇɪ! sᴍᴀʀᴛ ᴀɴᴛɪғʟᴏᴏᴅ ᴡᴀs ᴅᴇᴛᴇᴄᴛᴇᴅ ғᴏʀ ᴛʜɪs ᴜsᴇʀ!\n\nʏᴏᴜ ᴡɪʟʟ ʙᴇ ʀᴇsᴛʀɪᴄᴛᴇᴅ ғᴏʀ ᴀ ᴡʜɪʟᴇ.\n\nɪғ ʏᴏᴜ sᴛɪʟʟ ᴄᴏɴᴛɪɴᴜᴇs ɪ ᴡɪʟʟ ʙᴀɴ ᴀɴᴅ ᴄʀᴇᴀᴛᴇ ᴀ sᴘᴀᴍ ʀᴇᴘᴏʀᴛ ғᴏʀ ᴛʜɪs ᴜsᴇʀ!",
            reply_to_message_id=message.message_id,
        )
        return True
