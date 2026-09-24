#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
news_thumbnail_gen.py — High-CTR Breaking News Thumbnail Generation Engine.

Features:
- Standard 1280x720 (16:9) resolution with high visual contrast.
- Vibrant broadcast news color schemes (Crimson Red #D90429, Warning Yellow #FFD000, Deep Navy #0F172A).
- Urgent category badges (🔴 BREAKING, JUST IN, URGENT, AI ALERT).
- Real subject cutout / portrait integration with subtle outer stroke/glow.
- High-impact bold typography (2-4 punchy words) with multi-layered drop shadow for maximum mobile CTR.
"""

import os
import sys
import re
import random
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter

import config

THUMB_W = 1280
THUMB_H = 720


def _get_font(size: int, bold: bool = True) -> ImageFont.ImageFont:
    font_names = ["impact.ttf", "arialbd.ttf", "segoeuib.ttf", "tahomabd.ttf"] if bold else ["arial.ttf", "segoeui.ttf"]
    for fn in font_names:
        try:
            return ImageFont.truetype(fn, size)
        except Exception:
            continue
    return ImageFont.load_default()


def _extract_punchy_headline(title: str) -> str:
    """Condenses a long headline into 2-4 punchy high-CTR words."""
    clean = re.sub(r'[:\-–—].*$', '', title).strip()
    words = clean.split()
    if len(words) <= 4:
        return clean.upper()

    # Priority keywords if found
    for trigger in ["EXECUTIVE ORDER", "BREAKING NEWS", "JUST ANNOUNCED", "OPENAI LEAK", "TRUMP SAYS", "NEW DIRECTIVE"]:
        if trigger in clean.upper():
            return trigger

    # Filter filler words
    meaningful = [w for w in words if w.lower() not in ("the", "a", "an", "of", "and", "in", "to", "over", "for", "on", "from")]
    if len(meaningful) >= 3:
        return " ".join(meaningful[:3]).upper()
    return " ".join(words[:3]).upper()


def generate_news_thumbnail(
    title: str,
    category_label: str = "BREAKING",
    subject_image_path: str = None,
    output_path: str = None,
) -> str:
    """
    Creates a high-CTR breaking news thumbnail.
    """
    if not output_path:
        out_dir = getattr(config, "OUTPUT_DIR", "output")
        os.makedirs(out_dir, exist_ok=True)
        safe = re.sub(r'[^a-zA-Z0-9]+', '-', title).strip('-').lower()[:30] or "news"
        output_path = os.path.join(out_dir, f"thumb_{safe}.jpg")

    # 1. Base Canvas
    thumb = Image.new("RGB", (THUMB_W, THUMB_H), (15, 17, 26))

    # If subject image provided, create a textured background from it
    if subject_image_path and os.path.exists(subject_image_path):
        try:
            with Image.open(subject_image_path) as s_img:
                s_img = s_img.convert("RGB")
                bg = s_img.resize((THUMB_W, THUMB_H), Image.LANCZOS)
                bg = bg.filter(ImageFilter.GaussianBlur(radius=22))
                bg = ImageEnhance.Brightness(bg).enhance(0.40)
                thumb.paste(bg, (0, 0))

                # Place subject figure on right side
                sw, sh = s_img.size
                target_sh = int(THUMB_H * 0.90)
                target_sw = int(sw * (target_sh / max(1, sh)))
                target_sw = min(target_sw, int(THUMB_W * 0.52))

                subject_resized = s_img.resize((target_sw, target_sh), Image.LANCZOS)
                subject_resized = ImageEnhance.Contrast(subject_resized).enhance(1.25)
                subject_resized = ImageEnhance.Sharpness(subject_resized).enhance(1.3)

                pos_x = THUMB_W - target_sw - 20
                pos_y = (THUMB_H - target_sh) // 2

                # Outer border around subject
                draw_t = ImageDraw.Draw(thumb)
                draw_t.rectangle(
                    [(pos_x - 4, pos_y - 4), (pos_x + target_sw + 4, pos_y + target_sh + 4)],
                    outline=(220, 38, 38),
                    width=3,
                )
                thumb.paste(subject_resized, (pos_x, pos_y))
        except Exception as e:
            print(f"[news_thumbnail_gen] Error processing subject image: {e}")

    draw = ImageDraw.Draw(thumb)

    # 2. Dark contrast gradient on left side for text readability
    for x in range(int(THUMB_W * 0.65)):
        alpha = int(240 * (1.0 - (x / (THUMB_W * 0.65))))
        draw.line([(x, 0), (x, THUMB_H)], fill=(10, 12, 18))

    # 3. Urgent Category Badge (Top Left)
    font_badge = _get_font(34, bold=True)
    badge_label = category_label.upper()
    bbox_b = font_badge.getbbox(badge_label)
    bw = bbox_b[2] - bbox_b[0]
    bh = bbox_b[3] - bbox_b[1]

    bx, by = 60, 60
    pill_w = bw + 64
    pill_h = bh + 24
    draw.rounded_rectangle(
        [(bx, by), (bx + pill_w, by + pill_h)],
        radius=8,
        fill=(220, 38, 38),
    )
    # Draw solid white indicator circle
    dot_r = 7
    dot_cy = by + pill_h // 2
    dot_cx = bx + 24
    draw.ellipse([(dot_cx - dot_r, dot_cy - dot_r), (dot_cx + dot_r, dot_cy + dot_r)], fill=(255, 255, 255))
    draw.text((dot_cx + 18, by + 12), badge_label, font=font_badge, fill="white")

    # 4. Punchy Typography (3-4 words)
    punchy_words = _extract_punchy_headline(title)
    font_main = _get_font(74, bold=True)

    lines = punchy_words.split()
    line1 = " ".join(lines[:2])
    line2 = " ".join(lines[2:]) if len(lines) > 2 else ""

    ty = by + bh + 65
    tx = 60

    # Draw Line 1 (White with heavy black drop shadow)
    if line1:
        # Shadow
        for dx in range(-4, 5):
            for dy in range(-4, 5):
                draw.text((tx + dx, ty + dy), line1, font=font_main, fill=(0, 0, 0))
        draw.text((tx, ty), line1, font=font_main, fill=(255, 255, 255))
        ty += 85

    # Draw Line 2 (Vivid Yellow for high CTR hook)
    if line2:
        for dx in range(-4, 5):
            for dy in range(-4, 5):
                draw.text((tx + dx, ty + dy), line2, font=font_main, fill=(0, 0, 0))
        draw.text((tx, ty), line2, font=font_main, fill=(255, 220, 0))
        ty += 85

    # 5. Bottom Accent Line
    draw.rectangle([(0, THUMB_H - 12), (THUMB_W, THUMB_H)], fill=(220, 38, 38))

    thumb.save(output_path, "JPEG", quality=94)
    print(f"[news_thumbnail_gen] Saved high-CTR thumbnail: {output_path}")
    return output_path


if __name__ == "__main__":
    t_path = generate_news_thumbnail(
        title="Trump Administration Drops 760,000 Enrollees Over Healthcare Claims",
        category_label="BREAKING REPORT",
    )
    print("Generated Thumbnail:", t_path)
