"""Fast Slapstick Engine
محرك الأنيميشن الخاطف (Hyper-Fast Slapstick Animation):
يقوم بصناعة حركة كارتونية سريعة جداً (تقطيعات خاطفة 0.5 - 0.8 ثانية، زوم سريع، هزات شاشة قوية عند الصدمات، ومزامنة دقيقة للمؤثرات).
"""
import sys
import io
import math
import random
import logging
from pathlib import Path
import numpy as np
from PIL import Image

if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
if sys.stderr.encoding != 'utf-8':
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from moviepy import (
    ImageClip,
    AudioFileClip,
    CompositeVideoClip,
    concatenate_videoclips,
    CompositeAudioClip,
)
from moviepy.audio.fx import MultiplyVolume
from tools.gemini_tool import get_gemini_client
from google.genai import types

logger = logging.getLogger(__name__)

SFX_DIR = PROJECT_ROOT / "assets" / "sfx"
OUTPUT_DIR = PROJECT_ROOT / "output" / "fast_slapstick_test"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

TARGET_W = 720
TARGET_H = 1280
FPS = 24

def generate_shot_image(prompt: str, filename: str) -> Path:
    out_path = OUTPUT_DIR / filename
    if out_path.exists() and out_path.stat().st_size > 10000:
        return out_path
        
    client = get_gemini_client()
    master_prompt = (
        f"Masterpiece 3D CGI Pixar style cartoon scene: {prompt}. "
        "Unique character: a funny goofy electric-blue tiny monster bug with giant bulging googly eyes, "
        "two springy antennas, shiny glossy vinyl texture, slapstick comedy expression, "
        "setting is an urban kitchen floor next to a giant tin can and soda bottle cap, "
        "dramatic studio lighting, vivid bright colors, vertical 9:16 mobile composition, 8k render, crystal clear."
    )
    
    print(f"🎨 جاري رسم اللقطة السريعة: {filename}...")
    response = client.models.generate_content(
        model="gemini-3.1-flash-image",
        contents=master_prompt,
        config=types.GenerateContentConfig(response_modalities=["IMAGE", "TEXT"])
    )
    for part in response.candidates[0].content.parts:
        if hasattr(part, "inline_data") and part.inline_data:
            out_path.write_bytes(part.inline_data.data)
            return out_path
            
    raise RuntimeError(f"Failed to generate {filename}")

def prepare_vertical_frame(img_path: Path) -> np.ndarray:
    img = Image.open(img_path)
    w, h = img.size
    target_ratio = TARGET_W / TARGET_H
    if w / h > target_ratio:
        new_w = int(h * target_ratio)
        offset_x = (w - new_w) // 2
        img = img.crop((offset_x, 0, offset_x + new_w, h))
    else:
        new_h = int(w / target_ratio)
        offset_y = (h - new_h) // 2
        img = img.crop((0, offset_y, w, offset_y + new_h))
    img = img.resize((TARGET_W, TARGET_H), Image.Resampling.LANCZOS)
    return np.array(img)

def create_punch_zoom_clip(base_frame: np.ndarray, duration: float = 0.8, zoom_start: float = 1.0, zoom_end: float = 1.25) -> ImageClip:
    """زوم سريع خاطف على عين الشخصية لزيادة عنصر الكوميديا والمفاجأة."""
    frames = []
    num_frames = int(duration * FPS)
    h, w, c = base_frame.shape
    pil_base = Image.fromarray(base_frame)
    
    for i in range(num_frames):
        t = i / max(1, num_frames - 1)
        # Fast ease-in zoom
        cur_zoom = zoom_start + (zoom_end - zoom_start) * (t ** 1.8)
        crop_w = int(w / cur_zoom)
        crop_h = int(h / cur_zoom)
        x1 = (w - crop_w) // 2
        y1 = (h - crop_h) // 2
        cropped = pil_base.crop((x1, y1, x1 + crop_w, y1 + crop_h))
        resized = cropped.resize((w, h), Image.Resampling.BILINEAR)
        frames.append(np.array(resized))
        
    from moviepy.video.io.ImageSequenceClip import ImageSequenceClip
    return ImageSequenceClip(frames, fps=FPS)

