#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
news_thumbnail_gen.py — High-CTR Breaking News Thumbnail Generation Engine.

Features:
- Standard 1280x720 (16:9) broadcast resolution with high visual contrast.
- Bundled TrueType font support (Impact, Arial Bold) for 100% Linux/Ubuntu Actions fidelity.
- Full-bleed press photography with smooth alpha-gradient overlay (zero harsh solid blocks).
- Channel branding badge (● GLOBAL PULSE 24 | BREAKING REPORT).
- High-impact bold typography (86px+ 3D drop-shadow text) with yellow hook accents for high CTR.
- Bottom broadcast accent bar.
"""

import os
import sys
import re
import math
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter

import config

THUMB_W = 1280
THUMB_H = 720
ASSETS_DIR = getattr(config, "ASSETS_DIR", os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets"))


def _get_font(size: int, bold: bool = True, headline: bool = False) -> ImageFont.ImageFont:
    """Loads bundled TrueType fonts first, then OS system fonts, avoiding bitmap fallbacks."""
    candidates = []

    # 1. Bundled assets fonts (guaranteed to exist in repo)
    if headline:
        candidates.append(os.path.join(ASSETS_DIR, "font_headline.ttf"))
    if bold:
        candidates.append(os.path.join(ASSETS_DIR, "font_bold.ttf"))
    candidates.append(os.path.join(ASSETS_DIR, "font.ttf"))

    # 2. Linux / Ubuntu system fonts (GitHub Actions)
    if bold or headline:
        candidates.extend([
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
            "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
        ])
    else:
        candidates.extend([
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        ])

    # 3. Windows system fonts
    if headline:
        candidates.extend(["impact.ttf", "arialbd.ttf"])
    elif bold:
        candidates.extend(["arialbd.ttf", "segoeuib.ttf", "tahomabd.ttf"])
    else:
        candidates.extend(["arial.ttf", "segoeui.ttf"])

    for path in candidates:
        try:
            return ImageFont.truetype(path, size)
        except Exception:
            continue

    return ImageFont.load_default()


def _extract_punchy_headline(title: str) -> list:
    """
    Condenses a headline into 2-3 short, ultra-punchy lines (2 words per line)
    for maximum thumbnail CTR on mobile screens.
    """
    clean = re.sub(r'[:\-–—].*$', '', title).strip()
    clean = re.sub(r'[^\w\s,\$%\.]', '', clean).strip()
    words = clean.split()

    if len(words) <= 2:
        return [" ".join(words).upper()]

    if len(words) <= 4:
        return [" ".join(words[:2]).upper(), " ".join(words[2:]).upper()]

    # Meaningful keyword filter (keep numbers, $ amounts, names, strong verbs/nouns)
    filler = {
        "the", "a", "an", "of", "and", "in", "to", "over", "for", "on",
        "from", "with", "at", "by", "as", "into", "amid", "after", "before",
        "during", "about", "between", "through", "under", "that", "this",
    }
    meaningful = [w for w in words if w.lower() not in filler]
    if len(meaningful) < 3:
        meaningful = words

    lines = []
    if len(meaningful) >= 5:
        lines.append(" ".join(meaningful[:2]).upper())
        lines.append(" ".join(meaningful[2:4]).upper())
        lines.append(" ".join(meaningful[4:6]).upper())
    elif len(meaningful) == 4:
        lines.append(" ".join(meaningful[:2]).upper())
        lines.append(" ".join(meaningful[2:4]).upper())
    elif len(meaningful) == 3:
        lines.append(" ".join(meaningful[:2]).upper())
        lines.append(meaningful[2].upper())
    else:
        lines.append(" ".join(meaningful[:2]).upper())

    return [ln for ln in lines if ln]


def generate_news_thumbnail(
    title: str,
    category_label: str = "SPECIAL REPORT",
    subject_image_path: str = None,
    output_path: str = None,
) -> str:
    """
    Creates a high-CTR broadcast news thumbnail (1280x720).
    - Full-bleed cinematic subject imagery (cropped to remove any pre-baked corner archive badges).
    - True RGBA directional gradient for 100% text contrast.
    - Official Global Pulse 24 channel badge.
    - Massive 104px+ bold typography with heavy stroke + 3D drop-shadow.
    """
    if not output_path:
        out_dir = getattr(config, "OUTPUT_DIR", "output")
        os.makedirs(out_dir, exist_ok=True)
        safe = re.sub(r'[^a-zA-Z0-9]+', '-', title).strip('-').lower()[:30] or "news"
        output_path = os.path.join(out_dir, f"thumb_{safe}.jpg")

    # 1. Base Canvas & Subject Photo
    thumb = Image.new("RGB", (THUMB_W, THUMB_H), (12, 15, 23))

    if subject_image_path and os.path.exists(subject_image_path):
        try:
            with Image.open(subject_image_path) as s_img:
                s_img = s_img.convert("RGB")
                sw, sh = s_img.size
                target_ratio = THUMB_W / THUMB_H
                img_ratio = sw / sh

                # Smart crop to 16:9 keeping portrait subject prominent on the right half
                if abs(img_ratio - target_ratio) < 0.05:
                    photo = s_img.resize((THUMB_W, THUMB_H), Image.LANCZOS)
                elif img_ratio > target_ratio:
                    new_w = int(sh * target_ratio)
                    left = max(0, (sw - new_w) // 2)
                    photo = s_img.crop((left, 0, left + new_w, sh)).resize((THUMB_W, THUMB_H), Image.LANCZOS)
                else:
                    new_h = int(sw / target_ratio)
                    top = max(0, int((sh - new_h) * 0.12))
                    photo = s_img.crop((0, top, sw, min(sh, top + new_h))).resize((THUMB_W, THUMB_H), Image.LANCZOS)

                # Cleanly mask out any pre-stamped top-left archive badge (x < 460, y < 75)
                patch = photo.crop((0, 80, 460, 155)).filter(ImageFilter.GaussianBlur(radius=18))
                photo.paste(patch, (0, 0))

                photo = ImageEnhance.Contrast(photo).enhance(1.18)
                photo = ImageEnhance.Sharpness(photo).enhance(1.22)
                photo = ImageEnhance.Color(photo).enhance(1.10)
                thumb.paste(photo, (0, 0))
        except Exception as e:
            print(f"[news_thumbnail_gen] Error loading subject image '{subject_image_path}': {e}")
    else:
        # Fallback newsroom gradient canvas
        draw_bg = ImageDraw.Draw(thumb)
        for y in range(THUMB_H):
            ratio = y / THUMB_H
            r = int(12 + 10 * ratio)
            g = int(15 + 14 * ratio)
            b = int(24 + 22 * ratio)
            draw_bg.line([(0, y), (THUMB_W, y)], fill=(r, g, b))

    # 2. Smooth Directional Alpha Gradient Overlay (Left to Right)
    # Darkens the left 62% for dominant text contrast while keeping the right-side portrait vivid
    overlay = Image.new("RGBA", (THUMB_W, THUMB_H), (0, 0, 0, 0))
    d_overlay = ImageDraw.Draw(overlay)

    grad_width = int(THUMB_W * 0.66)
    for x in range(grad_width):
        factor = 1.0 - (x / grad_width)
        alpha = int(250 * (factor ** 1.30))
        d_overlay.line([(x, 0), (x, THUMB_H)], fill=(6, 8, 14, alpha))

    # Top soft vignette for badge contrast
    top_h = 115
    for y in range(top_h):
        alpha = int(150 * (1.0 - (y / top_h)))
        d_overlay.line([(0, y), (THUMB_W, y)], fill=(6, 8, 14, alpha))

    # Bottom soft vignette for accent bar
    bot_h = 90
    for y in range(bot_h):
        alpha = int(175 * (y / bot_h))
        d_overlay.line([(0, THUMB_H - bot_h + y), (THUMB_W, THUMB_H - bot_h + y)], fill=(6, 8, 14, alpha))

    thumb = Image.alpha_composite(thumb.convert("RGBA"), overlay).convert("RGB")
    draw = ImageDraw.Draw(thumb)

    # 3. Channel Branding Badge (Top Left)
    font_badge = _get_font(26, bold=True)
    clean_cat = category_label.replace("NEWS", "").strip() or "SPECIAL REPORT"
    badge_label = f"GLOBAL PULSE 24 | {clean_cat}".upper()

    bbox_b = font_badge.getbbox(badge_label)
    bw = bbox_b[2] - bbox_b[0]
    bh = bbox_b[3] - bbox_b[1]

    bx, by = 56, 46
    pill_w = bw + 66
    pill_h = bh + 24

    # Drop shadow under badge
    draw.rounded_rectangle(
        [(bx + 3, by + 4), (bx + pill_w + 3, by + pill_h + 4)],
        radius=8,
        fill=(0, 0, 0),
    )
    # Red badge background
    draw.rounded_rectangle(
        [(bx, by), (bx + pill_w, by + pill_h)],
        radius=8,
        fill=(220, 38, 38),
        outline=(255, 110, 110),
        width=2,
    )
    # Live white indicator dot
    dot_r = 6
    dot_cy = by + pill_h // 2
    dot_cx = bx + 22
    draw.ellipse([(dot_cx - dot_r, dot_cy - dot_r), (dot_cx + dot_r, dot_cy + dot_r)], fill=(255, 255, 255))
    draw.text((dot_cx + 15, by + 10), badge_label, font=font_badge, fill="white")

    # 4. Dominant High-CTR Typography (104px+ Bold with Stroke & 3D Drop-Shadow)
    lines = _extract_punchy_headline(title)

    font_size = 104 if len(lines) <= 2 else 96
    font_main = _get_font(font_size, bold=True, headline=True)

    # Ensure text fits cleanly inside the left 64% of the canvas
    max_text_w = int(THUMB_W * 0.64)
    for _ in range(7):
        widths = [font_main.getbbox(ln)[2] - font_main.getbbox(ln)[0] for ln in lines if ln]
        if widths and max(widths) > max_text_w and font_size > 64:
            font_size -= 6
            font_main = _get_font(font_size, bold=True, headline=True)
        else:
            break

    line_h = font_size + 18
    total_text_h = len(lines) * line_h
    avail_top = by + pill_h + 28
    avail_bot = THUMB_H - 36
    ty = max(avail_top, avail_top + (avail_bot - avail_top - total_text_h) // 2 - 10)
    tx = 56

    line_colors = [
        (255, 255, 255),  # Line 1: Pure White
        (255, 224, 0),    # Line 2: Vivid Warning Yellow
        (255, 255, 255),  # Line 3: Pure White
    ]

    for idx, ln in enumerate(lines):
        fill_col = line_colors[idx % len(line_colors)]
        # Multi-layer heavy black drop shadow + stroke for instant mobile readability
        for offset in range(2, 8, 2):
            draw.text((tx + offset, ty + offset), ln, font=font_main, fill=(0, 0, 0), stroke_width=3, stroke_fill=(0, 0, 0))
        draw.text((tx, ty), ln, font=font_main, fill=fill_col, stroke_width=3, stroke_fill=(0, 0, 0))
        ty += line_h

    # 5. Broadcast Lower-Third Accent Bar
    bar_y = THUMB_H - 16
    draw.rectangle([(0, bar_y), (THUMB_W, THUMB_H)], fill=(220, 38, 38))
    draw.rectangle([(0, bar_y - 3), (THUMB_W, bar_y)], fill=(255, 220, 0))

    thumb.save(output_path, "JPEG", quality=95)
    print(f"[news_thumbnail_gen] Saved broadcast thumbnail: {output_path}")
    return output_path


if __name__ == "__main__":
    t_path = generate_news_thumbnail(
        title="Trump Administration Drops 760,000 Enrollees Over Healthcare Claims",
        category_label="BREAKING REPORT",
    )
    print("Generated Thumbnail:", t_path)
