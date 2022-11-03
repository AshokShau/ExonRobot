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
# ""DEAR PRO PEOPLE,  DON'T REMOVE & CHANGE THIS LINE
# TG :- @Abishnoi1M
#     MY ALL BOTS :- Abishnoi_bots
#     GITHUB :- KingAbishnoi ""

import io
import os
import shutil

import cv2
import numpy as np
import requests
from PIL import Image, ImageDraw, ImageOps

from Exon import REM_BG_API_KEY


async def rotate_90(client, message):
    try:
        userid = str(message.chat.id)
        if not os.path.isdir(f"./DOWNLOADS/{userid}"):
            os.makedirs(f"./DOWNLOADS/{userid}")
        download_location = "./DOWNLOADS" + "/" + userid + "/" + userid + ".jpg"
        edit_img_loc = "./DOWNLOADS" + "/" + userid + "/" + "rotate_90.jpg"
        if not message.reply_to_message.empty:
            msg = await message.reply_to_message.reply_text(
                "Downloading image", quote=True
            )
            a = await client.download_media(
                message=message.reply_to_message, file_name=download_location
            )
            await msg.edit("ᴘʀᴏᴄᴇssɪɴɢ ɪᴍᴀɢᴇ.....")
            src = cv2.imread(a)
            image = cv2.rotate(src, cv2.cv2.ROTATE_90_CLOCKWISE)
            cv2.imwrite(edit_img_loc, image)
            await message.reply_chat_action("upload_photo")
            await message.reply_to_message.reply_photo(edit_img_loc, quote=True)
            await msg.delete()
        else:
            await message.reply_text("ᴡʜʏ ᴅɪᴅ ʏᴏᴜ ᴅᴇʟᴇᴛᴇ ᴛʜᴀᴛ??")
        try:
            shutil.rmtree(f"./DOWNLOADS/{userid}")
        except Exception:
            pass
    except Exception as e:
        print("rotate_90-error - " + str(e))
        if "USER_IS_BLOCKED" in str(e):
            return
        try:
            await message.reply_to_message.reply_text(
                "sᴏᴍᴇᴛʜɪɴɢ ᴡᴇɴᴛ ᴡʀᴏɴɢ!", quote=True
            )
        except Exception:
            return


async def rotate_180(client, message):
    try:
        userid = str(message.chat.id)
        if not os.path.isdir(f"./DOWNLOADS/{userid}"):
            os.makedirs(f"./DOWNLOADS/{userid}")
        download_location = "./DOWNLOADS" + "/" + userid + "/" + userid + ".jpg"
        edit_img_loc = "./DOWNLOADS" + "/" + userid + "/" + "rotate_180.jpg"
        if not message.reply_to_message.empty:
            msg = await message.reply_to_message.reply_text(
                "Downloading image", quote=True
            )
            a = await client.download_media(
                message=message.reply_to_message, file_name=download_location
            )
            await msg.edit("ᴘʀᴏᴄᴇssɪɴɢ ɪᴍᴀɢᴇ.....")
            src = cv2.imread(a)
            image = cv2.rotate(src, cv2.ROTATE_180)
            cv2.imwrite(edit_img_loc, image)
            await message.reply_chat_action("upload_photo")
            await message.reply_to_message.reply_photo(edit_img_loc, quote=True)
            await msg.delete()
        else:
            await message.reply_text("ᴡʜʏ ᴅɪᴅ ʏᴏᴜ ᴅᴇʟᴇᴛᴇ ᴛʜᴀᴛ??")
        try:
            shutil.rmtree(f"./DOWNLOADS/{userid}")
        except Exception:
            pass
    except Exception as e:
        print("rotate_180-error - " + str(e))
        if "USER_IS_BLOCKED" in str(e):
            return
        try:
            await message.reply_to_message.reply_text(
                "sᴏᴍᴇᴛʜɪɴɢ ᴡᴇɴᴛ ᴡʀᴏɴɢ!", quote=True
            )
        except Exception:
            return


