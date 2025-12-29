from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from SONALI import app

start_txt = """
✰ 𝗪ᴇʟᴄᴏᴍᴇ ✰
 
✰ 𝗥ᴇᴘᴏ ᴛᴏ 𝗡ʜɪ 𝗠ɪʟᴇɢᴀ 𝗬ʜᴀ
 
✰ 𝗣ᴀʜʟᴇ 𝗣ᴀᴘᴀ 𝗕ᴏʟ 𝗥ᴇᴘᴏ 𝗢ᴡɴᴇʀ ᴋᴏ 

✰ || @Ankitgupta21444 ||
 
✰ 𝗥ᴜɴ 24x7 𝗟ᴀɢ 𝗙ʀᴇᴇ 𝗪ɪᴛʜᴏᴜᴛ 𝗦ᴛᴏᴘ
 
"""

@app.on_message(filters.command("repo"))
async def start(_, msg):
    buttons = [
        [ 
          InlineKeyboardButton("𝗔ᴅᴅ ᴍᴇ 𝗠ᴀʙʏ", url=f"https://t.me/{app.username}?startgroup=true")
        ],
        [
          InlineKeyboardButton("𝗛ᴇʟᴘ", url="https://t.me/Ankitgupta21444"),
          InlineKeyboardButton("⍣ ፝֠֩ᴅᴇᴠɪʟ", url="https://t.me/Ankitgupta21444"),
          ],
               [
                InlineKeyboardButton("𝗕ᴏᴛs", url=f"https://t.me/A2globalupdate"),
],
[
InlineKeyboardButton("𝗠ᴀɪɴ", url=f"https://t.me/Ankitgupta21444"),

        ]]
    
    reply_markup = InlineKeyboardMarkup(buttons)
    
    await msg.reply_photo(
        photo="https://files.catbox.moe/o3djim.jpg",
        caption=start_txt,
        reply_markup=reply_markup
    )
