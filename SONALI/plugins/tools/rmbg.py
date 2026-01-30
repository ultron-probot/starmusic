import os
import aiohttp

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
)
async def rmbg_command(bot, message):
    # ===== reply check =====
    if not message.reply_to_message:
        return await message.reply_text("❌ Kisi photo pe reply karke command use karo.")

    reply = message.reply_to_message

    # ===== media check =====
    if not (reply.photo or reply.document):
        return await message.reply_text("❌ Sirf image photo/document pe reply karo.")

    if not REMOVE_BG_API_KEY:
        return await message.reply_text("❌ Remove.bg API key missing.")

    await bot.send_chat_action(message.chat.id, ChatAction.UPLOAD_PHOTO)
    status = await message.reply_text("🧠 Background remove ho raha hai...")

    # ===== filename handling =====
    if reply.document and reply.document.file_name:
        original_name, ext = os.path.splitext(reply.document.file_name)
        ext = ext.lstrip(".") or "png"
    else:
        # Photo has NO filename in Pyrogram
        original_name = "image"
        ext = "png"

    input_file = f"rmbg_input_{message.id}.{ext}"
    output_file = f"{original_name}_nobg.{ext}"

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
                        return await status.edit(
                            "❌ Background remove nahi ho paya.\n"
                            "⚠️ API error / limit ho sakta hai."
                        )

                    content = await resp.read()

        with open(output_file, "wb") as f:
            f.write(content)

        await message.reply_document(
            output_file,
            caption=f"✅ Background removed\n📁 `{output_file}`"
        )
        await status.delete()

    except Exception as e:
        await status.edit("❌ Image process karte waqt error aaya.")

    finally:
        for f in (input_file, output_file):
            if os.path.exists(f):
                os.remove(f)
