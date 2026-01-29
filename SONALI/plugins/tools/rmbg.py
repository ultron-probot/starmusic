import os
import requests

from pyrogram import Client, filters
from pyrogram.types import Message

from config import REMOVE_BG_API_KEY
from SONALI.utils.decorators.language import language


print("🔥 rmbg plugin loaded")


@Client.on_message(filters.command(["rmbg"]) & filters.reply)
@language
async def rmbg_command(client: Client, message: Message, _):
    reply = message.reply_to_message

    if not reply or not reply.photo:
        await message.reply_text("❌ Kisi photo pe reply karo.")
        return

    if not REMOVE_BG_API_KEY:
        await message.reply_text("❌ API key missing.")
        return

    await message.reply_text("🧠 Background remove ho raha hai...")

    input_file = f"rmbg_{message.id}.png"
    output_file = f"rmbg_out_{message.id}.png"

    await reply.download(input_file)

    try:
        response = requests.post(
            "https://api.remove.bg/v1.0/removebg",
            files={"image_file": open(input_file, "rb")},
            data={"size": "auto"},
            headers={"X-Api-Key": REMOVE_BG_API_KEY},
            timeout=60,
        )

        if response.status_code != 200:
            await message.reply_text("❌ Remove.bg API error.")
            return

        with open(output_file, "wb") as f:
            f.write(response.content)

        await message.reply_photo(output_file, caption="✅ Background removed")

    except Exception as e:
        await message.reply_text(f"❌ Error: {e}")

    finally:
        for f in (input_file, output_file):
            if os.path.exists(f):
                os.remove(f)
