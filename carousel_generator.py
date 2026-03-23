"""
Carousel Image Generator - Creates multiple slide images for LinkedIn.
Upgraded version with better visual flair and variety.
"""

import os
import json
import tempfile
import textwrap
from PIL import Image, ImageDraw, ImageFont

# Brand colors for Career Launchpad
COLORS = {
    "bg_dark": (15, 23, 42),        # Slate 900
    "bg_slate": (30, 41, 59),       # Slate 800
    "bg_accent": (30, 58, 138),     # Blue 800
    "bg_highlight": (79, 70, 229),  # Indigo 600
    "text_white": (255, 255, 255),
    "text_light": (203, 213, 225),  # Slate 300
    "accent_cyan": (34, 211, 238),  # Cyan 400
    "accent_green": (52, 211, 153), # Emerald 400
    "accent_pink": (244, 114, 182), # Pink 400
    "accent_orange": (251, 146, 60),# Orange 400
}

SLIDE_THEMES = [
    (COLORS["bg_dark"], COLORS["accent_cyan"]),
    (COLORS["bg_accent"], COLORS["accent_green"]),
    (COLORS["bg_highlight"], COLORS["accent_pink"]),
    (COLORS["bg_slate"], COLORS["accent_orange"]),
]

def load_fonts():
    try:
        # Standard Windows fonts
        f_title = ImageFont.truetype("arialbd.ttf", 72)
        f_head = ImageFont.truetype("arialbd.ttf", 54)
        f_body = ImageFont.truetype("arial.ttf", 38)
        f_small = ImageFont.truetype("arialbd.ttf", 28)
    except IOError:
        f_title = ImageFont.load_default(size=72)
        f_head = ImageFont.load_default(size=54)
        f_body = ImageFont.load_default(size=38)
        f_small = ImageFont.load_default(size=28)
    return f_title, f_head, f_body, f_small

def draw_gradient(draw, bg_color):
    """Draw a subtle vertical gradient effect using lines."""
    r, g, b = bg_color
    for y in range(1080):
        # Darken by up to 40 units at the bottom
        factor = (y / 1080) * 40
        nr = max(0, r - int(factor))
        ng = max(0, g - int(factor))
        nb = max(0, b - int(factor))
        draw.line([(0, y), (1080, y)], fill=(nr, ng, nb))

def draw_text_centered(draw, text, font, fill, y_start, max_width=900):
    lines = []
    for line in text.split('\n'):
        lines.extend(textwrap.wrap(line, width=int(max_width/(font.size*0.5))))
    
    current_y = y_start
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        w = bbox[2] - bbox[0]
        x = (1080 - w) / 2
        draw.text((x, current_y), line, font=font, fill=fill)
        current_y += bbox[3] - bbox[1] + 20
    return current_y

def draw_text_left(draw, text, font, fill, x, y, max_width=880):
    lines = []
    for line in text.split('\n'):
        lines.extend(textwrap.wrap(line, width=int(max_width/(font.size*0.5))))
    
    current_y = y
    for line in lines:
        draw.text((x, current_y), line, font=font, fill=fill)
        bbox = draw.textbbox((0, 0), line, font=font)
        current_y += bbox[3] - bbox[1] + 15
    return current_y

def create_title_slide(title, subtitle):
    img = Image.new("RGB", (1080, 1080))
    draw = ImageDraw.Draw(img)
    draw_gradient(draw, COLORS["bg_dark"])
    f_title, f_head, f_body, f_small = load_fonts()
    
    # Decorative shapes
    draw.rectangle([40, 40, 1040, 1040], outline=COLORS["accent_cyan"], width=3)
    draw.chord([800, -200, 1300, 300], 0, 360, fill=COLORS["bg_accent"])
    
    y = draw_text_centered(draw, title.upper(), f_title, COLORS["text_white"], 350)
    if subtitle:
        draw_text_centered(draw, subtitle, f_body, COLORS["accent_cyan"], y + 40)
        
    # Brand Footer
    draw.text((100, 960), "CAREER LAUNCHPAD", font=f_small, fill=COLORS["accent_cyan"])
    draw.rectangle([0, 1060, 1080, 1080], fill=COLORS["accent_cyan"])
    
    return img

def create_content_slide(idx, heading, body):
    bg, accent = SLIDE_THEMES[idx % len(SLIDE_THEMES)]
    img = Image.new("RGB", (1080, 1080))
    draw = ImageDraw.Draw(img)
    draw_gradient(draw, bg)
    f_title, f_head, f_body, f_small = load_fonts()
    
    # Border and number badge
    draw.rectangle([40, 40, 1040, 1040], outline=accent, width=2)
    draw.ellipse([80, 80, 160, 160], fill=accent)
    draw.text((105, 95), str(idx), font=f_small, fill=COLORS["bg_dark"])
    
    draw.text((100, 200), heading, font=f_head, fill=COLORS["text_white"])
    # Accent line under heading
    draw.rectangle([100, 270, 300, 275], fill=accent)
    
    draw_text_left(draw, body, f_body, COLORS["text_light"], 100, 320)
    
    draw.rectangle([1040, 0, 1080, 1080], fill=accent)
    return img

def create_cta_slide(text, hashtags):
    img = Image.new("RGB", (1080, 1080))
    draw = ImageDraw.Draw(img)
    draw_gradient(draw, COLORS["bg_highlight"])
    f_title, f_head, f_body, f_small = load_fonts()
    
    draw_text_centered(draw, text, f_head, COLORS["text_white"], 400)
    if hashtags:
        draw_text_centered(draw, hashtags, f_small, COLORS["accent_cyan"], 600)
        
    # Final branding
    draw_text_centered(draw, "CAREER LAUNCHPAD", f_small, COLORS["accent_green"], 950)
    draw.rectangle([0, 1050, 1080, 1080], fill=COLORS["accent_green"])
    return img

def generate_carousel_pdf(slides_json: str) -> str:
    """
    Returns a comma-separated string of file paths to generated images.
    """
    try:
        data = json.loads(slides_json)
    except json.JSONDecodeError as e:
        return f"ERROR: Invalid JSON provided. {str(e)}"

    images = []
    
    # 1. Title
    images.append(create_title_slide(data.get("title", "Career Launchpad"), data.get("subtitle", "")))
    
    # 2. Content
    for i, slide in enumerate(data.get("slides", []), 1):
        images.append(create_content_slide(i, slide.get("heading", ""), slide.get("body", "")))
        
    # 3. CTA
    images.append(create_cta_slide(data.get("cta", "Like & Follow for more!"), data.get("hashtags", "")))
    
    paths = []
    for i, img in enumerate(images):
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".png", prefix=f"slide_{i}_")
        img.save(tmp.name)
        paths.append(tmp.name)
        
    print(f"Generated {len(paths)} fancy slides.")
    return ",".join(paths)
