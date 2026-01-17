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

def short_title(title):
    words = title.split()
    return " ".join(words[:5]) + ("..." if len(words) > 5 else "")

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
                title = short_title(title)
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

        for _ in range(240):
            x = random.randint(0, 1280)
            y = random.randint(0, 720)
            r = random.randint(1, 3)
            draw.ellipse((x, y, x+r, y+r), fill="white")

        music_font = ImageFont.truetype("SONALI/assets/font.ttf", 28)
        for _ in range(18):
            x = random.randint(100, 1180)
            y = random.randint(60, 580)
            draw.text((x, y), "♪", fill="white", font=music_font)

        # ============ DOUBLE LINE DIAMONDS ============
        diamond = Image.new("RGBA", (260, 260), (255,255,255,0))
        ddraw = ImageDraw.Draw(diamond)

        ddraw.polygon(
            [(130,0),(260,130),(130,260),(0,130)],
            outline="orange",
            width=4
        )

        ddraw.polygon(
            [(130,10),(250,130),(130,250),(10,130)],
            outline="lime",
            width=4
        )

        try:
            note_img = Image.open("SONALI/assets/diamond_note.png").convert("RGBA")
            note_img = note_img.resize((110, 110))
            diamond.paste(note_img, (75, 75), note_img)
        except Exception as e:
            print("diamond_note.png load error:", e)

        background.paste(diamond, (20, 160), diamond)
        background.paste(diamond, (1000, 160), diamond)

        # ============ CENTER CIRCLE ============
        CIRCLE_SIZE = 420
        yt_thumb = youtube.resize((CIRCLE_SIZE, CIRCLE_SIZE))

        mask = Image.new("L", (CIRCLE_SIZE, CIRCLE_SIZE), 0)
        mdraw = ImageDraw.Draw(mask)
        mdraw.ellipse((0,0,CIRCLE_SIZE,CIRCLE_SIZE), fill=255)

        circ = Image.new("RGBA", (CIRCLE_SIZE, CIRCLE_SIZE))
        circ.paste(yt_thumb, (0,0), mask)

        RING_PADDING = 45
        ring_size = CIRCLE_SIZE + (RING_PADDING * 2)

        ring = Image.new("RGBA", (ring_size, ring_size), (0,0,0,0))
        rdraw = ImageDraw.Draw(ring)

        rdraw.ellipse(
            (10, 10, ring_size-10, ring_size-10),
            outline="white",
            width=5
        )

        center = ring_size // 2
        radius = (ring_size // 2) - 12

        for angle in range(0, 360, 6):
            rad = math.radians(angle)
            x1 = center + int(radius * math.cos(rad))
            y1 = center + int(radius * math.sin(rad))
            spike_length = random.randint(12, 55)
            x2 = center + int((radius + spike_length) * math.cos(rad))
            y2 = center + int((radius + spike_length) * math.sin(rad))
            rdraw.line([(x1, y1), (x2, y2)], fill="white", width=4)

        ring_x = 390
        ring_y = 80
        circle_x = ring_x + RING_PADDING
        circle_y = ring_y + RING_PADDING

        background.paste(ring, (ring_x, ring_y), ring)
        background.paste(circ, (circle_x, circle_y), circ)

        # ============ FONTS ============
        arial = ImageFont.truetype("SONALI/assets/font2.ttf", 30)
        font = ImageFont.truetype("SONALI/assets/font.ttf", 32)
        bold_font = ImageFont.truetype("SONALI/assets/font.ttf", 34)
        small_neon = ImageFont.truetype("SONALI/assets/font.ttf", 22)
        icon_font = ImageFont.truetype("SONALI/assets/font.ttf", 40)

        # WATERMARK
        text_size = draw.textsize("@Starmusic by devil", font=font)
        draw.text(
            (1280 - text_size[0] - 10, 10),
            "@Starmusic by devil",
            fill="yellow",
            font=font,
        )

        draw.text((980, 60), "   Credit", fill="cyan", font=small_neon)
        draw.text((980, 85), "@Ankitgupta21444", fill="white", font=small_neon)

        draw.text(
            (55, 540),
            f"{channel} | {views[:23]}",
            fill="white",
            font=arial,
        )

        # ===== CENTER TITLE (CYAN) =====
        title_w, _ = draw.textsize(title, font=font)
        title_x = (1280 - title_w) // 2
        draw.text(
            (title_x, 580),
            title,
            fill="cyan",
            font=font,
        )

        # ===== TIMELINE (VISIBLE + CENTER) =====
        timeline_text = "❍━━━ლ━━━❍"
        tw, _ = draw.textsize(timeline_text, font=bold_font)
        tx = (1280 - tw) // 2
        ty = 620
        draw.text((tx, ty), timeline_text, fill="white", font=bold_font)

        # ===== PLAYER CONTROLS (PROPER SHAPES - ALWAYS VISIBLE) =====
btn_y = 660

# SHUFFLE (left)
draw.line([(400, btn_y+10), (450, btn_y+10)], fill="white", width=3)
draw.line([(450, btn_y+10), (440, btn_y)], fill="white", width=3)
draw.line([(440, btn_y+20), (450, btn_y+10)], fill="white", width=3)

# PREVIOUS
draw.polygon([(520, btn_y), (560, btn_y+15), (520, btn_y+30)], fill="white")

# PLAY BUTTON (circle + triangle)
draw.ellipse((610, btn_y-5, 690, btn_y+35), outline="white", width=3)
draw.polygon([(635, btn_y+5), (665, btn_y+15), (635, btn_y+25)], fill="white")

# NEXT
draw.polygon([(760, btn_y), (720, btn_y+15), (760, btn_y+30)], fill="white")

# REPEAT (right)
draw.line([(820, btn_y+5), (870, btn_y+5)], fill="white", width=3)
draw.line([(870, btn_y+5), (860, btn_y-5)], fill="white", width=3)
draw.line([(860, btn_y+15), (870, btn_y+5)], fill="white", width=3)
        try:
            os.remove(f"cache/thumb{videoid}.png")
        except:
            pass

        background.save(f"cache/{videoid}.png")
        return f"cache/{videoid}.png"

    except Exception as e:
        print(e)
        return YOUTUBE_IMG_URL