async def rotate_270(client, message):
    try:
        userid = str(message.chat.id)
        if not os.path.isdir(f"./DOWNLOADS/{userid}"):
            os.makedirs(f"./DOWNLOADS/{userid}")
        download_location = "./DOWNLOADS" + "/" + userid + "/" + userid + ".jpg"
        edit_img_loc = "./DOWNLOADS" + "/" + userid + "/" + "rotate_270.jpg"
        if not message.reply_to_message.empty:
            msg = await message.reply_to_message.reply_text(
                "Downloading image", quote=True
            )
            a = await client.download_media(
                message=message.reply_to_message, file_name=download_location
            )
            await msg.edit("ᴘʀᴏᴄᴇssɪɴɢ ɪᴍᴀɢᴇ.....")
            src = cv2.imread(a)
            image = cv2.rotate(src, cv2.ROTATE_90_COUNTERCLOCKWISE)
            cv2.imwrite(edit_img_loc, image)
            await message.reply_chat_action("upload_photo")
            await message.reply_to_message.reply_photo(edit_img_loc, quote=True)
            await msg.delete()
        else:
            await message.reply_text("ᴡʜʏ ᴅɪᴅ ʏᴏᴜ ᴅᴇʟᴇᴛᴇ ᴛʜᴀᴛ??")
        try:
            shutil.rmtree(f"./DOWNLOADS/{userid}")
        except Exception:
            pass
    except Exception as e:
        print("rotate_270-error - " + str(e))
        if "USER_IS_BLOCKED" in str(e):
            return
        try:
            await message.reply_to_message.reply_text(
                "sᴏᴍᴇᴛʜɪɴɢ ᴡᴇɴᴛ ᴡʀᴏɴɢ!", quote=True
            )
        except Exception:
            return


def resize_photo(photo: str, userid: str) -> io.BytesIO:
    image = Image.open(photo)
    maxsize = 512
    scale = maxsize / max(image.width, image.height)
    new_size = (int(image.width * scale), int(image.height * scale))
    image = image.resize(new_size, Image.LANCZOS)
    resized_photo = io.BytesIO()
    resized_photo.name = "./DOWNLOADS" + "/" + userid + "resized.png"
    image.save(resized_photo, "PNG")
    return resized_photo


async def round_sticker(client, message):
    try:
        userid = str(message.chat.id)
        if not os.path.isdir(f"./DOWNLOADS/{userid}"):
            os.makedirs(f"./DOWNLOADS/{userid}")
        download_location = "./DOWNLOADS" + "/" + userid + "/" + userid + ".jpg"
        if not message.reply_to_message.empty:
            msg = await message.reply_to_message.reply_text(
                "ᴅᴏᴡɴʟᴏᴀᴅɪɴɢ ɪᴍᴀɢᴇ", quote=True
            )
            a = await client.download_media(
                message=message.reply_to_message, file_name=download_location
            )
            await msg.edit("ᴘʀᴏᴄᴇssɪɴɢ ɪᴍᴀɢᴇ.....")
            resized = resize_photo(a, userid)
            img = Image.open(resized).convert("RGB")
            npImage = np.array(img)
            h, w = img.size
            alpha = Image.new("L", img.size, 0)
            draw = ImageDraw.Draw(alpha)
            draw.pieslice([0, 0, h, w], 0, 360, fill=255)
            npAlpha = np.array(alpha)
            npImage = np.dstack((npImage, npAlpha))
            edit_img_loc = "./DOWNLOADS" + "/" + userid + "/" + "rounded.webp"
            Image.fromarray(npImage).save(edit_img_loc)
            await message.reply_chat_action("upload_photo")
            await message.reply_to_message.reply_sticker(edit_img_loc, quote=True)
            await msg.delete()
        else:
            await message.reply_text("ᴡʜʏ ᴅɪᴅ ʏᴏᴜ ᴅᴇʟᴇᴛᴇ ᴛʜᴀᴛ??")
        try:
            shutil.rmtree(f"./DOWNLOADS/{userid}")
        except Exception:
            pass
    except Exception as e:
        print("round_sticker-error - " + str(e))
        if "USER_IS_BLOCKED" in str(e):
            return
        try:
            await message.reply_to_message.reply_text(
                "sᴏᴍᴇᴛʜɪɴɢ ᴡᴇɴᴛ ᴡʀᴏɴɢ!", quote=True
            )
        except Exception:
            return


