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


import asyncio
import os
import shutil


async def normalglitch_1(client, message):
    try:
        userid = str(message.chat.id)
        if not os.path.isdir(f"./DOWNLOADS/{userid}"):
            os.makedirs(f"./DOWNLOADS/{userid}")
        download_location = "./DOWNLOADS" + "/" + userid + "/" + userid + ".jpg"
        edit_img_loc = "./DOWNLOADS" + "/" + userid + "/" + "normalglitch_1.jpg"
        if not message.reply_to_message.empty:
            msg = await message.reply_to_message.reply_text(
                "ᴅᴏᴡɴʟᴏᴀᴅɪɴɢ ɪᴍᴀɢᴇ", quote=True
            )
            await client.download_media(
                message=message.reply_to_message, file_name=download_location
            )
            await msg.edit("ᴘʀᴏᴄᴇssɪɴɢ ɪᴍᴀɢᴇ.....")
            cd = ["glitch_this", "-c", "-o", edit_img_loc, download_location, "1"]
            process = await asyncio.create_subprocess_exec(
                *cd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
            )
            await process.communicate()
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
        print("normalglitch_1-error - " + str(e))
        if "USER_IS_BLOCKED" in str(e):
            return
        try:
            await message.reply_to_message.reply_text(
                "sᴏᴍᴇᴛʜɪɴɢ ᴡᴇɴᴛ ᴡʀᴏɴɢ!", quote=True
            )
        except Exception:
            return


async def normalglitch_2(client, message):
    try:
        userid = str(message.chat.id)
        if not os.path.isdir(f"./DOWNLOADS/{userid}"):
            os.makedirs(f"./DOWNLOADS/{userid}")
        download_location = "./DOWNLOADS" + "/" + userid + "/" + userid + ".jpg"
        edit_img_loc = "./DOWNLOADS" + "/" + userid + "/" + "normalglitch_2.jpg"
        if not message.reply_to_message.empty:
            msg = await message.reply_to_message.reply_text(
                "ᴅᴏᴡɴʟᴏᴀᴅɪɴɢ ɪᴍᴀɢᴇ", quote=True
            )
            await client.download_media(
                message=message.reply_to_message, file_name=download_location
            )
            await msg.edit("ᴘʀᴏᴄᴇssɪɴɢ ɪᴍᴀɢᴇ.....")
            cd = ["glitch_this", "-c", "-o", edit_img_loc, download_location, "2"]
            process = await asyncio.create_subprocess_exec(
                *cd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
            )
            await process.communicate()
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
        print("normalglitch_2-error - " + str(e))
        if "USER_IS_BLOCKED" in str(e):
            return
        try:
            await message.reply_to_message.reply_text(
                "sᴏᴍᴇᴛʜɪɴɢ ᴡᴇɴᴛ ᴡʀᴏɴɢ!", quote=True
            )
        except Exception:
            return


async def normalglitch_3(client, message):
    try:
        userid = str(message.chat.id)
        if not os.path.isdir(f"./DOWNLOADS/{userid}"):
            os.makedirs(f"./DOWNLOADS/{userid}")
        download_location = "./DOWNLOADS" + "/" + userid + "/" + userid + ".jpg"
        edit_img_loc = "./DOWNLOADS" + "/" + userid + "/" + "normalglitch_3.jpg"
        if not message.reply_to_message.empty:
            msg = await message.reply_to_message.reply_text(
                "ᴅᴏᴡɴʟᴏᴀᴅɪɴɢ ɪᴍᴀɢᴇ", quote=True
            )
            await client.download_media(
                message=message.reply_to_message, file_name=download_location
            )
            await msg.edit("ᴘʀᴏᴄᴇssɪɴɢ ɪᴍᴀɢᴇ.....")
            cd = ["glitch_this", "-c", "-o", edit_img_loc, download_location, "3"]
            process = await asyncio.create_subprocess_exec(
                *cd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
            )
            await process.communicate()
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
        print("normalglitch_3-error - " + str(e))
        if "USER_IS_BLOCKED" in str(e):
            return
        try:
            await message.reply_to_message.reply_text(
                "sᴏᴍᴇᴛʜɪɴɢ ᴡᴇɴᴛ ᴡʀᴏɴɢ!", quote=True
            )
        except Exception:
            return


