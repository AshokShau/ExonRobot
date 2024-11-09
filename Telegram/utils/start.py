from Telegram import HELP_COMMANDS
from Telegram.utils.misc import ikb

PM_START_TEXT = """
<b>нєу</b> {} 🥀

๏ ᴛʜɪs ɪs {} !
➻ ᴛʜᴇ ᴍᴏsᴛ ᴄᴏᴍᴘʟᴇᴛᴇ ᴛᴇʟᴇɢʀᴀᴍ ʙᴏᴛ ғᴏʀ ᴍᴀɴᴀɢɪɴɢ ᴀɴᴅ ᴘʀᴏᴛᴇᴄᴛɪɴɢ ɢʀᴏᴜᴘs ᴄʜᴀᴛ ғʀᴏᴍ sᴘᴀᴍᴍᴇʀ ᴀɴᴅ sᴄᴏғғʟᴀᴡ.

──────────────────
<b>๏ ᴄʟɪᴄᴋ ᴏɴ ᴛʜᴇ ʜᴇʟᴩ ʙᴜᴛᴛᴏɴ ᴛᴏ ɢᴇᴛ ɪɴғᴏʀᴍᴀᴛɪᴏɴ ᴀʙᴏᴜᴛ ᴍʏ ᴍᴏᴅᴜʟᴇs ᴀɴᴅ ᴄᴏᴍᴍᴀɴᴅs.</b>
"""

PM_HELP_TEXT = """
────────────────────
<b>๏ ᴄʟɪᴄᴋ ᴏɴ ᴛʜᴇ ʜᴇʟᴩ ʙᴜᴛᴛᴏɴ ᴛᴏ ɢᴇᴛ ɪɴғᴏʀᴍᴀᴛɪᴏɴ ᴀʙᴏᴜᴛ ᴍʏ ᴍᴏᴅᴜʟᴇs ᴀɴᴅ ᴄᴏᴍᴍᴀɴᴅs.</b>
  ──────────────────
"""


def gen_help_keyboard():
    """Generate a keyboard with all commands."""
    kb = sorted(list(HELP_COMMANDS.keys()))
    return [kb[i : i + 3] for i in range(0, len(kb), 3)]


async def get_help_msg(help_option: str):
    """Get help message and keyboard."""
    help_cmd_keys = sorted(
        k
        for j in [HELP_COMMANDS[i]["alt_cmd"] for i in list(HELP_COMMANDS.keys())]
        for k in j
    )

    if help_option in help_cmd_keys:
        help_option_name = next(
            HELP_COMMANDS[i]
            for i in HELP_COMMANDS
            if help_option in HELP_COMMANDS[i]["alt_cmd"]
        )
        help_option_value = help_option_name["help_msg"]
        ou = next(
            HELP_COMMANDS[i]["buttons"]
            for i in HELP_COMMANDS
            if help_option in HELP_COMMANDS[i]["alt_cmd"]
        )
        help_kb = ikb(ou, "commands")
        help_msg = f"{help_option_value}"
    else:
        help_msg = PM_HELP_TEXT
        ou = gen_help_keyboard()
        help_kb = ikb(ou, "start_back")

    return help_msg, help_kb