async def inverted(client, message):
    try:
        userid = str(message.chat.id)
        if not os.path.isdir(f"./DOWNLOADS/{userid}"):
            os.makedirs(f"./DOWNLOADS/{userid}")
        download_location = "./DOWNLOADS" + "/" + userid + "/" + userid + ".jpg"
        if not message.reply_to_message.empty:
            msg = await message.reply_to_message.reply_text(
                "ᴅᴏᴡɴʟᴏᴀᴅɪɴɢ ɪᴍᴀɢᴇ", quote=True
            )
            a = await client.download_media(
                message=message.reply_to_message, file_name=download_location
            )
            await msg.edit("ᴘʀᴏᴄᴇssɪɴɢ ɪᴍᴀɢᴇ.....")
            image = Image.open(a)
            inverted_image = ImageOps.invert(image)
            edit_img_loc = "./DOWNLOADS" + "/" + userid + "/" + "inverted.png"
            inverted_image.save(edit_img_loc)
            await message.reply_chat_action("upload_photo")
            await message.reply_to_message.reply_photo(edit_img_loc, quote=True)
            await msg.delete()
        else:
            await message.reply_text("ᴡʜʏ ᴅɪᴅ ʏᴏᴜ ᴅᴇʟᴇᴛᴇ ᴛʜᴀᴛ??")
        try:
            shutil.rmtree(f"./DOWNLOADS/{userid}")
        except Exception:
            pass
    except Exception as e:
        print("inverted-error - " + str(e))
        if "USER_IS_BLOCKED" in str(e):
            return
        try:
            await message.reply_to_message.reply_text(
                "sᴏᴍᴇᴛʜɪɴɢ ᴡᴇɴᴛ ᴡʀᴏɴɢ!", quote=True
            )
        except Exception:
            return


async def removebg_plain(client, message):
    try:
        if REM_BG_API_KEY != "":
            userid = str(message.chat.id)
            if not os.path.isdir(f"./DOWNLOADS/{userid}"):
                os.makedirs(f"./DOWNLOADS/{userid}")
            download_location = "./DOWNLOADS" + "/" + userid + "/" + userid + ".jpg"
            edit_img_loc = "./DOWNLOADS" + "/" + userid + "/" + "nobgplain.png"
            if not message.reply_to_message.empty:
                msg = await message.reply_to_message.reply_text(
                    "ᴅᴏᴡɴʟᴏᴀᴅɪɴɢ ɪᴍᴀɢᴇ", quote=True
                )
                await client.download_media(
                    message=message.reply_to_message, file_name=download_location
                )
                await msg.edit("ᴘʀᴏᴄᴇssɪɴɢ ɪᴍᴀɢᴇ.....")

                response = requests.post(
                    "https://api.remove.bg/v1.0/removebg",
                    files={"image_file": open(download_location, "rb")},
                    data={"size": "auto"},
                    headers={"X-Api-Key": REM_BG_API_KEY},
                )
                if response.status_code == 200:
                    with open(f"{edit_img_loc}", "wb") as out:
                        out.write(response.content)
                else:
                    await message.reply_to_message.reply_text(
                        "Check if your api is correct", quote=True
                    )
                    return

                await message.reply_chat_action("upload_document")
                await message.reply_to_message.reply_document(edit_img_loc, quote=True)
                await msg.delete()
            else:
                await message.reply_text("ᴡʜʏ ᴅɪᴅ ʏᴏᴜ ᴅᴇʟᴇᴛᴇ ᴛʜᴀᴛ??")
            try:
                shutil.rmtree(f"./DOWNLOADS/{userid}")
            except Exception:
                pass
        else:
            await message.reply_to_message.reply_text(
                "ɢᴇᴛ ᴛʜᴇ ᴀᴘɪ ғʀᴏᴍ https://www.remove.bg/b/background-removal-api ᴀɴᴅ ᴀᴅᴅ ɪɴ ᴄᴏɴғɪɢ ᴠᴀʀ",
                quote=True,
                disable_web_page_preview=True,
            )
    except Exception as e:
        print("removebg_plain-error - " + str(e))
        if "USER_IS_BLOCKED" in str(e):
            return
        try:
            await message.reply_to_message.reply_text(
                "sᴏᴍᴇᴛʜɪɴɢ ᴡᴇɴᴛ ᴡʀᴏɴɢ!", quote=True
            )
        except Exception:
            return


