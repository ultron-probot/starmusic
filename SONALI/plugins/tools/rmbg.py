import os
import requests

from pyrogram import Client, filters
from pyrogram.types import Message

from config import REMOVE_BG_API_KEY


@Client.on_message(filters.command("rmbg") & filters.reply)
async def remove_bg(client: Client, message: Message):
    reply = message.reply_to_message

    # ✅ Check: reply me photo hai ya nahi
    if not reply.photo:
        await message.reply_text("🙂‍↔️Umhu.. Kisi photo pe reply karo.")
        return

    if not REMOVE_BG_API_KEY:
        await message.reply_text("Some Internal problem baby Meet him to solve @Ankitgupta21444.")
        return

    await message.reply_text(" Background remove ho raha hai, wait karo...")

    # Temporary file names
    input_file = f"input_{message.id}.png"
    output_file = f"output_{message.id}.png"

    # 📥 Download image
    await reply.download(input_file)

    try:
        # 🌐 API request
        response = requests.post(
            "https://api.remove.bg/v1.0/removebg",
            files={"image_file": open(input_file, "rb")},
            data={"size": "auto"},
            headers={"X-Api-Key": REMOVE_BG_API_KEY},
            timeout=60
        )

        if response.status_code != 200:
            await message.reply_text("Shitt.. Background remove failed.")
            return

        # 📤 Save output image
        with open(output_file, "wb") as f:
            f.write(response.content)

        # 📤 Send result
        await message.reply_photo(
            photo=output_file,
            caption="✅ Background removed successfully"
        )

    except Exception as e:
        await message.reply_text(f" Error: {e}")

    finally:
        # 🧹 Cleanup
        if os.path.exists(input_file):
            os.remove(input_file)
        if os.path.exists(output_file):
            os.remove(output_file)