async def normalglitch_4(client, message):
    try:
        userid = str(message.chat.id)
        if not os.path.isdir(f"./DOWNLOADS/{userid}"):
            os.makedirs(f"./DOWNLOADS/{userid}")
        download_location = "./DOWNLOADS" + "/" + userid + "/" + userid + ".jpg"
        edit_img_loc = "./DOWNLOADS" + "/" + userid + "/" + "normalglitch_4.jpg"
        if not message.reply_to_message.empty:
            msg = await message.reply_to_message.reply_text(
                "ᴅᴏᴡɴʟᴏᴀᴅɪɴɢ ɪᴍᴀɢᴇ", quote=True
            )
            await client.download_media(
                message=message.reply_to_message, file_name=download_location
            )
            await msg.edit("ᴘʀᴏᴄᴇssɪɴɢ ɪᴍᴀɢᴇ.....")
            cd = ["glitch_this", "-c", "-o", edit_img_loc, download_location, "4"]
            process = await asyncio.create_subprocess_exec(
                *cd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
            )
            await process.communicate()
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
        print("normalglitch_4-error - " + str(e))
        if "USER_IS_BLOCKED" in str(e):
            return
        try:
            await message.reply_to_message.reply_text(
                "sᴏᴍᴇᴛʜɪɴɢ ᴡᴇɴᴛ ᴡʀᴏɴɢ!", quote=True
            )
        except Exception:
            return


async def normalglitch_5(client, message):
    try:
        userid = str(message.chat.id)
        if not os.path.isdir(f"./DOWNLOADS/{userid}"):
            os.makedirs(f"./DOWNLOADS/{userid}")
        download_location = "./DOWNLOADS" + "/" + userid + "/" + userid + ".jpg"
        edit_img_loc = "./DOWNLOADS" + "/" + userid + "/" + "normalglitch_5.jpg"
        if not message.reply_to_message.empty:
            msg = await message.reply_to_message.reply_text(
                "ᴅᴏᴡɴʟᴏᴀᴅɪɴɢ ɪᴍᴀɢᴇ", quote=True
            )
            await client.download_media(
                message=message.reply_to_message, file_name=download_location
            )
            await msg.edit("ᴘʀᴏᴄᴇssɪɴɢ ɪᴍᴀɢᴇ.....")
            cd = ["glitch_this", "-c", "-o", edit_img_loc, download_location, "5"]
            process = await asyncio.create_subprocess_exec(
                *cd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
            )
            await process.communicate()
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
        print("normalglitch_5-error - " + str(e))
        if "USER_IS_BLOCKED" in str(e):
            return
        try:
            await message.reply_to_message.reply_text(
                "sᴏᴍᴇᴛʜɪɴɢ ᴡᴇɴᴛ ᴡʀᴏɴɢ!", quote=True
            )
        except Exception:
            return


async def scanlineglitch_1(client, message):
    try:
        userid = str(message.chat.id)
        if not os.path.isdir(f"./DOWNLOADS/{userid}"):
            os.makedirs(f"./DOWNLOADS/{userid}")
        download_location = "./DOWNLOADS" + "/" + userid + "/" + userid + ".jpg"
        edit_img_loc = "./DOWNLOADS" + "/" + userid + "/" + "scanlineglitch_1.jpg"
        if not message.reply_to_message.empty:
            msg = await message.reply_to_message.reply_text(
                "ᴅᴏᴡɴʟᴏᴀᴅɪɴɢ ɪᴍᴀɢᴇ", quote=True
            )
            await client.download_media(
                message=message.reply_to_message, file_name=download_location
            )
            await msg.edit("ᴘʀᴏᴄᴇssɪɴɢ ɪᴍᴀɢᴇ.....")
            cd = ["glitch_this", "-c", "-s", "-o", edit_img_loc, download_location, "1"]
            process = await asyncio.create_subprocess_exec(
                *cd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
            )
            await process.communicate()
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
        print("scanlineglitch_1-error - " + str(e))
        if "USER_IS_BLOCKED" in str(e):
            return
        try:
            await message.reply_to_message.reply_text(
                "sᴏᴍᴇᴛʜɪɴɢ ᴡᴇɴᴛ ᴡʀᴏɴɢ!", quote=True
            )
        except Exception:
            return


async def scanlineglitch_2(client, message):
    try:
        userid = str(message.chat.id)
        if not os.path.isdir(f"./DOWNLOADS/{userid}"):
            os.makedirs(f"./DOWNLOADS/{userid}")
        download_location = "./DOWNLOADS" + "/" + userid + "/" + userid + ".jpg"
        edit_img_loc = "./DOWNLOADS" + "/" + userid + "/" + "scanlineglitch_2.jpg"
        if not message.reply_to_message.empty:
            msg = await message.reply_to_message.reply_text(
                "Downloading image", quote=True
            )
            await client.download_media(
                message=message.reply_to_message, file_name=download_location
            )
            await msg.edit("ᴘʀᴏᴄᴇssɪɴɢ ɪᴍᴀɢᴇ.....")
            cd = ["glitch_this", "-c", "-s", "-o", edit_img_loc, download_location, "2"]
            process = await asyncio.create_subprocess_exec(
                *cd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
            )
            await process.communicate()
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
        print("scanlineglitch_2-error - " + str(e))
        if "USER_IS_BLOCKED" in str(e):
            return
        try:
            await message.reply_to_message.reply_text(
                "sᴏᴍᴇᴛʜɪɴɢ ᴡᴇɴᴛ ᴡʀᴏɴɢ!", quote=True
            )
        except Exception:
            return