async def removebg_white(client, message):
    try:
        if REM_BG_API_KEY != "":
            userid = str(message.chat.id)
            if not os.path.isdir(f"./DOWNLOADS/{userid}"):
                os.makedirs(f"./DOWNLOADS/{userid}")
            download_location = "./DOWNLOADS" + "/" + userid + "/" + userid + ".jpg"
            edit_img_loc = "./DOWNLOADS" + "/" + userid + "/" + "nobgwhite.png"
            if not message.reply_to_message.empty:
                msg = await message.reply_to_message.reply_text(
                    "ᴅᴏᴡɴʟᴏᴀᴅɪɴɢ ɪᴍᴀɢᴇ", quote=True
                )
                await client.download_media(
                    message=message.reply_to_message, file_name=download_location
                )
                await msg.edit("ᴘʀᴏᴄᴇssɪɴɢ ɪᴍᴀɢᴇ.....")

                response = requests.post(
                    "https://api.remove.bg/v1.0/removebg",
                    files={"image_file": open(download_location, "rb")},
                    data={"size": "auto"},
                    headers={"X-Api-Key": REM_BG_API_KEY},
                )
                if response.status_code == 200:
                    with open(f"{edit_img_loc}", "wb") as out:
                        out.write(response.content)
                else:
                    await message.reply_to_message.reply_text(
                        "ᴄʜᴇᴄᴋ ɪғ ʏᴏᴜʀ ᴀᴘɪ ɪs ᴄᴏʀʀᴇᴄᴛ", quote=True
                    )
                    return

                await message.reply_chat_action("upload_photo")
                await message.reply_to_message.reply_photo(edit_img_loc, quote=True)
                await msg.delete()
            else:
                await message.reply_text("ᴡʜʏ ᴅɪᴅ ʏᴏᴜ ᴅᴇʟᴇᴛᴇ ᴛʜᴀᴛ??")
            try:
                shutil.rmtree(f"./DOWNLOADS/{userid}")
            except Exception:
                pass
        else:
            await message.reply_to_message.reply_text(
                "ɢᴇᴛ ᴛʜᴇ ᴀᴘɪ ғʀᴏᴍ https://www.remove.bg/b/background-removal-api ᴀɴᴅ ᴀᴅᴅ ɪɴ ᴄᴏɴғɪɢ ᴠᴀʀ",
                quote=True,
                disable_web_page_preview=True,
            )
    except Exception as e:
        print("removebg_white-error - " + str(e))
        if "USER_IS_BLOCKED" in str(e):
            return
        try:
            await message.reply_to_message.reply_text(
                "sᴏᴍᴇᴛʜɪɴɢ ᴡᴇɴᴛ ᴡʀᴏɴɢ!", quote=True
            )
        except Exception:
            return


async def removebg_sticker(client, message):
    try:
        if REM_BG_API_KEY != "":
            userid = str(message.chat.id)
            if not os.path.isdir(f"./DOWNLOADS/{userid}"):
                os.makedirs(f"./DOWNLOADS/{userid}")
            download_location = "./DOWNLOADS" + "/" + userid + "/" + userid + ".jpg"
            edit_img_loc = "./DOWNLOADS" + "/" + userid + "/" + "nobgsticker.webp"
            if not message.reply_to_message.empty:
                msg = await message.reply_to_message.reply_text(
                    "Downloading image", quote=True
                )
                await client.download_media(
                    message=message.reply_to_message, file_name=download_location
                )
                await msg.edit("ᴘʀᴏᴄᴇssɪɴɢ ɪᴍᴀɢᴇ.....")

                response = requests.post(
                    "https://api.remove.bg/v1.0/removebg",
                    files={"image_file": open(download_location, "rb")},
                    data={"size": "auto"},
                    headers={"X-Api-Key": REM_BG_API_KEY},
                )
                if response.status_code == 200:
                    with open(f"{edit_img_loc}", "wb") as out:
                        out.write(response.content)
                else:
                    await message.reply_to_message.reply_text(
                        "ᴄʜᴇᴄᴋ ɪғ ʏᴏᴜʀ ᴀᴘɪ ɪs ᴄᴏʀʀᴇᴄᴛ", quote=True
                    )
                    return

                await message.reply_chat_action("upload_photo")
                await message.reply_to_message.reply_sticker(edit_img_loc, quote=True)
                await msg.delete()
            else:
                await message.reply_text("ᴡʜʏ ᴅɪᴅ ʏᴏᴜ ᴅᴇʟᴇᴛᴇ ᴛʜᴀᴛ??")
            try:
                shutil.rmtree(f"./DOWNLOADS/{userid}")
            except Exception:
                pass
        else:
            await message.reply_to_message.reply_text(
                "ɢᴇᴛ ᴛʜᴇ ᴀᴘɪ ғʀᴏᴍ https://www.remove.bg/b/background-removal-api ᴀɴᴅ ᴀᴅᴅ ɪɴ ᴄᴏɴғɪɢ ᴠᴀʀ",
                quote=True,
                disable_web_page_preview=True,
            )
    except Exception as e:
        print("removebg_sticker-error - " + str(e))
        if "USER_IS_BLOCKED" in str(e):
            return
        try:
            await message.reply_to_message.reply_text(
                "sᴏᴍᴇᴛʜɪɴɢ ᴡᴇɴᴛ ᴡʀᴏɴɢ!", quote=True
            )
        except Exception:
            return
