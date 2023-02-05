from telethon import events

from Exon import telethn


def register(**args):
    """ʀᴇɢɪsᴛᴇʀs ᴀ ɴᴇᴡ ᴍᴇssᴀɢᴇ."""
    pattern = args.get("pattern")

    r_pattern = r"^[/!]"

    if pattern is not None and not pattern.startswith("(?i)"):
        args["pattern"] = "(?i)" + pattern

    args["pattern"] = pattern.replace("^/", r_pattern, 1)

    def decorator(func):
        telethn.add_event_handler(func, events.NewMessage(**args))
        return func

    return decorator


def Asuinline(**args):
    def decorator(func):
        telethn.add_event_handler(func, events.CallbackQuery(**args))
        return func

    return decorator
