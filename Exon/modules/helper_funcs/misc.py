from html import escape
from math import ceil
from typing import Dict, List

from telegram import Bot, InlineKeyboardButton, ParseMode
from telegram.constants import MessageLimit, ParseMode
from telegram.error import TelegramError

from Exon import NO_LOAD


class EqInlineKeyboardButton(InlineKeyboardButton):
    def __eq__(self, other):
        return self.text == other.text

    def __lt__(self, other):
        return self.text < other.text

    def __gt__(self, other):
        return self.text > other.text


def split_message(msg: str) -> List[str]:
    if len(msg) < MessageLimit.MAX_TEXT_LENGTH:
        return [msg]

    lines = msg.splitlines(True)
    small_msg = ""
    result = []
    for line in lines:
        if len(small_msg) + len(line) < MessageLimit.MAX_TEXT_LENGTH:
            small_msg += line
        else:
            result.append(small_msg)
            small_msg = line
    else:
        # Else statement at the end of the for loop, so append the leftover string.
        result.append(small_msg)

    return result


def paginate_modules(page_n: int, module_dict: Dict, prefix, chat=None) -> List:
    if not chat:
        modules = sorted(
            [
                EqInlineKeyboardButton(
                    x.__mod_name__,
                    callback_data="{}_module({})".format(
                        prefix, x.__mod_name__.replace(" ", "_").lower()
                    ),
                )
                for x in module_dict.values()
            ]
        )
    else:
        modules = sorted(
            [
                EqInlineKeyboardButton(
                    x.__mod_name__,
                    callback_data="{}_module({},{})".format(
                        prefix, chat, x.__mod_name__.replace(" ", "_").lower()
                    ),
                )
                for x in module_dict.values()
            ]
        )

    pairs = list(zip(modules[::3], modules[1::3], modules[2::3]))
    i = 0
    for m in pairs:
        for _ in m:
            i += 1
    if len(modules) - i == 1:
        pairs.append((modules[-1],))
    elif len(modules) - i == 2:
        pairs.append(
            (
                modules[-2],
                modules[-1],
            )
        )

    COLUMN_SIZE = 4

    max_num_pages = ceil(len(pairs) / COLUMN_SIZE)
    modulo_page = page_n % max_num_pages

    # can only have a certain amount of buttons side by side
    if len(pairs) > COLUMN_SIZE:
        pairs = pairs[modulo_page * COLUMN_SIZE : COLUMN_SIZE * (modulo_page + 1)] + [
            (
                EqInlineKeyboardButton(
                    "☜",
                    callback_data="{}_prev({})".format(prefix, modulo_page),
                ),
                EqInlineKeyboardButton(
                    "ɢᴏ ʜᴏᴍᴇ",
                    callback_data="start_back",
                ),
                EqInlineKeyboardButton(
                    "☞",
                    callback_data="{}_next({})".format(prefix, modulo_page),
                ),
            )
        ]

    return pairs


async def send_to_list(
    bot: Bot,
    send_to: list,
    message: str,
    markdown=False,
    html=False,
) -> None:
    if html and markdown:
        raise Exception("Can only send with either markdown or HTML!")
    for user_id in set(send_to):
        try:
            if markdown:
                await bot.send_message(user_id, message, parse_mode=ParseMode.MARKDOWN)
            elif html:
                await bot.send_message(user_id, message, parse_mode=ParseMode.HTML)
            else:
                await bot.send_message(user_id, message)
        except TelegramError:
            pass  # ignore users who fail


def build_keyboard(buttons):
    keyb = []
    for btn in buttons:
        if btn.same_line and keyb:
            keyb[-1].append(InlineKeyboardButton(btn.name, url=btn.url))
        else:
            keyb.append([InlineKeyboardButton(btn.name, url=btn.url)])

    return keyb


def revert_buttons(buttons):
    res = ""
    for btn in buttons:
        if btn.same_line:
            res += "\n[{}](buttonurl://{}:same)".format(btn.name, btn.url)
        else:
            res += "\n[{}](buttonurl://{})".format(btn.name, btn.url)

    return res


def build_keyboard_parser(bot, chat_id, buttons):
    keyb = []
    for btn in buttons:
        if btn.url == "{rules}":
            btn.url = "http://t.me/{}?start={}".format(bot.username, chat_id)
        if btn.same_line and keyb:
            keyb[-1].append(InlineKeyboardButton(btn.name, url=btn.url))
        else:
            keyb.append([InlineKeyboardButton(btn.name, url=btn.url)])

    return keyb


def is_module_loaded(name):
    return name not in NO_LOAD


# function to mention username for chats https://t.me/username
def mention_username(username: str, name: str) -> str:
    """
    Args:
        username (:obj:`str`): The username of chat which you want to mention.
        name (:obj:`str`): The name the mention is showing.

    Returns:
        :obj:`str`: The inline mention for the user as HTML.
    """
    return f'<a href="t.me/{username}">{escape(name)}</a>'
