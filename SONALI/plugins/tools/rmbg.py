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

    if not message.reply_to_message:
        return await message.reply_text("❌ Kisi photo pe reply karke command use karo.")

    reply = message.reply_to_message

    if not (reply.photo or reply.document):
        return await message.reply_text("❌ Sirf image photo/document pe reply karo.")

    if not REMOVE_BG_API_KEY:
        return await message.reply_text("❌ Remove.bg API key missing.")

    await bot.send_chat_action(message.chat.id, ChatAction.UPLOAD_PHOTO)
    status = await message.reply_text("🧠 Background remove ho raha hai...")

    # ===== filename =====
    if reply.document and reply.document.file_name:
        base_name = os.path.splitext(reply.document.file_name)[0]
    else:
        base_name = "image"

    input_file = f"rmbg_input_{message.id}.png"
    output_file = f"{base_name}_nobg.png"

    try:
        await reply.download(input_file)

        async with aiohttp.ClientSession() as session:
            with open(input_file, "rb") as img:
                form = aiohttp.FormData()
                form.add_field(
                    "image_file",
                    img,
                    filename="image.png",
                    content_type="image/png"
                )
                form.add_field("size", "auto")

                async with session.post(
                    "https://api.remove.bg/v1.0/removebg",
                    data=form,
                    headers={"X-Api-Key": REMOVE_BG_API_KEY},
                    timeout=aiohttp.ClientTimeout(total=60),
                ) as resp:

                    if resp.status != 200:
                        error_text = await resp.text()
                        return await status.edit(
                            f"❌ Remove.bg API error ({resp.status})"
                        )

                    content = await resp.read()

        if not content:
            return await status.edit("❌ Empty response from Remove.bg.")

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
