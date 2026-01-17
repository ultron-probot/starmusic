import os
import re
import random
import math
import aiohttp
import aiofiles
from SONALI import app
from config import YOUTUBE_IMG_URL
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
from py_yt import VideosSearch

def clear(text):
    return re.sub("\s+", " ", text).strip()

async def get_thumb(videoid):
    if os.path.isfile(f"cache/{videoid}.png"):
        return f"cache/{videoid}.png"

    url = f"https://www.youtube.com/watch?v={videoid}"
    try:
        results = VideosSearch(url, limit=1)
        for result in (await results.next())["result"]:
            try:
                title = result["title"]
                title = re.sub("\W+", " ", title)
            except:
                title = "Unsupported Title"

            try:
                duration = result["duration"]
            except:
                duration = "Unknown"

            thumbnail = result["thumbnails"][0]["url"].split("?")[0]

            try:
                views = result["viewCount"]["short"]
            except:
                views = "Unknown"

            try:
                channel = result["channel"]["name"]
            except:
                channel = "Unknown Channel"

        # -------- DOWNLOAD YT THUMB --------
        async with aiohttp.ClientSession() as session:
            async with session.get(thumbnail) as resp:
                if resp.status == 200:
                    async with aiofiles.open(f"cache/thumb{videoid}.png", mode="wb") as f:
                        await f.write(await resp.read())

        youtube = Image.open(f"cache/thumb{videoid}.png").convert("RGBA")

        # ============ BACKGROUND ============
        background = youtube.resize((1280, 720)).filter(ImageFilter.GaussianBlur(radius=18))
        enhancer = ImageEnhance.Brightness(background)
        background = enhancer.enhance(0.45)
        draw = ImageDraw.Draw(background)

        # ---- WHITE SPRINKLE ----
        for _ in range(260):
            x = random.randint(0, 1280)
            y = random.randint(0, 720)
            r = random.randint(1, 3)
            draw.ellipse((x, y, x+r, y+r), fill="white")

        # ---- MUSIC NOTE SPRINKLE BACKGROUND ----
        music_font = ImageFont.truetype("SONALI/assets/font.ttf", 28)
        for _ in range(18):
            x = random.randint(100, 1180)
            y = random.randint(40, 500)
            draw.text((x, y), "♪", fill="white", font=music_font)

        # ============ DIAMONDS (UP SHIFT) ============
        diamond = Image.new("RGBA", (260, 260), (255,255,255,0))
        ddraw = ImageDraw.Draw(diamond)

        ddraw.polygon(
            [(130,0),(260,130),(130,260),(0,130)],
            outline="white",
            width=6
        )

        try:
            note_img = Image.open("SONALI/assets/diamond_note.png").convert("RGBA")
            note_img = note_img.resize((110, 110))
            diamond.paste(note_img, (75, 75), note_img)
        except Exception as e:
            print("diamond_note.png load error:", e)

        # MOVE DIAMONDS UP
        background.paste(diamond, (40, 70), diamond)
        background.paste(diamond, (980, 70), diamond)

        # ============ CENTER CIRCLE (SMALLER + UP) ============
        CIRCLE_SIZE = 380
        yt_thumb = youtube.resize((CIRCLE_SIZE, CIRCLE_SIZE))

        mask = Image.new("L", (CIRCLE_SIZE, CIRCLE_SIZE), 0)
        mdraw = ImageDraw.Draw(mask)
        mdraw.ellipse((0,0,CIRCLE_SIZE,CIRCLE_SIZE), fill=255)

        circ = Image.new("RGBA", (CIRCLE_SIZE, CIRCLE_SIZE))
        circ.paste(yt_thumb, (0,0), mask)

        # ============ MULTI-LAYER CIRCLES + SPIKES ============
        RING_PADDING = 45
        ring_size = CIRCLE_SIZE + (RING_PADDING * 2)

        ring = Image.new("RGBA", (ring_size, ring_size), (0,0,0,0))
        rdraw = ImageDraw.Draw(ring)

        # 3 LAYER CIRCLES
        rdraw.ellipse((10,10,ring_size-10,ring_size-10), outline="white", width=5)
        rdraw.ellipse((35,35,ring_size-35,ring_size-35), outline="white", width=3)
        rdraw.ellipse((60,60,ring_size-60,ring_size-60), outline="white", width=2)

        center = ring_size // 2
        radius = (ring_size // 2) - 12

        # DENSER + THICKER SPIKES
        for angle in range(0, 360, 5):
            rad = math.radians(angle)
            x1 = center + int(radius * math.cos(rad))
            y1 = center + int(radius * math.sin(rad))
            spike_length = random.randint(18, 65)
            x2 = center + int((radius + spike_length) * math.cos(rad))
            y2 = center + int((radius + spike_length) * math.sin(rad))
            rdraw.line([(x1, y1), (x2, y2)], fill="white", width=5)

        # MOVE CIRCLE UP
        ring_x = 360
        ring_y = -10
        circle_x = ring_x + RING_PADDING
        circle_y = ring_y + RING_PADDING

        background.paste(ring, (ring_x, ring_y), ring)
        background.paste(circ, (circle_x, circle_y), circ)

        # ============ FONTS ============
        arial = ImageFont.truetype("SONALI/assets/font2.ttf", 26)
        font = ImageFont.truetype("SONALI/assets/font.ttf", 28)
        bold_font = ImageFont.truetype("SONALI/assets/font.ttf", 30)
        small_neon = ImageFont.truetype("SONALI/assets/font.ttf", 20)

        # DejaVu for buttons
        icon_font = ImageFont.truetype("SONALI/assets/DejaVuSans.ttf", 42)

        # WATERMARK
        text_size = draw.textsize("@Starmusic by devil", font=font)
        draw.text(
            (1280 - text_size[0] - 10, 10),
            "@Starmusic by devil",
            fill="yellow",
            font=font,
        )

        draw.text((980, 40), "Credit", fill="cyan", font=small_neon)
        draw.text((980, 65), "@Ankitgupta21444", fill="white", font=small_neon)

        # CHANNEL + VIEWS (GREEN)
        draw.text(
            (55, 520),
            f"{channel} | {views[:23]}",
            fill=(0, 255, 0),
            font=arial,
        )

        # TITLE (CENTER UNDER CIRCLE)
        tw, _ = draw.textsize(title, font=font)
        draw.text(
            ((1280 - tw)//2, 560),
            title,
            fill="cyan",
            font=font,
        )

        # ===== MEDIUM WHITE CENTER TIMELINE =====
        timeline = "❍━━━ლ━━━❍"
        tw, _ = draw.textsize(timeline, font=bold_font)
        draw.text(((1280-tw)//2, 600), timeline, fill="white", font=bold_font)

        # ===== PLAYER CONTROLS (NO IMAGE) =====
        controls = "🔀   ⏮   ▶️   ⏭   🔁"
        cw, _ = draw.textsize(controls, font=icon_font)
        draw.text(((1280-cw)//2, 645), controls, fill="white", font=icon_font)

        try:
            os.remove(f"cache/thumb{videoid}.png")
        except:
            pass

        background.save(f"cache/{videoid}.png")
        return f"cache/{videoid}.png"

    except Exception as e:
        print(e)
        return YOUTUBE_IMG_URL
