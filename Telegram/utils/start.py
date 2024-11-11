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
    """
    Generate a keyboard layout for help commands.

    This function creates a keyboard layout by organizing the keys of the HELP_COMMANDS into rows, with each row containing up to three keys. The keys are sorted alphabetically to ensure a consistent order in the generated keyboard.

    Returns:
        list: A list of lists, where each inner list contains up to three help command keys.

    """
    kb = sorted(list(HELP_COMMANDS.keys()))
    return [kb[i : i + 3] for i in range(0, len(kb), 3)]


async def get_help_msg(help_option: str):
    """
    Get the help message and keyboard based on the provided help option.

    This asynchronous function retrieves a help message and a corresponding keyboard layout based on the specified help option. If the help option is found in the predefined commands, it returns the associated help message and buttons; otherwise, it returns a general help message and a default keyboard.

    Args:
        help_option (str): The help option to look up in the HELP_COMMANDS.

    Returns:
        tuple: A tuple containing the help message (str) and the keyboard layout (various types depending on ikb implementation).

    """
    if help_option_data := next(
        (data for data in HELP_COMMANDS.values() if help_option in data["alt_cmd"]),
        None,
    ):
        help_msg = help_option_data["help_msg"]
        buttons = help_option_data["buttons"]
        help_kb = ikb(buttons, "commands")
    else:
        help_msg = PM_HELP_TEXT
        buttons = gen_help_keyboard()
        help_kb = ikb(buttons, "start_back")

    return help_msg, help_kb
