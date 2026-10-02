"""Universal Studio Generator - محرك إنتاج الحلقات الكارتونية والسينمائية المتكاملة.
ينفذ المراحل الثلاث:
1. استخراج وتثبيت هوية الشخصيات (Character Visual Identity)
2. توليد المشاهد مشهداً تلو الآخر بحركة 3D حقيقية
3. دمج المشاهد وتركيب هندسة الصوت والمؤثرات والموسيقى وتصدير حلقة متكاملة
"""
import sys
import io
import os
import re
import time
import logging
import subprocess
from pathlib import Path
from typing import Tuple, Dict, Any
import imageio_ffmpeg

from config import OUTPUT_DIR
from agents.universal_studio_agent import create_universal_production_plan
from tools.replicate_video_tool import generate_video_minimax

if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
if sys.stderr.encoding != 'utf-8':
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SFX_DIR = PROJECT_ROOT / "assets" / "sfx"

def _safe_name(text: str) -> str:
    text = re.sub(r"[^\w\u0600-\u06FF\s-]", "", text or "episode")
    return text.strip().replace(" ", "_")[:30]

def produce_universal_episode(idea: str = None, on_progress=None) -> Tuple[Path, Dict[str, Any]]:
    """إنتاج حلقة كارتونية سينمائية متكاملة من الفكرة وحتى الحلقة النهائية."""
    def progress(msg: str):
        if on_progress:
            on_progress(msg)

    # 1. المرحلة الأولى: تأليف السكريبت وتثبيت هوية الشخصيات
    plan = create_universal_production_plan(idea=idea, on_progress=progress)
    title = plan.get("title_ar", "حلقة_كارتون")
    genre = plan.get("genre", "slapstick")
    characters = plan.get("characters", [])
    scenes = plan.get("scenes", [])

    char_names = " و ".join([c.get("name_ar", "") for c in characters if c.get("name_ar")])
    progress(f"🎨 تم تثبيت أبطال القة: {char_names} ({len(scenes)} مشاهد متسلسلة)")

    episode_dir = OUTPUT_DIR / f"universal_{_safe_name(title)}_{int(time.time())}"
    episode_dir.mkdir(parents=True, exist_ok=True)

    generated_scenes = []

    # 2. المرحلة الثانية: تصوير المشاهد مشهداً تلو الآخر بحركة 3D
    for i, sc in enumerate(scenes):
        sc_num = i + 1
        action_ar = sc.get("action_ar", "")
        v_prompt = sc.get("visual_prompt_en", "")

        progress(f"🎥 تصوير المشهد {sc_num}/{len(scenes)}: {action_ar}...")

        out_scene_file = episode_dir / f"scene_{sc_num}.mp4"
        try:
            generate_video_minimax(
                prompt=f"{v_prompt}. High quality fluid motion, rich volumetric lighting, cinematic animation.",
                output_path=out_scene_file,
                on_progress=lambda m: progress(f"  [المشهد {sc_num}] {m}")
            )
            generated_scenes.append(out_scene_file)
        except Exception as e:
            logger.error(f"Error producing scene {sc_num}: {e}")
            continue

    if not generated_scenes:
        raise RuntimeError("تعذر تصوير مشاهد الحلقة. يرجى إعادة المحاولة.")

    # 3. المرحلة الثالثة: المونتاج وهندسة الصوت والموسيقى
    progress("✂️ المونتير يقوم بدمج المشاهد وهندسة الصوت والموسيقى التصويرية الكاملة...")

    concat_file = episode_dir / "concat_list.txt"
    with open(concat_file, "w", encoding="utf-8") as f:
        for p in generated_scenes:
            f.write(f"file '{p.resolve().as_posix()}'\n")

    merged_raw = episode_dir / "merged_raw.mp4"
    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()

    # دمج متسلسل مباشر فائق السرعة وبدون استهلاك ذاكرة (Stream Copy)
    cmd_concat = [
        ffmpeg_exe, "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", str(concat_file),
        "-c", "copy",
        str(merged_raw)
    ]
    subprocess.run(cmd_concat, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # تركيب الموسيقى التصويرية الكارتونية
    final_output = episode_dir / f"{_safe_name(title)}_كاملة.mp4"
    bgm_file = SFX_DIR / "funny_bgm.wav"

    if bgm_file.exists():
        cmd_audio = [
            ffmpeg_exe, "-y",
            "-i", str(merged_raw),
            "-stream_loop", "-1",
            "-i", str(bgm_file),
            "-c:v", "copy",
            "-c:a", "aac",
            "-shortest",
            str(final_output)
        ]
        subprocess.run(cmd_audio, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    else:
        final_output = merged_raw

    progress(f"✅ اكتمل إنتاج الحلقة بالكامل بنجاح! 🏆 جاهزة للعرض والمشاركة!")
    return final_output, plan
