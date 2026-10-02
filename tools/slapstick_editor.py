"""Slapstick Video & Audio Editor
مونتير الكوميديا الصامتة - يقوم بدمج اللقطات الكارتونية وتركيب المؤثرات الصوتية والموسيقى بدقة عالية وبدون أي كلام.
يتميز بحركات سريعة خاطفة (Punch Zooms & Impact Screen Shakes) تحاكي كارتون لارفا تماماً.
"""
import sys
import io
import math
import random
import logging
from pathlib import Path
import numpy as np
from PIL import Image
from moviepy import (
    ImageClip,
    AudioFileClip,
    CompositeVideoClip,
    concatenate_videoclips,
    CompositeAudioClip,
)
from moviepy.audio.fx import MultiplyVolume
from moviepy.video.io.ImageSequenceClip import ImageSequenceClip

if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
if sys.stderr.encoding != 'utf-8':
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SFX_DIR = PROJECT_ROOT / "assets" / "sfx"

TARGET_WIDTH = 540
TARGET_HEIGHT = 960
FPS = 18

def _fit_image_vertical(image_path: Path, target_w: int = TARGET_WIDTH, target_h: int = TARGET_HEIGHT) -> np.ndarray:
    """تعديل وتوسيط الصورة لتناسب أبعاد الموبايل والريلز (9:16) بدقة عالية."""
    img = Image.open(image_path)
    src_w, src_h = img.size
    target_ratio = target_w / target_h
    
    if src_w / src_h > target_ratio:
        new_w = int(src_h * target_ratio)
        offset_x = (src_w - new_w) // 2
        img = img.crop((offset_x, 0, offset_x + new_w, src_h))
    else:
        new_h = int(src_w / target_ratio)
        offset_y = (src_h - new_h) // 2
        img = img.crop((0, offset_y, src_w, offset_y + new_h))
        
    img = img.resize((target_w, target_h), Image.Resampling.LANCZOS)
    return np.array(img)

def _create_punch_zoom(base_frame: np.ndarray, duration: float, zoom_end: float = 1.25) -> ImageSequenceClip:
    """زوم سريع ومفاجئ يركز على رد الفعل الهزلي."""
    frames = []
    num_frames = max(1, int(duration * FPS))
    h, w, _ = base_frame.shape
    pil_base = Image.fromarray(base_frame)
    
    for i in range(num_frames):
        t = i / max(1, num_frames - 1)
        cur_zoom = 1.0 + (zoom_end - 1.0) * (t ** 1.8)
        crop_w = int(w / cur_zoom)
        crop_h = int(h / cur_zoom)
        x1 = (w - crop_w) // 2
        y1 = (h - crop_h) // 2
        cropped = pil_base.crop((x1, y1, x1 + crop_w, y1 + crop_h))
        resized = cropped.resize((w, h), Image.Resampling.BILINEAR)
        frames.append(np.array(resized))
        
    return ImageSequenceClip(frames, fps=FPS)

def _create_impact_shake(base_frame: np.ndarray, duration: float, shake_intensity: int = 24) -> ImageSequenceClip:
    """هزة شاشة عنيفة وسريعة تعطي إحساس الصدمة الكارتونية (Impact Shake)."""
    frames = []
    num_frames = max(1, int(duration * FPS))
    
    for i in range(num_frames):
        t = i / max(1, num_frames - 1)
        decay = math.exp(-6.0 * t)
        dx = int(random.uniform(-1, 1) * shake_intensity * decay)
        dy = int(random.uniform(-1, 1) * shake_intensity * decay)
        shifted = np.roll(base_frame, dx, axis=1)
        shifted = np.roll(shifted, dy, axis=0)
        frames.append(shifted)
        
    return ImageSequenceClip(frames, fps=FPS)

