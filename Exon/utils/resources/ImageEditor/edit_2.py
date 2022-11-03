"""
MIT License

Copyright (c) 2022 Aʙɪsʜʜɴᴏɪ

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
import numpy as np
from PIL import Image, ImageDraw, ImageEnhance


async def circle_with_bg(client, message):
    try:
        userid = str(message.chat.id)
        if not os.path.isdir(f"./DOWNLOADS/{userid}"):
            os.makedirs(f"./DOWNLOADS/{userid}")
        download_location = "./DOWNLOADS" + "/" + userid + "/" + userid + ".jpg"
        if not message.reply_to_message.empty:
            msg = await message.reply_to_message.reply_text(
                "Downloading image", quote=True
            )
            a = await client.download_media(
                message=message.reply_to_message, file_name=download_location
            )
            await msg.edit("Processing Image...")
            img = Image.open(a).convert("RGB")
            npImage = np.array(img)
            h, w = img.size
            alpha = Image.new("L", img.size, 0)
            draw = ImageDraw.Draw(alpha)
            draw.pieslice([0, 0, h, w], 0, 360, fill=255)
            npAlpha = np.array(alpha)
            npImage = np.dstack((npImage, npAlpha))
            edit_img_loc = "./DOWNLOADS" + "/" + userid + "/" + "circle.png"
            Image.fromarray(npImage).save(edit_img_loc)
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
        print("circle_with_bg-error - " + str(e))
        if "USER_IS_BLOCKED" in str(e):
            return
        try:
            await message.reply_to_message.reply_text(
                "sᴏᴍᴇᴛʜɪɴɢ ᴡᴇɴᴛ ᴡʀᴏɴɢ!", quote=True
            )
        except Exception:
            return


async def circle_without_bg(client, message):
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
            img = Image.open(a).convert("RGB")
            npImage = np.array(img)
            h, w = img.size
            alpha = Image.new("L", img.size, 0)
            draw = ImageDraw.Draw(alpha)
            draw.pieslice([0, 0, h, w], 0, 360, fill=255)
            npAlpha = np.array(alpha)
            npImage = np.dstack((npImage, npAlpha))
            edit_img_loc = "./DOWNLOADS" + "/" + userid + "/" + "circle.png"
            Image.fromarray(npImage).save(edit_img_loc)
            await message.reply_chat_action("upload_document")
            await message.reply_to_message.reply_document(edit_img_loc, quote=True)
            await msg.delete()
        else:
            await message.reply_text("ᴡʜʏ did ʏᴏᴜ ᴅᴇʟᴇᴛᴇ ᴛʜᴀᴛ??")
        try:
            shutil.rmtree(f"./DOWNLOADS/{userid}")
        except Exception:
            pass
    except Exception as e:
        print("circle_without_bg-error - " + str(e))
        if "USER_IS_BLOCKED" in str(e):
            return
        try:
            await message.reply_to_message.reply_text(
                "sᴏᴍᴇᴛʜɪɴɢ ᴡᴇɴᴛ ᴡʀᴏɴɢ!", quote=True
            )
        except Exception:
            return


async def sticker(client, message):
    try:
        userid = str(message.chat.id)
        if not os.path.isdir(f"./DOWNLOADS/{userid}"):
            os.makedirs(f"./DOWNLOADS/{userid}")
        download_location = "./DOWNLOADS" + "/" + userid + "/" + userid + ".jpg"
        edit_img_loc = "./DOWNLOADS" + "/" + userid + "/" + "sticker.webp"
        if not message.reply_to_message.empty:
            msg = await message.reply_to_message.reply_text(
                "ᴅᴏᴡɴʟᴏᴀᴅɪɴɢ ɪᴍᴀɢᴇ", quote=True
            )
            a = await client.download_media(
                message=message.reply_to_message, file_name=download_location
            )
            await msg.edit("ᴘʀᴏᴄᴇssɪɴɢ ɪᴍᴀɢᴇ...")
            os.rename(a, edit_img_loc)
            await message.reply_to_message.reply_sticker(edit_img_loc, quote=True)
            await msg.delete()
        else:
            await message.reply_text("ᴡʜʏ ᴅɪᴅ ʏᴏᴜ ᴅᴇʟᴇᴛᴇ ᴛʜᴀᴛ??")
        try:
            shutil.rmtree(f"./DOWNLOADS/{userid}")
        except Exception:
            pass
    except Exception as e:
        print("sticker-error - " + str(e))
        if "USER_IS_BLOCKED" in str(e):
            return
        try:
            await message.reply_to_message.reply_text(
                "sᴏᴍᴇᴛʜɪɴɢ ᴡᴇɴᴛ ᴡʀᴏɴɢ!", quote=True
            )
        except Exception:
            return


def add_corners(im, rad):
    circle = Image.new("L", (rad * 2, rad * 2), 0)
    draw = ImageDraw.Draw(circle)
    draw.ellipse((0, 0, rad * 2, rad * 2), fill=255)
    alpha = Image.new("L", im.size, 255)
    w, h = im.size
    alpha.paste(circle.crop((0, 0, rad, rad)), (0, 0))
    alpha.paste(circle.crop((0, rad, rad, rad * 2)), (0, h - rad))
    alpha.paste(circle.crop((rad, 0, rad * 2, rad)), (w - rad, 0))
    alpha.paste(circle.crop((rad, rad, rad * 2, rad * 2)), (w - rad, h - rad))
    im.putalpha(alpha)
    return im


async def edge_curved(client, message):
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
            im = Image.open(a)
            im = add_corners(im, 100)
            edit_img_loc = "./DOWNLOADS" + "/" + userid + "/" + "edge_curved.webp"
            im.save(edit_img_loc)
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
        print("edge_curved-error - " + str(e))
        if "USER_IS_BLOCKED" in str(e):
            return
        try:
            await message.reply_to_message.reply_text(
                "sᴏᴍᴇᴛʜɪɴɢ ᴡᴇɴᴛ ᴡʀᴏɴɢ!", quote=True
            )
        except Exception:
            return


async def contrast(client, message):
    try:
        userid = str(message.chat.id)
        if not os.path.isdir(f"./DOWNLOADS/{userid}"):
            os.makedirs(f"./DOWNLOADS/{userid}")
        download_location = "./DOWNLOADS" + "/" + userid + "/" + userid + ".jpg"
        if not message.reply_to_message.empty:
            msg = await message.reply_to_message.reply_text(
                "Downloading image", quote=True
            )
            a = await client.download_media(
                message=message.reply_to_message, file_name=download_location
            )
            await msg.edit("ᴘʀᴏᴄᴇssɪɴɢ ɪᴍᴀɢᴇ...")
            image = Image.open(a)
            contrast = ImageEnhance.Contrast(image)
            edit_img_loc = "./DOWNLOADS" + "/" + userid + "/" + "contrast.jpg"
            contrast.enhance(1.5).save(edit_img_loc)
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
        print("contrast-error - " + str(e))
        if "USER_IS_BLOCKED" in str(e):
            return
        try:
            await message.reply_to_message.reply_text(
                "sᴏᴍᴇᴛʜɪɴɢ ᴡᴇɴᴛ ᴡʀᴏɴɢ!", quote=True
            )
        except Exception:
            return


def sepia(img):
    width, height = img.size
    new_img = img.copy()
    for x in range(width):
        for y in range(height):
            red, green, blue = img.getpixel((x, y))
            new_val = 0.3 * red + 0.59 * green + 0.11 * blue
            new_red = int(new_val * 2)
            new_red = min(new_red, 255)
            new_green = int(new_val * 1.5)
            new_green = min(new_green, 255)
            new_blue = int(new_val)
            new_blue = min(new_blue, 255)

            new_img.putpixel((x, y), (new_red, new_green, new_blue))

    return new_img


async def sepia_mode(client, message):
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
            new_img = sepia(image)
            edit_img_loc = "./DOWNLOADS" + "/" + userid + "/" + "sepia.jpg"
            new_img.save(edit_img_loc)
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
        print("sepia_mode-error - " + str(e))
        if "USER_IS_BLOCKED" in str(e):
            return
        try:
            await message.reply_to_message.reply_text(
                "sᴏᴍᴇᴛʜɪɴɢ ᴡᴇɴᴛ ᴡʀᴏɴɢ!", quote=True
            )
        except Exception:
            return


def dodgeV2(x, y):
    return cv2.divide(x, 255 - y, scale=256)


async def pencil(client, message):
    try:
        userid = str(message.chat.id)
        if not os.path.isdir(f"./DOWNLOADS/{userid}"):
            os.makedirs(f"./DOWNLOADS/{userid}")
        download_location = "./DOWNLOADS" + "/" + userid + "/" + userid + ".jpg"
        edit_img_loc = "./DOWNLOADS" + "/" + userid + "/" + "pencil.jpg"
        if not message.reply_to_message.empty:
            msg = await message.reply_to_message.reply_text(
                "ᴅᴏᴡɴʟᴏᴀᴅɪɴɢ ɪᴍᴀɢᴇ", quote=True
            )
            a = await client.download_media(
                message=message.reply_to_message, file_name=download_location
            )
            await msg.edit("ᴘʀᴏᴄᴇssɪɴɢ ɪᴍᴀɢᴇ...")
            img = cv2.imread(a)
            img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            img_invert = cv2.bitwise_not(img_gray)
            img_smoothing = cv2.GaussianBlur(img_invert, (21, 21), sigmaX=0, sigmaY=0)
            final_img = dodgeV2(img_gray, img_smoothing)
            cv2.imwrite(edit_img_loc, final_img)
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
        print("pencil-error - " + str(e))
        if "USER_IS_BLOCKED" in str(e):
            return
        try:
            await message.reply_to_message.reply_text(
                "sᴏᴍᴇᴛʜɪɴɢ ᴡᴇɴᴛ ᴡʀᴏɴɢ!", quote=True
            )
        except Exception:
            return


def color_quantization(img, k):
    data = np.float32(img).reshape((-1, 3))
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 20, 1.0)
    _, label, center = cv2.kmeans(
        data, k, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS
    )
    center = np.uint8(center)
    result = center[label.flatten()]
    result = result.reshape(img.shape)
    return result


async def cartoon(client, message):
    try:
        userid = str(message.chat.id)
        if not os.path.isdir(f"./DOWNLOADS/{userid}"):
            os.makedirs(f"./DOWNLOADS/{userid}")
        download_location = "./DOWNLOADS" + "/" + userid + "/" + userid + ".jpg"
        edit_img_loc = "./DOWNLOADS" + "/" + userid + "/" + "kang.jpg"
        if not message.reply_to_message.empty:
            msg = await message.reply_to_message.reply_text(
                "ᴅᴏᴡɴʟᴏᴀᴅɪɴɢ ɪᴍᴀɢᴇ", quote=True
            )
            a = await client.download_media(
                message=message.reply_to_message, file_name=download_location
            )
            await msg.edit("ᴘʀᴏᴄᴇssɪɴɢ ɪᴍᴀɢᴇ...")
            img = cv2.imread(a)
            edges = cv2.Canny(img, 100, 200)
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            edges = cv2.adaptiveThreshold(
                gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 9, 5
            )
            color = cv2.bilateralFilter(img, d=9, sigmaColor=200, sigmaSpace=200)

            cv2.bitwise_and(color, color, mask=edges)
            img_1 = color_quantization(img, 7)
            cv2.imwrite(edit_img_loc, img_1)
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
        print("cartoon-error - " + str(e))
        if "USER_IS_BLOCKED" in str(e):
            return
        try:
            await message.reply_to_message.reply_text(
                "sᴏᴍᴇᴛʜɪɴɢ ᴡᴇɴᴛ ᴡʀᴏɴɢ!", quote=True
            )
        except Exception:
            return
