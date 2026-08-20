import os
import math
import wave
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter
from moviepy import (
    AudioFileClip, VideoClip, concatenate_videoclips,
    AudioArrayClip
)
from moviepy.video.fx import CrossFadeIn, FadeIn, FadeOut

BASE_DIR = r"c:\Users\soham\OneDrive\Desktop\TASK-VIDEO"
IMG_DIR = os.path.join(BASE_DIR, "assets", "images")
AUDIO_DIR = os.path.join(BASE_DIR, "assets", "audio")
DELIVERABLES_DIR = os.path.join(BASE_DIR, "deliverables")

W, H = 1080, 1920
CROSSFADE = 0.30

# Original Scene Configuration (Exact 36.2s timeline)
SCENE_CONFIG = [
    {
        "id": 1,
        "img": "scene_1.jpg",
        "audio": "scene_1.wav",
        "duration": 3.5,
        "motion": "push_in_pan_down",
        "tag": "INDUSTRY TRANSFORMATION",
        "title": "BUSINESS IS MOVING FASTER",
        "highlight_word": "FASTER",
        "sub": "Speed & agility define modern success",
        "badge_type": "standard",
        "vfx": "light_shimmer"
    },
    {
        "id": 2,
        "img": "scene_2.jpg",
        "audio": "scene_2.wav",
        "duration": 6.8,
        "motion": "pull_back_vignette",
        "tag": "THE MODERN BOTTLENECK",
        "title": "MANUAL TASKS SLOW YOU DOWN",
        "highlight_word": "SLOW",
        "sub": "Repetitive workflows bottleneck company growth",
        "badge_type": "warning",
        "vfx": "dark_focus"
    },
    {
        "id": 3,
        "img": "scene_3.jpg",
        "audio": "scene_3.wav",
        "duration": 4.2,
        "motion": "snap_zoom_pulse",
        "tag": "AUTONOMOUS INTELLIGENCE",
        "title": "WHAT IF AI COULD DO THE WORK?",
        "highlight_word": "AI",
        "sub": "Transforming operations with next-gen AI",
        "badge_type": "cyan_glow",
        "vfx": "radial_pulse"
    },
    {
        "id": 4,
        "img": "scene_4.jpg",
        "audio": "scene_4.wav",
        "duration": 5.4,
        "motion": "regal_push_in",
        "tag": "ENTERPRISE AI SOLUTIONS",
        "title": "MEET AD TECH",
        "highlight_word": "AD TECH",
        "sub": "Your Partner in Intelligent Automation",
        "badge_type": "brand_gold",
        "vfx": "brand_aura"
    },
    {
        "id": 5,
        "img": "scene_5.jpg",
        "audio": "scene_5.wav",
        "duration": 10.8,
        "motion": "pan_scan_high_tech",
        "tag": "FULL-STACK CAPABILITIES",
        "title": "END-TO-END AI ECOSYSTEM",
        "highlight_word": "AI ECOSYSTEM",
        "sub": "Building scalable software for future enterprise",
        "badge_type": "capabilities_grid",
        "vfx": "scanline_sweep"
    },
    {
        "id": 6,
        "img": "scene_6.jpg",
        "audio": "scene_6.wav",
        "duration": 5.5,
        "motion": "energetic_pull_out",
        "tag": "THE AI ADVANTAGE",
        "title": "ACCELERATE YOUR BUSINESS",
        "highlight_word": "ACCELERATE",
        "sub": "Work Smarter • Move Faster • Scale Effortlessly",
        "badge_type": "triple_pill",
        "vfx": "contrast_bloom"
    },
    {
        "id": 7,
        "img": "scene_7.jpg",
        "audio": "scene_7.wav",
        "duration": 5.0,
        "motion": "majestic_finale",
        "tag": "FUTURE-READY ENTERPRISE",
        "title": "MAKE YOUR BUSINESS AI-FIRST",
        "highlight_word": "AI-FIRST",
        "sub": "AD TECH Enterprises Pvt. Ltd. | Building Future Tech Talent",
        "badge_type": "finale_signature",
        "vfx": "starlight_shimmer"
    },
]

