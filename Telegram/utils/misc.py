from telegram import InlineKeyboardButton, InlineKeyboardMarkup

ParseWords: list[str] = [
    "first",
    "last",
    "fullname",
    "id",
    "username",
    "mention",
    # "chatname",
    "preview",
    "protect",
    "spoiler",
    "owner",
    "user",
    "admin",
]

StartPic: list[str] = [
    "https://telegra.ph//file/0879fbdb307005c1fa8ab.jpg",
    "https://telegra.ph//file/19e3a9d5c0985702497fb.jpg",
    "https://telegra.ph//file/b5fa277081dddbddd0b12.jpg",
    "https://telegra.ph//file/96e96245fe1afb82d0398.jpg",
    "https://telegra.ph//file/fb140807129a3ccb60164.jpg",
    "https://telegra.ph//file/09c9ea0e2660efae6f62a.jpg",
    "https://telegra.ph//file/3b59b15e1914b4fa18b71.jpg",
    "https://telegra.ph//file/efb26cc17eef6fe82d910.jpg",
    "https://telegra.ph//file/ab4925a050e07b00f63c5.jpg",
    "https://telegra.ph//file/d169a77fd52b46e421414.jpg",
    "https://telegra.ph//file/dab9fc41f214f9cded1bb.jpg",
    "https://telegra.ph//file/e05d6e4faff7497c5ae56.jpg",
    "https://telegra.ph//file/1e54f0fff666dd53da66f.jpg",
    "https://telegra.ph//file/18e98c60b253d4d926f5f.jpg",
    "https://telegra.ph//file/b1f7d9702f8ea590b2e0c.jpg",
    "https://telegra.ph//file/7bb62c8a0f399f6ee1f33.jpg",
    "https://telegra.ph//file/dd00c759805082830b6b6.jpg",
    "https://telegra.ph//file/3b996e3241cf93d102adc.jpg",
    "https://telegra.ph//file/610cc4522c7d0f69e1eb8.jpg",
    "https://telegra.ph//file/bc97b1e9bbe6d6db36984.jpg",
    "https://telegra.ph//file/2ddf3521636d4b17df6dd.jpg",
    "https://telegra.ph//file/72e4414f618111ea90a57.jpg",
    "https://telegra.ph//file/a958417dcd966d341bfe2.jpg",
    "https://telegra.ph//file/0afd9c2f70c6328a1e53a.jpg",
    "https://telegra.ph//file/82ff887aad046c3bcc9a3.jpg",
    "https://telegra.ph//file/8ba64d5506c23acb67ff4.jpg",
    "https://telegra.ph//file/8ba64d5506c23acb67ff4.jpg",
    "https://telegra.ph//file/a7cba6e78bb63e1b4aefb.jpg",
    "https://telegra.ph//file/f8ba75bdbb9931cbc8229.jpg",
    "https://telegra.ph//file/07bb5f805178ec24871d3.jpg",
]


def ikb(rows=None, back=None):
    """
    Helper function to create inline keyboard.

    Args:
        rows (list, optional): List of lists of tuples, where each tuple contains
            the text and value of the button. Defaults to None.
        back (str, optional): Callback data for the back button. Defaults to None.

    Returns:
        InlineKeyboardMarkup: Inline keyboard.
    """
    if rows is None:
        rows = []
    lines = []
    for row in rows:
        line = [btn(*button) for button in row]
        lines.append(line)

    if back:
        back_btn = [(btn("« ʙᴀᴄᴋ", back))]
        lines.append(back_btn)
    return InlineKeyboardMarkup(inline_keyboard=lines)


def btn(text, value, type="callback_data"):
    """
    Helper function to create inline keyboard button.

    Args:
        text (str): Button text.
        value (str): Callback data for the button.
        type (str, optional): Type of the button. Defaults to "callback_data".

    Returns:
        InlineKeyboardButton: Inline keyboard button.
    """
    return InlineKeyboardButton(text, **{type: value})
