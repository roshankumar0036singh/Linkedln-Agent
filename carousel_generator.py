"""
Carousel PDF Generator - Creates multi-slide carousel PDFs for LinkedIn document posts.
Uses fpdf2 for PDF generation.
"""

import os
import json
import tempfile
import textwrap
from fpdf import FPDF


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


class CarouselPDF(FPDF):
    """Custom PDF class for LinkedIn carousel slides."""

    def __init__(self):
        super().__init__(orientation="L", unit="mm", format=(190, 240))
        # Use built-in fonts only for maximum compatibility
        self.set_auto_page_break(auto=False)

    def add_title_slide(self, title: str, subtitle: str = ""):
        """Add an eye-catching title slide."""
        self.add_page()
        bg = COLORS["bg_dark"]
        self.set_fill_color(*bg)
        self.rect(0, 0, 240, 190, "F")

        # Decorative accent bar at top
        self.set_fill_color(*COLORS["accent_cyan"])
        self.rect(0, 0, 240, 4, "F")

        # Title
        self.set_font("Helvetica", "B", 28)
        self.set_text_color(*COLORS["text_white"])
        self.set_y(50)
        self.multi_cell(220, 14, title, align="C", new_x="LEFT", new_y="NEXT")

        # Subtitle
        if subtitle:
            self.set_font("Helvetica", "", 14)
            self.set_text_color(*COLORS["text_light"])
            self.set_y(self.get_y() + 10)
            self.multi_cell(220, 8, subtitle, align="C", new_x="LEFT", new_y="NEXT")

        # Brand footer
        self.set_font("Helvetica", "B", 12)
        self.set_text_color(*COLORS["accent_cyan"])
        self.set_y(165)
        self.cell(220, 8, "Career Launchpad", align="C", new_x="LEFT", new_y="NEXT")

        # Bottom accent bar
        self.set_fill_color(*COLORS["accent_green"])
        self.rect(0, 186, 240, 4, "F")

    def add_content_slide(self, slide_number: int, heading: str, body: str):
        """Add a content slide with heading and body text."""
        self.add_page()
        color_idx = slide_number % len(SLIDE_COLORS)
        bg = SLIDE_COLORS[color_idx]
        self.set_fill_color(*bg)
        self.rect(0, 0, 240, 190, "F")

        # Slide number badge
        self.set_fill_color(*COLORS["accent_cyan"])
        self.set_font("Helvetica", "B", 14)
        self.set_text_color(*COLORS["bg_dark"])
        self.set_xy(10, 10)
        self.cell(16, 16, str(slide_number), align="C", new_x="LEFT", new_y="TOP", fill=True)

        # Heading
        self.set_font("Helvetica", "B", 22)
        self.set_text_color(*COLORS["text_white"])
        self.set_xy(10, 35)
        # Wrap heading text
        wrapped_heading = textwrap.fill(heading, width=40)
        self.multi_cell(220, 11, wrapped_heading, align="L", new_x="LEFT", new_y="NEXT")

        # Body text
        self.set_font("Helvetica", "", 13)
        self.set_text_color(*COLORS["text_light"])
        self.set_y(self.get_y() + 8)
        wrapped_body = textwrap.fill(body, width=60)
        self.multi_cell(220, 7, wrapped_body, align="L", new_x="LEFT", new_y="NEXT")

        # Bottom accent
        accent = COLORS["accent_green"] if slide_number % 2 == 0 else COLORS["accent_pink"]
        self.set_fill_color(*accent)
        self.rect(0, 186, 240, 4, "F")

    def add_cta_slide(self, text: str, hashtags: str = ""):
        """Add a call-to-action closing slide."""
        self.add_page()
        bg = COLORS["bg_highlight"]
        self.set_fill_color(*bg)
        self.rect(0, 0, 240, 190, "F")

        # CTA text
        self.set_font("Helvetica", "B", 24)
        self.set_text_color(*COLORS["text_white"])
        self.set_y(50)
        wrapped = textwrap.fill(text, width=35)
        self.multi_cell(220, 12, wrapped, align="C", new_x="LEFT", new_y="NEXT")

        # Hashtags
        if hashtags:
            self.set_font("Helvetica", "", 11)
            self.set_text_color(*COLORS["accent_cyan"])
            self.set_y(self.get_y() + 15)
            self.multi_cell(220, 7, hashtags, align="C", new_x="LEFT", new_y="NEXT")

        # Brand
        self.set_font("Helvetica", "B", 14)
        self.set_text_color(*COLORS["accent_green"])
        self.set_y(160)
        self.cell(220, 8, "Career Launchpad", align="C", new_x="LEFT", new_y="NEXT")

        # Bottom bar
        self.set_fill_color(*COLORS["accent_cyan"])
        self.rect(0, 186, 240, 4, "F")


def generate_carousel_pdf(slides_json: str) -> str:
    """
    Generates a carousel PDF from a JSON string describing the slides.
    
    Expected JSON format:
    {
        "title": "Main Title",
        "subtitle": "Optional subtitle",
        "slides": [
            {"heading": "Slide 1 Title", "body": "Slide 1 content..."},
            {"heading": "Slide 2 Title", "body": "Slide 2 content..."}
        ],
        "cta": "Follow for more!",
        "hashtags": "#Career #Internships"
    }
    
    Returns the file path to the generated PDF.
    """
    try:
        data = json.loads(slides_json)
    except json.JSONDecodeError as e:
        return f"ERROR: Invalid JSON provided. {str(e)}"

    title = data.get("title", "Career Launchpad")
    subtitle = data.get("subtitle", "")
    slides = data.get("slides", [])
    cta = data.get("cta", "Follow Career Launchpad for more!")
    hashtags = data.get("hashtags", "")

    pdf = CarouselPDF()

    # Title slide
    pdf.add_title_slide(title, subtitle)

    # Content slides
    for i, slide in enumerate(slides, 1):
        heading = slide.get("heading", f"Point {i}")
        body = slide.get("body", "")
        pdf.add_content_slide(i, heading, body)

    # CTA slide
    pdf.add_cta_slide(cta, hashtags)

    # Save to temp file
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf", prefix="carousel_")
    pdf.output(tmp.name)
    tmp.close()

    print(f"Carousel PDF generated: {tmp.name}")
    return tmp.name
