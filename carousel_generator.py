"""
Carousel Image Generator - Creates multiple slide images for LinkedIn.
Uses Pillow to generate PNGs instead of a PDF.
"""

import os
import json
import tempfile
import textwrap
from PIL import Image, ImageDraw, ImageFont

# Brand colors for Career Launchpad
COLORS = {
    "bg_dark": (15, 23, 42),        # Slate 900
    "bg_accent": (30, 58, 138),     # Blue 800
    "bg_highlight": (79, 70, 229),  # Indigo 600
    "text_white": (255, 255, 255),
    "text_light": (203, 213, 225),  # Slate 300
    "accent_cyan": (34, 211, 238),  # Cyan 400
    "accent_green": (52, 211, 153), # Emerald 400
    "accent_pink": (244, 114, 182), # Pink 400
}

SLIDE_COLORS = [
    COLORS["bg_dark"],
    COLORS["bg_accent"],
    COLORS["bg_highlight"],
    COLORS["bg_dark"],
    COLORS["bg_accent"],
]

def load_fonts():
    try:
        font_large = ImageFont.truetype("arialbd.ttf", 60)
        font_medium = ImageFont.truetype("arial.ttf", 40)
        font_small = ImageFont.truetype("arial.ttf", 30)
    except IOError:
        font_large = ImageFont.load_default(size=60)
        font_medium = ImageFont.load_default(size=40)
        font_small = ImageFont.load_default(size=30)
    return font_large, font_medium, font_small

def draw_text_wrapped(draw, text, font, fill, x, y, max_width):
    lines = []
    words = text.split()
    current_line = ""
    for word in words:
        test_line = f"{current_line} {word}".strip()
        bbox = draw.textbbox((0, 0), test_line, font=font)
        w = bbox[2] - bbox[0]
        if w <= max_width:
            current_line = test_line
        else:
            if current_line:
                lines.append(current_line)
            current_line = word
    if current_line:
        lines.append(current_line)
    
    current_y = y
    for line in lines:
        draw.text((x, current_y), line, font=font, fill=fill)
        bbox = draw.textbbox((0, 0), line, font=font)
        h = bbox[3] - bbox[1]
        current_y += h + 15 # line spacing padding
    return current_y

def create_title_slide(title, subtitle):
    img = Image.new("RGB", (1080, 1080), COLORS["bg_dark"])
    draw = ImageDraw.Draw(img)
    f_large, f_medium, f_small = load_fonts()
    
    # Top accent
    draw.rectangle([0, 0, 1080, 20], fill=COLORS["accent_cyan"])
    
    # Text
    y = draw_text_wrapped(draw, title, f_large, COLORS["text_white"], 100, 300, 880)
    if subtitle:
        draw_text_wrapped(draw, subtitle, f_medium, COLORS["text_light"], 100, y + 50, 880)
        
    # Bottom brand
    draw.text((100, 950), "Career Launchpad", font=f_small, fill=COLORS["accent_cyan"])
    draw.rectangle([0, 1060, 1080, 1080], fill=COLORS["accent_green"])
    
    return img

def create_content_slide(idx, heading, body):
    bg = SLIDE_COLORS[idx % len(SLIDE_COLORS)]
    img = Image.new("RGB", (1080, 1080), bg)
    draw = ImageDraw.Draw(img)
    f_large, f_medium, f_small = load_fonts()
    
    # Slide number mark
    draw.ellipse([80, 80, 150, 150], fill=COLORS["accent_cyan"])
    draw.text((100, 95), str(idx), font=f_large, fill=COLORS["bg_dark"])
    
    y = draw_text_wrapped(draw, heading, f_large, COLORS["text_white"], 100, 250, 880)
    draw_text_wrapped(draw, body, f_medium, COLORS["text_light"], 100, y + 40, 880)
    
    accent = COLORS["accent_green"] if idx % 2 == 0 else COLORS["accent_pink"]
    draw.rectangle([0, 1060, 1080, 1080], fill=accent)
    return img

def create_cta_slide(text, hashtags):
    img = Image.new("RGB", (1080, 1080), COLORS["bg_highlight"])
    draw = ImageDraw.Draw(img)
    f_large, f_medium, f_small = load_fonts()
    
    y = draw_text_wrapped(draw, text, f_large, COLORS["text_white"], 100, 400, 880)
    if hashtags:
        draw_text_wrapped(draw, hashtags, f_medium, COLORS["accent_cyan"], 100, y + 50, 880)
        
    draw.text((100, 950), "Career Launchpad", font=f_small, fill=COLORS["accent_green"])
    draw.rectangle([0, 1060, 1080, 1080], fill=COLORS["accent_cyan"])
    return img

def generate_carousel_pdf(slides_json: str) -> str:
    """
    STILL NAMED generate_carousel_pdf to avoid breaking existing imports,
    but actually generates images and returns a comma-separated string of paths.
    """
    try:
        data = json.loads(slides_json)
    except json.JSONDecodeError as e:
        return f"ERROR: Invalid JSON provided. {str(e)}"

    images = []
    
    img = create_title_slide(data.get("title", "Career Launchpad"), data.get("subtitle", ""))
    images.append(img)
    
    for i, slide in enumerate(data.get("slides", []), 1):
        img = create_content_slide(i, slide.get("heading", f"Point {i}"), slide.get("body", ""))
        images.append(img)
        
    img = create_cta_slide(data.get("cta", "Follow Career Launchpad for more!"), data.get("hashtags", ""))
    images.append(img)
    
    paths = []
    for i, img in enumerate(images):
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".png", prefix=f"slide_{i}_")
        img.save(tmp.name)
        paths.append(tmp.name)
        
    print(f"Generated {len(paths)} carousel images.")
    # Return comma-separated string for easy tool parsing
    return ",".join(paths)
