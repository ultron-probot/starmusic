import os
import aiohttp
import mimetypes

from SONALI import app
from config import REMOVE_BG_API_KEY
from pyrogram import filters
from pyrogram.enums import ChatAction


print("🔥 RMBG tool loaded")


@app.on_message(
    filters.command(
        ["rmbg", "removebg"],
        prefixes=["+", ".", "/", "-", "", "$", "#", "&"]
    )
    & filters.reply
)
async def rmbg_command(bot, message):
    reply = message.reply_to_message

    if not reply or not reply.photo:
        return await message.reply_text("❌ Kisi photo pe reply karo.")

    if not REMOVE_BG_API_KEY:
        return await message.reply_text("❌ Remove.bg API key missing.")

    await bot.send_chat_action(message.chat.id, ChatAction.UPLOAD_PHOTO)
    status = await message.reply_text("🧠 Background remove ho raha hai...")

    # ===== filename handling =====
    original_name = "image"
    ext = "png"

    if reply.photo.file_name:
        original_name, ext = os.path.splitext(reply.photo.file_name)
        ext = ext.replace(".", "") or "png"

    input_file = f"rmbg_input_{message.id}.{ext}"
    output_file = f"{original_name}_nobg.{ext}"

    try:
        await reply.download(input_file)

        success = False

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

                    if resp.status == 200:
                        content = await resp.read()
                        with open(output_file, "wb") as f:
                            f.write(content)
                        success = True

        # ===== FALLBACK MESSAGE =====
        if not success:
            return await status.edit(
                "❌ Background remove nahi ho paya.\n"
                "⚠️ API limit / error ho sakta hai."
            )

        await message.reply_document(
            output_file,
            caption=f"✅ Background removed\n📁 `{output_file}`"
        )
        await status.delete()

    except Exception:
        await status.edit("❌ Image process karte waqt error aaya.")

    finally:
        for f in (input_file, output_file):
            if os.path.exists(f):
                os.remove(f)
