import os
import aiohttp

from pyrogram import Client, filters
from pyrogram.types import Message

from config import REMOVE_BG_API_KEY
from SONALI.utils.decorators.language import language

print("🔥 RMBG tool loaded")


@Client.on_message(filters.command("rmbg") & filters.reply)
@language
async def rmbg_command(client: Client, message: Message, _):
    reply = message.reply_to_message

    if not reply or not reply.photo:
        await message.reply_text("❌ Kisi photo pe reply karo.")
        return

    if not REMOVE_BG_API_KEY:
        await message.reply_text("❌ Remove.bg API key missing.")
        return

    status = await message.reply_text("🧠 Background remove ho raha hai...")

    input_file = f"rmbg_{message.id}.png"
    output_file = f"rmbg_out_{message.id}.png"

    try:
        await reply.download(input_file)

        async with aiohttp.ClientSession() as session:
            with open(input_file, "rb") as img:
                form = aiohttp.FormData()
                form.add_field("image_file", img)
                form.add_field("size", "auto")

                async with session.post(
                    "https://api.remove.bg/v1.0/removebg",
                    data=form,
                    headers={"X-Api-Key": REMOVE_BG_API_KEY},
                    timeout=aiohttp.ClientTimeout(total=60),
                ) as resp:

                    if resp.status != 200:
                        await status.edit("❌ Remove.bg API error.")
                        return

                    result = await resp.read()

        with open(output_file, "wb") as f:
            f.write(result)

        await message.reply_photo(
            output_file,
            caption="✅ Background removed"
        )

        await status.delete()

    except Exception:
        await status.edit("❌ Image process karte waqt error aaya.")

    finally:
        for file in (input_file, output_file):
            if os.path.exists(file):
                os.remove(file)
