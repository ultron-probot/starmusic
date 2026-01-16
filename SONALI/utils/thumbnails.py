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
                title = title.title()
            except:
                title = "Unsupported Title"
            try:
                duration = result["duration"]
            except:
                duration = "Unknown Mins"
            thumbnail = result["thumbnails"][0]["url"].split("?")[0]
            try:
                views = result["viewCount"]["short"]
            except:
                views = "Unknown Views"
            try:
                channel = result["channel"]["name"]
            except:
                channel = "Unknown Channel"

        # -------- DOWNLOAD YT THUMB --------
        async with aiohttp.ClientSession() as session:
            async with session.get(thumbnail) as resp:
                if resp.status == 200:
                    f = await aiofiles.open(f"cache/thumb{videoid}.png", mode="wb")
                    await f.write(await resp.read())
                    await f.close()

        youtube = Image.open(f"cache/thumb{videoid}.png").convert("RGBA")

        # ============ BACKGROUND ============
        background = youtube.resize((1280, 720)).filter(ImageFilter.GaussianBlur(radius=18))
        enhancer = ImageEnhance.Brightness(background)
        background = enhancer.enhance(0.45)
        draw = ImageDraw.Draw(background)

        # ---- WHITE SPRINKLE ----
        for _ in range(220):
            x = random.randint(0, 1280)
            y = random.randint(0, 720)
            r = random.randint(1, 3)
            draw.ellipse((x, y, x+r, y+r), fill="white")

        # ---- MUSIC NOTE SPRINKLE BACKGROUND ----
        music_font = ImageFont.truetype("SONALI/assets/font.ttf", 28)
        for _ in range(15):
            x = random.randint(100, 1180)
            y = random.randint(80, 640)
            draw.text((x, y), "♪", fill="white", font=music_font)

        # ============ DIAMONDS (ANDAR + NOTES INSIDE) ============
        diamond = Image.new("RGBA", (260, 260), (255,255,255,0))
        ddraw = ImageDraw.Draw(diamond)

        ddraw.polygon(
            [(130,0),(260,130),(130,260),(0,130)],
            outline="white",
            width=6
        )

        # music notes inside diamonds
        note_font = ImageFont.truetype("SONALI/assets/font.ttf", 36)
        ddraw.text((95, 95), "🎵", fill="white", font=note_font)

        # FIXED POSITIONS (ANDAR)
        background.paste(diamond, (20, 230), diamond)     # LEFT
        background.paste(diamond, (1000, 230), diamond)  # RIGHT

        # ============ CENTER CIRCLE ============
        CIRCLE_SIZE = 420
        yt_thumb = youtube.resize((CIRCLE_SIZE, CIRCLE_SIZE))

        mask = Image.new("L", (CIRCLE_SIZE, CIRCLE_SIZE), 0)
        mdraw = ImageDraw.Draw(mask)
        mdraw.ellipse((0,0,CIRCLE_SIZE,CIRCLE_SIZE), fill=255)

        circ = Image.new("RGBA", (CIRCLE_SIZE, CIRCLE_SIZE))
        circ.paste(yt_thumb, (0,0), mask)

        # ============ DENSE MUSIC SPIKES ============
        RING_PADDING = 40
        ring_size = CIRCLE_SIZE + (RING_PADDING * 2)

        ring = Image.new("RGBA", (ring_size, ring_size), (0,0,0,0))
        rdraw = ImageDraw.Draw(ring)

        # base circle
        rdraw.ellipse(
            (10, 10, ring_size-10, ring_size-10),
            outline="white",
            width=4
        )

        center = ring_size // 2
        radius = (ring_size // 2) - 10

        # DENSE + RANDOM spikes
        for angle in range(0, 360, 8):   # more dense
            rad = math.radians(angle)

            x1 = center + int(radius * math.cos(rad))
            y1 = center + int(radius * math.sin(rad))

            spike_length = random.randint(10, 45)

            x2 = center + int((radius + spike_length) * math.cos(rad))
            y2 = center + int((radius + spike_length) * math.sin(rad))

            rdraw.line([(x1, y1), (x2, y2)], fill="white", width=3)

        # center align
        ring_x = 400
        ring_y = 120
        circle_x = ring_x + RING_PADDING
        circle_y = ring_y + RING_PADDING

        background.paste(ring, (ring_x, ring_y), ring)
        background.paste(circ, (circle_x, circle_y), circ)

        # ============ TEXT (YOUR STYLE) ============
        arial = ImageFont.truetype("SONALI/assets/font2.ttf", 30)
        font = ImageFont.truetype("SONALI/assets/font.ttf", 30)
        bold_font = ImageFont.truetype("SONALI/assets/font.ttf", 33)
        small_neon = ImageFont.truetype("SONALI/assets/font.ttf", 22)

        text_size = draw.textsize("@Starmusic by devil  ", font=font)
        draw.text(
            (1280 - text_size[0] - 10, 10),
            "@Starmusic",
            fill="yellow",
            font=font,
        )

        draw.text((980, 60), "Credit", fill="cyan", font=small_neon)
        draw.text((980, 85), "@Ankitgupta21444", fill="white", font=small_neon)

        draw.text(
            (55, 580),
            f"{channel} | {views[:23]}",
            (255, 255, 255),
            font=arial,
        )

        draw.text(
            (57, 620),
            title,
            (255, 255, 255),
            font=font,
        )

        draw.text((55, 655), "00:00", fill="white", font=bold_font)

        start_x = 150
        end_x = 1130
        line_y = 670
        draw.line([(start_x, line_y), (end_x, line_y)], fill="white", width=4)

        draw.text((end_x + 10, 655), duration, fill="white", font=bold_font)

        try:
            os.remove(f"cache/thumb{videoid}.png")
        except:
            pass

        background.save(f"cache/{videoid}.png")
        return f"cache/{videoid}.png"

    except Exception as e:
        print(e)
        return YOUTUBE_IMG_URL