def create_impact_shake_clip(base_frame: np.ndarray, duration: float = 0.6, shake_intensity: int = 24) -> ImageClip:
    """هزة شاشة عنيفة عند الصدمة (Screen Shake) تحاكي ارتطام كارتون لارفا الخاطف."""
    frames = []
    num_frames = int(duration * FPS)
    h, w, c = base_frame.shape
    pil_base = Image.fromarray(base_frame)
    
    for i in range(num_frames):
        t = i / max(1, num_frames - 1)
        decay = math.exp(-6.0 * t)
        dx = int(random.uniform(-1, 1) * shake_intensity * decay)
        dy = int(random.uniform(-1, 1) * shake_intensity * decay)
        
        # Roll / shift image
        shifted = np.roll(base_frame, dx, axis=1)
        shifted = np.roll(shifted, dy, axis=0)
        frames.append(shifted)
        
    from moviepy.video.io.ImageSequenceClip import ImageSequenceClip
    return ImageSequenceClip(frames, fps=FPS)

def run_fast_slapstick_test():
    print("🚀 بدء صناعة حلقة كارتونية سريعة وخاطفة (Hyper-Fast Slapstick)...")
    
    # 4 لقطات خاطفة متتابعة
    shots_info = [
        ("The blue monster bug sees a shiny golden peanut, eyes bulging out in comic shock, gasp expression", "shot_1_gasp.png", "zoom", 0.8, "gasp.wav", 0.1),
        ("The blue bug coils like an elastic spring and shoots forward into the air, flying high speed", "shot_2_leap.png", "punch", 0.6, "boing.wav", 0.05),
        ("The blue bug crashes face-first flat into a metal tin can, head squashed flat with comic stars", "shot_3_bonk.png", "shake", 0.7, "bonk.wav", 0.05),
        ("The blue bug slides down the tin can into a puddle of goo, dizzy spiral eyes, silly smile", "shot_4_splat.png", "zoom", 1.1, "splat.wav", 0.1),
    ]
    
    video_clips = []
    audio_clips = []
    current_time = 0.0
    
    for prompt, filename, effect, dur, sfx, sfx_offset in shots_info:
        img_path = generate_shot_image(prompt, filename)
        frame_arr = prepare_vertical_frame(img_path)
        
        if effect == "shake":
            clip = create_impact_shake_clip(frame_arr, duration=dur, shake_intensity=28)
        elif effect == "punch":
            clip = create_punch_zoom_clip(frame_arr, duration=dur, zoom_start=1.0, zoom_end=1.35)
        else:
            clip = create_punch_zoom_clip(frame_arr, duration=dur, zoom_start=1.0, zoom_end=1.15)
            
        video_clips.append(clip)
        
        # Audio cue
        sfx_path = SFX_DIR / sfx
        if sfx_path.exists():
            sfx_audio = AudioFileClip(str(sfx_path)).with_start(current_time + sfx_offset)
            audio_clips.append(sfx_audio)
            
        current_time += dur
        
    final_video = concatenate_videoclips(video_clips, method="compose")
    total_dur = final_video.duration
    
    # Funny BGM
    bgm_path = SFX_DIR / "funny_bgm.wav"
    if bgm_path.exists():
        bgm = AudioFileClip(str(bgm_path)).subclipped(0, min(total_dur, 12.0)).with_effects([MultiplyVolume(0.35)])
        all_audio = [bgm] + audio_clips
        final_video = final_video.with_audio(CompositeAudioClip(all_audio))
    elif audio_clips:
        final_video = final_video.with_audio(CompositeAudioClip(audio_clips))
        
    out_file = OUTPUT_DIR / "hyper_fast_larva_style.mp4"
    print("🎬 جاري رندر وتصدير الفيديو السريع...")
    final_video.write_videofile(
        str(out_file),
        fps=FPS,
        codec="libx264",
        audio_codec="aac",
        logger=None
    )
    print(f"✅ تم الانتهاء بنجاح! مسار الفيديو:\n{out_file}")
    return out_file

if __name__ == "__main__":
    run_fast_slapstick_test()
