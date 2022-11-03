"""
MIT License
Copyright (c) 2022 Aʙɪsʜɴᴏɪ
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

from Exon import REDIS


def is_user_afk(userid):
    rget = REDIS.get(f"is_afk_{userid}")
    if rget:
        return True
    else:
        return False


def start_afk(userid, reason):
    REDIS.set(f"is_afk_{userid}", reason)


def afk_reason(userid):
    return strb(REDIS.get(f"is_afk_{userid}"))


def end_afk(userid):
    REDIS.delete(f"is_afk_{userid}")
    return True


def strb(redis_string):
    return str(redis_string)
