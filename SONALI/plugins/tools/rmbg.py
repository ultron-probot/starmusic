import os
import aiohttp
import traceback

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
        return await message.reply_text(
            "❌ Kisi photo pe reply karke `/rmbg` use karo."
        )

    reply = message.reply_to_message

    # ===== media check =====
    if not (reply.photo or reply.document):
        return await message.reply_text(
            "❌ Sirf image photo ya document pe reply karo."
        )

    if not REMOVE_BG_API_KEY:
        return await message.reply_text("❌ Remove.bg API key missing.")

    try:
        await bot.send_chat_action(message.chat.id, ChatAction.UPLOAD_PHOTO)
    except Exception:
        pass

    status = await message.reply_text("🧠 Background remove ho raha hai...")

    # ===== filename handling =====
    if reply.document and reply.document.file_name:
        base_name = os.path.splitext(reply.document.file_name)[0]
    else:
        base_name = "image"

    input_file = f"rmbg_input_{message.id}.png"
    output_file = f"{base_name}_nobg.png"

    try:
        # Download image
        await reply.download(input_file)

        # Call remove.bg API
        async with aiohttp.ClientSession() as session:
            with open(input_file, "rb") as img:
                form = aiohttp.FormData()
                form.add_field(
                    "image_file",
                    img,
                    filename="image.png",
                    content_type="image/png",
                )
                form.add_field("size", "auto")

                async with session.post(
                    "https://api.remove.bg/v1.0/removebg",
                    data=form,
                    headers={"X-Api-Key": REMOVE_BG_API_KEY},
                    timeout=aiohttp.ClientTimeout(total=90),
                ) as resp:

                    if resp.status != 200:
                        text = await resp.text()
                        await status.edit(
                            f"❌ Remove.bg API error\n"
                            f"Status: `{resp.status}`"
                        )
                        print("RMBG API ERROR:", resp.status, text)
                        return

                    content = await resp.read()

        if not content:
            await status.edit("❌ Remove.bg ne empty response diya.")
            return

        with open(output_file, "wb") as f:
            f.write(content)

        await message.reply_document(
            output_file,
            caption=f"✅ Background removed\n📁 `{output_file}`",
        )
        await status.delete()

    except Exception as e:
        # 🔥 REAL ERROR OUTPUT
        err = "".join(traceback.format_exception_only(type(e), e)).strip()
        print("RMBG ERROR:", err)

        await status.edit(
            "❌ RMBG Error aaya:\n"
            f"`{err}`"
        )

    finally:
        for f in (input_file, output_file):
            if os.path.exists(f):
                try:
                    os.remove(f)
                except Exception:
                    pass
