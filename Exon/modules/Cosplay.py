# If you want to either add or remove a image, please contact us at https://t.me/tyranteyeeee

import requests

from pyrogram import filters

from pyrogram.types import Message

from Shikimori import pbot

@pbot.on_message(filters.command('cosplay'))

async def cosplay(_, message:Message):

    r = requests.get("https://sugoi-api.vercel.app/cosplay")

    if r.status_code == 200:

        data = r.json()['url']

        return await message.reply_photo(photo=data)

    elif r.status_code == 429:

        return await message.reply_text("Error: Too many requests. Please wait a few moments.")

    elif r.status_code >= 500:

        return await message.reply_text("Error: API server error. Contact us at @tyranteyeeee.")

    else:

        return await message.reply_text("Error: Unknown Error Occurred. Contact us at @tyranteyeeee.")

  

@pbot.on_message(filters.command('ncosplay'))

async def ncosplay(_, message:Message):

    r = requests.get("https://sugoi-api.vercel.app/ncosplay")

    if r.status_code == 200:

        data = r.json()['url']

        return await message.reply_photo(photo=data)

    elif r.status_code == 429:

        return await message.reply_text("Error: Too many requests. Please wait a few moments.")

    elif r.status_code >= 500:

        return await message.reply_text("Error: API server error. Contact us at @tyranteyeeee.")

    else:

        return await message.reply_text("Error: Unknown Error Occurred. Contact us at @tyranteyeeee.")
