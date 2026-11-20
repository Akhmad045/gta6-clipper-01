#!/usr/bin/env python3
"""Build the gta6-clipper-01 YouTube Short (1080x1920, ~38 s).

Every visual is original art generated for this entry (the neon Vice City
boulevard, the gaming room and the ghost-agent desk scenes in assets/).
Scenes are framed with Pillow: a slow Ken Burns zoom per scene via ffmpeg's
zoompan, a bold hook inside the first two seconds, caption bands, then the
make.fun pitch and the $500 bounty call to action. The soundtrack is the
original synth loop from make_audio.py. No Rockstar footage, no
copyrighted audio.

Run: python3 make_audio.py && python3 build_video.py
Output: assets/gta6-clipper.mp4
"""
import os
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(HERE, "assets")
WORK = os.path.join(HERE, ".video-work")
OUT_PATH = os.path.join(ASSETS, "gta6-clipper.mp4")

FONT_BOLD = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
FONT_REG = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"

W, H = 1080, 1920
FPS = 30
WHITE = (255, 255, 255)
PINK = (255, 62, 165)
CYAN = (38, 230, 218)
YELLOW = (255, 205, 64)
NAVY = (10, 10, 26)

# (image, seconds, big lines [(text, colour)], caption, crop anchor)
SCENES = [
    ("scene-boulevard.png", 3.5,
     [("GTA VI IS", WHITE), ("FINALLY HERE", YELLOW)],
     "after 13 years of waiting...", "center"),
    ("scene-gaming.png", 5.5,
     [("POV:", CYAN), ("IT'S LAUNCH WEEK", WHITE)],
     "the whole world is playing right now", "center"),
    ("scene-ghost.png", 5.5,
     [("VICE CITY", PINK), ("NEVER LOOKED THIS GOOD", WHITE)],
     "every sunset hits different", "center"),
    ("scene-agent.png", 7.0,
     [("THIS CLIP?", WHITE), ("MADE BY MY AI AGENT", CYAN)],
     "it makes clips while I play GTA VI", "center"),
    ("scene-agent.png", 7.0,
     [("MAKE CLIPS WITH AI", WHITE), ("EARN REAL MONEY", YELLOW)],
     "people + their AI agents win bounties on make.fun", "bottom"),
    ("scene-boulevard.png", 6.0,
     [("THIS VIDEO IS IN A", WHITE), ("$500 BOUNTY", YELLOW)],
     "make.fun/bounty/gta6-clipper-01 - link in description", "bottom"),
    ("scene-gaming.png", 3.5,
     [("SEE YOU IN", WHITE), ("VICE CITY", PINK)],
     "made by my AI agent - make.fun", "bottom"),
]


def font(size, bold=True):
    return ImageFont.truetype(FONT_BOLD if bold else FONT_REG, size)


def fit(draw, text, size, max_w, bold=True):
    while size > 24:
        f = font(size, bold)
        if draw.textbbox((0, 0), text, font=f, stroke_width=size // 13)[2] <= max_w:
            return f
        size -= 4
    return font(size, bold)


def cover(img, anchor="center"):
    """Crop/resize an image to fill 1080x1920."""
    iw, ih = img.size
    scale = max(W / iw, H / ih)
    img = img.resize((round(iw * scale), round(ih * scale)), Image.LANCZOS)
    x = (img.size[0] - W) // 2
    if anchor == "top":
        y = 0
    elif anchor == "bottom":
        y = img.size[1] - H
    else:
        y = (img.size[1] - H) // 2
    return img.crop((x, y, x + W, y + H))


def gradient(img, top=True, height=860, strength=165):
    """A navy gradient band for text legibility."""
    band = Image.new("L", (1, height))
    for i in range(height):
        frac = i / height
        band.putpixel((0, i), int(strength * (1 - frac) if top else strength * frac))
    band = band.resize((W, height))
    black = Image.new("RGBA", (W, height), NAVY + (0,))
    black.putalpha(band)
    img.alpha_composite(black, (0, 0 if top else H - height))
    return img


def frame(scene, idx):
    name, _dur, lines, caption, anchor = scene
    img = Image.open(os.path.join(ASSETS, name)).convert("RGBA")
    img = cover(img, anchor)
    img = gradient(img, top=True, height=900, strength=150)
    img = gradient(img, top=False, height=520, strength=170)
    d = ImageDraw.Draw(img)

    y = 250
    for text, colour in lines:
        # keep the text inside the centre 80%: the Ken Burns zoom (up to
        # 1.10x) crops the frame edges, and edge-to-edge text would clip
        f = fit(d, text, 118, W - 220)
        box = d.textbbox((0, 0), text, font=f, stroke_width=10)
        tw = box[2] - box[0]
        d.text(((W - tw) / 2 - box[0], y), text, font=f, fill=colour,
               stroke_width=10, stroke_fill=(5, 5, 16))
        y += int(f.size * 1.16)

    # caption band
    cf = fit(d, caption, 47, W - 240, bold=False)
    box = d.textbbox((0, 0), caption, font=cf)
    tw, th = box[2] - box[0], box[3] - box[1]
    pad_x, pad_y = 34, 22
    bx0 = (W - tw) / 2 - pad_x
    by0 = H - 250 - pad_y
    d.rounded_rectangle([bx0, by0, bx0 + tw + 2 * pad_x, by0 + th + 2 * pad_y],
                        radius=26, fill=(8, 8, 22, 205))
    d.text(((W - tw) / 2 - box[0], by0 + pad_y - box[1]), caption, font=cf,
           fill=(235, 238, 250))

    path = os.path.join(WORK, f"frame-{idx}.png")
    img.convert("RGB").save(path, "PNG")
    return path


def run(cmd):
    print("+", " ".join(cmd[:3]), "...")
    subprocess.run(cmd, check=True, capture_output=True, text=True)


def main():
    os.makedirs(WORK, exist_ok=True)
    audio = os.path.join(ASSETS, "soundtrack.wav")
    if not os.path.exists(audio):
        sys.exit("soundtrack.wav missing - run make_audio.py first")

    clips = []
    for idx, scene in enumerate(SCENES):
        png = frame(scene, idx)
        dur = scene[1]
        frames = int(dur * FPS)
        clip = os.path.join(WORK, f"clip-{idx}.mp4")
        vf = (
            "scale=2160:3840:flags=lanczos,"
            f"zoompan=z='min(zoom+0.0009,1.10)':x='iw/2-(iw/zoom/2)':"
            f"y='ih/2-(ih/zoom/2)':d={frames}:s={W}x{H}:fps={FPS},"
            "format=yuv420p"
        )
        run(["ffmpeg", "-y", "-loop", "1", "-i", png, "-vf", vf,
             "-t", str(dur), "-c:v", "libx264", "-crf", "24",
             "-preset", "medium", "-r", str(FPS), clip])
        clips.append(clip)

    listfile = os.path.join(WORK, "concat.txt")
    with open(listfile, "w") as fh:
        for clip in clips:
            fh.write(f"file '{clip}'\n")
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", listfile,
         "-i", audio, "-map", "0:v", "-map", "1:a", "-c:v", "copy",
         "-c:a", "aac", "-b:a", "160k", "-shortest",
         "-movflags", "+faststart", OUT_PATH])
    size = os.path.getsize(OUT_PATH) / 1e6
    print(f"wrote {OUT_PATH} ({size:.1f} MB)")


if __name__ == "__main__":
    main()
