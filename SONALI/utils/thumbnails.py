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

        async with aiohttp.ClientSession() as session:
            async with session.get(thumbnail) as resp:
                if resp.status == 200:
                    f = await aiofiles.open(f"cache/thumb{videoid}.png", mode="wb")
                    await f.write(await resp.read())
                    await f.close()

        youtube = Image.open(f"cache/thumb{videoid}.png").convert("RGBA")

        
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
            y = random.randint(80, 640)
            draw.text((x, y), "♪", fill="white", font=music_font)

        
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

        # FIXED POSITIONS (ANDAR)
        background.paste(diamond, (20, 230), diamond)     # LEFT
        background.paste(diamond, (1000, 230), diamond)  # RIGHT

        
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

        
        for angle in range(0, 360, 8):   # extra dense
            rad = math.radians(angle)

            x1 = center + int(radius * math.cos(rad))
            y1 = center + int(radius * math.sin(rad))

            spike_length = random.randint(12, 55)  

            x2 = center + int((radius + spike_length) * math.cos(rad))
            y2 = center + int((radius + spike_length) * math.sin(rad))

            rdraw.line([(x1, y1), (x2, y2)], fill="white", width=4)

        # center align
        ring_x = 390
        ring_y = 115
        circle_x = ring_x + RING_PADDING
        circle_y = ring_y + RING_PADDING

        background.paste(ring, (ring_x, ring_y), ring)
        background.paste(circ, (circle_x, circle_y), circ)

        
        arial = ImageFont.truetype("SONALI/assets/font2.ttf", 30)
        font = ImageFont.truetype("SONALI/assets/font.ttf", 30)
        bold_font = ImageFont.truetype("SONALI/assets/font.ttf", 33)
        small_neon = ImageFont.truetype("SONALI/assets/font.ttf", 22)

        text_size = draw.textsize("STARMUSIC by DEVIL  ", font=font)
        draw.text(
            (1280 - text_size[0] - 10, 10),
            "STARMUSIC by DEVIL",
            fill="yellow",
            font=font,
        )

        draw.text((980, 60), "  •", fill="cyan", font=small_neon)
        draw.text((980, 85), "°", fill="white", font=small_neon)

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

        draw.text((55, 655), "00:00", fill="cyan", font=bold_font)

        start_x = 150
        end_x = 1130
        line_y = 670
        draw.line([(start_x, line_y), (end_x, line_y)], fill="yellow", width=5)

        draw.text((end_x + 10, 655), duration, fill="yellow", font=bold_font)

        try:
            os.remove(f"cache/thumb{videoid}.png")
        except:
            pass

        background.save(f"cache/{videoid}.png")
        return f"cache/{videoid}.png"

    except Exception as e:
        print(e)
        return YOUTUBE_IMG_URL
        