TOTAL_DURATION = sum(c["duration"] for c in SCENE_CONFIG) - (len(SCENE_CONFIG) - 1) * CROSSFADE


def get_font(size, bold=True):
    font_names = ["segoeuib.ttf" if bold else "segoeui.ttf", "arialbd.ttf" if bold else "arial.ttf", "calibrib.ttf"]
    for fn in font_names:
        fp = os.path.join(r"C:\Windows\Fonts", fn)
        if os.path.exists(fp):
            try:
                return ImageFont.truetype(fp, size)
            except Exception:
                pass
    return ImageFont.load_default()


def grade_image(img):
    """Cinematic HDR grade: deeper contrast, enriched color tone, sharp clarity."""
    enh_c = ImageEnhance.Contrast(img).enhance(1.08)
    enh_s = ImageEnhance.Color(enh_c).enhance(1.05)
    enh_b = ImageEnhance.Brightness(enh_s).enhance(1.02)
    return enh_b


def pop_out_ease(p, s=1.35):
    """Snappy zoom pop-out easing curve from center with clean overshoot."""
    t = min(max(p, 0.0), 1.0)
    return 1.0 + (s + 1.0) * ((t - 1.0) ** 3) + s * ((t - 1.0) ** 2)


_CARD_SURFACE_CACHE = {}


