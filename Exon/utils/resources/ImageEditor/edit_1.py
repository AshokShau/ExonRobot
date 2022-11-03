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


import os
import shutil

import cv2
from PIL import Image, ImageEnhance, ImageFilter


async def bright(client, message):
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
            await msg.edit("ᴘʀᴏᴄᴇssɪɴɢ ɪᴍᴀɢᴇ...")
            image = Image.open(a)
            brightness = ImageEnhance.Brightness(image)
            edit_img_loc = "./DOWNLOADS" + "/" + userid + "/" + "brightness.jpg"
            brightness.enhance(1.5).save(edit_img_loc)
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
        print("bright-error - " + str(e))
        if "USER_IS_BLOCKED" in str(e):
            return
        try:
            await message.reply_to_message.reply_text(
                "sᴏᴍᴇᴛʜɪɴɢ ᴡᴇɴᴛ ᴡʀᴏɴɢ!", quote=True
            )
        except Exception:
            return


async def mix(client, message):
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
            await msg.edit("ᴘʀᴏᴄᴇssɪɴɢ ɪᴍᴀɢᴇ...")
            image = Image.open(a)
            red, green, blue = image.split()
            new_image = Image.merge("RGB", (green, red, blue))
            edit_img_loc = "./DOWNLOADS" + "/" + userid + "/" + "mix.jpg"
            new_image.save(edit_img_loc)
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
        print("mix-error - " + str(e))
        if "USER_IS_BLOCKED" in str(e):
            return
        try:
            await message.reply_to_message.reply_text(
                "sᴏᴍᴇᴛʜɪɴɢ ᴡᴇɴᴛ ᴡʀᴏɴɢ!", quote=True
            )
        except Exception:
            return


async def black_white(client, message):
    try:
        userid = str(message.chat.id)
        if not os.path.isdir(f"./DOWNLOADS/{userid}"):
            os.makedirs(f"./DOWNLOADS/{userid}")
        download_location = "./DOWNLOADS" + "/" + userid + "/" + userid + ".jpg"
        edit_img_loc = "./DOWNLOADS" + "/" + userid + "/" + "black_white.jpg"
        if not message.reply_to_message.empty:
            msg = await message.reply_to_message.reply_text(
                "ᴅᴏᴡɴʟᴏᴀᴅɪɴɢ ɪᴍᴀɢᴇ", quote=True
            )
            a = await client.download_media(
                message=message.reply_to_message, file_name=download_location
            )
            await msg.edit("ᴘʀᴏᴄᴇssɪɴɢ ɪᴍᴀɢᴇ...")
            image_file = cv2.imread(a)
            grayImage = cv2.cvtColor(image_file, cv2.COLOR_BGR2GRAY)
            cv2.imwrite(edit_img_loc, grayImage)
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
        print("black_white-error - " + str(e))
        if "USER_IS_BLOCKED" in str(e):
            return
        try:
            await message.reply_to_message.reply_text(
                "sᴏᴍᴇᴛʜɪɴɢ ᴡᴇɴᴛ ᴡʀᴏɴɢ!", quote=True
            )
        except Exception:
            return


async def normal_blur(client, message):
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
            await msg.edit("ᴘʀᴏᴄᴇssɪɴɢ ɪᴍᴀɢᴇ...")
            OriImage = Image.open(a)
            blurImage = OriImage.filter(ImageFilter.BLUR)
            edit_img_loc = "./DOWNLOADS" + "/" + userid + "/" + "BlurImage.jpg"
            blurImage.save(edit_img_loc)
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
        print("normal_blur-error - " + str(e))
        if "USER_IS_BLOCKED" in str(e):
            return
        try:
            await message.reply_to_message.reply_text(
                "sᴏᴍᴇᴛʜɪɴɢ ᴡᴇɴᴛ ᴡʀᴏɴɢ!", quote=True
            )
        except Exception:
            return


async def g_blur(client, message):
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
            await msg.edit("ᴘʀᴏᴄᴇssɪɴɢ ɪᴍᴀɢᴇ...")
            im1 = Image.open(a)
            im2 = im1.filter(ImageFilter.GaussianBlur(radius=5))
            edit_img_loc = "./DOWNLOADS" + "/" + userid + "/" + "gaussian_blur.jpg"
            im2.save(edit_img_loc)
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
        print("g_blur-error - " + str(e))
        if "USER_IS_BLOCKED" in str(e):
            return
        try:
            await message.reply_to_message.reply_text(
                "sᴏᴍᴇᴛʜɪɴɢ ᴡᴇɴᴛ ᴡʀᴏɴɢ!", quote=True
            )
        except Exception:
            return


async def box_blur(client, message):
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
            await msg.edit("ᴘʀᴏᴄᴇssɪɴɢ ɪᴍᴀɢᴇ...")
            im1 = Image.open(a)
            im2 = im1.filter(ImageFilter.BoxBlur(0))
            edit_img_loc = "./DOWNLOADS" + "/" + userid + "/" + "box_blur.jpg"
            im2.save(edit_img_loc)
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
        print("box_blur-error - " + str(e))
        if "USER_IS_BLOCKED" in str(e):
            return
        try:
            await message.reply_to_message.reply_text(
                "sᴏᴍᴇᴛʜɪɴɢ went ᴡʀᴏɴɢ!", quote=True
            )
        except Exception:
            return