async def scanlineglitch_3(client, message):
    try:
        userid = str(message.chat.id)
        if not os.path.isdir(f"./DOWNLOADS/{userid}"):
            os.makedirs(f"./DOWNLOADS/{userid}")
        download_location = "./DOWNLOADS" + "/" + userid + "/" + userid + ".jpg"
        edit_img_loc = "./DOWNLOADS" + "/" + userid + "/" + "scanlineglitch_3.jpg"
        if not message.reply_to_message.empty:
            msg = await message.reply_to_message.reply_text(
                "ᴅᴏᴡɴʟᴏᴀᴅɪɴɢ ɪᴍᴀɢᴇ", quote=True
            )
            await client.download_media(
                message=message.reply_to_message, file_name=download_location
            )
            await msg.edit("ᴘʀᴏᴄᴇssɪɴɢ ɪᴍᴀɢᴇ.....")
            cd = ["glitch_this", "-c", "-s", "-o", edit_img_loc, download_location, "3"]
            process = await asyncio.create_subprocess_exec(
                *cd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
            )
            await process.communicate()
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
        print("scanlineglitch_3-error - " + str(e))
        if "USER_IS_BLOCKED" in str(e):
            return
        try:
            await message.reply_to_message.reply_text(
                "sᴏᴍᴇᴛʜɪɴɢ ᴡᴇɴᴛ ᴡʀᴏɴɢ!", quote=True
            )
        except Exception:
            return


async def scanlineglitch_4(client, message):
    try:
        userid = str(message.chat.id)
        if not os.path.isdir(f"./DOWNLOADS/{userid}"):
            os.makedirs(f"./DOWNLOADS/{userid}")
        download_location = "./DOWNLOADS" + "/" + userid + "/" + userid + ".jpg"
        edit_img_loc = "./DOWNLOADS" + "/" + userid + "/" + "scanlineglitch_4.jpg"
        if not message.reply_to_message.empty:
            msg = await message.reply_to_message.reply_text(
                "ᴅᴏᴡɴʟᴏᴀᴅɪɴɢ ɪᴍᴀɢᴇ", quote=True
            )
            await client.download_media(
                message=message.reply_to_message, file_name=download_location
            )
            await msg.edit("ᴘʀᴏᴄᴇssɪɴɢ ɪᴍᴀɢᴇ.....")
            cd = ["glitch_this", "-c", "-s", "-o", edit_img_loc, download_location, "4"]
            process = await asyncio.create_subprocess_exec(
                *cd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
            )
            await process.communicate()
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
        print("scanlineglitch_4-error - " + str(e))
        if "USER_IS_BLOCKED" in str(e):
            return
        try:
            await message.reply_to_message.reply_text(
                "sᴏᴍᴇᴛʜɪɴɢ ᴡᴇɴᴛ ᴡʀᴏɴɢ!", quote=True
            )
        except Exception:
            return


async def scanlineglitch_5(client, message):
    try:
        userid = str(message.chat.id)
        if not os.path.isdir(f"./DOWNLOADS/{userid}"):
            os.makedirs(f"./DOWNLOADS/{userid}")
        download_location = "./DOWNLOADS" + "/" + userid + "/" + userid + ".jpg"
        edit_img_loc = "./DOWNLOADS" + "/" + userid + "/" + "scanlineglitch_5.jpg"
        if not message.reply_to_message.empty:
            msg = await message.reply_to_message.reply_text(
                "ᴅᴏᴡɴʟᴏᴀᴅɪɴɢ ɪᴍᴀɢᴇ", quote=True
            )
            await client.download_media(
                message=message.reply_to_message, file_name=download_location
            )
            await msg.edit("ᴘʀᴏᴄᴇssɪɴɢ ɪᴍᴀɢᴇ.....")
            cd = ["glitch_this", "-c", "-s", "-o", edit_img_loc, download_location, "5"]
            process = await asyncio.create_subprocess_exec(
                *cd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
            )
            await process.communicate()
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
        print("scanlineglitch_5-error - " + str(e))
        if "USER_IS_BLOCKED" in str(e):
            return
        try:
            await message.reply_to_message.reply_text(
                "sᴏᴍᴇᴛʜɪɴɢ ᴡᴇɴᴛ ᴡʀᴏɴɢ!", quote=True
            )
        except Exception:
            return