def build_card_surface(cfg):
    """Draws the crisp, high-definition card surface once onto an isolated buffer."""
    badge_type = cfg.get("badge_type", "standard")
    font_title = get_font(52, bold=True)
    font_sub = get_font(28, bold=False)
    font_tag = get_font(22, bold=True)
    font_pill = get_font(26, bold=True)

    card_w = W - 120  # 960px
    if badge_type == "capabilities_grid":
        card_h = 320
    elif badge_type == "triple_pill":
        card_h = 300
    elif badge_type == "finale_signature":
        card_h = 280
    else:
        card_h = 240

    pad = 32
    surf_w = card_w + pad * 2
    surf_h = card_h + pad * 2
    surf = Image.new("RGBA", (surf_w, surf_h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(surf)

    cx = pad
    cy = pad

    glow_color = (0, 200, 255)
    if badge_type == "warning":
        glow_color = (255, 120, 0)
    elif badge_type == "brand_gold":
        glow_color = (0, 180, 255)
    elif badge_type == "cyan_glow":
        glow_color = (0, 230, 255)

    # Multi-layer soft neon glow
    for g_pad, alpha in [(16, 25), (10, 42), (4, 65)]:
        g_box = [cx - g_pad, cy - g_pad, cx + card_w + g_pad, cy + card_h + g_pad]
        draw.rounded_rectangle(g_box, radius=28 + g_pad, fill=(glow_color[0], glow_color[1], glow_color[2], alpha))

    # Frosted solid sapphire card body (100% opaque to block all background distractions)
    card_box = [cx, cy, cx + card_w, cy + card_h]
    border_color = (0, 210, 255, 230) if badge_type != "warning" else (255, 140, 40, 230)
    draw.rounded_rectangle(card_box, radius=24, fill=(7, 15, 34, 255), outline=border_color, width=2)

    # Top-edge neon laser line
    line_col = (140, 245, 255, 255) if badge_type != "warning" else (255, 200, 120, 255)
    draw.line([cx + 36, cy, cx + card_w - 36, cy], fill=line_col, width=3)

    # Tag Badge (Top Pill)
    tag_text = cfg["tag"]
    tbbox = draw.textbbox((0, 0), tag_text, font=font_tag)
    tw = tbbox[2] - tbbox[0]
    tag_bg = [(surf_w - tw) // 2 - 18, cy + 24, (surf_w + tw) // 2 + 18, cy + 54]
    draw.rounded_rectangle(tag_bg, radius=10, fill=(0, 75, 160, 255), outline=(0, 220, 255, 240), width=1)
    draw.text(((surf_w - tw) // 2, cy + 27), tag_text, font=font_tag, fill=(0, 245, 255, 255))

    # Content Area Rendering
    if badge_type == "capabilities_grid":
        pills = [
            ("Custom AI Agents", (0, 210, 255)),
            ("Intelligent Automation", (100, 240, 255)),
            ("Data & AI Solutions", (0, 220, 180)),
            ("Scalable Software", (255, 200, 80))
        ]
        row1_y = cy + 80
        row2_y = cy + 150
        gap = 20
        w1 = draw.textbbox((0, 0), pills[0][0], font=font_pill)[2] - draw.textbbox((0, 0), pills[0][0], font=font_pill)[0] + 36
        w2 = draw.textbbox((0, 0), pills[1][0], font=font_pill)[2] - draw.textbbox((0, 0), pills[1][0], font=font_pill)[0] + 36
        total_w = w1 + w2 + gap
        start_x = (surf_w - total_w) // 2

        draw.rounded_rectangle([start_x, row1_y, start_x + w1, row1_y + 52], radius=14, fill=(12, 28, 58, 255), outline=(0, 200, 255, 220), width=1)
        draw.text((start_x + 18, row1_y + 10), pills[0][0], font=font_pill, fill=(240, 250, 255, 255))

        p2_x = start_x + w1 + gap
        draw.rounded_rectangle([p2_x, row1_y, p2_x + w2, row1_y + 52], radius=14, fill=(12, 28, 58, 255), outline=(0, 200, 255, 220), width=1)
        draw.text((p2_x + 18, row1_y + 10), pills[1][0], font=font_pill, fill=(240, 250, 255, 255))

        w3 = draw.textbbox((0, 0), pills[2][0], font=font_pill)[2] - draw.textbbox((0, 0), pills[2][0], font=font_pill)[0] + 36
        w4 = draw.textbbox((0, 0), pills[3][0], font=font_pill)[2] - draw.textbbox((0, 0), pills[3][0], font=font_pill)[0] + 36
        total_w2 = w3 + w4 + gap
        start_x2 = (surf_w - total_w2) // 2

        draw.rounded_rectangle([start_x2, row2_y, start_x2 + w3, row2_y + 52], radius=14, fill=(12, 28, 58, 255), outline=(0, 200, 255, 220), width=1)
        draw.text((start_x2 + 18, row2_y + 10), pills[2][0], font=font_pill, fill=(240, 250, 255, 255))

        p4_x = start_x2 + w3 + gap
        draw.rounded_rectangle([p4_x, row2_y, p4_x + w4, row2_y + 52], radius=14, fill=(12, 28, 58, 255), outline=(255, 190, 60, 220), width=1)
        draw.text((p4_x + 18, row2_y + 10), pills[3][0], font=font_pill, fill=(255, 240, 200, 255))

        sub_text = cfg["sub"]
        sbbox = draw.textbbox((0, 0), sub_text, font=font_sub)
        sw = sbbox[2] - sbbox[0]
        draw.text(((surf_w - sw) // 2, cy + 240), sub_text, font=font_sub, fill=(190, 225, 255, 255))

    elif badge_type == "triple_pill":
        items = [
            ("WORK SMARTER", (80, 255, 160)),
            ("MOVE FASTER", (0, 230, 255)),
            ("SCALE EFFORTLESSLY", (255, 210, 80))
        ]
        row_y = cy + 78
        gap = 14
        widths = [draw.textbbox((0, 0), it[0], font=font_pill)[2] - draw.textbbox((0, 0), it[0], font=font_pill)[0] + 32 for it in items]
        total_w = sum(widths) + gap * 2
        start_x = (surf_w - total_w) // 2

        cur_x = start_x
        for (label, col), pw in zip(items, widths):
            draw.rounded_rectangle([cur_x, row_y, cur_x + pw, row_y + 50], radius=14, fill=(12, 24, 48, 255), outline=col, width=1)
            draw.text((cur_x + 16, row_y + 10), label, font=font_pill, fill=col)
            cur_x += pw + gap

        sub_title = "BUILD YOUR AI ADVANTAGE"
        st_font = get_font(38, bold=True)
        st_bbox = draw.textbbox((0, 0), sub_title, font=st_font)
        st_w = st_bbox[2] - st_bbox[0]
        draw.text(((surf_w - st_w) // 2, cy + 155), sub_title, font=st_font, fill=(255, 255, 255, 255))

        sub_text = "Transform operations with intelligent systems"
        sbbox = draw.textbbox((0, 0), sub_text, font=font_sub)
        sw = sbbox[2] - sbbox[0]
        draw.text(((surf_w - sw) // 2, cy + 225), sub_text, font=font_sub, fill=(190, 225, 255, 255))

    else:
        title_text = cfg["title"]
        t_font = font_title
        tbbox = draw.textbbox((0, 0), title_text, font=t_font)
        tw = tbbox[2] - tbbox[0]
        if tw > card_w - 60:
            t_font = get_font(42, bold=True)
            tbbox = draw.textbbox((0, 0), title_text, font=t_font)
            tw = tbbox[2] - tbbox[0]

        tx = (surf_w - tw) // 2
        ty = cy + 74
        draw.text((tx + 2, ty + 2), title_text, font=t_font, fill=(0, 0, 0, 220))
        draw.text((tx, ty), title_text, font=t_font, fill=(255, 255, 255, 255))

        sub_text = cfg["sub"]
        sbbox = draw.textbbox((0, 0), sub_text, font=font_sub)
        sw = sbbox[2] - sbbox[0]
        sub_font = font_sub
        if sw > card_w - 60:
            sub_font = get_font(24, bold=False)
            sbbox = draw.textbbox((0, 0), sub_text, font=sub_font)
            sw = sbbox[2] - sbbox[0]
        draw.text(((surf_w - sw) // 2, cy + 150), sub_text, font=sub_font, fill=(190, 225, 255, 255))

    return surf, card_w, card_h


def get_cached_card(cfg):
    cid = cfg["id"]
    if cid not in _CARD_SURFACE_CACHE:
        _CARD_SURFACE_CACHE[cid] = build_card_surface(cfg)
    return _CARD_SURFACE_CACHE[cid]


def build_scene_video(cfg):
    dur = cfg["duration"]
    img_path = os.path.join(IMG_DIR, cfg["img"])
    base_raw = Image.open(img_path).convert("RGBA")
    graded_raw = grade_image(base_raw)

    bw, bh = graded_raw.size
    target_ratio = W / H
    current_ratio = bw / bh

    if current_ratio > target_ratio:
        new_w = int(bh * target_ratio)
        offset_x = (bw - new_w) // 2
        crop_box = (offset_x, 0, offset_x + new_w, bh)
    else:
        new_h = int(bw / target_ratio)
        offset_y = (bh - new_h) // 2
        crop_box = (0, offset_y, bw, offset_y + new_h)

    base_frame = graded_raw.crop(crop_box).resize((W, H), Image.Resampling.LANCZOS)
    motion = cfg["motion"]
    card_surf, card_w, card_h = get_cached_card(cfg)

    def make_frame(t):
        progress = t / dur

        # God-Level 3D Dynamic Camera Kinetics
        if motion == "push_in_pan_down":
            scale = 1.0 + 0.12 * (progress ** 1.1)
            tx = int(15 * math.sin(progress * math.pi))
            ty = int(35 * progress)
        elif motion == "pull_back_vignette":
            scale = 1.14 - 0.11 * (progress ** 0.9)
            tx = int(-20 * math.sin(progress * math.pi))
            ty = int(-25 * progress)
        elif motion == "snap_zoom_pulse":
            scale = 1.0 + 0.16 * (1.0 - math.exp(-3.5 * progress))
            tx = 0
            ty = int(10 * math.sin(progress * 2 * math.pi))
        elif motion == "regal_push_in":
            scale = 1.04 + 0.13 * (progress ** 1.2)
            tx = int(18 * progress)
            ty = int(-20 * progress)
        elif motion == "pan_scan_high_tech":
            scale = 1.12
            tx = int(60 * (progress - 0.5))
            ty = int(15 * math.sin(progress * math.pi))
        elif motion == "energetic_pull_out":
            scale = 1.16 - 0.13 * (progress ** 0.85)
            tx = int(-30 * (progress - 0.5))
            ty = int(20 * progress)
        else:  # majestic_finale
            scale = 1.0 + 0.12 * progress
            tx = 0
            ty = int(-25 * progress)

        sw = int(W * scale)
        sh = int(H * scale)
        scaled = base_frame.resize((sw, sh), Image.Resampling.BILINEAR)

        left = (sw - W) // 2 + tx
        top = (sh - H) // 2 + ty
        left = max(0, min(left, sw - W))
        top = max(0, min(top, sh - H))

        frame = scaled.crop((left, top, left + W, top + H)).copy()

        # Dynamic Vignette / Focus Shader
        if cfg.get("vfx") == "dark_focus":
            v_overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            v_draw = ImageDraw.Draw(v_overlay)
            v_alpha = int(45 + 20 * math.sin(progress * math.pi))
            v_draw.rectangle([0, 0, W, H], fill=(0, 0, 0, v_alpha))
            frame = Image.alpha_composite(frame, v_overlay)

        # Snappy Pop-Out Spring Physics Entrance
        card_t = min(max(t / 0.50, 0.0), 1.0)
        eased_pop = pop_out_ease(card_t)

        final_card_y = H - card_h - 140
        start_card_y = H - card_h - 60
        cur_card_y = int(start_card_y + (final_card_y - start_card_y) * card_t)

        cw = int(card_surf.width * eased_pop)
        ch = int(card_surf.height * eased_pop)
        if cw > 10 and ch > 10:
            sc_card = card_surf.resize((cw, ch), Image.Resampling.BILINEAR)
            cx_pos = (W - cw) // 2
            cy_pos = cur_card_y + (card_surf.height - ch) // 2
            frame.paste(sc_card, (cx_pos, cy_pos), sc_card)

        return np.array(frame.convert("RGB"))

    return VideoClip(make_frame, duration=dur)


def build_master_soundtrack(total_dur, sample_rate=44100):
    """Builds a high-impact, studio-mastered soundtrack:
    1. Crystal-clear, loud broadcast-standard voiceover (normalized to 0.92 peak)
    2. Subtle, warm ambient background pad (ducked during speech)
    3. Studio soft limiter with analog headroom."""
    num_samples = int((total_dur + 1.0) * sample_rate)
    master_vo = np.zeros((num_samples, 2), dtype=np.float32)

    current_time = 0.0
    for idx, cfg in enumerate(SCENE_CONFIG):
        wav_path = os.path.join(AUDIO_DIR, cfg["audio"])
        clip = AudioFileClip(wav_path)
        arr = clip.to_soundarray(fps=sample_rate)

        # Vocal normalization & punch
        sc_peak = np.max(np.abs(arr))
        if sc_peak > 1e-4:
            arr = (arr / sc_peak) * 0.92

        # Short in/out fades so each clip's edit point never hard-cuts mid-waveform
        # (an abrupt cut here produces an audible click/pop at the splice).
        fade_len = min(int(0.02 * sample_rate), len(arr) // 2)
        if fade_len > 0:
            fade_in = np.linspace(0.0, 1.0, fade_len)[:, None]
            fade_out = np.linspace(1.0, 0.0, fade_len)[:, None]
            arr[:fade_len] *= fade_in
            arr[-fade_len:] *= fade_out

        start_sample = int((current_time + 0.12) * sample_rate)
        end_sample = start_sample + len(arr)

        if end_sample <= num_samples:
            master_vo[start_sample:end_sample] += arr

        current_time += cfg["duration"] - CROSSFADE

    # Warm, cinematic ambient music pad
    # (kept quiet enough that it stays a felt bed rather than an audible drone
    # during the near-silent gaps between scene voice lines, where ducking
    # relaxes back toward full volume and would otherwise expose it)
    t = np.linspace(0, total_dur + 1.0, num_samples, endpoint=False)
    pad_l = 0.016 * (np.sin(2 * np.pi * 110.0 * t) + np.sin(2 * np.pi * 164.8 * t + 0.2))
    pad_r = 0.016 * (np.sin(2 * np.pi * 110.3 * t + 0.1) + np.sin(2 * np.pi * 165.2 * t + 0.3))

    # Auto-ducking during speech
    vo_env = np.maximum(np.abs(master_vo[:, 0]), np.abs(master_vo[:, 1]))
    duck = 1.0 - 0.70 * np.clip(vo_env * 2.5, 0.0, 1.0)
    pad_l *= duck
    pad_r *= duck

    bg_bed = np.vstack([pad_l, pad_r]).T
    fade_len = int(0.6 * sample_rate)
    bg_bed[:fade_len] *= np.linspace(0, 1, fade_len)[:, None]
    bg_bed[-fade_len:] *= np.linspace(1, 0, fade_len)[:, None]

    target_samples = int(total_dur * sample_rate)
    master_mix = master_vo[:target_samples] + bg_bed[:target_samples]

    peak = np.max(np.abs(master_mix))
    if peak > 0.95:
        master_mix = (master_mix / peak) * 0.95

    return AudioArrayClip(master_mix, fps=sample_rate)


def main():
    print(f"==================================================")
    print(f"Rendering Original Master Video (Exact 36.2s)")
    print(f"Total target duration: {TOTAL_DURATION:.2f}s | Resolution: {W}x{H}")
    print(f"==================================================")

    vclips = [build_scene_video(cfg) for cfg in SCENE_CONFIG]

    # Crossfade timeline transitions
    faded_vclips = [vclips[0].with_effects([FadeIn(0.4)])]
    for v in vclips[1:]:
        faded_vclips.append(v.with_effects([CrossFadeIn(CROSSFADE)]))
    faded_vclips[-1] = faded_vclips[-1].with_effects([FadeOut(0.6)])

    final_video = concatenate_videoclips(faded_vclips, padding=-CROSSFADE, method="compose")

    print("Building master studio soundtrack...")
    master_audio = build_master_soundtrack(final_video.duration)
    final_video = final_video.with_audio(master_audio)

    os.makedirs(DELIVERABLES_DIR, exist_ok=True)
    out_file_1 = os.path.join(DELIVERABLES_DIR, "ad_tech_promo_vertical_final.mp4")
    out_file_2 = os.path.join(DELIVERABLES_DIR, "ad_tech_promo_vertical_advanced.mp4")
    root_file = os.path.join(BASE_DIR, "final.mp4")

    print("Rendering final master MP4 video to:", out_file_1)
    final_video.write_videofile(
        out_file_1, fps=30, codec="libx264", audio_codec="aac", threads=4
    )

    print("Copying deliverables to backup and root final.mp4...")
    import shutil
    shutil.copy(out_file_1, out_file_2)
    shutil.copy(out_file_1, root_file)

    print("Original 36.2s Master Render Completed Successfully!")


if __name__ == "__main__":
    main()
