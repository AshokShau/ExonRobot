from datetime import datetime, timedelta

import pytz


def create_time(time_raw: str) -> datetime:
    unit_map = {
        "d": "days",
        "h": "hours",
        "m": "minutes",
        "s": "seconds",
    }
    now = datetime.now(pytz.timezone("Asia/Kolkata"))
    time_val = int(time_raw[:-1])
    unit = time_raw[-1]
    if unit == "s" and time_val < 30:
        time_val = 40
    return now + timedelta(**{unit_map[unit]: time_val})


def tl_time(time_raw):
    time_val = int(time_raw[:-1])
    unit = time_raw[-1]

    if unit == "d":
        if time_val > 366:
            return "ғᴏʀᴇᴠᴇʀ"
        return f"{time_val} {'ᴅᴀʏ' if time_val == 1 else 'ᴅᴀʏs'}"
    if unit == "h":
        if time_val > 8786:
            return "ғᴏʀᴇᴠᴇʀ"
        return f"{time_val} {'ʜᴏᴜʀ' if time_val == 1 else 'ʜᴏᴜʀs'}"
    if unit == "m":
        if time_val > 525600:
            return "ғᴏʀᴇᴠᴇʀ"
        return f"{time_val} {'ᴍɪɴᴜᴛᴇ' if time_val == 1 else 'ᴍɪɴᴜᴛᴇs'}"
    if unit == "s":
        if time_val > 31539600:
            return "ғᴏʀᴇᴠᴇʀ"
        return f"{time_val if time_val >= 30 else 40} {'sᴇᴄᴏɴᴅ' if time_val == 1 else 'sᴇᴄᴏɴᴅs'}"

    return ""