def build_slapstick_video(shots_data: list[dict], output_path: Path, on_progress=None) -> Path:
    if on_progress:
        on_progress("✂️ المونتير يبدأ تقطيع اللقطات وتركيب المؤثرات الصوتية وحركات الكاميرا الخاطفة...")

    video_clips = []
    audio_clips = []
    current_timeline_time = 0.0
    
    for idx, shot in enumerate(shots_data):
        img_path = Path(shot["image_path"])
        # نسحب مدة اللقطة لتكون سريعة (0.8 - 1.4 ثانية) لنفس رتم كارتون لارفا
        raw_dur = float(shot.get("duration", 1.2))
        duration = max(0.7, min(1.4, raw_dur))
        
        frame_arr = _fit_image_vertical(img_path)
        sfx_name = shot.get("sfx_cue", "").lower().strip()
        
        # اختيار نوع الحركة البصرية بناءً على المؤثر الكوميدي
        if "bonk" in sfx_name or "splat" in sfx_name or "fall" in sfx_name:
            clip = _create_impact_shake(frame_arr, duration=duration, shake_intensity=26)
        elif "boing" in sfx_name or "jump" in sfx_name:
            clip = _create_punch_zoom(frame_arr, duration=duration, zoom_end=1.3)
        elif "gasp" in sfx_name:
            clip = _create_punch_zoom(frame_arr, duration=duration, zoom_end=1.2)
        else:
            clip = _create_punch_zoom(frame_arr, duration=duration, zoom_end=1.12)
            
        video_clips.append(clip)
        
        # ربط ملف المؤثر الصوتي
        sfx_file = SFX_DIR / f"{sfx_name}.wav"
        if not sfx_file.exists():
            if "boing" in sfx_name or "jump" in sfx_name:
                sfx_file = SFX_DIR / "boing.wav"
            elif "splat" in sfx_name or "slip" in sfx_name or "fall" in sfx_name:
                sfx_file = SFX_DIR / "splat.wav"
            elif "bonk" in sfx_name or "hit" in sfx_name:
                sfx_file = SFX_DIR / "bonk.wav"
            elif "whistle" in sfx_name:
                sfx_file = SFX_DIR / "whistle_fall.wav"
            elif "pop" in sfx_name:
                sfx_file = SFX_DIR / "pop.wav"
            elif "gasp" in sfx_name:
                sfx_file = SFX_DIR / "gasp.wav"
            else:
                sfx_file = SFX_DIR / "boing.wav"
                
        if sfx_file.exists():
            sfx_offset = 0.05  # توقيت فوري مع بداية اللقطة لتعزيز السرعة
            sfx_global_start = current_timeline_time + sfx_offset
            try:
                sfx_audio = AudioFileClip(str(sfx_file)).with_start(sfx_global_start)
                audio_clips.append(sfx_audio)
            except Exception as e:
                logger.warning(f"Failed to attach SFX {sfx_file}: {e}")
                
        current_timeline_time += duration

    # دمج مقاطع الفيديو
    final_video = concatenate_videoclips(video_clips, method="compose")
    total_duration = final_video.duration
    
    # إضافة الموسيقى الهزلية السريعة بالخلفية
    bgm_file = SFX_DIR / "funny_bgm.wav"
    if bgm_file.exists():
        try:
            bgm = AudioFileClip(str(bgm_file))
            bgm = bgm.subclipped(0, min(total_duration, bgm.duration)).with_effects([MultiplyVolume(0.35)])
            all_audios = [bgm] + audio_clips
            composite_audio = CompositeAudioClip(all_audios)
            final_video = final_video.with_audio(composite_audio)
        except Exception as e:
            logger.warning(f"Failed to mix BGM: {e}")
            if audio_clips:
                final_video = final_video.with_audio(CompositeAudioClip(audio_clips))
    elif audio_clips:
        final_video = final_video.with_audio(CompositeAudioClip(audio_clips))

    if on_progress:
        on_progress("🎬 جاري رندر وتصدير فيديو MP4 الكارتوني الخاطف فائق الدقة...")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    final_video.write_videofile(
        str(output_path),
        fps=FPS,
        codec="libx264",
        audio_codec="aac",
        preset="ultrafast",
        threads=1,
        logger=None,
    )
    
    try:
        final_video.close()
    except Exception:
        pass
        
    if on_progress:
        on_progress("✅ اكتمل المونتاج! كارتون سريع وخاطف ومضحك بدون أي كلام وبأعلى جودة!")
        
    return output_path
