import re

from ptbmod import Admins
from telegram import Update
from telegram.ext import ContextTypes

from Telegram import Cmd
from Telegram.database.antiRaid_db import AntiRaidDB
from Telegram.utils.formatters import create_time, tl_time


# Remove existing job by name
def remove_job_if_exists(name: str, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """Remove existing job by name"""
    current_jobs = context.job_queue.get_jobs_by_name(name)
    if not current_jobs:
        return False
    for job in current_jobs:
        job.schedule_removal()
    return True


# Anti-raid mode timeout function
async def raid_timeout(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Anti-raid mode timeout function"""
    await AntiRaidDB(context.job.chat_id).set_anti_raid(False)
    await context.bot.send_message(
        chat_id=context.job.chat_id, text="Anti-Raid mode has been disabled. Timeout!"
    )
    return None


@Cmd(command=["autoEndRaid", "endRaid"])
@Admins(permissions="can_restrict_members", is_both=True)
async def raid_raidTime(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Anti-raid mode timeout function"""
    m = update.effective_message
    db = AntiRaidDB(update.effective_chat.id)
    raid_db = await db.get_anti_raid()
    args = context.args

    if len(args) >= 1:
        timeout = args[0]
        if not re.match(r"^(\d+[dhms])+$", timeout.lower()):
            await m.reply_text("Invalid time format! Use: 1d, 2h, 3m, or 60s.")
            return

        await db.set_raid_time(timeout)
        await m.reply_text(f"Anti-Raid mode will be disabled after {tl_time(timeout)}")
    if raid_time := raid_db.get("raid_time"):
        await m.reply_text(
            f"Anti-Raid mode will be disabled after {tl_time(raid_time)}"
        )
    else:
        await m.reply_text("No raid timeout is set.")


@Cmd(command=["raidBanTime", "raidMuteTime"])
@Admins(permissions="can_restrict_members", is_both=True)
async def raid_banTime(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Set raid ban time"""
    m = update.effective_message
    db = AntiRaidDB(update.effective_chat.id)
    args = context.args

    if len(args) >= 1:
        banTime = args[0]
        if not re.match(r"^(\d+[dhms])+$", banTime.lower()):
            await m.reply_text("Invalid time format! Use: 1d, 2h, 3m, or 60s.")
            return

        await db.set_ban_time(banTime)
        await m.reply_text(f"Raid ban time set to {tl_time(banTime)}.")
        return

    # Display current ban time if no argument is provided
    raid_db = await db.get_anti_raid()
    if ban_time := raid_db.get("ban_time"):
        await m.reply_text(f"Current raid ban time is {tl_time(ban_time)}.")
    else:
        await m.reply_text("No raid ban time is set.")


@Cmd(command=["raidMode", "antiRaidMode"])
@Admins(permissions="can_restrict_members", is_both=True)
async def raid_mode(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Set raid mode"""
    m = update.effective_message
    db = AntiRaidDB(update.effective_chat.id)
    args = context.args

    if len(args) >= 1:
        mode = args[0].lower()

        if mode not in ["ban", "mute"]:
            await m.reply_text("Invalid raid mode! Use: ban or mute.")
            return

        await db.set_raid_mode(mode)
        await m.reply_text(f"Raid mode set to {mode}.")
        return

    # Display current raid mode if no argument is provided
    raid_db = await db.get_anti_raid()
    if raidMode := raid_db.get("raid_mode"):
        await m.reply_text(f"Current raid mode is {raidMode}.")
    else:
        await m.reply_text("No raid mode is set.")


@Cmd(command=["raid", "antiRaid"])
@Admins(permissions="can_restrict_members", is_both=True)
async def raid(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Enable or disable Anti-Raid"""
    m = update.effective_message
    chat_id = update.effective_chat.id
    db = AntiRaidDB(chat_id)
    raid_db = await db.get_anti_raid()
    args = context.args

    if len(args) >= 1:
        if args[0].lower() in ("on", "yes"):
            time = raid_db["raid_time"]
            duration = create_time(time)
            job_removed = remove_job_if_exists(f"ANTI_RAID_{chat_id}", context)
            context.job_queue.run_once(
                raid_timeout,
                duration,
                name=f"ANTI_RAID_{chat_id}",
                data=update.effective_chat.full_name,
                chat_id=chat_id,
            )
            text = "Anti-Raid mode has been enabled."
            if job_removed:
                text += "\nPrevious job has been removed."
            await m.reply_text(text)
            await db.set_anti_raid(True)
            return
        if args[0].lower() in ("off", "no"):
            await m.reply_text("Anti-Raid mode has been disabled.")
            await db.set_anti_raid(False)
            return
        await m.reply_text("Invalid argument. Use: on or off.")

    await m.reply_text(f"Anti-Raid mode is {raid_db['anti_raid']}")


__mod_name__ = "Anti-Raid"
__alt_name__ = ["antiRaid", "raid", "raidMode", "raidBanTime", "autoEndRaid"]
__help__ = """
<b>Description:</b>
Some people on telegram find it entertaining to "raid" chats. During a raid, hundreds of users join a chat to spam.

The antiRaid module allows you to quickly stop anyone from joining when such a raid is happening.
All new joins will be temporarily banned for the next few hours, allowing you to wait out the spam attack until the trolls stop.
────────────────────────

- /raid [on/off]: Enable or disable Anti-Raid mode.
- /raidMode [ban/mute]: Set the raid mode to (ban or mute).
- /raidBanTime [time]: Set the raid ban time.
- /autoEndRaid [time]: Set the raid timeout.

<b>Example:</b>
- /raid on
- /raidMode ban
- /raidBanTime 1h
"""
