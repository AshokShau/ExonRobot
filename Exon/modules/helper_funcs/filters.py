"""
MIT License

Copyright (c) 2022 ABISHNOI69 

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from emoji import UNICODE_EMOJI
from telegram import Message
from telegram.ext import MessageFilter

from Exon import DEMONS, DEV_USERS


class CustomFilters:
    class _Supporters(MessageFilter):
        def filter(self, message: Message):
            return bool(message.from_user and message.from_user.id in DEMONS)

    support_filter = _Supporters()

    class _Sudoers(MessageFilter):
        def filter(self, message: Message):
            return bool(message.from_user and message.from_user.id in DEV_USERS)

    dev_filter = _Sudoers()

    class _MimeType(MessageFilter):
        def __init__(self, mimetype):
            self.mime_type = mimetype
            self.name = "CustomFilters.mime_type({})".format(self.mime_type)

        def filter(self, message: Message):
            return bool(
                message.document and message.document.mime_type == self.mime_type
            )

    mime_type = _MimeType

    class _HasText(MessageFilter):
        def filter(self, message: Message):
            return bool(
                message.text
                or message.sticker
                or message.photo
                or message.document
                or message.video
            )

    has_text = _HasText()

    class _HasEmoji(MessageFilter):
        def filter(self, message: Message):
            text = ""
            if message.text:
                text = message.text
            for emoji in UNICODE_EMOJI:
                for letter in text:
                    if letter == emoji:
                        return True
            return False

    has_emoji = _HasEmoji()

    class _IsEmoji(MessageFilter):
        def filter(self, message: Message):
            if message.text and len(message.text) == 1:
                for emoji in UNICODE_EMOJI:
                    for letter in message.text:
                        if letter == emoji:
                            return True
            return False

    is_emoji = _IsEmoji()

    class _IsAnonChannel(MessageFilter):
        def filter(self, message: Message):
            if message.from_user and message.from_user.id == 136817688:
                return True
            return False

    is_anon_channel = _IsAnonChannel()
