import aiohttp
import io
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

    # ===== Reply check =====
    if not message.reply_to_message:
        return await message.reply_text(
            "❌ Kisi photo pe reply karke `/rmbg` use karo."
        )

    reply = message.reply_to_message

    # ===== Media check =====
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

    try:
        # 🔥 Download image in memory (bytes)
        image_bytes = await reply.download(in_memory=True)

        if not image_bytes:
            return await status.edit("❌ Image download failed.")

        # Filename handling
        if reply.document and reply.document.file_name:
            base_name = reply.document.file_name.rsplit(".", 1)[0]
        else:
            base_name = "image"

        output_filename = f"{base_name}_nobg.png"

        # 🔥 Send image bytes to remove.bg
        async with aiohttp.ClientSession() as session:
            form = aiohttp.FormData()
            form.add_field(
                "image_file",
                image_bytes,
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
                    print("RMBG API ERROR:", resp.status, text)
                    return await status.edit(
                        f"❌ Remove.bg API error\nStatus: `{resp.status}`"
                    )

                result_bytes = await resp.read()

        if not result_bytes:
            return await status.edit("❌ Empty response from Remove.bg.")

        # 🔥 Send result back to chat (no InputFile)
        await message.reply_document(
            document=io.BytesIO(result_bytes),
            file_name=output_filename,
            caption=f"✅ Background removed\n📁 `{output_filename}`"
        )
        await status.delete()

    except Exception as e:
        err = "".join(traceback.format_exception_only(type(e), e)).strip()
        print("RMBG ERROR:", err)
        await status.edit(
            "❌ RMBG Error aaya:\n"
            f"`{err}`"
        )
