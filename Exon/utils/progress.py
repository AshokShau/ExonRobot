"""
MIT License

Copyright (c) 2022 ABIAHNOI69 

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


import math
import time

from .exceptions import CancelProcess
from .tools import humanbytes, time_formatter


async def progress(
    current, total, gdrive, start, prog_type, file_name=None, is_cancelled=False
):
    now = time.time()
    diff = now - start
    if is_cancelled is True:
        raise CancelProcess

    if round(diff % 10.00) == 0 or current == total:
        percentage = current * 100 / total
        speed = current / diff
        elapsed_time = round(diff)
        eta = round((total - current) / speed)
        if "upload" in prog_type.lower():
            status = "Uploading"
        elif "download" in prog_type.lower():
            status = "Downloading"
        else:
            status = "Unknown"
        progress_str = "`{0}` | [{1}{2}] `{3}%`".format(
            status,
            "".join("●" for i in range(math.floor(percentage / 10))),
            "".join("○" for i in range(10 - math.floor(percentage / 10))),
            round(percentage, 2),
        )
        tmp = (
            f"{progress_str}\n"
            f"`{humanbytes(current)} of {humanbytes(total)}"
            f" @ {humanbytes(speed)}`\n"
            f"`ETA` -> {time_formatter(eta)}\n"
            f"`Duration` -> {time_formatter(elapsed_time)}"
        )
        await gdrive.edit(f"`{prog_type}`\n\n" f"`Status`\n{tmp}")
