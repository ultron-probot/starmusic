import os
import re
import random
import aiohttp
import aiofiles
from SONALI import app
from config import YOUTUBE_IMG_URL
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
from py_yt import VideosSearch

def clear(text):
    return re.sub("\s+", " ", text).strip()

def changeImageSize(maxWidth, maxHeight, image):
    widthRatio = maxWidth / image.size[0]
    heightRatio = maxHeight / image.size[1]
    newWidth = int(image.size[0] * min(widthRatio, heightRatio))
    newHeight = int(image.size[1] * min(widthRatio, heightRatio))
    return image.resize((newWidth, newHeight))

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

        # ============ NEW DESIGN START ============

        # 1) BLUR DARK BACKGROUND
        background = youtube.resize((1280, 720)).filter(ImageFilter.GaussianBlur(radius=18))
        enhancer = ImageEnhance.Brightness(background)
        background = enhancer.enhance(0.45)
        draw = ImageDraw.Draw(background)

        # 2) WHITE SPRINKLE EFFECT
        for _ in range(220):
            x = random.randint(0, 1280)
            y = random.randint(0, 720)
            r = random.randint(1, 3)
            draw.ellipse((x, y, x+r, y+r), fill="white")

        # 3) MUSIC NOTE SPRINKLE
        music_font = ImageFont.truetype("SONALI/assets/font.ttf", 28)
        for _ in range(15):
            x = random.randint(100, 1180)
            y = random.randint(80, 640)
            draw.text((x, y), "♪", fill="white", font=music_font)

        # 4) LEFT & RIGHT DIAMOND SHAPES
        diamond = Image.new("RGBA", (260, 260), (255,255,255,0))
        ddraw = ImageDraw.Draw(diamond)
        ddraw.polygon(
            [(130,0),(260,130),(130,260),(0,130)],
            outline="white",
            width=6
        )

        background.paste(diamond, (-60, 230), diamond)
        background.paste(diamond, (1080, 230), diamond)

        # 5) CENTER CIRCLE (YOUTUBE THUMBNAIL)
        CIRCLE_SIZE = 420
        yt_thumb = youtube.resize((CIRCLE_SIZE, CIRCLE_SIZE))

        mask = Image.new("L", (CIRCLE_SIZE, CIRCLE_SIZE), 0)
        mdraw = ImageDraw.Draw(mask)
        mdraw.ellipse((0,0,CIRCLE_SIZE,CIRCLE_SIZE), fill=255)

        circ = Image.new("RGBA", (CIRCLE_SIZE, CIRCLE_SIZE))
        circ.paste(yt_thumb, (0,0), mask)

        # Beats ring
        ring = Image.new("RGBA", (CIRCLE_SIZE+60, CIRCLE_SIZE+60), (0,0,0,0))
        rdraw = ImageDraw.Draw(ring)
        rdraw.ellipse(
            (10,10,CIRCLE_SIZE+50,CIRCLE_SIZE+50),
            outline="white",
            width=6
        )

        background.paste(ring, (430, 140), ring)
        background.paste(circ, (460, 170), circ)

        # ============ TEXT & CREDITS ============

        arial = ImageFont.truetype("SONALI/assets/font2.ttf", 30)
        font = ImageFont.truetype("SONALI/assets/font.ttf", 30)
        bold_font = ImageFont.truetype("SONALI/assets/font.ttf", 33)
        small_neon = ImageFont.truetype("SONALI/assets/font.ttf", 22)

        # MAIN WATERMARK
        text_size = draw.textsize("@XCLUSOR by DEVIL  ", font=font)
        draw.text(
            (1280 - text_size[0] - 10, 10),
            "@Starmusic by devil",
            fill="yellow",
            font=font,
        )

        # ----- NEW THUMBNAIL CREDIT -----
        draw.text(
            (980, 60),
            "Credit",
            fill="cyan",
            font=small_neon,
        )

        draw.text(
            (980, 85),
            "@Ankitgupta21444",
            fill="white",
            font=small_neon,
        )

        # CHANNEL + VIEWS
        draw.text(
            (55, 580),
            f"{channel} | {views[:23]}",
            (255, 255, 255),
            font=arial,
        )

        # TITLE
        draw.text(
            (57, 620),
            title,
            (255, 255, 255),
            font=font,
        )

        # TIMELINE
        draw.text((55, 655), "00:00", fill="white", font=bold_font)

        start_x = 150
        end_x = 1130
        line_y = 670
        draw.line([(start_x, line_y), (end_x, line_y)], fill="white", width=4)

        duration_text_size = draw.textsize(duration, font=bold_font)
        draw.text((end_x + 10, 655), duration, fill="white", font=bold_font)

        # REMOVE TEMP FILE
        try:
            os.remove(f"cache/thumb{videoid}.png")
        except:
            pass

        # SAVE FINAL
        background.save(f"cache/{videoid}.png")
        return f"cache/{videoid}.png"

    except Exception as e:
        print(e)
        return YOUTUBE_IMG_URL
